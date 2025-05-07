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



### 📂 Repository Structure
 - **online_appendix.pdf**: file with extended tables from those shown in the paper.
 - **src**: directory containing the source code of the recommenders used in the experiments
 - **scripts**: directory containing the bash scripts for generating the recommendations
  * POI: contains the scripts to perform POI recommendations. Order of execution:
    * step1_prepare_data.sh
    * step2_generate_recommenders.sh
  * Route: contains the scripts to perform route recommendations. Order of execution:
    * step1_prepare_routes_data.sh
    * step2_generate_route_recommenders.sh



 - **NOTE**: the data used in this repository can be found in the repository [Context-Trails-Data](https://github.com/pablosanchezp/ContextTrailsData/)



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
