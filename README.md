# Context Trails

Repository containing the code used in the paper:  
**Context Trails: A dataset to study contextual and tour recommendation**

## 📌 Requirements
To run the code in this repository, you need the following prerequisites:

### 🖥️ Required Software
- **Java** (version 8 or higher)
- **Mono** (to run MyMediaLite)
- **Matlab** (to run IRenMF)
- **Python** (version 3.8 or higher)

### 📦 Python Dependencies
To install the required libraries, run the following command:

```bash
pip install \
    Cython==0.29.6 \
    h5py==2.9.0 \
    nltk==3.4.5 \
    nose==1.3.7 \
    numpy==1.16.2 \
    pandas==0.24.2 \
    scikit-learn==0.20.3 \
    scikit-optimize==0.5.2 \
    scipy==1.2.1 \
    tqdm==4.31.1 \
    implicit==0.4.4 \
    similaripy==0.1.2
```
  Probably, you will need to install also these libraries:
```
  sudo apt install g++
  conda install -c conda-forge libstdcxx-ng
```



### 📂 Repository Structure
 - **online_appendix.pdf**: file with extended tables from those shown in the paper.
 - **src**: directory containing the source code of the recommenders used in the experiments
 - **scripts**: directory containing the bash scripts for generating the recommendations. **IMPORTANT**: ensure that scripts end with the end-of-line character of LF, not CRLF.
  * POI: contains the scripts to perform POI recommendations. Follow this order of execution:
    * **step1_prepare_data.sh**: script that will prepare all necessary files to execute the experiments for POI recommendation. **NOTE**: configure properly the ''path_source_data_repository'' variable. This variable must reference to the path of the repository [ContextTrailsData](https://github.com/pablosanchezp/ContextTrailsData/) repository.
    * **step2_generate_recommenders.sh**: script that will execute the experiments for POI recommendation. It will generates a recommendation folder and a results folder for each city. The format of each recommendation file (one per each hyperparameter configuration of each recommender) is: user_id \t venue_id \t score. The format of each result file (one per each hyperparameter configuration of each recommender) is: metric \t result.
    **NOTE**:you will need to set the ''fullpathMatlab'' variable to refer to the path of your Matlab installation.
  * Route: contains the scripts to perform route recommendations. Order of execution:
    * **step1_prepare_routes_data.sh**: script that will prepare all necessary files to execute the experiments for Route recommendation. **NOTE**: configure properly the ''path_source_data_repository'' variable. This variable must reference to the path of the repository [ContextTrailsData](https://github.com/pablosanchezp/ContextTrailsData/) repository.
    * **step2_generate_route_recommenders.sh**: script that will execute the experiments for Route recommendation. It will generates a recommendation folder and a results folder for each city. Each recommendation/result file will follow the same format as in POI recommendation.



 - **NOTE**: the data used in this repository can be found in the repository [ContextTrailsData](https://github.com/pablosanchezp/ContextTrailsData/). It is necessary to have the data repository in order to run the experiments correctly.



### 🛠️ Additional algorithms/frameworks used in the experiments
  * [MyMedialite](http://www.mymedialite.net/) (for BPR)
  * [Embarrassingly Shallow Autoencoders for Sparse Data](https://dl.acm.org/doi/10.1145/3308558.3313710) (for EASEr): [source code](https://github.com/Darel13712/ease_rec) (directory ease_rec).
  * [Updatable, Accurate, Diverse, and Scalable Recommendations for Interactive Applications](https://dl.acm.org/doi/10.1145/2955101) (for RP3beta): [source code](https://github.com/StivenMetaj/Recommender_Systems_Challenge_2020) (directory recommender-systems).



### 👥Authors
- Pablo Sánchez - [Universidad Pontificia Comillas](https://www.comillas.edu/)
- Alejandro Bellogín - [Universidad Autónoma de Madrid](https://uam.es)
- José Luis Jorro Aragoneses - [Universidad Autónoma de Madrid](https://uam.es)

### 📬 Contact

* **Pablo Sánchez** - <psperez@icai.comillas.edu>


### 🙏 Acknowledgments
 - This work was supported by grant PID2022-139131NB-I00 funded by MCIN/AEI/10.13039/501100011033 and by ``ERDF A way of making Europe.''
