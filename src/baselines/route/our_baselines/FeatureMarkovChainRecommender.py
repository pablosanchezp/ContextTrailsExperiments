from Recommenders import BasicRouteRecommender, TieBreaker, VisitFilter
import utils as ut
from typing import List
from enum import Enum
import numpy as np
import pandas as pd

class FeatureMarkovRouteRecommender(BasicRouteRecommender):
    """
    Recommender system based on first-order Markov chains, maximizing transitions between features of POIs.
    """
    def __init__(self, poi_df: pd.DataFrame, trail_df: pd.DataFrame, feature_column: str):
        super().__init__(poi_df, trail_df)

        # Create dictionaries for POI mapping
        self.id_to_int = {poi_id: idx for idx, poi_id in enumerate(poi_df['venue_id'].unique())}
        self.int_to_id = {idx: poi_id for poi_id, idx in self.id_to_int.items()}

        self.feature_column = feature_column
        self.feature_transition_matrix = self._calculate_feature_transition_matrix()
        self.poi_popularity = self._calculate_popularity()
        self.distance_cache = self._calculate_distance_cache()

    def _calculate_distance_cache(self) -> pd.DataFrame:
        """
        Precomputes a distance matrix for all POIs with valid coordinates.

        Returns:
        - pd.DataFrame: A DataFrame where element (i, j) represents the distance between POI i and POI j.
        """
        valid_pois = self.poi_df[(self.poi_df['latitude'] != -1) & (self.poi_df['longitude'] != -1)]
        poi_ids = valid_pois['venue_id'].values
        latitudes = valid_pois['latitude'].values
        longitudes = valid_pois['longitude'].values

        n = len(poi_ids)
        distance_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                dist = ut.haversine(latitudes[i], longitudes[i], latitudes[j], longitudes[j])
                distance_matrix[i, j] = dist
                distance_matrix[j, i] = dist

        return pd.DataFrame(distance_matrix, index=poi_ids, columns=poi_ids)

    def _calculate_feature_transition_matrix(self) -> pd.DataFrame:
        """
        Calculates the feature transition matrix for the Markov chain.

        Returns:
        - pd.DataFrame: A DataFrame where rows and columns represent features,
          and values represent probabilities of transitioning between features.
        """
        # Extract features from the POI dataframe
        poi_features = self.poi_df[[self.feature_column, 'venue_id']].dropna()
        transitions = []

        # Iterate over trails to collect transitions between features
        for _, trail_data in self.trail_df.groupby('trail_id'):
            pois_in_trail = trail_data['venue_id'].tolist()

            # Map POIs in the trail to their features
            features_in_trail = poi_features[poi_features['venue_id'].isin(pois_in_trail)][self.feature_column].tolist()

            # Collect transitions between consecutive features
            transitions.extend(zip(features_in_trail, features_in_trail[1:]))

        # Count transitions and normalize
        transition_df = pd.DataFrame(transitions, columns=['from', 'to'])
        transition_counts = transition_df.groupby(['from', 'to']).size().unstack(fill_value=0)
        feature_transition_matrix = transition_counts.div(transition_counts.sum(axis=1), axis=0).fillna(0)

        return feature_transition_matrix

    def _calculate_popularity(self) -> pd.Series:
        """
        Calculates the popularity of each POI based on visits.

        Returns:
        - pd.Series: A series with POI IDs as the index and visit counts as values.
        """
        return self.trail_df['venue_id'].value_counts()

    def recommend_for_user(self, user: int, n_items: int, filter_visits: VisitFilter, tiebreaker: TieBreaker) -> List[int]:
        user_trails = self.trail_df[self.trail_df['user_id'] == user]
        visited_pois = set(user_trails['venue_id'].tolist())

        if user_trails.empty:
            return []

        last_poi = user_trails['venue_id'].iloc[-1]
        last_feature = self.poi_df[self.poi_df['venue_id'] == last_poi][self.feature_column].iloc[0]

        return self._recommend_from_feature(last_feature, n_items, filter_visits, tiebreaker, visited_pois, )

    def recommend_from_poi(self, user: int, n_items: int, starting_poi: int, filter_visits: VisitFilter, tiebreaker: TieBreaker) -> List[int]:
        if starting_poi not in self.id_to_int:
            raise ValueError(f"Starting POI {starting_poi} does not exist in the dataset.")

        starting_feature = self.poi_df[self.poi_df['venue_id'] == starting_poi][self.feature_column].iloc[0]
        user_trails = self.trail_df[self.trail_df['user_id'] == user]
        visited_pois = set(user_trails['venue_id'].tolist())


        # Continue recommending based on features
        recommendations = self._recommend_from_feature(
            starting_feature, n_items - 1, filter_visits, tiebreaker, visited_pois, starting_poi
        )

        return recommendations

    def _recommend_from_feature(self, feature: str, n_items: int, filter_visits: VisitFilter, tiebreaker: TieBreaker, visited_pois: set, starting_poi: int) -> List[int]:
        recommendations = []
        recommendations.append(starting_poi) # Always insert the starting POI
        current_feature = feature
        next_poi = starting_poi 
        while len(recommendations) < n_items - 1:
            if current_feature not in self.feature_transition_matrix.index:
                break  # No outgoing transitions from this feature

            # Get the transition probabilities for the current feature
            transition_probs = self.feature_transition_matrix.loc[current_feature]
            max_prob = transition_probs.max()

            if max_prob == 0:
                break  # No valid transitions

            # Get features with the highest transition probability
            candidate_features = transition_probs[transition_probs == max_prob].index

            # Map features to POIs
            candidate_pois = self.poi_df[self.poi_df[self.feature_column].isin(candidate_features)].copy()

            # Exclude already recommended POIs
            candidate_pois = candidate_pois[~candidate_pois['venue_id'].isin(recommendations)]

            # Apply VisitFilter
            if filter_visits == VisitFilter.EXCLUDE_PREVIOUS_VISITS:
                candidate_pois = candidate_pois[~candidate_pois['venue_id'].isin(visited_pois)]

            if candidate_pois.empty:
                break

            # Resolve ties at POI level
            if tiebreaker == TieBreaker.POPULARITY:
                candidate_pois['popularity'] = candidate_pois['venue_id'].map(lambda poi: self.poi_popularity.get(poi, 0))
                candidate_pois = candidate_pois.sort_values(by='popularity', ascending=False)
            elif tiebreaker == TieBreaker.DISTANCE:
                # Filter POIs to ensure they exist in the distance cache
                candidate_pois = candidate_pois[
                    (candidate_pois['venue_id'].isin(self.distance_cache.columns)) &
                    (candidate_pois['venue_id'].isin(self.distance_cache.index))
                ]

                if candidate_pois.empty:
                    break

                candidate_pois['distance'] = candidate_pois['venue_id'].map(
                    lambda poi: self.distance_cache.loc[next_poi, poi]
                ).copy()
                candidate_pois = candidate_pois.sort_values(by='distance')

            # Select the next POI
            next_poi = candidate_pois.iloc[0]['venue_id']
            next_feature = candidate_pois.iloc[0][self.feature_column]

            recommendations.append(next_poi)
            visited_pois.add(next_poi)
            current_feature = next_feature

        return recommendations


