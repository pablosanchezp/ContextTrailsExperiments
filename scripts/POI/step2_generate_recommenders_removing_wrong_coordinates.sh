: '
  Script for generating the recommenders

'

# !/bin/bash
path_baselines_poi="../../src/baselines/classic"
JAR="$path_baselines_poi/SequentialRecommenders.jar"
jvmMemory=-Xmx100G


javaCommand=java




# This cities are for the original dataset of Foursquare

recPrefix=rec_flt_wrng_poi

# cities selected to perform the experiments
cities="PetalingJaya" #"" #"" # "

recFolder=RecommendationFolderRemovedWrongCoordinates
resultFolder=ResultFolderRemovedWrongCoordinates

allneighbours="10 20 30 40 50 60 70 80 90 100"
itemsRecommended=100


allKFactorizerRankSys="10 50 100"
allLambdaFactorizerRankSys="0.1 1 10"
allAlphaFactorizerRankSys="0.1 1 10"


cutoffs="5,10,20"
cutoffsWrite="5-10-20"

mymedialitePath="$path_baselines_poi"/"MyMediaLite-3.11/bin"
BPRFactors=$allKFactorizerRankSys
BPRBiasReg="0 0.5 1"
BPRLearnRate=0.05
BPRNumIter=50
BPRRegU="0.0025 0.001 0.005 0.01 0.1"
BPRRegJ="0.00025 0.0001 0.0005 0.001 0.01"
extensionMyMediaLite=MyMedLt
geoBPRmaxDists="1 4"
#IRenMF parameters and data
fullpathMatlab="/home/pablosanchez/MatlabInstalation/bin/matlab"
# CAUTION. This command is used to locate the instalation of Matlab in your computer. If there is an error launching the script, substitute the variable pathMatlab with the full path of your matlab executable
pathMatlab="$(dirname $fullpathMatlab)"

fullPath="$(pwd)"
pathIrenMF=$fullPath/IRenMFWithScore

pathDest=$fullPath

#Variables for IrenMF (paper of ExperimentalEvaluation. Most of these variables are updated in the configureFile)
lambda1=0.015
lambda2=0.015
GeoNN=10

allKIRENMF="100 50"
allAlphaIRENMF="0.4 0.6"
allLambda3IRENMF="1 0.1"
clustersIRENMF="5 50"
extensionCoords=_Coords.txt



# For rankGeoFM
cs_RANKGEOFM="1"
alphas_RANKGEOFM="0.1 0.2"
epsilons_RANKGEOFM="0.3"
kfactors_RANKGEOFM=$allKFactorizerRankSys

ns_RANKGEOFM="10 50 100 200"
iters_RANKGEOFM="50 120 200"
decays_RANKGEOFM="1"
isboldDriver_RANKGEOFM="true"
learnRates_RANKGEOFM="0.001"
maxRates_RANKGEOFM="0.001"


# For FMFMGM
alphas_FMFMGM="0.2 0.4"
thetas_FMFMGM="0.02 0.1"
distances_FMFMGM="15"
iters_FMFMGM="30"
kfactors_FMFMGM="50 100"
alphas2_FMFMGM="20 40"
betas_FMFMGM="0.2"
learningRates_FMFMGM="0.0001"
sigmoids_FMFMGM="false"





