# 11. Glossary and Terms

This document provides a beginner-friendly reference for domain jargon, machine learning concepts, and repository-specific terminology used in the Predictive Guardians platform.

---

## 1. Domain & Crime Analytics Jargon

* **FIR (First Information Report)**: A formal document prepared by police agencies in India when they receive information about the commission of a cognizable offense. It is the initial registration document that starts the criminal investigation.
* **Beat (Police Beat)**: The smallest geographical area assigned to specific police officers for foot or vehicle patrol. Beats segment a city or district to ensure comprehensive coverage and response.
* **Village Area Name**: A sub-district census area or neighborhood used as a geographical division within police beat boundaries.
* **Police Unit**: A local police station (e.g. *Amengad PS*) responsible for enforcing public safety within its assigned territory.
* **Sanctioned Strength**: The official headcount of police officers approved by administrative authorities for a specific rank or district.
* **ASI (Assistant Sub-Inspector)**: A non-commissioned officer rank in the Indian Police forces. Typically responsible for investigating minor crimes and managing sub-units.
* **CHC (Head Constable)**: A senior constable rank responsible for supervising constables and supporting beat operations.
* **CPC (Police Constable)**: The foundational police rank responsible for active patrols, guard duties, and primary field response.
* **MOB (Modus Operandi Bureau)**: A specialized police database and analysis unit that catalogs the specific methods (modus operandi) used by criminals.
* **Rowdy Sheeter**: A term used in Indian law enforcement to describe individuals who are listed on a police station's "rowdy sheet" due to habitual involvement in local violence, extortion, or public nuisance.

---

## 2. Machine Learning Terminology

* **AutoML (Automated Machine Learning)**: The process of automating the end-to-end steps of training machine learning models, including feature engineering, model selection, hyperparameter tuning, and ensemble building.
* **Stacked Ensemble**: A meta-learning model that combines predictions from multiple base models (e.g. Gradient Boosting, Deep Learning, Random Forest) to output a single prediction class or value, maximizing performance.
* **MOJO (Model Object, Optimized)**: A lightweight, Java-based runtime format developed by H2O.ai. MOJO files packages model parameters into bytecode that can run in any Java-enabled system without requiring a full H2O cluster.
* **DBSCAN (Density-Based Spatial Clustering of Applications with Noise)**: An unsupervised clustering algorithm that groups coordinate points that are close to each other based on distance parameters, while marking isolated points in low-density regions as noise.
* **Frequency Encoding (Count Encoding)**: A preprocessing technique that maps categorical string values to numerical frequencies or occurrence ratios in the dataset:
  $$\text{Encoded Value} = \frac{\text{Count of Category}}{\text{Total Rows}}$$
* **StandardScaler**: A normalization method that standardizes features by removing the mean and scaling to unit variance:
  $$z = \frac{x - \mu}{\sigma}$$
* **Class Imbalance**: A dataset characteristic where one target class has significantly more samples than the other class. If not addressed (e.g. using sampling), models will favor the majority class.
* **RandomOverSampler / RandomUnderSampler**: Techniques used to address class imbalance:
  * **Over-sampling**: Replicates minority class samples.
  * **Under-sampling**: Discards majority class samples.

---

## 3. System & Architecture Terminology

* **Streamlit**: An open-source Python web framework used to build interactive data applications and dashboards quickly.
* **Folium**: A Python wrapper library used to render Leaflet.js interactive maps in web applications.
* **PuLP**: A linear programming library in Python that allows developers to model optimization problems using decision variables, objective functions, and constraints.
* **MIME (Multipurpose Internet Mail Extensions)**: A standard format for email messages that allows for sending attachments, HTML formatting, and multiple message body parts.
* **StartTLS**: A protocol command that tells an email server that the client wants to upgrade an existing insecure SMTP connection to a secure encrypted TLS connection.
* **Devcontainer**: A container configuration specification that allows developers to launch a pre-configured development environment in VSCode or GitHub Codespaces.
* **Flat-file Database**: A database model that stores all data in a single table or file (like a CSV or text file), without using relational schemas or a database server.
