%{
function [Tr, Te]=dataPreparationOriginal(configure_file)
    
    EXPTYPE='dataprepare';
    eval(configure_file);
        
    %-------------------- print parameters to the file --------------------%
    fid=fopen([datafolder,configure_file,'_Results.txt'], 'a+');   
    fprintf(fid, 'dataset: %s, clusterflag: %s\n', dataset_name, clusterflag);
    fclose(fid);
      
    %-------------------------data files--------------------%
    trainingfile=[datasetfolder, datasetTrain_name];
    testingfile=[datasetfolder, datasetTest_name];
    POIfile=[datasetfolder, datasetPOIS_COORDS];    

    pidNNfile=[datasetfolder, dataset_name, '_GeoNN.txt'];  
   
    trainingdata=dlmread(trainingfile);
    testingdata=dlmread(testingfile);

    Tr.users = trainingdata(:,1); Tr.items = trainingdata(:,2); Tr.times = trainingdata(:,3);    
    Te.users = testingdata(:,1); Te.items = testingdata(:,2); Te.times = testingdata(:,3);
    
    pidNN=dlmread(pidNNfile);
    

    POIdata=dlmread(POIfile);
    
    [val, index]=sort(POIdata(:, 1));
    POIdata=POIdata(index, :);
    
    Tr.CorrM=geographicalCorr(POIdata, pidNN, geoNN_Num);
    
    % Geographical groups
%     clusterInx=geographicalGroup(POIdata, gridpara, grid_flag); 

    %--------------Geo-kmeans (Matlab)----------------------------------%
    if strcmp(clusterflag, 'kmeans')
        cluster_file=[datasetfolder, dataset_name, '_', num2str(num_cluster), '_clusters.mat'];
        if ~exist(cluster_file, 'file')
            [IDX, C]=kmeans(POIdata(:, 2:3), num_cluster);
            clusterInx=[POIdata(:, 1), IDX];
            save(cluster_file, 'clusterInx')
        else
            load(cluster_file, '-mat');
        end
    elseif strcmp(clusterflag, 'spectral')
        cluster_file=[datasetfolder, dataset_name, '_', num2str(num_cluster), '_spectral_clusters.mat'];
        if ~exist(cluster_file, 'file')
            IDX=PoiSpectralClustering(trainingdata, pidNN, 15, num_cluster);
            clusterInx=[POIdata(:, 1), IDX];
            save(cluster_file, 'clusterInx');
        else
            load(cluster_file, '-mat');
        end
    elseif strcmp(clusterflag, 'kmeans_history')
        cluster_file=[datasetfolder, dataset_name, '_', num2str(num_cluster), '_kmeans_history.mat'];
        if ~exist(cluster_file, 'file')
            IDX=PoiHistoryKmeans(trainingdata, num_cluster);
            clusterInx=[POIdata(:, 1), IDX];
            save(cluster_file, 'clusterInx');
        else
            load(cluster_file, '-mat');
        end
    end
        
    Tr.groupInX=getGroupInx(clusterInx);
 
%     Tr= struct ('users', trainingdata(:, 1), 'items', trainingdata(:,2), 'times', trainingdata(:,3));
%     Te= struct ('users', testingdata(:, 1), 'items', testingdata(:,2), 'times', testingdata(:,3));
   
end
%}
function [Tr,TrUsers,userInvMapping,itemInvMapping,userMapping,itemMapping]=dataPreparation(configure_file,trainFile, poisCoordsFile,GeoNNFile,clusterFile)
    
    EXPTYPE='dataprepare';
    eval(configure_file);
    fprintf('alpha')
    disp(geo_alpha)
        
    %-------------------- print parameters to the file --------------------%
   % fid=fopen([datafolder,configure_file,'_Results.txt'], 'a+');   
    %fprintf(fid, 'dataset: %s, clusterflag: %s\n', dataset_name, clusterflag);
    %fclose(fid);
      
    %-------------------------data files--------------------%
    trainingfile=trainFile;
    POIfile=poisCoordsFile;    

    pidNNfile=GeoNNFile;  
   
    POIdata=dlmread(POIfile);
    %% process this matrix with mappings
    %
    itemMapping = containers.Map; %OurId -> idMatlab
    itemInvMapping = containers.Map; %idMatlab -> ourId
    userMapping = containers.Map; %OurId -> idMatlab
    userInvMapping = containers.Map; %idMatlab -> ourId
    
    trainingdata=dlmread(trainingfile);
    %% obtain old-new user/item mappings + new-old user/item mapping (to be returned)
    defaultMissingId = -1; % id to be used for users and items not in training
    TrUsers=unique(trainingdata(:,1));
    
    TrItems=unique(trainingdata(:,2));

    
    for i = 1 : length(TrUsers)
        userMapping(num2str(TrUsers(i))) = i; %map of users to increment (trainUsers)
        userInvMapping(num2str(i)) = TrUsers(i); %inverse map
    end
    

      
    for i = 1 : length(TrItems);
        itemMapping(num2str(TrItems(i))) = i; %maps of thetraining items
        itemInvMapping(num2str(i)) = TrItems(i);
    end
    pidNN2=dlmread(pidNNfile); %%nn-POIFile
    [nrows,ncols] = size(pidNN2);
    
    actualMax = length(TrItems) + 1;
    for i = 1: nrows
        if not(isKey(itemMapping,num2str(pidNN2(i,1))))
            itemMapping(num2str(pidNN2(i,1))) = actualMax; %Only if the items are not in the train (but we need all the items to be in train)
            itemInvMapping(num2str(actualMax)) = pidNN2(i,1);
            actualMax = actualMax + 1;
        end
    end
       
    %
    %% process each matrix with mappings
    [nrows,ncols] = size(trainingdata);
    for i= 1: nrows
        trainingdata(i,1)=userMapping(num2str(trainingdata(i,1))); %newuser
        trainingdata(i,2)=itemMapping(num2str(trainingdata(i,2))); %newitem
    end %Training data has now matlabs ids
    
    %
    Tr.users = trainingdata(:,1); Tr.items = trainingdata(:,2); Tr.times = trainingdata(:,3);    
    %Te.users = testingdata(:,1); Te.items = testingdata(:,2); Te.times = testingdata(:,3);    
    
    %% process this matrix with mappings
    %
    [nrows,ncols] = size(pidNN2);
    pidNN = zeros(nrows,ncols);
    for i= 1: nrows
        externalId = pidNN2(i,1);
        matlabId = itemMapping(num2str(externalId)); % this is the row to update
        for j= 1: ncols
            pidNN(matlabId, j) = itemMapping(num2str(pidNN2(i, j))); %Update all values of the NN
        end
    end
    
    %%Update now the ids of the file of coordinates
    [nrows,ncols] = size(POIdata);
    for i= 1:nrows
        if isKey(itemMapping, num2str(POIdata(i,1))) %Only if the POI exists
            POIdata(i,1) = itemMapping(num2str(POIdata(i,1)));
        end
    end

    
    %%We should also modify POIdata
    
    
    [val, index]=sort(POIdata(:, 1));
    POIdata=POIdata(index, :);
    
    Tr.CorrM=geographicalCorr(POIdata, pidNN, geoNN_Num);
    
    % Geographical groups