# For IRenMF
function obtainConfigureFile() #The arguments are the k, the alpha and the lambda3
{
  configureFileSimple=""
  if [ "$1" == "100" ] && [ "$2" == "0.4" ] && [ "$3" == "1" ] && [ "$4" == "50" ] ; then
    configureFileSimple="configure00" #Configure 0
  fi

  if [ "$1" == "100" ] && [ "$2" == "0.4" ] && [ "$3" == "0.1" ] && [ "$4" == "50" ] ; then
    configureFileSimple="configure01" #Configure 1
  fi

  if [ "$1" == "100" ] && [ "$2" == "0.6" ] && [ "$3" == "1" ] && [ "$4" == "50" ] ; then
    configureFileSimple="configure02" #Configure 2
  fi

  if [ "$1" == "100" ] && [ "$2" == "0.6" ] && [ "$3" == "0.1" ] && [ "$4" == "50" ] ; then
    configureFileSimple="configure03" #Configure 3
  fi

  if [ "$1" == "50" ] && [ "$2" == "0.4" ] && [ "$3" == "1" ] && [ "$4" == "50" ] ; then
    configureFileSimple="configure04" #Configure 4
  fi

  if [ "$1" == "50" ] && [ "$2" == "0.4" ] && [ "$3" == "0.1" ] && [ "$4" == "50" ] ; then
    configureFileSimple="configure05" #Configure 5
  fi

  if [ "$1" == "50" ] && [ "$2" == "0.6" ] && [ "$3" == "1" ] && [ "$4" == "50" ] ; then
    configureFileSimple="configure06" #Configure 6
  fi

  if [ "$1" == "50" ] && [ "$2" == "0.6" ] && [ "$3" == "0.1" ] && [ "$4" == "50" ] ; then
    configureFileSimple="configure07" #Configure 7
  fi

  #Change of clusters
  if [ "$1" == "100" ] && [ "$2" == "0.4" ] && [ "$3" == "1" ] && [ "$4" == "5" ] ; then
    configureFileSimple="configure08" #Configure 0
  fi

  if [ "$1" == "100" ] && [ "$2" == "0.4" ] && [ "$3" == "0.1" ] && [ "$4" == "5" ] ; then
    configureFileSimple="configure09" #Configure 1
  fi

  if [ "$1" == "100" ] && [ "$2" == "0.6" ] && [ "$3" == "1" ] && [ "$4" == "5" ] ; then
    configureFileSimple="configure10" #Configure 2
  fi

  if [ "$1" == "100" ] && [ "$2" == "0.6" ] && [ "$3" == "0.1" ] && [ "$4" == "5" ] ; then
    configureFileSimple="configure11" #Configure 3
  fi

  if [ "$1" == "50" ] && [ "$2" == "0.4" ] && [ "$3" == "1" ] && [ "$4" == "5" ] ; then
    configureFileSimple="configure12" #Configure 4
  fi

  if [ "$1" == "50" ] && [ "$2" == "0.4" ] && [ "$3" == "0.1" ] && [ "$4" == "5" ] ; then
    configureFileSimple="configure13" #Configure 5
  fi

  if [ "$1" == "50" ] && [ "$2" == "0.6" ] && [ "$3" == "1" ] && [ "$4" == "5" ] ; then
    configureFileSimple="configure14" #Configure 6
  fi

  if [ "$1" == "50" ] && [ "$2" == "0.6" ] && [ "$3" == "0.1" ] && [ "$4" == "5" ] ; then
    configureFileSimple="configure15" #Configure 7
  fi


  echo "$configureFileSimple"
}



#NOTE: WE REMOVE FROM THE TRAINING AND TEST SETS THOSE POIS WHICH HAVE WRONG COORDINATES


