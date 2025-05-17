import pandas as pd
import logging

from ranx import Qrels, Run, evaluate

CITIES = ['NewYork', 'Tokyo', 'PentalingJaya']
ALGORITHMS = ['Random', 'MostPop', 'PopGeoNN']
CONTEXTS = ['full', 'time', 'weather']

TEST_DATA_FILE = 'data/predictions/{}/test_context.csv'
PREDICTIONS_FILES = 'data/predictions/{}/rec_{}_{}_context.csv'
METRIC = "ndcg@5"

def init_logger():
    logging.basicConfig(
        filename='logs/evaluation.log',
        level=logging.INFO, 
        format='%(asctime)s - %(message)s')

def load_qrels(city):
    
    test_df = pd.read_csv(TEST_DATA_FILE.format(city), sep='\t', names=['user_id', 'poi', 'rating', 'timestamp', 'temperature', 'precipitations', 'weather_type'])
    test_df['poi'] = test_df['poi'].astype(str)

    qrels = Qrels.from_df(
        df = test_df,
        q_id_col = 'user_id',
        doc_id_col = 'poi',
        score_col = 'rating'
    )

    return qrels

def load_run(city, algorithm, context):
    
    predictions_df = pd.read_csv(PREDICTIONS_FILES.format(city, algorithm, context), sep='\t', names=['user_id', 'poi', 'rating', 'rank'])

    predictions_d# Almacenamos los resultados en un csvf['poi'] = predictions_df['poi'].astype(str)

    run = Run.from_df(
        df = predictions_df,
        q_id_col = 'user_id',
        doc_id_col = 'poi',
        score_col = 'rating'
    )

    return run

def main():

    init_logger()

    metrics_evaluations = []

    for city in CITIES:
        
        qrels = load_qrels(city)

        for algorithm in ALGORITHMS:

            for context in CONTEXTS:

                logging.info(f'Evaluating predictions for {city} with {algorithm} algorithm and {context} context...')

                run = load_run(city, algorithm, context)

                results = evaluate(
                    qrels = qrels,
                    run = run,
                    metrics = [METRIC]
                )

                logging.info(f'{METRIC} for {city} with {algorithm} algorithm and {context} context: {results}')

                metrics_evaluations.append({
                    'city': city,
                    'algorithm': algorithm,
                    'context': context,
                    'metric': METRIC,
                    'value': results
                })

    results_df = pd.DataFrame(metrics_evaluations)
    results_df.to_csv('data/predictions/evaluation.csv', sep='\t', header=False, index=False)

    logging.info('Evaluation done!')

if __name__ == '__main__':
    main()