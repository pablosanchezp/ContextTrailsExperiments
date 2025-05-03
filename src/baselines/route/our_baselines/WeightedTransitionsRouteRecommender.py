from Recommenders import BasicRouteRecommender, TieBreaker, VisitFilter
from typing import List, Dict
import pandas as pd
import numpy as np
from collections import defaultdict
from tqdm import tqdm
import utils as ut

class WeightedTransitionsRouteRecommender(BasicRouteRecommender):
    """
    Random Walk-based recommender system for POI recommendation.
    """
    def __init__(self, poi_df: pd.DataFrame, trail_df: pd.DataFrame):
        super().__init__(poi_df, trail_df)
        self.distance_weights = defaultdict(lambda: defaultdict(float))
        self.transition_weights = defaultdict(lambda: defaultdict(float))
        self.category_weights = defaultdict(lambda: defaultdict(float))
        self.poi_popularity = self._calculate_popularity()
        self._build_poi_graph_components()

    def _build_poi_graph_components(self):
        """
        Constructs individual weight components for the POI graph: distance, transitions, and categories.
        """
        max_distance, min_distance = 0, float('inf')
        max_transitions, min_transitions = 0, float('inf')
        max_category_transitions, min_category_transitions = 0, float('inf')

        poi_with_coords = self.poi_df[(self.poi_df['latitude'] != -1) & (self.poi_df['longitude'] != -1)]

        # Compute distance weights
        for i, poi_i in tqdm(poi_with_coords.iterrows(), desc="Computing distances", total=len(poi_with_coords)):
            for j, poi_j in poi_with_coords.iloc[i + 1:].iterrows():  # Start from i + 1 to avoid redundant calculations
                dist = ut.haversine(poi_i['latitude'], poi_i['longitude'], poi_j['latitude'], poi_j['longitude'])
                if dist > 0:
                    weight = 1 / dist
                    self.distance_weights[poi_i['venue_id']][poi_j['venue_id']] += weight
                    self.distance_weights[poi_j['venue_id']][poi_i['venue_id']] += weight  # Symmetry
                    max_distance = max(max_distance, weight)
                    min_distance = min(min_distance, weight)

        # Compute transition weights
        for _, trail_data in tqdm(self.trail_df.groupby('trail_id'), desc="Computing transitions"):
            pois = trail_data['venue_id'].tolist()
            for i in range(len(pois) - 1):
                self.transition_weights[pois[i]][pois[i + 1]] += 1
                max_transitions = max(max_transitions, self.transition_weights[pois[i]][pois[i + 1]])
                min_transitions = min(min_transitions, self.transition_weights[pois[i]][pois[i + 1]])

        # Compute category transition weights
        if 'category_lvlFs' in self.poi_df.columns:
            for _, trail_data in tqdm(self.trail_df.groupby('trail_id'), desc="Computing category transitions"):
                pois = trail_data['venue_id'].tolist()
                for i in range(len(pois) - 1):
                    category_i = self.poi_df[self.poi_df['venue_id'] == pois[i]]['category_lvlFs'].iloc[0]
                    category_j = self.poi_df[self.poi_df['venue_id'] == pois[i + 1]]['category_lvlFs'].iloc[0]
                    if pd.notna(category_i) and pd.notna(category_j):
                        self.category_weights[pois[i]][pois[i + 1]] += 1
                        max_category_transitions = max(max_category_transitions, self.category_weights[pois[i]][pois[i + 1]])
                        min_category_transitions = min(min_category_transitions, self.category_weights[pois[i]][pois[i + 1]])

        # Normalize weights
        for poi, neighbors in self.distance_weights.items():
            for neighbor in neighbors:
                if max_distance > min_distance:
                    neighbors[neighbor] = (neighbors[neighbor] - min_distance) / (max_distance - min_distance)

        for poi, neighbors in self.transition_weights.items():
            for neighbor in neighbors:
                if max_transitions > min_transitions:
                    neighbors[neighbor] = (neighbors[neighbor] - min_transitions) / (max_transitions - min_transitions)

        for poi, neighbors in self.category_weights.items():
            for neighbor in neighbors:
                if max_category_transitions > min_category_transitions:
                    neighbors[neighbor] = (neighbors[neighbor] - min_category_transitions) / (max_category_transitions - min_category_transitions)

    def _calculate_popularity(self) -> pd.Series:
        """
        Calculates the popularity of each POI based on visits.

        Returns:
            pd.Series: A series with POI IDs as the index and visit counts as values.
        """
        return self.trail_df['venue_id'].value_counts()

    def recommend_from_poi(self, user: int, n_items: int, starting_poi: int, filter_visits: VisitFilter, tiebreaker: TieBreaker) -> List[int]:
        """
        Recommends POIs starting from a specific POI using a random walk strategy.

        Args:
            user (int): The user ID for which to generate recommendations.
            n_items (int): The number of POIs to recommend.
            starting_poi (int): The starting POI.
            filter_visits (VisitFilter): Whether to exclude previously visited POIs.
            tiebreaker (TieBreaker): Strategy for resolving ties.

        Returns:
            List[int]: A list of recommended POI IDs.
        """
        recommendations = [starting_poi]
        visited_pois = set(recommendations)

        # Get user's visited POIs from training if filter_visits is enabled
        user_visited_pois = set()
        if filter_visits == VisitFilter.EXCLUDE_PREVIOUS_VISITS:
            user_visited_pois = set(self.trail_df[self.trail_df['user_id'] == user]['venue_id'])

        current_poi = starting_poi

        while len(recommendations) < n_items:
            combined_weights = defaultdict(float)

            # Combine weights from all components
            for neighbor, weight in self.distance_weights.get(current_poi, {}).items():
                combined_weights[neighbor] += weight

            for neighbor, weight in self.transition_weights.get(current_poi, {}).items():
                combined_weights[neighbor] += weight

            for neighbor, weight in self.category_weights.get(current_poi, {}).items():
                combined_weights[neighbor] += weight

            # Filter neighbors if required
            combined_weights = {
                poi: weight for poi, weight in combined_weights.items()
                if poi not in visited_pois and poi not in user_visited_pois
            }

            if not combined_weights:
                break

            # Get maximum weight
            max_weight = max(combined_weights.values())

            # Resolve ties
            candidates = [poi for poi, weight in combined_weights.items() if weight == max_weight]
            if len(candidates) == 0:
                return recommendations

            if len(candidates) > 1:
                if tiebreaker == TieBreaker.POPULARITY:
                    candidates.sort(key=lambda poi: self.poi_popularity.get(poi, 0), reverse=True)
                elif tiebreaker == TieBreaker.DISTANCE:
                    candidates.sort(
                        key=lambda poi: self.distance_weights[current_poi].get(poi, float('inf'))
                    )

                    '''
                    candidates.sort(key=lambda poi: ut.haversine(
                        current_coords['latitude'], current_coords['longitude'],
                        self.poi_df[self.poi_df['venue_id'] == poi]['latitude'].iloc[0],
                        self.poi_df[self.poi_df['venue_id'] == poi]['longitude'].iloc[0]
                    ) if poi in self.poi_df['venue_id'].values else float('inf'))
                    '''

            next_poi = candidates[0]

            recommendations.append(next_poi)
            visited_pois.add(next_poi)
            current_poi = next_poi

        return recommendations
