from Recommenders import BasicRouteRecommender, VisitFilter, TieBreaker
import utils as ut
from typing import List
import math
import pandas as pd
import numpy as np

class ClosestNNRouteRecommender(BasicRouteRecommender):
    """
    Recommender system that suggests POIs based on proximity to a starting POI and iteratively
    recommends the closest POI to the current location, with caching for distances.
    """

    def __init__(self, poi_df: pd.DataFrame, trail_df: pd.DataFrame):
        super().__init__(poi_df, trail_df)
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

    def recommend_for_user(self, user: int, n_items: int, filter_visits: VisitFilter, tiebreaker: TieBreaker) -> List[int]:
        pass
        '''
        user_trails = self.trail_df[self.trail_df['user_id'] == user]
        visited_pois = user_trails['venue_id'].tolist()

        if not visited_pois:
            raise ValueError(f"User {user} has not visited any POIs.")

        # Calculate the midpoint
        midpoint = self.calculate_midpoint(visited_pois)
        return self._recommend_closest(midpoint, n_items, visited_pois, filter_visits, tiebreaker)
        '''

    def recommend_from_poi(self, user: int, n_items: int, starting_poi: int, filter_visits: VisitFilter, tiebreaker: TieBreaker) -> List[int]:
        if starting_poi not in self.poi_df['venue_id'].values:
            raise ValueError(f"Starting POI {starting_poi} does not exist in the dataset.")

        user_trails = self.trail_df[self.trail_df['user_id'] == user]
        visited_pois = user_trails['venue_id'].tolist()


        return self._recommend_closest(starting_poi, n_items, visited_pois, filter_visits, tiebreaker)

    def calculate_midpoint(self, visited_pois):
        visited_coords = self.poi_df[self.poi_df['venue_id'].isin(visited_pois)][['latitude', 'longitude']]

        x = sum(math.cos(math.radians(lat)) * math.cos(math.radians(lon)) for lat, lon in zip(visited_coords['latitude'], visited_coords['longitude']))
        y = sum(math.cos(math.radians(lat)) * math.sin(math.radians(lon)) for lat, lon in zip(visited_coords['latitude'], visited_coords['longitude']))
        z = sum(math.sin(math.radians(lat)) for lat in visited_coords['latitude'])

        total = len(visited_coords)
        if total == 0:
            return None

        x /= total
        y /= total
        z /= total

        central_longitude = math.atan2(y, x)
        central_latitude = math.atan2(z, math.sqrt(x ** 2 + y ** 2))
        return math.degrees(central_latitude), math.degrees(central_longitude)

    def _recommend_closest(self, starting_poi, n_items, visited_pois, filter_visits, tiebreaker) -> List[int]:
        all_pois = self.poi_df[['venue_id', 'latitude', 'longitude']]

        # Exclude invalid POIs (-1, -1 coordinates)
        all_pois = all_pois[(all_pois['latitude'] != -1) & (all_pois['longitude'] != -1)]

        if filter_visits == VisitFilter.EXCLUDE_PREVIOUS_VISITS:
            all_pois = all_pois[~all_pois['venue_id'].isin(visited_pois)]

        candidates = all_pois['venue_id'].values
        recommendations = []
        recommendations.append(starting_poi)
        candidates = [poi for poi in candidates if poi != starting_poi]
        current_origin = starting_poi

        while len(recommendations) < n_items:
            closest_pois = self._find_closest_pois(current_origin, candidates)

            # Apply tiebreaker if there are ties
            if len(closest_pois) > 1:
                if tiebreaker == TieBreaker.POPULARITY:
                    closest_pois = sorted(
                        closest_pois,
                        key=lambda poi: self.trail_df[self.trail_df['venue_id'] == poi].shape[0],
                        reverse=True
                    )

            closest_poi = closest_pois[0]
            recommendations.append(closest_poi)
            candidates = [poi for poi in candidates if poi != closest_poi]
            if len(candidates) == 0:
                break

            # Update the origin for next iteration
            current_origin = closest_poi

        return recommendations

    def _find_closest_pois(self, origin, poi_candidates) -> List[int]:
        valid_candidates = [poi for poi in poi_candidates if poi in self.distance_cache.columns and origin in self.distance_cache.index]
        distances = [(poi, self.distance_cache.loc[origin, poi]) for poi in valid_candidates]
        min_distance = min(distances, key=lambda x: x[1])[1]

        # Return POIs with the minimum distance
        return [poi_id for poi_id, distance in distances if distance == min_distance]
