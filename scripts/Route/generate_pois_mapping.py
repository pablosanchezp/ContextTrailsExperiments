import pandas as pd
import argparse

def generate_poi_mapping(input_csv: str, output_csv: str):
    """
    Generates a mapping from venue_id to an internal integer ID and writes it to a CSV file.

    Parameters:
    - input_csv: str, path to the input CSV file.
    - output_csv: str, path to the output CSV file for the POI mapping.
    """
    # Read the input CSV
    df = pd.read_csv(input_csv, usecols=['venue_id'], sep=";")

    # Get unique venue_ids and map them to integers
    unique_venues = df['venue_id'].drop_duplicates().reset_index(drop=True)
    venue_mapping = pd.DataFrame({
        'original_venue_id': unique_venues,
        'mapped_id': range(len(unique_venues))
    })

    # Write the mapping to a CSV file
    venue_mapping.to_csv(output_csv, index=False, sep="\t")

    print(f"POI mapping file '{output_csv}' has been generated.")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate a POI mapping file from a venue_id column.")
    parser.add_argument(
        "-i", "--input_file", 
        type=str, 
        required=True, 
        help="Path to the input CSV file containing the venue_id column."
    )
    parser.add_argument(
        "-o", "--output_file", 
        type=str, 
        required=True, 
        help="Path to the output CSV file for the POI mapping."
    )

    # Parse arguments
    args = parser.parse_args()

    # Generate the POI mapping
    generate_poi_mapping(args.input_file, args.output_file)
