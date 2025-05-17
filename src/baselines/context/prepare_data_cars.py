import pandas as pd
import numpy as np
import os

# Constants
CITIES = ['NewYork', 'Tokyo', 'PetalingJaya']
TRAIN_FILES = 'data/raw/{}/{}_mapped_trails_weather_aggregated_Temp80train.csv'
TEST_FILES = 'data/raw/{}/{}_mapped_trails_weather_aggregated_Temp20test.csv'
POIS_FILES = 'data/raw/{}/POIS_{}.csv'
POIS_INFO_FILES = 'data/raw/{}/POIS_INFO_{}.csv'
WEATHER_PATH = 'data/raw/{}/weather/'

# Function to get the weather for a given timestamp
def get_weather(timestamp, df_weather):
    return df_weather.iloc[(df_weather['timestamp']-timestamp).abs().argsort()[:1]].values[0][:-1]

# Function to get the weather for a dataframe
def add_context(df, df_weather):
    weathers = df['timestamp'].apply(lambda x: get_weather(x, df_weather))
    df['temperature'] = weathers.apply(lambda x: x[0])
    df['preciptype'] = weathers.apply(lambda x: x[1])
    df['weather'] = weathers.apply(lambda x: x[2])
    return df

def main():

    for city in CITIES:
        print('Cargando datos de entrenamiento de la ciudad de {}'.format(city))

        # Load the training data
        train_df = pd.read_csv(TRAIN_FILES.format(city,city), sep='\t', names=['user', 'item', 'rating', 'timestamp'])
        print('Datos de entrenamiento:', train_df.shape)
        
        # Load the test data
        test_df = pd.read_csv(TEST_FILES.format(city,city), sep='\t', names=['user', 'item', 'rating', 'timestamp'])
        print('Datos de test:', test_df.shape)

        # Load the POIS data
        pois_df = pd.read_csv(POIS_FILES.format(city,city), names=['fsq_id'])
        pois_df['item'] = np.arange(pois_df.shape[0])
        pois_df.set_index('fsq_id', inplace=True)
        pois_df.reset_index(inplace=True)
        print('Datos de POIS:', pois_df.shape)

        # Load the POIS_INFO data
        pois_info_df = pd.read_csv(POIS_INFO_FILES.format(city,city))
        print('Datos de POIS_INFO en bruto:', pois_info_df.shape)

        # Concat dataframes
        pois_df = pois_df.merge(pois_info_df, on='fsq_id', how='left')
        pois_cleaned_df = pois_df.drop(columns=['fsq_id', 'latitude', 'longitude', 'category','price', 'rating', 'total_ratings', 'total_tips'])
        print('Datos de POIS_INFO:', pois_cleaned_df.shape)

        # Load the weather data
        weather_files = [f for f in os.listdir(WEATHER_PATH.format(city)) if f.endswith('.csv')]
        weather_df = pd.concat([pd.read_csv(WEATHER_PATH.format(city) + f) for f in weather_files])
        print('Datos de clima:', weather_df.shape)

        # Convert datetime to timestamp
        weather_df['timestamp'] = pd.to_datetime(weather_df['datetime']).astype(int) / 10**9
        weather_df.drop(columns=['datetime'], inplace=True)

        # Remove unnecessary columns
        weather_cleaned_df = weather_df.drop(columns=['name', 'feelslike', 'dew', 'humidity', 'precip', 'precipprob', 'snow', 'snowdepth', 'windgust', 'windspeed', 'winddir', 'sealevelpressure', 'cloudcover', 'visibility', 'solarradiation', 'solarenergy', 'uvindex', 'severerisk','icon', 'stations'])

        # NaN values in preciptype are filled with 'none'
        weather_cleaned_df['preciptype'] = weather_cleaned_df['preciptype'].fillna('none')
        print('Datos de clima limpios:', weather_cleaned_df.shape)

        # Add context to train_df
        train_df = add_context(
train_df, weather_cleaned_df)
        print('Datos de entrenamiento con contexto:', train_df.shape)

        # Add context to test_df
        test_df = add_context(test_df, weather_cleaned_df)
        print('Datos de test con contexto:', test_df.shape)

        # check if there are any NaN values in the dataframes
        print('Valores NaN en train_df:', train_df.isnull().sum().sum())
        print('Valores NaN en test_df:', test_df.isnull().sum().sum())

        # save the dataframes to csv files
        train_df.to_csv('data/cleaned/{}/train.csv'.format(city), sep='\t', header=False, index=False)
        test_df.to_csv('data/cleaned/{}/test.csv'.format(city), sep='\t', header=False, index=False)
        pois_cleaned_df.to_csv('data/cleaned/{}/pois_info.csv'.format(city), sep='\t', header=False, index=False)

if __name__ == '__main__':
    main()