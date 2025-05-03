import pandas as pd
import argparse
from datetime import datetime

def process_user_poi_data(input_csv: str, mapping_csv: str, output_csv: str):
    """
    Processes the user-POI interaction data to generate a file with user ID, mapped POI ID, rating, and timestamp.

    Parameters:
    - input_csv: str, path to the input CSV file containing the user and venue interaction data.
    - mapping_csv: str, path to the POI mapping CSV file.
    - output_csv: str, path to the output CSV file to write the processed data.
    """
    # Read the input and mapping files
    user_data = pd.read_csv(input_csv, sep=";")
    mapping_data = pd.read_csv(mapping_csv, sep="\t")

    # Create a dictionary for mapping venue IDs to integers
    venue_mapping = dict(zip(mapping_data['original_venue_id'], mapping_data['mapped_id']))

    # Replace venue_id with the mapped integer
    user_data['mapped_venue_id'] = user_data['venue_id'].map(venue_mapping)

    # Convertir la columna 'timestamp' a datetime, manejar errores y asignar UTC si es necesario
    user_data['timestamp'] = user_data['timestamp'].str.replace(' ', 'T')

    
    # Convertir la columna 'timestamp' a datetime
    user_data['timestamp'] = pd.to_datetime(user_data['timestamp'], errors='coerce')
    user_data['timestamp'] = user_data['timestamp'].apply(lambda x: datetime.timestamp(x) if pd.notnull(x) else None)


    # Select relevant columns
    processed_data = user_data[['user_id', 'mapped_venue_id', 'number_of_visits', 'timestamp']]
    processed_data.rename(columns={'number_of_visits': 'rating'}, inplace=True)

    # Write the output to a CSV file
    processed_data.to_csv(output_csv, index=False, sep="\t", header=False)

    print(f"Processed data has been written to '{output_csv}'.")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process user-POI data and generate a formatted output.")
    parser.add_argument(
        "-i", "--input_file",
        type=str,
        required=True,
        help="Path to the input CSV file containing user and venue interaction data."
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
        help="Path to the output CSV file to save the processed data."
    )

    # Parse arguments
    args = parser.parse_args()

    # Process the data
    process_user_poi_data(args.input_file, args.mapping_file, args.output_file)