%     clusterInx=geographicalGroup(POIdata, gridpara, grid_flag); 

    %--------------Geo-kmeans (Matlab)----------------------------------%
    if strcmp(clusterflag, 'kmeans')
        cluster_file=[clusterFile, '_clusters.mat'];
        if ~exist(cluster_file, 'file')
            [IDX, C]=kmeans(POIdata(:, 2:3), num_cluster);
            clusterInx=[POIdata(:, 1), IDX];
            save(cluster_file, 'clusterInx')
        else
            load(cluster_file, '-mat');
        end
    elseif strcmp(clusterflag, 'spectral')
        cluster_file=[clusterFile, '_spectral_clusters.mat'];
        if ~exist(cluster_file, 'file')
            IDX=PoiSpectralClustering(trainingdata, pidNN, 15, num_cluster);
            clusterInx=[POIdata(:, 1), IDX];
            save(cluster_file, 'clusterInx');
        else
            load(cluster_file, '-mat');
        end
    elseif strcmp(clusterflag, 'kmeans_history')
        cluster_file=[clusterFile, '_kmeans_history.mat'];
        if ~exist(cluster_file, 'file')
            IDX=PoiHistoryKmeans(trainingdata, num_cluster);
            clusterInx=[POIdata(:, 1), IDX];
            save(cluster_file, 'clusterInx');
        else
            load(cluster_file, '-mat');
        end
    end
        
    Tr.groupInX=getGroupInx(clusterInx);   
