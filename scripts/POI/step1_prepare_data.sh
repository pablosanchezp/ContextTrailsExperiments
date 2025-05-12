#!/bin/bash

# List of cities
cities="NewYorkCity Tokyo PetalingJaya"

mapping_script="generate_pois_mapping.py"
mapped_lat_lon_script="generate_pois_details_mapping.py"
final_mapped_lat_long_script_wrong_substitute_by_midpoints="generate_POIs_data_substituteWrongByMidpoints.py"

generate_train_test="generate_final_training_test_files.py"


#CHANGE THIS PATH TO THE REPOSITORY OF THE DATA
path_source_data_repository="../../../ContextTrailsData"

mkdir -p ../../data
# For each city
for city in $cities; do
    echo "Processing city: $city"

    prefix=""

    if [[ $city == "NewYorkCity" ]]; then
        prefix="Q60_NewYorkCity"
    fi

    if [[ $city == "Tokyo" ]]; then
        prefix="Q308891_Tokyo"
    fi

    if [[ $city == "PetalingJaya" ]]; then
        prefix="Q864965_PetalingJaya"
    fi

    final_source_city_path="$path_source_data_repository"/data/$city
    final_source_destination_city_path="../../data/POI/$city"
    mkdir -p ../../data/POI/$city
    cp $final_source_city_path/"$prefix""_trails_weather_aggregated.zip" $final_source_destination_city_path
    unzip ../../data/POI/$city/"$prefix""_trails_weather_aggregated.zip" -d $final_source_destination_city_path
    cp $final_source_city_path/POIS_INFO_"$prefix"_lvl1_categories.csv $final_source_destination_city_path



    # Specific files
    input_file="$final_source_destination_city_path/${prefix}_trails_weather_aggregated.csv"
    out_mapping_file="$final_source_destination_city_path/${prefix}_POIS_Mapping.csv"
    poi_details_file=$final_source_destination_city_path/"POIS_INFO_"${prefix}"_lvl1_categories.csv"
    or_training_file="$final_source_destination_city_path/${prefix}_trails_weather_aggregated_Temp80train.csv"
    or_test_file="$final_source_destination_city_path/${prefix}_trails_weather_aggregated_Temp20test.csv"

    mapped_training_file="$final_source_destination_city_path/${prefix}_mapped_trails_weather_aggregated_Temp80train.csv"
    mapped_test_file="$final_source_destination_city_path/${prefix}_mapped_trails_weather_aggregated_Temp20test.csv"

    #Now the outputfiles
    output_file="$final_source_destination_city_path/${prefix}_mapped_lat_lon.csv"

    # POI mapping
    echo "Generating POIS mapping for $prefix..."
    python "$mapping_script" --input_file "$input_file" --output_file "$out_mapping_file"

    # Execute the script to map the latitudes and longitudes
    echo "Generating mapped lat/lon for $city..."
    python "$mapped_lat_lon_script" --input_file "$poi_details_file" --mapping_file "$out_mapping_file" --output_file "$output_file"

    # Training and test
    python "$generate_train_test" --input_file "$or_training_file" --mapping_file "$out_mapping_file" --output_file "$mapped_training_file"
    python "$generate_train_test" --input_file "$or_test_file" --mapping_file "$out_mapping_file" --output_file "$mapped_test_file"

    # We generate the new coordinates files
    output_substituting_wrong_coordinates_by_midpoint_file="$final_source_destination_city_path/${prefix}_mapped_lat_lon_wrong_coordinates_by_midpoint.csv"
    python "$final_mapped_lat_long_script_wrong_substitute_by_midpoints" --input_file "$output_file" --output_file "$output_substituting_wrong_coordinates_by_midpoint_file"

    echo "Finished processing $city."
done
