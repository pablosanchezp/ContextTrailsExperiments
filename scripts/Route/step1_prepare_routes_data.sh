#!/bin/bash

# List of cities
cities="NewYorkCity Tokyo PetalingJaya"

mapping_script="generate_pois_mapping.py"
mapped_lat_lon_script="generate_pois_details_mapping.py"
final_mapped_lat_long_script_wrong_substitute_by_midpoints="generate_POIs_data_substituteWrongByMidpoints.py"

# We maintain the trail_id
generate_train_test="generate_final_route_training_test_files.py"


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
    final_source_destination_city_path="../../data/Route/$city"

    mkdir -p ../../data/Route/$city
    cp $final_source_city_path/"$prefix""_trails_weather.zip" $final_source_destination_city_path
    unzip ../../data/Route/$city/"$prefix""_trails_weather.zip" -d $final_source_destination_city_path
    cp $final_source_city_path/"$prefix""_trails_routes_2_minroutes_4_minPois_training_test.zip" $final_source_destination_city_path
    unzip ../../data/Route/$city/"$prefix""_trails_routes_2_minroutes_4_minPois_training_test.zip" -d $final_source_destination_city_path
    cp $final_source_city_path/POIS_INFO_"$prefix"_lvl1_categories.csv $final_source_destination_city_path


    # Specific files -> Remember, for the routes we DONT use the aggregated
    input_file="$final_source_destination_city_path/${prefix}_trails_weather.csv"
    poi_details_file=$final_source_destination_city_path/"POIS_INFO_"${prefix}"_lvl1_categories.csv"

    out_mapping_file="$final_source_destination_city_path/${prefix}_POIS_Mapping.csv"
    or_training_file="$final_source_destination_city_path/${prefix}_trails_weather_2_minroutes_4_minPOIs_TestRouteTraining.csv"
    or_test_file="$final_source_destination_city_path/${prefix}_trails_weather_2_minroutes_4_minPOIs_TestRouteTest.csv"

    mapped_training_file="$final_source_destination_city_path/${prefix}_mapped_trails_weather_2_minroutes_4_minPOIs_TestRouteTraining.csv"
    mapped_test_file="$final_source_destination_city_path/${prefix}_mapped_trails_weather_2_minroutes_4_minPOIs_TestRouteTest.csv"

    #Now the outputfiles
    output_file="$final_source_destination_city_path/${prefix}_mapped_lat_lon.csv"
    output_file_feat="$final_source_destination_city_path/${prefix}_mapped_feature.csv"

    # POI mapping
    echo "Generating POIS mapping for $prefix..."
    python "$mapping_script" --input_file "$input_file" --output_file "$out_mapping_file"

    # Ejecutar el script para generar latitud y longitud mapeadas
    echo "Generating mapped lat/lon for $prefix..."
    python "$mapped_lat_lon_script" --input_file "$poi_details_file" --mapping_file "$out_mapping_file" --output_file "$output_file" --use_feature "True"

    # Training and test
    python "$generate_train_test" --input_file "$or_training_file" --mapping_file "$out_mapping_file" --output_file "$mapped_training_file"
    python "$generate_train_test" --input_file "$or_test_file" --mapping_file "$out_mapping_file" --output_file "$mapped_test_file"

    output_substituting_wrong_coordinates_by_midpoint_file="$final_source_destination_city_path/${prefix}_mapped_lat_lon_wrong_coordinates_by_midpoint.csv"
    python "$final_mapped_lat_long_script_wrong_substitute_by_midpoints" --input_file "$output_file" --output_file "$output_substituting_wrong_coordinates_by_midpoint_file"


    echo "Finished processing $city."
done
