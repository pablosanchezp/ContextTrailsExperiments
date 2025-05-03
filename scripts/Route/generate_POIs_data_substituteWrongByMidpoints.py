import pandas as pd
import math
import argparse

def calculate_midpoint(df):
    """
    Calculate the midpoint of valid coordinates.
    """
    valid_coords = df[(df['latitude'] != -1) & (df['longitude'] != -1)]

    if valid_coords.empty:
        raise ValueError("No valid coordinates found to calculate the midpoint.")

    x = sum(math.cos(math.radians(lat)) * math.cos(math.radians(lon)) for lat, lon in zip(valid_coords['latitude'], valid_coords['longitude']))
    y = sum(math.cos(math.radians(lat)) * math.sin(math.radians(lon)) for lat, lon in zip(valid_coords['latitude'], valid_coords['longitude']))
    z = sum(math.sin(math.radians(lat)) for lat in valid_coords['latitude'])

    total = len(valid_coords)
    x /= total
    y /= total
    z /= total

    central_longitude = math.atan2(y, x)
    central_latitude = math.atan2(z, math.sqrt(x ** 2 + y ** 2))

    return math.degrees(central_latitude), math.degrees(central_longitude)

def process_poi_coordinates(input_file, output_file):
    """
    Process the POI coordinates by replacing invalid coordinates with the midpoint.
    """
    # Load the file without headers
    df = pd.read_csv(input_file, header=None, sep="\t")

    # Determine the number of columns and assign appropriate headers
    if df.shape[1] == 3:
        df.columns = ['fsq_id', 'latitude', 'longitude']
    elif df.shape[1] == 4:
        df.columns = ['fsq_id', 'latitude', 'longitude', 'category_lvlFs']
    else:
        raise ValueError("Unexpected number of columns. The file must have 3 or 4 columns.")

    # Calculate the midpoint for valid coordinates
    midpoint_lat, midpoint_lon = calculate_midpoint(df)

    # Replace invalid coordinates with the midpoint
    df.loc[(df['latitude'] == -1) & (df['longitude'] == -1), ['latitude', 'longitude']] = [midpoint_lat, midpoint_lon]

    # Save the processed dataframe
    df.to_csv(output_file, index=False, header=False, sep="\t")

def main():
    parser = argparse.ArgumentParser(description="Replace invalid POI coordinates with the calculated midpoint.")
    parser.add_argument('--input_file', required=True, help="Path to the input CSV file without headers.")
    parser.add_argument('--output_file', required=True, help="Path to save the processed CSV file.")
    args = parser.parse_args()

    try:
        process_poi_coordinates(args.input_file, args.output_file)
        print(f"Processed file saved to {args.output_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
