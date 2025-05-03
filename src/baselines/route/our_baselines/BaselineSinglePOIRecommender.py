from Recommenders import BasicRouteRecommender, VisitFilter, TieBreaker
from typing import List

class BaselineSinglePOIRecommender(BasicRouteRecommender):
    """
    Baseline recommender that simply returns the starting POI as the recommendation.
    """

    def __init__(self, poi_df, trail_df):
        super().__init__(poi_df, trail_df)

    def recommend_from_poi(self, user: int, n_items: int, starting_poi: int, filter_visits: VisitFilter, tiebreaker: TieBreaker) -> List[int]:
        """
        Recommends only the starting POI.

        Args:
            user (int): The user ID for which to generate recommendations.
            n_items (int): The number of POIs to recommend.
            starting_poi (int): The starting POI.
            filter_visits: Not used in this recommender.
            tiebreaker: Not used in this recommender.

        Returns:
            List[int]: A list containing only the starting POI.
        """
        return [starting_poi]
