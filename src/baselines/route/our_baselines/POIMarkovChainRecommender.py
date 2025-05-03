from Recommenders import BasicRouteRecommender, VisitFilter, TieBreaker
import utils as ut
from typing import List
import numpy as np
import pandas as pd

class MarkovRouteRecommender(BasicRouteRecommender):
    """
    Recommender system based on first-order Markov chains with precomputed distance caching.
    """
    def __init__(self, poi_df: pd.DataFrame, trail_df: pd.DataFrame):
        super().__init__(poi_df, trail_df)

        # Create dictionaries for POI mapping
        self.id_to_int = {poi_id: idx for idx, poi_id in enumerate(poi_df['venue_id'].unique())}
        self.int_to_id = {idx: poi_id for poi_id, idx in self.id_to_int.items()}

        # Calculate transition matrix, popularity, and distance cache
        self.transition_matrix = self._calculate_transition_matrix()
        self.poi_popularity = self._calculate_popularity()
        self.distance_cache = self._calculate_distance_cache()

    def _calculate_transition_matrix(self) -> np.ndarray:
        """
        Calculates the transition matrix for the Markov chain.

        Returns:
        - np.ndarray: A square matrix where element (i, j) represents the probability of transitioning
          from POI i to POI j.
        """
        num_pois = len(self.id_to_int)
        matrix = np.zeros((num_pois, num_pois))

        for _, trail_data in self.trail_df.groupby('trail_id'):
            transitions = zip(trail_data['venue_id'], trail_data['venue_id'][1:])

            for poi_from, poi_to in transitions:
                if poi_from in self.id_to_int and poi_to in self.id_to_int:
                    matrix[self.id_to_int[poi_from], self.id_to_int[poi_to]] += 1

        # Normalize rows to probabilities
        matrix = matrix / matrix.sum(axis=1, keepdims=True)
        matrix[np.isnan(matrix)] = 0  # Handle rows with no outgoing transitions

        return matrix

    def _calculate_popularity(self) -> pd.Series:
        """
        Calculates the popularity of each POI based on visits.

        Returns:
        - pd.Series: A series with POI IDs as the index and visit counts as values.
        """
        return self.trail_df['venue_id'].value_counts()

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

    def recommend_for_user(self, user: int, n_items: int, filter_visits: VisitFilter, tiebreaker: TieBreaker) -> List[int]:
        user_trails = self.trail_df[self.trail_df['user_id'] == user]
        if user_trails.empty:
            return []

        last_poi = user_trails['venue_id'].iloc[-1]
        return self._recommend_from_poi(last_poi, n_items, filter_visits, tiebreaker, last_poi)

    def recommend_from_poi(self, user: int, n_items: int, starting_poi: int, filter_visits: VisitFilter, tiebreaker: TieBreaker) -> List[int]:
        """
        Recommends POIs starting from a specific POI based on Markov chain transitions.
        
        The starting POI is guaranteed to be the first recommendation.
        """
        if starting_poi not in self.id_to_int:
            raise ValueError(f"Starting POI {starting_poi} does not exist in the dataset.")

        # Ensure the starting POI is always the first recommendation
        user_trails = self.trail_df[self.trail_df['user_id'] == user]
        visited_pois = set(user_trails['venue_id'].tolist())

        # Continue recommending based on Markov chain logic
        recommendations = self._recommend_from_poi(
            starting_poi, n_items, filter_visits, tiebreaker, visited_pois
        )

        return recommendations

    def _recommend_from_poi(self, poi: int, n_items: int, filter_visits: VisitFilter, tiebreaker: TieBreaker, visited_pois:set) -> List[int]:
        """
        Core logic for recommending POIs from a specific starting POI.
        """
        recommendations = []
        recommendations.append(poi)

        current_poi = poi

        while len(recommendations) < n_items - 1:
            if current_poi not in self.id_to_int:
                break

            poi_index = self.id_to_int[current_poi]
            transition_probs = self.transition_matrix[poi_index]
            max_prob = np.max(transition_probs)

            if max_prob == 0:
                break  # No valid transitions

            # Get POIs with the highest transition probability
            candidate_indices = np.where(transition_probs == max_prob)[0]
            candidate_pois = [self.int_to_id[idx] for idx in candidate_indices]

            # Exclude already recommended POIs
            candidate_pois = [poi for poi in candidate_pois if poi not in recommendations]

            # Apply VisitFilter
            if filter_visits == VisitFilter.EXCLUDE_PREVIOUS_VISITS:
                candidate_pois = [poi for poi in candidate_pois if poi not in visited_pois]

            if not candidate_pois:
                break

            # Resolve ties at POI level
            if len(candidate_pois) > 1:
                if tiebreaker == TieBreaker.POPULARITY:
                    candidate_pois = sorted(
                        candidate_pois,
                        key=lambda poi: self.poi_popularity.get(poi, 0),
                        reverse=True
                    )
                elif tiebreaker == TieBreaker.DISTANCE:
                    # Filter POIs to ensure they exist in the distance cache
                    candidate_pois = [
                        poi for poi in candidate_pois
                        if poi in self.distance_cache.columns and poi in self.distance_cache.index
                    ]

                    if not candidate_pois:
                        break

                    candidate_pois = sorted(
                        candidate_pois,
                        key=lambda poi: self.distance_cache.loc[current_poi, poi]
                    )

            if not candidate_pois:
                break

            next_poi = candidate_pois[0]
            recommendations.append(next_poi)
            visited_pois.add(next_poi)
            current_poi = next_poi

        return recommendations
