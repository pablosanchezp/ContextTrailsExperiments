import pandas as pd
import argparse

def generate_mapped_lat_lon(input_csv: str, mapping_csv: str, output_csv: str, use_feat:bool = False):
    """
    Generates a file with the mapped POI ID, latitude, and longitude, without headers.

    Parameters:
    - input_csv: str, path to the input CSV file containing POI details.
    - mapping_csv: str, path to the POI mapping CSV file.
    - output_csv: str, path to the output CSV file.
    """
    # Read the input and mapping files
    poi_data = None
    if use_feat:
        poi_data = pd.read_csv(input_csv, usecols=['fsq_id', 'latitude', 'longitude', 'category_lvlFs'], sep=",")
    else:
        poi_data = pd.read_csv(input_csv, usecols=['fsq_id', 'latitude', 'longitude'], sep=",")
    mapping_data = pd.read_csv(mapping_csv, sep="\t")

    # Create a dictionary for mapping fsq_id to mapped_id
    poi_mapping = dict(zip(mapping_data['original_venue_id'], mapping_data['mapped_id']))

    # Add the mapped ID column to the POI data
    poi_data['mapped_id'] = poi_data['fsq_id'].map(poi_mapping)
    unmatched = poi_data[poi_data['mapped_id'].isna()]
    if not unmatched.empty:
        print("Empty fsq_id")
        print(unmatched['fsq_id'].tolist())

    poi_data = poi_data.dropna(subset=['mapped_id'])
    poi_data['mapped_id'] = poi_data['mapped_id'].astype(int)


    # Filter the required columns
    if use_feat:
        result_data = poi_data[['mapped_id', 'latitude', 'longitude', 'category_lvlFs']]
    else:
        result_data = poi_data[['mapped_id', 'latitude', 'longitude']]

    # Write to the output file without headers
    result_data.to_csv(output_csv, index=False, header=False, sep="\t")

    print(f"Mapped file '{output_csv}' has been generated.")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate a file with mapped POI ID, latitude, and longitude.")
    parser.add_argument(
        "-i", "--input_file",
        type=str,
        required=True,
        help="Path to the input CSV file containing POI details."
    )
    parser.add_argument(
        "-m", "--mapping_file",
        type=str,
        required=True,
        help="Path to the POI mapping CSV file."
    )
    parser.add_argument(
        "-o", "--output_file",
        type=str,
        required=True,
        help="Path to the output CSV file."
    )

    parser.add_argument(
        "-f", "--use_feature",
        type=bool,
        required=False,
        help="Check if using feature or not.",
        default=False
    )

    # Parse arguments
    args = parser.parse_args()

    # Generate the mapped lat/lon file
    generate_mapped_lat_lon(args.input_file, args.mapping_file, args.output_file, args.use_feature)
