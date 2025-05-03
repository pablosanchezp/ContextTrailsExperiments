%% Location Group LASSO
function ItemGroupPOI(configure_file, trainFile, poisCoordsFile,GeoNNFile,testingFile, candidatesFile,outFile,clusterFile)

    addpath(genpath('spectral_clustering/')); % the folder of spectral clustering algorithm
    t0=cputime;
    
    for i = 1 : 1
        EXPTYPE='global';     
        eval(configure_file); % load the configure parameters    
		
		testingFiles=strsplit(testingFile,',');
        candidatesFiles=strsplit(candidatesFile,',');
        outFiles=strsplit(outFile,',');

        fprintf('Testing, candidates and out \n');
		disp(testingFiles)
		disp(candidatesFiles)
		disp(outFiles)
		

		fprintf('Testing, candidates and out \n');

		for j = 1 : length(testingFiles)
            disp(strcat('Working with test file->', testingFiles{j}))
            disp(strcat('Working with candidate file->', candidatesFiles{j}))
            disp(strcat('Result file will be->', outFiles{j}))
		end
	
        
		%-------------data preparation ------------------%   
        [Tr, TrUsers,mapUsersInV, mapItemsInv, mapUsers, mapItems]=dataPreparation(configure_file,trainFile, poisCoordsFile,GeoNNFile,clusterFile);  
        fprintf('complete the data preparation\n');
        
        %-------------data sampling ------------------% 
        [Tr.R, Tr.W, Tr.wMat]= checkinMandWeightingMatrix(Tr, configure_file);
        fprintf('complete constructing the checkin and weighting matrices\n');

        %--------------learn the model parameters ------------------%            
        [userW, itemW]= locationGSSLFM(Tr, configure_file);
        %Splits if we are optimizing
        
        
        for j = 1 : length(testingFiles)
            disp(strcat('Working with test file->', testingFiles{j}))
            disp(strcat('Working with candidate file->', candidatesFiles{j}))
            disp(strcat('Result file will be->', outFiles{j}))
    
            testingdata=dlmread(testingFiles{j});
            TeUsers=unique(testingdata(:,1));
            RecUsers2 = intersect(TrUsers,TeUsers); %recUsers2 contains the external Ids            
            RecUsers = zeros(1, length(RecUsers2));
            for k = 1: length(RecUsers2)
                RecUsers(k) = mapUsers(num2str(RecUsers2(k))); %store all users
            end
            
            %--------------Evaluate the model performance ------------------%  
            topN_recommendation(Tr, RecUsers, userW, itemW, configure_file,mapUsersInV,mapItemsInv,candidatesFiles{j},outFiles{j});
        end 
        
    end
    
    t=cputime-t0;
    
    fprintf('total time used: %g\n', t);
    
end
    
