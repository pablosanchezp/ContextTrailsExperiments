from Recommenders import BasicRouteRecommender, TieBreaker, VisitFilter
from typing import List
import numpy as np
import pandas as pd
from collections import defaultdict
import utils as ut
from tqdm import tqdm


class KNNRouteRecommender(BasicRouteRecommender):
    """
    KNN-based route recommender using user similarities and iterative POI recommendations.
    """
    def __init__(self, poi_df: pd.DataFrame, trail_df: pd.DataFrame, k: int):
        super().__init__(poi_df, trail_df)
        self.k = k
        user_ids = self.trail_df['user_id'].unique()
        self.user_uidx_map = {user_id: idx for idx, user_id in enumerate(user_ids)}
        self.uidx_user_map = {idx: user_id for user_id, idx in self.user_uidx_map.items()}
        self.user_similarity_matrix = self._calculate_user_similarity_matrix()
        self.poi_popularity = self._calculate_popularity()


    def _calculate_user_similarity_matrix(self) -> np.ndarray:
        n_users = len(self.user_uidx_map)
        similarity_matrix = np.zeros((n_users, n_users))   
        user_pois = self.trail_df.groupby('user_id')['venue_id'].apply(set)

        for i in tqdm(range(n_users), desc="Calculating user similarities"):
            pois_i = user_pois[self.uidx_user_map[i]]
            for j in range(i + 1, n_users):
                pois_j = user_pois[self.uidx_user_map[j]]

                if pois_i and pois_j:
                    intersection = len(pois_i & pois_j)
                    if intersection == 0:
                        similarity = 0
                    else:
                        union = len(pois_i | pois_j)
                        similarity = intersection / union if union > 0 else 0
                else:
                    similarity = 0

                similarity_matrix[i, j] = similarity_matrix[j, i] = similarity

        return similarity_matrix


    '''
    # This similarity computation is by routes, not by POIS
    def _calculate_user_similarity_matrix(self) -> np.ndarray:
        """
        Calculates the user similarity matrix based on route overlaps.

        Returns:
            np.ndarray: A symmetric matrix where element (i, j) is the similarity between user i and user j.
        """
        

        n_users = len(self.user_uidx_map)
        similarity_matrix = np.zeros((n_users, n_users))

        # Group routes by user
        user_routes = self.trail_df.groupby('user_id')['trail_id'].apply(set)

        for i in tqdm(range(n_users), desc="Calculating user similarities"):
            user_i_routes = user_routes[self.uidx_user_map[i]]
            for j in range(i + 1, n_users):
                user_j_routes = user_routes[self.uidx_user_map[j]]

                similarities = []
                for route_i in user_i_routes:
                    pois_i = set(self.trail_df[self.trail_df['trail_id'] == route_i]['venue_id'])
                    for route_j in user_j_routes:
                        pois_j = set(self.trail_df[self.trail_df['trail_id'] == route_j]['venue_id'])

                        if pois_i and pois_j:
                            intersection = len(pois_i & pois_j)
                            if intersection == 0:
                                similarities.append(0)
                            else:
                                union = len(pois_i | pois_j)
                                similarities.append(intersection / union)

                similarity_matrix[i, j] = similarity_matrix[j, i] = np.mean(similarities) if similarities else 0

        return similarity_matrix
    '''

    def _calculate_popularity(self) -> pd.Series:
        """
        Calculates the popularity of each POI based on visits.

        Returns:
            pd.Series: A series with POI IDs as the index and visit counts as values.
        """
        return self.trail_df['venue_id'].value_counts()

    def recommend_from_poi(self, user: int, n_items: int, starting_poi: int, filter_visits: VisitFilter, tiebreaker: TieBreaker) -> List[int]:
        """
        Recommends POIs starting from a specific POI using KNN-based scoring.

        Args:
            user (int): The user ID for which to generate recommendations.
            n_items (int): The number of POIs to recommend.
            starting_poi (int): The starting POI.
            filter_visits (VisitFilter): Whether to exclude previously visited POIs.
            tiebreaker (TieBreaker): Strategy for resolving ties.

        Returns:
            List[int]: A list of recommended POI IDs.
        """
        recommendations = []
        visited_pois = set()
        user_index = self.user_uidx_map[user]

        # Add the starting POI to recommendations
        recommendations.append(starting_poi)
        visited_pois.add(starting_poi)

        current_poi = starting_poi

        similarities = self.user_similarity_matrix[user_index]
        neighbor_indices = np.argsort(similarities)[::-1][:self.k]

        all_pois = self.poi_df[['venue_id', 'latitude', 'longitude']]
        all_pois = all_pois[(all_pois['latitude'] != -1) & (all_pois['longitude'] != -1)]
        
        if filter_visits == VisitFilter.EXCLUDE_PREVIOUS_VISITS:
            all_pois = all_pois[~all_pois['venue_id'].isin(visited_pois)]


        candidates = all_pois['venue_id'].values
        while len(recommendations) < n_items:
            scores = {}
            # Find k nearest neighbors
            

            for neighbor_idx in neighbor_indices:
                neighbor_id = self.uidx_user_map[neighbor_idx]
                # neighbor_id = self.trail_df['user_id'].unique()[neighbor_idx]
                neighbor_trails = self.trail_df[self.trail_df['user_id'] == neighbor_id]

                for trail_id in neighbor_trails['trail_id'].unique():
                    trail_pois = neighbor_trails[neighbor_trails['trail_id'] == trail_id]['venue_id'].tolist()

                    if current_poi in trail_pois:
                        poi_index = trail_pois.index(current_poi)
                        if poi_index < len(trail_pois) - 1:
                            next_poi = trail_pois[poi_index + 1]
                            if next_poi not in visited_pois and next_poi in candidates:
                                scores[next_poi] = scores.get(next_poi, 0) + similarities[neighbor_idx]

            if not scores:
                break

            # Select the next POI based on scores
            max_score = max(scores.values())
            max_score_pois = [poi for poi, score in scores.items() if score == max_score]
            
            if len(max_score_pois) > 1:
                if tiebreaker == TieBreaker.POPULARITY:
                    next_poi = max(max_score_pois, key=lambda poi: self.poi_popularity.get(poi, 0))
                elif tiebreaker == TieBreaker.DISTANCE:
                    current_coords = self.poi_df[self.poi_df['venue_id'] == current_poi][['latitude', 'longitude']].iloc[0]
                    next_poi = min(max_score_pois,
                                   key=lambda poi: ut.haversine(current_coords['latitude'], current_coords['longitude'],
                                   self.poi_df[self.poi_df['venue_id'] == poi]['latitude'].iloc[0],
                                   self.poi_df[self.poi_df['venue_id'] == poi]['longitude'].iloc[0]
                ))
            else:
                next_poi = max_score_pois[0]

            recommendations.append(next_poi)
            visited_pois.add(next_poi)
            current_poi = next_poi

        return recommendations