# For each city (single domain, each city individually)
for city in $cities
do
  # The test file is always the same
  path_inputs="../../data/POI/${city_or}"

  trainFile=$path_inputs/${city}"_mapped_trails_weather_aggregated_Temp80train.csv"
  testfile=$path_inputs/${city}"_mapped_trails_weather_aggregated_Temp20test.csv"

  cityCompletePOICoords=$path_inputs/${city}"_mapped_lat_lon_wrong_coordinates_by_midpoint.csv"
  cityPOICoords=$cityCompletePOICoords

  # We need to generate the new files:

  outtrainFile=$path_inputs/${city}"_mapped_trails_weather_aggregated_Temp80train_filtered_wrong_pois.csv"
  outtestfile=$path_inputs/${city}"_mapped_trails_weather_aggregated_Temp20test_filtered_wrong_pois.csv"
  outcityCompletePOICoords=$path_inputs/${city}"_mapped_lat_lon_filtered_wrong_pois.csv"
  python filter_checkins_file_by_wrong_coordinates.py --poi_file $cityCompletePOICoords --data_file $trainFile --column_index 2 --output_data_file $outtrainFile --output_pois_file $outcityCompletePOICoords
  python filter_checkins_file_by_wrong_coordinates.py --poi_file $cityCompletePOICoords --data_file $testfile --column_index 2 --output_data_file $outtestfile --output_pois_file $outcityCompletePOICoords

  cityPOICoords=$outcityCompletePOICoords
  trainFile=$outtrainFile
  testfile=$outtestfile




  recommendationFolder=${city}"_"${recFolder}
  mkdir -p $recommendationFolder

  echo "Current trainFile is $trainFile"
  echo "Current testfile is $testfile"
  echo "Current coord is $cityCompletePOICoords"
  echo "Current coord is $cityPOICoords"



  for ranksysRecommender in PopularityRecommender RandomRecommender
  do
    outputRecfile=$recommendationFolder/"$recPrefix"_"$city"_RSys_"$ranksysRecommender".txt
    $javaCommand $jvmMemory -jar $JAR -o ranksysOnlyComplete -trf $trainFile -tsf $testfile -cIndex true -rr "$ranksysRecommender" -rs "notUsed" -nI $itemsRecommended -n 20 -orf $outputRecfile
    $javaCommand $jvmMemory -jar $JAR -o CheckRecommendationsFile -trf $trainFile -tsf $testfile -rf $outputRecfile

  done
  wait

  for neighbours in $allneighbours
  do

        # ranksys with similarities UserBased
    for UBsimilarity in SJUS VCUS
    do
      outputRecfile=$recommendationFolder/"$recPrefix"_"$city"_RSys_UB_"$UBsimilarity"_k"$neighbours".txt
      $javaCommand $jvmMemory -jar $JAR -o ranksysOnlyComplete -trf $trainFile -tsf $testfile -cIndex false -rr UserNeighborhoodRecommender -rs $UBsimilarity -nI $itemsRecommended -n $neighbours -orf $outputRecfile
      $javaCommand $jvmMemory -jar $JAR -o CheckRecommendationsFile -trf $trainFile -tsf $testfile -rf $outputRecfile

    done
    wait

    # Ranksys with similarities ItemBased
    for IBsimilarity in SJIS VCIS
    do
       outputRecfile=$recommendationFolder/"$recPrefix"_"$city"_RSys_IB_"$IBsimilarity"_k"$neighbours".txt
       $javaCommand $jvmMemory -jar $JAR -o ranksysOnlyComplete -trf $trainFile -tsf $testfile -cIndex false -rr ItemNeighborhoodRecommender -rs $IBsimilarity -nI $itemsRecommended -n $neighbours -orf $outputRecfile
       $javaCommand $jvmMemory -jar $JAR -o CheckRecommendationsFile -trf $trainFile -tsf $testfile -rf $outputRecfile
    done
    wait # End IB Sim

  done # End Neighbours
  wait


    #Our GeoBPRMF from ranksys
    #distance neighs is 4kms
  for repetition in 1 #2 3 4 5
  do
    for factor in $BPRFactors
    do
      for bias_reg in $BPRBiasReg
        do
          for regU in $BPRRegU #Regularization for items and users is the same
          do
            for maxDist in $geoBPRmaxDists
            do
              outputRecfile=$recommendationFolder/"$recPrefix"_"$city"_RSys_GeoBPRMF_nF"$factor"_nIt"$BPRNumIter"_LR"$BPRLearnRate"_BR"$bias_reg"_RU"$regU"_RI"$regU"_MaxD"$maxDist"_Rep"$repetition".txt
              $javaCommand $jvmMemory -jar $JAR -o ranksysOnlyComplete -trf $trainFile -tsf $testfile -cIndex false -rr GeoBPRMF -nI $itemsRecommended -n 20 -orf $outputRecfile -kFactorizer $factor -nIFactorizer $BPRNumIter -svdLearnRate $BPRLearnRate -svdRegBias $bias_reg -svdRegUser $regU -svdRegItem $regU -coordFile $cityPOICoords -maxDist $maxDist &
              #$javaCommand $jvmMemory -jar $JAR -o CheckRecommendationsFile -trf $trainFile -tsf $testfile -rf $outputRecfile

            done
            wait
          done # Reg U
          wait
        done # Bias reg
        wait
      done # Factors
      wait
    done # Repetition
    wait

    # As this is for the pure approach, it is not Necessary to use repeated items

  for repetition in 1 #2 3 4
  do
    for factor in $BPRFactors
    do
      for bias_reg in $BPRBiasReg
      do
        for regU in $BPRRegU #Regularization for items and users is the same
        do
          regJ=$(echo "$regU/10" | bc -l)

          outputRecfile=$recommendationFolder/"$recPrefix"_"$city"_"$extensionMyMediaLite"_BPRMF_nF"$factor"_nIt"$BPRNumIter"_LR"$BPRLearnRate"_BR"$bias_reg"_RU"$regU"_RI"$regU"_RJ"$regJ""Rep$repetition".txt
          echo $outputRecfile
          if [ ! -f "$outputRecfile" ]; then

            outputRecfile2=$outputRecfile"Aux".txt
            echo "./$mymedialitePath/item_recommendation --training-file=$trainFile --recommender=BPRMF --random-seed 45 --prediction-file=$outputRecfile2 --predict-items-number=$itemsRecommended --recommender-options="num_factors=$factor bias_reg=$bias_reg reg_u=$regU reg_i=$regU reg_j=$regJ learn_rate=$BPRLearnRate UniformUserSampling=false WithReplacement=false num_iter=$BPRNumIter""
            ./$mymedialitePath/item_recommendation --training-file=$trainFile --recommender=BPRMF --prediction-file=$outputRecfile2 --predict-items-number=$itemsRecommended --recommender-options="num_factors=$factor bias_reg=$bias_reg reg_u=$regU reg_i=$regU reg_j=$regJ learn_rate=$BPRLearnRate UniformUserSampling=false WithReplacement=false num_iter=$BPRNumIter"
            $javaCommand $jvmMemory -jar $JAR -o ParseMyMediaLite -trf $outputRecfile2 $testfile $outputRecfile
            rm $outputRecfile2
           fi
        done # Reg U
        wait
      done # Bias reg
      wait
    done # Factors
    wait
  done # Repetition
  wait

      # HKV
      for rankRecommenderNoSim in MFRecommenderHKV
      do
        for kFactor in $allKFactorizerRankSys
        do
          for lambdaValue in $allLambdaFactorizerRankSys
          do
            for alphaValue in $allAlphaFactorizerRankSys
            do
              # Neighbours is put to 20 because this recommender does not use it

              outputRecfile=$recommendationFolder/"$recPrefix"_"$city"_RSys_"$rankRecommenderNoSim"_kF"$kFactor"_aF"$alphaValue"_lF"$lambdaValue".txt
              $javaCommand $jvmMemory -jar $JAR -o ranksysOnlyComplete -trf $trainFile -trf2 -tsf $testfile -cIndex false -rr $rankRecommenderNoSim -rs "notUsed" -nI $itemsRecommended -n 20 -orf $outputRecfile -kFactorizer $kFactor -aFactorizer $alphaValue -lFactorizer $lambdaValue
              $javaCommand $jvmMemory -jar $JAR -o CheckRecommendationsFile -trf $trainFile -tsf $testfile -rf $outputRecfile

            done
            wait # End alpha values
          done
          wait # End lambda
        done
        wait # End KFactor
      done
      wait # End RankRecommender

      for poiRecommender in AverageDistanceUserGEO
      do
        outputRecfile=$recommendationFolder/"$recPrefix"_"$city"_RSys_POI_"$poiRecommender"SIMPLE.txt
        $javaCommand $jvmMemory -jar $JAR -o ranksysOnlyComplete -trf $trainFile -tsf $testfile -cIndex false -rr $poiRecommender -rs "notUsed" -nI $itemsRecommended -n 20 -orf $outputRecfile -coordFile $cityPOICoords
        $javaCommand $jvmMemory -jar $JAR -o CheckRecommendationsFile -trf $trainFile -tsf $testfile -rf $outputRecfile
      done # End poiRecommender
      wait

      # Using the SUM
      for poiRecommender in AverageDistanceUserGEO
      do
        outputRecfile=$recommendationFolder/"$recPrefix"_"$city"_RSys_POI_"$poiRecommender"FREQUENCY.txt
        $javaCommand $jvmMemory -jar $JAR -o ranksysOnlyComplete -trf $trainFile -tsf $testfile -cIndex false -rr $poiRecommender -rs "notUsed" -nI $itemsRecommended -n 20 -orf $outputRecfile -coordFile $cityPOICoords -scoreFreq FREQUENCY
        $javaCommand $jvmMemory -jar $JAR -o CheckRecommendationsFile -trf $trainFile -tsf $testfile -rf $outputRecfile
      done
      wait


      for poiRecommender in KDEstimatorRecommender
      do
        outputRecfile=$recommendationFolder/"$recPrefix"_"$city"_RSys_POI_"$poiRecommender".txt
        $javaCommand $jvmMemory -jar $JAR -o ranksysOnlyComplete -trf $trainFile -tsf $testfile -cIndex false -rr $poiRecommender -rs "notUsed" -nI $itemsRecommended -n 20 -orf $outputRecfile -coordFile $cityPOICoords
        $javaCommand $jvmMemory -jar $JAR -o CheckRecommendationsFile -trf $trainFile -tsf $testfile -rf $outputRecfile

      done # End poiRecommender
      wait



      #FMFMGM

      for repetition in 1 #2 3 4 5
      do
        for alpha_FMFMGM in $alphas_FMFMGM
        do
          for theta_FMFMGM in $thetas_FMFMGM
          do
            for distance_FMFMGM in $distances_FMFMGM #
            do
              for iter_FMFMGM in $iters_FMFMGM
              do
                for kfactor_FMFMGM in $kfactors_FMFMGM
                do
                  for alpha2_FMFMGM in $alphas2_FMFMGM
                  do
                    for beta_FMFMGM in $betas_FMFMGM
                    do
                      for learningRate_FMFMGM in $learningRates_FMFMGM
                      do
                        for sigmoid_FMFMGM in $sigmoids_FMFMGM
                        do

                          outputRecfile=$recommendationFolder/"$recPrefix"_"$city"_RSys_POI_"FMFMGM"_a"$alpha_FMFMGM"_t"$theta_FMFMGM"_d"$distance_FMFMGM"_i"$iter_FMFMGM"_f"$kfactor_FMFMGM"_a2"$alpha2_FMFMGM"_b"$beta_FMFMGM"_lR"$learningRate_FMFMGM"_sig"$sigmoid_FMFMGM".txt
                          $javaCommand $jvmMemory -jar $JAR -o ranksysOnlyComplete -trf $trainFile -tsf $testfile -cIndex false -rr "FMFMGM" -coordFile $cityPOICoords -aFactorizer $alpha_FMFMGM -thetaFactorizer $theta_FMFMGM -maxDist $distance_FMFMGM -nIFactorizer $iter_FMFMGM -kFactorizer $kfactor_FMFMGM -aFactorizer2 $alpha2_FMFMGM -svdBeta $beta_FMFMGM -svdLearnRate $learningRate_FMFMGM -useSigmoid $sigmoid_FMFMGM -n 20 -nI $itemsRecommended -orf $outputRecfile
                          $javaCommand $jvmMemory -jar $JAR -o CheckRecommendationsFile -trf $trainFile -tsf $testfile -rf $outputRecfile

                        done # sigmoid
                        wait
                      done # learningRate
                      wait
                    done # beta
                    wait
                   done # alphas2
                   wait
                  done # kFactor
                  wait
                done # iters
                wait
              done # distance
              wait
            done # Theta
            wait
          done # alphas
          wait
        done # Repetition
        wait


