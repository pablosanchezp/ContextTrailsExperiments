import pandas as pd
import numpy as np
import logging
import time

from context_posfiltering import ContextPosfilterig

# Constants
CITIES = ['NewYork', 'Tokyo', 'PentalingJaya']
ALGORITHMS = ['Random', 'MostPop', 'PopGeoNN']

TRAIN_DATA_FILE = 'data/cleaned/{}/train.csv'
TEST_DATA_FILE = 'data/cleaned/{}/test.csv'
POIS_INFO_DATA_FILE = 'data/cleaned/{}/pois_info.csv'
RECOMMENDATIONS_FILES = 'data/cleaned/{}/rec_{}.csv'
PREDICTIONS_FULL_FILES = 'data/predictions/{}/rec_{}_full_context.csv'
PREDICTIONS_TIME_FILES = 'data/predictions/{}/rec_{}_time_context.csv'
PREDICTIONS_WEATHER_FILES = 'data/predictions/{}/rec_{}_weather_context.csv'

def init_logger():
    logging.basicConfig(
        filename='logs/full_experiment.log',
        level=logging.INFO, 
        format='%(asctime)s - %(message)s')


def main():

    init_logger()

    for city in CITIES:

        logging.info(f'Running experiment for {city}...')

        # Load data
        train = pd.read_csv(TRAIN_DATA_FILE.format(city), sep='\t', names=['user', 'poi', 'rating', 'timestamp', 'temperature', 'precipitation_type', 'condition'])
        test = pd.read_csv(TEST_DATA_FILE.format(city), sep='\t', names=['user', 'poi', 'rating', 'timestamp', 'temperature', 'precipitation_type', 'condition'])
        pois_info = pd.read_csv(POIS_INFO_DATA_FILE.format(city), sep='\t', names=['poi', 'Weekday_EarlyMorning','Weekday_Morning','Weekday_Afternoon','Weekday_Night','Weekend_EarlyMorning','Weekend_Morning','Weekend_Afternoon','Weekend_Night'])

        logging.info('Data loaded...')
        logging.info(f'Train shape: {train.shape}')
        logging.info(f'Test shape: {test.shape}')
        logging.info(f'POIs info shape: {pois_info.shape}')

        # Create context-posfiltering object
        context_posfiltering = ContextPosfilterig(train, pois_info)
        context_posfiltering.fit()

        logging.info('Context-posfiltering object created...')

        for algorithm in ALGORITHMS:
            
            logging.info(f'Running algorithm {algorithm}...')

            # Load recommendations
            recommendations = pd.read_csv(RECOMMENDATIONS_FILES.format(city, algorithm), sep='\t', names=['user', 'poi', 'rating', 'rank'])

            logging.info('Recommendations loaded...')
            logging.info(f'Recommendations shape: {recommendations.shape}')

            # Predict
            predictions_full = context_posfiltering.recalculate_recommendations(test, recommendations, context_type=None)
            predictions_time = context_posfiltering.recalculate_recommendations(test, recommendations, context_type='time')
            predictions_weather = context_posfiltering.recalculate_recommendations(test, recommendations, context_type='weather')

            logging.info('Predictions created...')

            # Save predictions
            predictions_full.to_csv(PREDICTIONS_FULL_FILES.format(city, algorithm), sep='\t', header=False, index=False)
            predictions_time.to_csv(PREDICTIONS_TIME_FILES.format(city, algorithm), sep='\t', header=False, index=False)
            predictions_weather.to_csv(PREDICTIONS_WEATHER_FILES.format(city, algorithm), sep='\t', header=False, index=False)

            logging.info('Predictions saved...')

        # Modify the user_id of test to contain the timestamp
        test['user'] = test['user'].astype(str) + '_' + test['timestamp'].astype(int).astype(str)

        # Save the new test for evaluation
        test.to_csv(f'data/predictions/{city}/test_context.csv', sep='\t', header=False, index=False)

        logging.info(f'Experiment for {city} done!')

    logging.info('Full experiment done!')

if __name__ == '__main__':
    main()