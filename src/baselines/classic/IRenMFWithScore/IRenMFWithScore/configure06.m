%%%%%% Global configuration file  %%%%%%
%%% Holds all the parameters used in all parts of the code, enable the
%%% exact reproduction of the experiement at some future date.
    
    
global geo_alpha %datasetfolder dataset_name datafolder datasetGeoNN datafolderResult datasetTrain_name datasetTest_name datasetPOIS_COORDS datasetPOIS_candidates

switch lower(EXPTYPE)
    case 'global'    
        %fullPath='/home/pablosanchez/Escritorio/UMUAIExperimentsFoursqr/TrainTest/CitiesSplit/';                   
        %datasetfolder=strcat(fullPath,'Fold0/BR_SaoPaulo/');
        %datafolder=strcat(fullPath,'Fold0/BR_SaoPaulo/');
        addpath('common/');
        %dataset_name='BR_SaoPaulo';
        %datasetTest_name='split_BR_SaoPaulo__test0.dat'; %test subset
        %datasetTrain_name='split_BR_SaoPaulo__trainingAggrAVERAGE0.dat'; %train subset
        %datasetGeoNN='POIS_BR_SaoPaulo_10NN.txt'; %neighbourPOIS
        %datasetPOIS_COORDS='POIS_BR_SaoPaulo__Coords.txt'; %coordinates pois
        %datasetPOIS_candidates=datasetGeoNN;
        %datafolderResult=strcat(fullPath,'Fold0/BR_SaoPaulo/RecommendationFolder/');
        geo_alpha=0.6; % the geographical influence parameter

        

    case 'dataprepare'
        num_cluster=50;            
        geoNN_Num=10;
        clusterflag='kmeans'; % 'kmeans' for kmeans clustering
                                % 'spectral' for spectral clustering

    case 'checkin_weighting'
        weighting.alpha=10;    

    %-------------------------- model parameters ----------------------%            
    case 'gsslfm'              
        gsslfm.num_factors=50;
        gsslfm.epoches=150;
        gsslfm.lambda=[0.015, 0.015, 1];        % regularization term for group lasso    
        gsslfm.threshold=1e-5;

    %-------------------------- user latent factor parameters ----------------------%
    case 'userapg'
        userapg.epoches=70;
        userapg.tau=1e6;
        userapg.t=1;
        userapg.eta=0.7;
        userapg.threshold=1e-5;

    %-------------------------- item latent factor parameters ----------------------%
    case 'itemapg'
        itemapg.epoches=70;
        itemapg.tau=1e7;
        itemapg.t=1;
        itemapg.eta=0.7;
        itemapg.threshold=1e-5;

    case 'model_eval'
        N=[100]; %changed to return 100 items

end

