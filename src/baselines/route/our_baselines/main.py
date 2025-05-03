import pandas as pd
import argparse
from Recommenders import VisitFilter
from ClosestNNRouteRecommender import ClosestNNRouteRecommender
from FeatureMarkovChainRecommender import FeatureMarkovRouteRecommender
from POIMarkovChainRecommender import MarkovRouteRecommender
from KNNRouteRecommender import KNNRouteRecommender
from BaselineSinglePOIRecommender import BaselineSinglePOIRecommender
from WeightedTransitionsRouteRecommender import WeightedTransitionsRouteRecommender
from enum import Enum
from POIMarkovChainRecommender import TieBreaker

def main():
    # Definir los argumentos
    parser = argparse.ArgumentParser(description="Run a recommender system with specified parameters.")
    parser.add_argument("--training_file", type=str, help="Path to the training file.", default="NewYork_mapped_trails_weather2_minroutes_4_minPOIs_TestRouteTraining.csv")
    parser.add_argument("--test_file", type=str, help="Path to the test file.", default="NewYork_mapped_trails_weather2_minroutes_4_minPOIs_TestRouteTest.csv")
    parser.add_argument("--feat_file", type=str, help="Path to the feature file.", default="NewYork_mapped_lat_lon.csv")
    parser.add_argument("--output_file", type=str, help="Path to the output file.", default="salida.txt")
    parser.add_argument("--recommender", type=str, choices=[
        "ClosestNNRouteRecommender", 
        "MarkovRouteRecommender", 
        "FeatureMarkovRouteRecommender",
        "KNNRouteRecommender",
        "BaselineSinglePOIRecommender",
        "WeightedTransitionsRouteRecommender"
    ], help="Type of recommender to use.", default="WeightedTransitionsRouteRecommender")
    parser.add_argument("--n_items", type=int, default=10, help="Number of items to recommend.")
    parser.add_argument("--n_neigh", type=int, default=100, help="Number of neighbours (for KNNRouteRecommender) .")
    parser.add_argument("--filter_visits", type=str, default="ALLOW", choices=["ALLOW", "EXCLUDE"], help="Visit filter.")
    parser.add_argument("--tiebreaker", type=str, default="DISTANCE", choices=["POPULARITY", "DISTANCE"], help="Tie-breaking strategy for Markov recommenders.")

    # Parsear los argumentos
    args = parser.parse_args()
    print(f"Training file {args.training_file}")
    print(f"Test file {args.test_file}")
    print(f"Feat file {args.feat_file}")
    print(f"Output file {args.output_file}")
    print(f"Recommender selected {args.recommender}")
    print(f"Number of rec items {args.n_items}")
    print(f"Number of neighbours {args.n_neigh}")

    print(f"Allow previous visits {args.filter_visits}")
    print(f"Tie beaker {args.tiebreaker}")

    # Map filter_visits argument to VisitFilter enum
    filter_visits = VisitFilter.ALLOW_PREVIOUS_VISITS if args.filter_visits == "ALLOW" else VisitFilter.EXCLUDE_PREVIOUS_VISITS

    # Map tiebreaker argument to TieBreaker enum
    tiebreaker = TieBreaker.POPULARITY if args.tiebreaker == "POPULARITY" else TieBreaker.DISTANCE

    # Leer los ficheros con cabeceras definidas a fuego
    train_headers = ["trail_id", "user_id", "venue_id", "timestamp"]
    test_headers = ["trail_id", "user_id", "venue_id", "timestamp"]
    feat_headers = ["venue_id", "latitude", "longitude", "category_lvlFs"]

    training_data = pd.read_csv(args.training_file, header=None, names=train_headers, sep="\t")
    test_data = pd.read_csv(args.test_file, header=None, names=test_headers, sep="\t")
    feat_data = pd.read_csv(args.feat_file, header=None, names=feat_headers, sep="\t")

    # Instanciar el recomendador
    if args.recommender == "ClosestNNRouteRecommender":
        recommender = ClosestNNRouteRecommender(feat_data, training_data)
    elif args.recommender == "MarkovRouteRecommender":
        recommender = MarkovRouteRecommender(feat_data, training_data)
    elif args.recommender == "FeatureMarkovRouteRecommender":
        recommender = FeatureMarkovRouteRecommender(feat_data, training_data, "category_lvlFs")
    elif args.recommender == "KNNRouteRecommender":
        recommender = KNNRouteRecommender(feat_data, training_data, args.n_neigh)
    elif args.recommender == "BaselineSinglePOIRecommender":
        recommender = BaselineSinglePOIRecommender(feat_data, training_data)
    elif args.recommender == "WeightedTransitionsRouteRecommender":
        recommender = WeightedTransitionsRouteRecommender(feat_data, training_data)
    else:
        raise ValueError(f"Unsupported recommender: {args.recommender}")

    # Procesar cada usuario del fichero de test
    with open(args.output_file, 'w') as f:
        for user in test_data["user_id"].unique():
            try:
                user_data = test_data[test_data["user_id"] == user]
                starting_poi = user_data.loc[user_data["timestamp"].idxmin(), "venue_id"]
                recommendations = recommender.recommend_from_poi(
                    user=user,
                    n_items=args.n_items,
                    starting_poi=starting_poi,
                    filter_visits=filter_visits,
                    tiebreaker=tiebreaker
                )



                # Write recommendations to the output file
                for poi in recommendations:
                    f.write(f"{user}\t{poi}\t1\n")
            except Exception as e:
                print(f"Error processing user {user}: {e}")

    print(f"Recommendations saved to {args.output_file}")

if __name__ == "__main__":
    main()
