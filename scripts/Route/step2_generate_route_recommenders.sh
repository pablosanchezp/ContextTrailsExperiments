: '
  Script for generating the recommenders

'

# !/bin/bash

path_baselines_route="../../src/baselines/route/"
JAR="$path_baselines_route/SequentialRecommenders.jar"
jvmMemory=-Xmx24G


javaCommand=java




# This cities are for the original dataset of Foursquare

recPrefix=rec

# cities selected to perform the experiments
cities="NewYorkCity Tokyo PetalingJaya"

recFolder=RouteRecommendationFolder
resultFolder=RouteResultFolder

itemsRecommended=100



cutoffs="5,10,20"
cutoffsWrite="5-10-20"


# For each city (single domain, each city individually)

for city_or in $cities
do
  # The test file is always the same

  if [[ $city_or == "NewYorkCity" ]]; then
      city="Q60_NewYorkCity"
  fi

  if [[ $city_or == "Tokyo" ]]; then
      city="Q308891_Tokyo"
  fi

  if [[ $city_or == "PetalingJaya" ]]; then
      city="Q864965_PetalingJaya"
  fi

  path_inputs="../../data/Route/${city_or}"

  trainFile=$path_inputs/${city}"_mapped_trails_weather_2_minroutes_4_minPOIs_TestRouteTraining.csv"
  testfile=$path_inputs/${city}"_mapped_trails_weather_2_minroutes_4_minPOIs_TestRouteTest.csv"

  cityCompletePOICoords=$path_inputs/${city}"_mapped_lat_lon_wrong_coordinates_by_midpoint.csv"


  recommendationFolder=${city}"_"${recFolder}
  mkdir -p $recommendationFolder

  echo "Current trainFile is $trainFile"
  echo "Current testfile is $testfile"
  echo "Current coord is $cityCompletePOICoords"

  routes_path="$path_baselines_route"/our_baselines

  # ClosestNNRoute Recommender

  for filter_visits in "ALLOW" "EXCLUDE"
  do
    for tiebreaker in "POPULARITY" "DISTANCE"
    do
      for recommender in "BaselineSinglePOIRecommender" "WeightedTransitionsRouteRecommender" "ClosestNNRouteRecommender" "MarkovRouteRecommender" "FeatureMarkovRouteRecommender"
      do
        recommendation_file=$recommendationFolder/rec_"$city"_"$recommender"_"PrevVisits"$filter_visits"_TieBreaker"$tiebreaker"_WrongCoordsByMidpoint.txt"

        if [ ! -f $recommendation_file ]; then
          echo "NO EXISTE $recommendation_file"
          python "$routes_path"/main.py --training_file $trainFile --test_file $testfile --feat_file $cityCompletePOICoords --output_file $recommendation_file --recommender $recommender --n_items 50 --filter_visits $filter_visits --tiebreaker $tiebreaker
        fi

      done
      wait

      for neigh in "100" "200"
      do
        recommender="KNNRouteRecommender"
        recommendation_file=$recommendationFolder/rec_"$city"_"$recommender"_"PrevVisits"$filter_visits"_TieBreaker"$tiebreaker"neighs"$neigh"_WrongCoordsByMidpoint.txt"
        if [ ! -f $recommendation_file ]; then
          python "$routes_path"/main.py --training_file $trainFile --test_file $testfile --feat_file $cityCompletePOICoords --output_file $recommendation_file --recommender $recommender --n_items 50 --filter_visits $filter_visits --tiebreaker $tiebreaker --n_neigh $neigh
        fi
        sleep 1
      done
      wait



    done
    wait

  done
  wait


done # End cities
wait







: '
Evaluation part
'

cities="NewYorkCity Tokyo PetalingJaya"
nonaccresultsPrefix=naev
evthreshold=1
path_baselines_poi="../../src/baselines/classic"
JAR="$path_baselines_poi/SequentialRecommenders.jar"

for city_or in $cities
do
  path_inputs="../../data/Route/${city_or}"

  if [[ $city_or == "NewYorkCity" ]]; then
      city="Q60_NewYorkCity"
  fi

  if [[ $city_or == "Tokyo" ]]; then
      city="Q308891_Tokyo"
  fi

  if [[ $city_or == "PetalingJaya" ]]; then
      city="Q864965_PetalingJaya"
  fi


  resFolder=${city}"_"$resultFolder
  recommendationFolder=${city}"_"${recFolder}
  mkdir -p $resFolder


  # In every case -> We need to generate other training and test files, as the first column is the trail
  originaltrainFile=$path_inputs/${city}"_mapped_trails_weather_2_minroutes_4_minPOIs_TestRouteTraining.csv"
  originaltestfile=$path_inputs/${city}"_mapped_trails_weather_2_minroutes_4_minPOIs_TestRouteTest.csv"

  trainFile=$path_inputs/${city}"_mapped_trails_weather_2_minroutes_4_minPOIs_TestRouteTraining_NoTrailsID.csv"
  testfile=$path_inputs/${city}"_mapped_trails_weather_2_minroutes_4_minPOIs_TestRouteTest_NoTrailsID.csv"

  awk -F'\t' 'BEGIN { OFS="\t" } { print $2, $3, 1 }' $originaltrainFile > $trainFile
  # We need to create a file with 1s in test
  awk -F'\t' 'BEGIN { OFS="\t" } { print $2, $3, 1 }' $originaltestfile > $testfile

  wc -l $trainFile
  wc -l $testfile

  echo $city
  echo $trainFile
  echo $testfile
  sleep 1

  find $recommendationFolder/ -name "rec_*" | while read recFile; do

    recFileName=$(basename "$recFile" .txt) #extension removed

    #The trainFile must be the non imputed
    outputResultfile=$resFolder/"$nonaccresultsPrefix"_EvTh"$evthreshold"_"$recFileName"_C"$cutoffsWrite".txt
    $javaCommand $jvmMemory -jar $JAR -o ranksysNonAccuracyMetricsEvaluation -trf $trainFile -tsf $testfile -rf $recFile -thr $evthreshold -rc $cutoffs -orf $outputResultfile -onlyAcc false

  done # End Find
  wait

done # End cities
wait