# RankGeoTest

  for c in $cs_RANKGEOFM
  do
    for alphaF in $alphas_RANKGEOFM
    do
      for epsilon in $epsilons_RANKGEOFM
      do
        for kFactorizer in $kfactors_RANKGEOFM
        do
          for kNeighbour in $ns_RANKGEOFM
          do
            for numIter in $iters_RANKGEOFM
            do

              for decay in $decays_RANKGEOFM
              do

                for isboldDriver in $isboldDriver_RANKGEOFM
                do

                  for learnRate in $learnRates_RANKGEOFM
                  do
                    for maxRate in $maxRates_RANKGEOFM
                    do

                      outputRecfile=$recommendationFolder/"$recPrefix"_"$city"_RSys_POI_"RankGeoFM""kFac"$kFactorizer"kNgh"$kNeighbour"dec"$decay"bDriv"$isboldDriver"It"$numIter"lR"$learnRate"mR"$maxRate"a"$alphaF"c"$c"eps"$epsilon"".txt
                      $javaCommand $jvmMemory -jar $JAR -o ranksysOnlyComplete -trf $trainFile -tsf $testfile -cIndex false -rr "RankGeoFMRecommender" -coordFile $cityPOICoords -n $kNeighbour -nIFactorizer $numIter -kFactorizer $kFactorizer -aFactorizer $alphaF -epsilon $epsilon -c $c -svdDecay $decay -svdIsboldDriver $isboldDriver -svdLearnRate $learnRate -svdMaxLearnRate $maxRate -nI $itemsRecommended -orf $outputRecfile
                      $javaCommand $jvmMemory -jar $JAR -o CheckRecommendationsFile -trf $trainFile -tsf $testfile -rf $outputRecfile

                    done # ENd max learn
                    wait

                  done # Learn rate
                  wait
                done # End bold
                wait

              done # End decay
              wait
            done # End iter
            wait

          done # ENd neigh
          wait

        done # End kFactors
        wait
      done # Epsilon
      wait
    done # Alpha
    wait
  done # End c
  wait



  lambda_easer=0.5
  output_rec_file=$recommendationFolder/"$recPrefix"_"$city"_"easer"_"lambda"$lambda_easer"_ImplicitTrue".txt
  python "$path_baselines_poi"/ease_r/main.py --training $trainFile --test $testfile --implicit True --lamb $lambda_easer --nI $itemsRecommended --result $output_rec_file

  output_rec_file=$recommendationFolder/"$recPrefix"_"$city"_"easer"_"lambda"$lambda_easer"_ImplicitFalse".txt
  python "$path_baselines_poi"/ease_r/main.py --training $trainFile --test $testfile --lamb $lambda_easer --nI $itemsRecommended --result $output_rec_file



  for beta in "0.6" "0.7"
  do
    for alpha in "1" "2"
    do

        output_rec_file=$recommendationFolder/"$recPrefix"_"$city"_"RP3beta"_"beta"$beta"_"alpha""$alpha"_ImplicitTrue".txt
        python "$path_baselines_poi"/rp3beta/run2.py --training $trainFile --test $testfile --nI $itemsRecommended --result $output_rec_file --implicit True --alpha $alpha --beta $beta

        output_rec_file=$recommendationFolder/"$recPrefix"_"$city"_"RP3beta"_"beta"$beta"_"alpha""$alpha"_ImplicitFalse".txt
        python "$path_baselines_poi"/rp3beta/run2.py --training $trainFile --test $testfile --nI $itemsRecommended --result $output_rec_file --alpha $alpha --beta $beta

    done
    wait
  done # Repetition
  wait


  #Second baseline: popularity, knn and minimum distance. This recommender is H-PUM in the paper
  for poiRecommender in PopGeoNN
  do
    for UBsimilarity in SJUS VCUS
    do
      for neighbours in $allneighbours
      do
        outputRecfile=$recommendationFolder/"$recPrefix"_"$city"_RSys_POI_"$poiRecommender"_UBSim_"$UBsimilarity"_k"$neighbours".txt
        $javaCommand $jvmMemory -jar $JAR -o ranksysOnlyComplete -trf $trainFile -tsf $testfile -cIndex true -rr $poiRecommender -rs $UBsimilarity -nI $itemsRecommended -n $neighbours -orf $outputRecfile -coordFile $cityCompletePOICoords
        $javaCommand $jvmMemory -jar $JAR -o CheckRecommendationsFile -trf $trainFile -tsf $testfile -rf $outputRecfile

      done # End neighbours
      wait
    done # End UB similarity
    wait
  done # End poiRecommender
  wait

  resultFileNNCityFile=$pathDest/POIS_""$city""_"$GeoNN"NN.txt
  poisCoordsOfCityFile=$pathDest/"$processedCities"/POIS_""$city""_"$extensionCoords"
  specificCityPOICoords=$path_inputs/${city}"_mapped_lat_lon_ONLYTRAINING_WrongCoordsByMidpoint.csv"
  $javaCommand $jvmMemory -jar $JAR -o SpecificPOICoords -trf $trainFile -coordFile $cityCompletePOICoords -orf $specificCityPOICoords


  if [ ! -f $resultFileNNCityFile ]; then
    $javaCommand $jvmMemory -jar $JAR -o printClosestPOIs -trf $trainFile $specificCityPOICoords $resultFileNNCityFile $poisCoordsOfCityFile $GeoNN

  fi


  for KIRENMF in $allKIRENMF
  do
    for alphaIRENMF in $allAlphaIRENMF
    do
      for lambda3IRENMF in $allLambda3IRENMF
      do
        for clusterIRENMF in $clustersIRENMF
        do
          configureFileSimple=$(obtainConfigureFile "$KIRENMF" "$alphaIRENMF" "$lambda3IRENMF" "$clusterIRENMF")

          echo "Parameters K=$KIRENMF alpha=$alphaIRENMF lambda3=$lambda3IRENMF clusters=$clusterIRENMF"
          echo "File " $title " working with configure " $configureFileSimple

          configureFileToSelect="configure"_"K"$KIRENMF"_Alpha""$alphaIRENMF""_L1_"$lambda1"_L2_"$lambda2"_L3_"$lambda3IRENMF"_GeoNN"$GeoNN"_clusters"$clusterIRENMF
          outputRecfile=$pathDest/$recommendationFolder/"$recPrefix"_"$city"_IRENMF_"$configureFileToSelect".txt

          clusterFile=$pathDest/$recommendationFolder/$city"_"Clusters$clusterIRENMF"_"
          rm $clusterFile"_clusters".mat

          if [ ! -f $outputRecfile ]; then
              #ItemGroupPOI(configure_file, trainFile, poisCoordsFile,GeoNNFile,testingFile, candidatesFile,outFile,clusterFile)
              "$fullpathMatlab" -nodisplay -nodesktop -r "restoredefaultpath; rehash toolboxcache; cd '$pathIrenMF/'; ItemGroupPOI('$configureFileSimple', '$pathDest/$trainFile', '$poisCoordsOfCityFile', '$resultFileNNCityFile', '$pathDest/$testfile', '$resultFileNNCityFile', '$outputRecfile', '$clusterFile'); quit"
          fi

          echo "Finished $configureFileSimple"

        done #End cluster
        wait
      done
      wait #End lambda
    done
    wait #End alpha IrenMF
  done
  wait #End KIRENMF







done # End cities
wait







: '
Evaluation part
'

cities="PetalingJaya"
JAR=SequentialRecommenders.jar
nonaccresultsPrefix=naev
evthreshold=1

for city in $cities
do
  path_inputs="Cities/"${city}/Original
  resFolder=${city}"_"$resultFolder
  recommendationFolder=${city}"_"${recFolder}
  mkdir -p $resFolder


  # In every case
  trainFile=$path_inputs/${city}"_mapped_trails_weather_aggregated_Temp80train_filtered_wrong_pois.csv"
  testfile=$path_inputs/${city}"_mapped_trails_weather_aggregated_Temp20test_filtered_wrong_pois.csv"

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
