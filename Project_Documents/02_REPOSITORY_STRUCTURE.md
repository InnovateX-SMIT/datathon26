# 02. Repository Structure

This document outlines the organization of the Predictive Guardians repository, detailing the purpose of each directory, key entry points, and component mapping.

---

## Directory Tree

The workspace is structured as follows:

```text
Predictive_Guardians-main/
│   .gitignore
│   dockerfile
│   packages.txt
│   Readme.md
│   requirements.txt
│   tree.txt
│   
├───.devcontainer
│       devcontainer.json
│       
├───app
│       app.py
│       Continuous_Learning_and_Feedback.py
│       Crime_Pattern_Analysis.py
│       Criminal_Profiling.py
│       Predictive_modeling.py
│       Resource_Allocation.py
│       __init__.py
│       
├───assets/
│       (Contains PNG and JPG screenshots of application components and maps)
│       
├───Component_datasets
│       Crime_Pattern_Analysis_Cleaned.csv
│       Crime_Type_cleaned_data.csv
│       Criminal_Profiling_cleaned.csv
│       Feedback.csv
│       Recidivism_cleaned_data.csv
│       Resource_Allocation_Cleaned.csv
│       
├───Continuous_learning_and_feedback
│       alert.py
│       feedback.py
│       __init__.py
│       
├───Crime_Pattern_Analysis
│       clean_data.py
│       ingest_data.py
│       __init__.py
│       
├───Criminal_Profiling
│       clean_data.py
│       ingest_data.py
│       
├───models
│   └───Recidivism_model
│           frequency_encoding.json
│           h2o-genmodel.jar
│           scaler.pkl
│           StackedEnsemble_BestOfFamily_2_AutoML_1_20240719_183320.zip
│           
├───pipelines
│       training_pipeline.py
│       
├───Predictive_Modeling
│   └───Recidivism_Prediction
│           clean_data.py
│           ingest_data.py
│           train_model.py
│           transform_data.py
│               
└───Resource_Allocation
        clean_data.py
        ingest_data.py
```

---

## Folder Explanations

### 1. `app/`
Contains the frontend logic of the application. Built entirely on Streamlit.
* **`app.py`**: The primary entry point of the interactive dashboard. Organizes sidebar navigation, handles global cache, and renders the home page.
* **`Continuous_Learning_and_Feedback.py`**: Renders forms for user feedback, visualizes the feedback alert progress bars, allows manual updates of sanctioned personnel counts, and manages the stakeholder invitation form.
* **`Crime_Pattern_Analysis.py`**: Renders temporal trend charts, folium heatmaps, and choropleth maps. Implements the DBSCAN clustering logic for displaying hotspots.
* **`Criminal_Profiling.py`**: Draws socio-demographic graphs (age, sex, caste, occupation) using Plotly and outputs crime groups and sub-category analyses.
* **`Predictive_modeling.py`**: Builds the interactive repeat offense prediction form. Loads the H2O MOJO zip model, standardization scaler, and frequency encoding JSON to make predictions.
* **`Resource_Allocation.py`**: Contains the Streamlit layout for selecting districts, configuring sanctioned strengths, and displaying the results of the linear programming solver.

### 2. `Component_datasets/`
Holds pre-processed, cleaned datasets in CSV format. These files are loaded directly by the Streamlit application layer to ensure fast dashboard rendering.
* **`Crime_Pattern_Analysis_Cleaned.csv`**: Crime incident log containing coordinates, victim counts, and accused counts.
* **`Crime_Type_cleaned_data.csv`**: Cleaned data detailing crime groups and incident date limits.
* **`Criminal_Profiling_cleaned.csv`**: Offender demographic details, including age, occupation, caste, and crime category.
* **`Feedback.csv`**: Persistent log where user feedback entries, ratings, and comments are stored.
* **`Recidivism_cleaned_data.csv`**: Offender profiles mapped to binary classification labels indicating repeat offenses.
* **`Resource_Allocation_Cleaned.csv`**: Detailed record of beats, police units, crime counts, and normalized severity coefficients per beat.

### 3. `models/`
Stores serialization binaries, configuration schemas, and trained machine learning artifacts.
* **`Recidivism_model/`**: Contains the `frequency_encoding.json` lookup dictionary, the `scaler.pkl` standardization object, the H2O MOJO zip archive containing the `StackedEnsemble` predictor, and `h2o-genmodel.jar` (required for running the Java-backed H2O engine).

### 4. `pipelines/`
Houses the continuous training pipeline.
* **`training_pipeline.py`**: A master execution script designed to orchestrate data ingestion, cleaning, and model training. *(Note: Contains missing import paths and argument list mismatches, rendering it broken out-of-the-box)*.

### 5. `Crime_Pattern_Analysis/`, `Criminal_Profiling/`, `Predictive_Modeling/`, and `Resource_Allocation/`
These folders correspond to the discrete ETL (Extract, Transform, Load) pipelines for each module.
* **`ingest_data.py`**: Imports raw files from the parent data folder (`../datasets/`) and selects relevant features.
* **`clean_data.py`**: Cleans raw datasets, maps district names to match standard formats, handles outliers, and writes the output files back into `Component_datasets/`.
* **`Predictive_Modeling/Recidivism_Prediction/transform_data.py`**: Implements frequency encoding and trains standard scalers.
* **`Predictive_Modeling/Recidivism_Prediction/train_model.py`**: Sets up H2O, splits the dataset, trains AutoML models, evaluates metrics, and downloads the best model as a MOJO file.

### 6. `Continuous_learning_and_feedback/`
Houses background services.
* **`alert.py`**: Sends automated emails to the development team when rating metrics cross thresholds.
* **`feedback.py`**: Triggers automated email invitations (with CSV attachments) to stakeholders.

---

## Entry Points

* **Dashboard Web Interface**: Renders the Streamlit frontend.
  * *Path*: `app/app.py`
  * *Execution Command*: `streamlit run app/app.py`
* **ETL Training Pipeline**: Orchestrates ETL processes.
  * *Path*: `pipelines/training_pipeline.py`
  * *Execution Command*: `python pipelines/training_pipeline.py` (Must execute from root directory; currently contains compilation errors due to missing files and signature mismatches).

---

## Component Mapping

| Functional Module | ETL Logic | UI Logic | Datasets Used | Model/Output Artifacts |
| :--- | :--- | :--- | :--- | :--- |
| **Crime Pattern Analysis** | `Crime_Pattern_Analysis/` | `app/Crime_Pattern_Analysis.py` | `Crime_Pattern_Analysis_Cleaned.csv` | Distict-level geojson, DBSCAN cluster models |
| **Criminal Profiling** | `Criminal_Profiling/` | `app/Criminal_Profiling.py` | `Criminal_Profiling_cleaned.csv` | Plotly charts |
| **Predictive Modeling** | `Predictive_Modeling/` | `app/Predictive_modeling.py` | `Recidivism_cleaned_data.csv`, `Crime_Type_cleaned_data.csv` | `Recidivism_model/` (MOJO ensemble, scaler, json map) |
| **Resource Allocation** | `Resource_Allocation/` | `app/Resource_Allocation.py` | `Resource_Allocation_Cleaned.csv` | PuLP integer variables, allocation tables |
| **Continuous Learning** | `Continuous_learning_and_feedback/` | `app/Continuous_Learning_and_Feedback.py` | `Feedback.csv` | System status email alerts, session invites |
