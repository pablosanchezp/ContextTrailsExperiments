import pandas as pd
from enum import Enum
from typing import List



class VisitFilter(Enum):
    """
    Enumeration to control whether previously visited POIs should be included in recommendations.
    """
    ALLOW_PREVIOUS_VISITS = 1
    EXCLUDE_PREVIOUS_VISITS = 2

class TieBreaker(Enum):
    """
    Enumeration to resolve ties in transition probabilities.
    """
    POPULARITY = 1
    DISTANCE = 2

class BasicRouteRecommender:
    """
    A basic route recommender system.
    """
    def __init__(self, poi_df: pd.DataFrame, trail_df: pd.DataFrame):
        """
        Initializes the recommender with mappings and dataframes.
        
        Parameters:
        - poi_df: pd.DataFrame, DataFrame containing POI information.
        - trail_df: pd.DataFrame, DataFrame containing user trail information.
        """
        self.poi_df = poi_df
        self.trail_df = trail_df

    def recommend_for_user(self, user: int, n_items: int, filter_visits: VisitFilter, tiebreaker: TieBreaker) -> List[int]:
        """
        Recommends a number of POIs for a given user.

        Parameters:
        - user: int, the user ID to recommend POIs for.
        - n_items: int, the number of POIs to recommend.
        - filter_visits: VisitFilter, whether to exclude previously visited POIs.

        Returns:
        - List[int]: A list of recommended POI IDs (as integers).
        """
        pass

    def recommend_from_poi(self, user: int, n_items: int, starting_poi: int, filter_visits: VisitFilter, tiebreaker: TieBreaker) -> List[int]:
        """
        Recommends a number of POIs for a given user, starting from a specific POI.

        Parameters:
        - user: int, the user ID to recommend POIs for.
        - n_items: int, the number of POIs to recommend.
        - starting_poi: int, the POI to start recommendations from.
        - filter_visits: VisitFilter, whether to exclude previously visited POIs.

        Returns:
        - List[int]: A list of recommended POI IDs (as integers).
        """
        pass

