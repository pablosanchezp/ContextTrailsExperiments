import pandas as pd
import numpy as np
import time

from scipy.spatial import distance

from concurrent.futures import ThreadPoolExecutor

class ContextPosfilterig:

    def __init__(self, train_data, pois_info):
        self.train_data = train_data
        self.pois_info = pois_info

        self.TIMES_MOMENTS = ['Weekday_EarlyMorning', 'Weekday_Morning', 'Weekday_Afternoon','Weekday_Night', 'Weekend_EarlyMorning', 'Weekend_Morning','Weekend_Afternoon', 'Weekend_Night']

    def __get_context_information(self):
        self.context_information = dict()
        self.context_information['temperature_quartiles'] = self.train_data['temperature'].quantile([0.25, 0.5, 0.75]).values
        self.context_information['precipitation_types'] = self.train_data['precipitation_type'].unique()
        self.context_information['weather_conditions'] = self.train_data['condition'].unique()

    def __get_poi_context_profiles(self, poi_id):
        poi_context_profile = dict()

        poi_context_profile['opening_time'] = self.pois_info.loc[self.pois_info['poi'] == poi_id, 'Weekday_EarlyMorning':'Weekend_Night'].values[0]

        poi_train_data = self.train_data.loc[self.train_data['poi'] == poi_id].values

        poi_context_profile['temperature'] = np.zeros(4, dtype=int)
        poi_context_profile['precipitation_type'] = np.zeros(len(self.context_information['precipitation_types']), dtype=int)
        poi_context_profile['condition'] = np.zeros(len(self.context_information['weather_conditions']), dtype=int)

        temp_bins = self.context_information['temperature_quartiles']
        temperature_indices = np.searchsorted(temp_bins, poi_train_data[:, 4])  # Columna temperatura
        np.add.at(poi_context_profile['temperature'], temperature_indices, 1)
        
        unique_precipitations, precipitation_counts = np.unique(poi_train_data[:, 5], return_counts=True)
        unique_conditions, condition_counts = np.unique(poi_train_data[:, 6], return_counts=True)

        count_prec_dict = dict(zip(unique_precipitations, precipitation_counts))
        count_cond_dict = dict(zip(unique_conditions, condition_counts))

        poi_context_profile['precipitation_type'][:] = [count_prec_dict.get(p, 0) for p in self.context_information['precipitation_types']]
        poi_context_profile['condition'][:] = [count_cond_dict.get(c, 0) for c in self.context_information['weather_conditions']]
             
        return poi_context_profile
    
    def __get_time_profile(self, timestamp):
        weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        early_morning = ['00', '01', '02', '03', '04', '05']
        morning = ['06', '07', '08', '09', '10', '11']
        afternoon = ['12', '13', '14', '15', '16', '17']

        timestamp = pd.to_datetime(timestamp, unit='s')
        day = timestamp.strftime('%A')
        hour = timestamp.strftime('%H')

        if day in weekday:
            day = 'Weekday'
        else:
            day = 'Weekend'

        if hour in early_morning:
            hour = 'EarlyMorning'
        elif hour in morning:
            hour = 'Morning'
        elif hour in afternoon:
            hour = 'Afternoon'
        else:
            hour = 'Night'

        return "{}_{}".format(day, hour)
    
    def fit(self):
        self.__get_context_information()
        self.context_profiles = dict()
        unique_poids = self.train_data['poi'].unique()
        for poi_id in unique_poids:
            self.context_profiles[poi_id] = self.__get_poi_context_profiles(poi_id)

    def get_query_context_profile(self, interaction):
        query_profile = {}

        query_profile['time_interaction'] = np.zeros(8).astype(int)

        time_moment = self.__get_time_profile(interaction[3])
        query_profile['time_interaction'][self.TIMES_MOMENTS.index(time_moment)] = 1

        query_profile['temperature'] = np.zeros(4).astype(int)
        
        temp_bins = self.context_information['temperature_quartiles']
        temperature_indices = np.searchsorted(temp_bins, interaction[4])  # Columna temperatura
        np.add.at(query_profile['temperature'], temperature_indices, 1)

        if interaction[4] <= self.context_information['temperature_quartiles'][0]:
            query_profile['temperature'][0] = 1
        elif interaction[4] <= self.context_information['temperature_quartiles'][1]:
            query_profile['temperature'][1] = 1
        elif interaction[4] <= self.context_information['temperature_quartiles'][2]:
            query_profile['temperature'][2] = 1
        else:
            query_profile['temperature'][3] = 1

        query_profile['precipitation'] = np.zeros(len(self.context_information['precipitation_types'])).astype(int)

        if interaction[5] in self.context_information['precipitation_types']:
            query_profile['precipitation'][np.where(self.context_information['precipitation_types'] == interaction[5])[0][0]] = 1

        query_profile['condition'] = np.zeros(len(self.context_information['weather_conditions'])).astype(int)

        if interaction[6] in self.context_information['weather_conditions']:
            query_profile['condition'][np.where(self.context_information['weather_conditions'] == interaction[6])[0][0]] = 1

        return query_profile
    
    def __filter_by_time(self, context_profile, query_profile):
        if np.all(context_profile == -1):
            return 0
        else:
            return np.dot(context_profile, query_profile)
        
    def __cosine_similarity(self, poi_context_profile, query_profile):
        return 1 - distance.cosine(poi_context_profile, query_profile)
    
    def get_poi_context_score(self, poi_context, query_context, context_type = None):
        score = 0

        if context_type == 'time' or context_type == None:
            score = float('-inf')

            if self.__filter_by_time(poi_context['opening_time'], query_context['time_interaction']) != 0:
                score = self.__filter_by_time(poi_context['opening_time'], query_context['time_interaction'])
            else:
                score = float('-inf')
            
        if context_type == 'weather' or context_type == None:
            if score == float('-inf'):
                return score
            
            temperature_score = self.__cosine_similarity(poi_context['temperature'], query_context['temperature'])
            precipitation_score = self.__cosine_similarity(poi_context['precipitation_type'], query_context['precipitation'])
            condition_score = self.__cosine_similarity(poi_context['condition'], query_context['condition'])

            score = temperature_score + precipitation_score + condition_score/3

        return score

    def recalculate_interaction_predictions(self, predictions, interaction, timestamp, context_type=None):
        query_context = self.get_query_context_profile(interaction)

        pois = predictions['poi'].values
        context_profiles = [self.context_profiles[poi] for poi in pois]
        
        context_scores = np.array([self.get_poi_context_score(cp, query_context, context_type=context_type) for cp in context_profiles])

        new_predictions = predictions.copy()
        new_predictions['rating'] = context_scores

        sorted_indices = np.argsort(-context_scores)  
        new_predictions = new_predictions.iloc[sorted_indices].reset_index(drop=True)

        new_predictions['rank'] = np.arange(1, len(new_predictions) + 1)
        
        new_predictions['user'] = new_predictions['user'].astype(str) + '_' + str(int(timestamp))

        return new_predictions

    def recalculate_recommendations(self, test_df, predictions_df, context_type):
        start = time.time()

        results = []

        predictions_by_user = {user: group for user, group in predictions_df.groupby('user')}

        for i, interaction in enumerate(test_df.itertuples(index=False)):  # itertuples es más rápido que iloc
            if i % 100 == 0 and i > 0:
                loop_time = time.time() - start
                start = time.time()
                print(f"Recalculating interaction {i} of {len(test_df)}. Time: {loop_time:.4f} s")

            user = interaction.user
            timestamp = interaction.timestamp
            predictions = predictions_by_user.get(user, None)

            if predictions is not None:
                new_predictions = self.recalculate_interaction_predictions(predictions, interaction, timestamp, context_type)
                results.append(new_predictions)

        new_predictions_df = pd.concat(results, ignore_index=True)

        return new_predictions_df