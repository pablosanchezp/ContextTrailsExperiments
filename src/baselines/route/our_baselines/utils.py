import math
import pandas as pd

def haversine(lat1:float, lon1:float, lat2:float, lon2:float):
     
    # distance between latitudes
    # and longitudes
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0
 
    # convert to radians
    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0
 
    # apply formulae
    a = (pow(math.sin(dLat / 2), 2) +
         pow(math.sin(dLon / 2), 2) *
             math.cos(lat1) * math.cos(lat2));
    rad = 6371
    c = 2 * math.asin(math.sqrt(a))
    return rad * c

#NOT USED
def read_poi_file(file_path: str, simple=True) -> tuple:
    """
    Reads a points-of-interest file and returns a DataFrame with selected columns,
    along with mapping dictionaries for IDs and categories.

    Parameters:
    - file_path: str, path to the CSV file.

    Returns:
    - df: pandas.DataFrame, DataFrame with the selected columns.
    - id_to_int: dict, mapping from the original 'fsq_id' to integers.
    - int_to_id: dict, mapping from integers back to the original 'fsq_id'.
    - category_to_int: dict, mapping from category values to integers (if 'category_lvlFs' is present).
    - int_to_category: dict, mapping from integers back to category values (if 'category_lvlFs' is present).
    """
    if simple: # Only the necessary 
        columns_to_read = ["fsq_id", "latitude", "longitude", "category_lvlFs"]
    else:
        columns_to_read = ["fsq_id", "latitude", "longitude", "category_lvlFs", "price", "rating", "total_ratings", 
                           "Weekday_EarlyMorning", "Weekday_Morning", "Weekday_Afternoon", "Weekday_Night", 
                           "Weekend_EarlyMorning", "Weekend_Morning", "Weekend_Afternoon", "Weekend_Night"]

    fsq_id = 'fsq_id'
    categories_col = 'category_lvlFs'     
    # Read the CSV file with only the specified columns
    df = pd.read_csv(file_path, usecols=columns_to_read)

    # Create a mapping from 'fsq_id' to integers
    unique_ids = df[fsq_id].unique()
    id_to_int = {id_: idx for idx, id_ in enumerate(unique_ids)}
    int_to_id = {idx: id_ for id_, idx in id_to_int.items()}
    
    # Replace 'fsq_id' in the DataFrame with its integer mapping
    df[fsq_id] = df[fsq_id].map(id_to_int)

    unique_categories = df[categories_col].dropna().unique()
    category_to_int = {cat: idx for idx, cat in enumerate(unique_categories)}
    int_to_category = {idx: cat for cat, idx in category_to_int.items()}
    
    # Replace category values in the DataFrame with their integer mappings
    df[categories_col] = df[categories_col].map(category_to_int)


    return df, id_to_int, int_to_id, category_to_int, int_to_category


#NOT USED
def read_trail_file(file_path: str, id_to_int: dict) -> pd.DataFrame:
    """
    Reads a trail file and replaces 'venue_id' with its corresponding integer mapping.

    Parameters:
    - file_path: str, path to the CSV file.
    - id_to_int: dict, mapping from original venue_id (fsq_id) to integers.

    Returns:
    - df: pandas.DataFrame, DataFrame with all original columns, but 'venue_id' replaced by its mapped integer.
    """
    # Define the expected columns
    expected_columns = ['trail_id', 'user_id', 'venue_id', 'timestamp', 'temp', 'precip', 'windspeed', 'preciptype', 'conditions']

    # Read the CSV file
    df = pd.read_csv(file_path)

    # Validate the structure of the file
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"The file is missing the following columns: {missing_columns}")

    # Replace 'venue_id' with its corresponding integer using the provided dictionary
    if 'venue_id' in df.columns:
        df['venue_id'] = df['venue_id'].map(id_to_int)
        if df['venue_id'].isnull().any():
            unmapped_ids = df[df['venue_id'].isnull()]['venue_id'].unique()
            raise ValueError(f"The following venue IDs could not be mapped: {unmapped_ids}")
    else:
        raise ValueError("'venue_id' column is missing in the file.")

    return df