end

function CorrM=geographicalCorr(POICoords, geoNN_InX, geoNN_Num)
    Corr=[]; [m, n]=size(geoNN_InX);
    
    for i = 1 : m
        geoSim=L2_distance(POICoords(geoNN_InX(i, 1), 2:3)', POICoords(geoNN_InX(i, 2: geoNN_Num+1), 2:3)'); % may need some modification
        geoSim=exp(-10*geoSim);
        temp=[ones(geoNN_Num, 1)*geoNN_InX(i, 1), geoNN_InX(i, 2: (geoNN_Num+1))', geoSim'/sum(geoSim)];
        Corr=[Corr; temp];
    end

    CorrM=sparse(Corr(:, 1), Corr(:, 2), Corr(:, 3), m, m);    

end

function CorrM=pidCorrelation(pidNN)
    pids=unique(pidNN(:, 1)); m=length(pids); data=pidNN;
    for i= 1 : m
        index=(pidNN(:, 1)==pids(i));
        data(index, 3)=exp(data(index, 3))/sum(exp(data(index, 3)));
    end
    
    CorrM=sparse(data(:, 1), data(:, 2), data(:, 3), m, m);

end

function IDX=PoiSpectralClustering(trainingdata, pidNN, geoNN_Num, num_cluster)
    M=sparse(trainingdata(:, 1), trainingdata(:, 2), ones(1, length(trainingdata(:,1))), max(trainingdata(:, 1)), max(trainingdata(:, 2)));
    itemnum=max(pidNN(:, 1)); Similarity=[];
    
    for i = 1 : itemnum
        distance= full(slmetric_pw(M(:,i), M(:, pidNN(i, 2 : geoNN_Num+1)), 'nrmcorr'));
        Similarity=[Similarity; [i*ones(geoNN_Num, 1), pidNN(i, 2 : geoNN_Num+1)', distance']];
    end
    SimM=sparse(Similarity(:, 1), Similarity(:, 2), Similarity(:, 3)+0.001, itemnum, itemnum);
    SimM=0.5*(SimM+ SimM'+abs(SimM-SimM'));

    fprintf('begin the spectral clustering\n');
    [IDX, L, U] = SpectralClustering(SimM, num_cluster, 3);

end

function IDX=PoiHistoryKmeans(trainingdata, num_cluster)
    M=sparse(trainingdata(:, 1), trainingdata(:, 2), ones(1, length(trainingdata(:,1))), max(trainingdata(:, 1)), max(trainingdata(:, 2)));
%     IDX=kmeans(M', num_cluster);
    
    cluster_options.maxiters= 200;
    cluster_options.verbose =1;
    [CX, sse] = vgg_kmeans(full(M), num_cluster, cluster_options);
    L2D=L2_distance(M, CX);
    [minD, tempToken]=min(L2D');
    IDX = tempToken';
    
end
