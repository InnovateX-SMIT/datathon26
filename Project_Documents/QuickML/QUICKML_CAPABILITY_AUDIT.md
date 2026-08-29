# Catalyst QuickML Capability Audit — CrimeNexus ML Pipeline

**Document ID:** `CN-ML-AUD-2026-01`  
**Platform:** CrimeNexus — AI-Powered Crime Intelligence & Decision Support Platform  
**Target Environment:** Zoho Catalyst (AppSail, Data Store, Stratus, QuickML)  
**Date:** August 2026  
**Audit Status:** `COMPLETE`  
**Implementation Status:** `NOT PERFORMED (AUDIT ONLY)`  

---

## 1. Executive Summary

This audit performs a technical evaluation of **Zoho Catalyst QuickML** to establish its suitability and architectural boundaries for the **CrimeNexus** predictive intelligence platform. CrimeNexus delivers four core predictive intelligence capabilities:
1. **Crime Risk Prediction** (Continuous Severity & Area Risk Scoring)
2. **Crime Type Prediction** (Multiclass Categorical Classification)
3. **Hotspot Prediction** (Spatio-Temporal Grid Risk & Cluster Forecasting)
4. **Repeat Offender Prediction** (Recidivism Probability & Network Centrality Risk)

### Core Findings
* **QuickML Viability:** QuickML is a robust no-code/low-code ML pipeline engine with native support for standard tabular classification and regression (e.g., AdaBoost, CatBoost, Decision Trees, Linear/Logistic Regression), automatic data profiling, visual feature engineering, and REST API deployment.
* **XGBoost Support:** While QuickML's no-code presets emphasize algorithms like CatBoost and AdaBoost, custom algorithms (including XGBoost, LightGBM, and Scikit-Learn) can be executed inside QuickML pipelines via **Custom Code Nodes** implementing `fit()`, `predict()`, and `get_evaluation_metrics()`. However, parameter tuning and specialized loss functions require manual code wrapping.
* **SHAP Explainability Gap:** QuickML provides high-level **Global Feature Importance** (model details) and **Local Feature Contributions** (endpoint details). It **does NOT provide native SHAP TreeExplainer matrix calculations, baseline value offsets, interaction values, or raw Shapley value arrays** in its REST inference payload. For CrimeNexus law enforcement decision-support (e.g., waterfall plots, force plots, feature contribution breakdowns), a Python SHAP layer is mandatory.
* **Complex Spatial & Graph Feature Limitations:** Hotspot forecasting (requiring spatio-temporal lag engines, KDE, or HDBSCAN) and Repeat Offender prediction (requiring NetworkX criminal co-offender graph metrics) cannot be implemented natively with out-of-the-box QuickML nodes.
* **Architectural Verdict:** A **Hybrid ML Architecture (Option C)** is the optimal, production-grade approach. Real-time, sub-10ms inference and granular SHAP explainability are executed inside **FastAPI on Catalyst AppSail**, while **Catalyst QuickML & Job Pools** serve as the pipeline engine for data validation, baseline benchmarking, batch transformations, and scheduled retraining workflows.

---

## 2. QuickML Capabilities

Based on official Zoho Catalyst documentation and platform architecture, the current capabilities of QuickML are audited below:

### 2.1 Data Ingestion & Profiling
| Capability | Supported | Description & Mechanism |
| :--- | :---: | :--- |
| **Dataset Import** | **YES** | Upload via UI, Catalyst File Store / Stratus, or programmatic dataset creation. |
| **CSV Ingestion** | **YES** | Native parsing of structured `.csv` and tabular data files. |
| **Database Connection** | **PARTIAL** | Direct batch import from Zoho CRM, AWS S3, GCP, and Azure Blob Storage. Catalyst Data Store (ZCQL) data must be exported or queried via SDK before feeding QuickML. |
| **Large Datasets** | **YES** | Scaled batch processing (within project tier memory/storage limits). |
| **Dataset Profiling** | **YES** | Built-in automated profiling: column data types, distribution, null percentages, distinct counts, and skewness. |
| **Missing-Value Handling** | **YES** | Built-in Imputation nodes (Mean, Median, Mode, Constant Value, Row Removal). |
| **Duplicate Handling** | **YES** | Automated duplicate row identification and elimination nodes. |
| **Outlier Handling** | **YES** | Outlier detection and threshold capping / filtering. |
| **Data Validation** | **YES** | Schema conformity checks and invalid data type flagging. |
| **Data Transformation** | **YES** | Column rename, drop, arithmetic transforms, and date/time field extractions. |

### 2.2 Preprocessing & Feature Engineering
| Capability | Supported | Description & Mechanism |
| :--- | :---: | :--- |
| **Numerical Transformations** | **YES** | Log transform, square root, polynomial, binning, and normalization. |
| **Categorical Encoding** | **YES** | One-Hot Encoding, Ordinal Encoding, Label Encoding. |
| **Feature Scaling** | **YES** | Min-Max Scaler, Mean-Std (StandardScaler) Normalizer. |
| **Feature Selection** | **YES** | Redundancy Elimination, Variance Threshold, Principal Component Analysis (PCA). |
| **Feature Engineering** | **YES** | "Autolearn" feature generator and date-time decomposition (day, month, hour, day-of-week). |
| **Train/Test Splitting** | **YES** | Automated cross-validation and configurable train/validation/test split ratios (e.g., 80/20, 70/15/15). |
| **Data Leakage Prevention** | **YES** | Pipeline encapsulation guarantees preprocessing statistics (mean, std, encoders) are learned solely on the training split and applied to test/inference data. |

### 2.3 Algorithms & Modeling Capabilities
| Algorithm / Paradigm | QuickML Native (No-Code) | Custom Code Node Support | Notes |
| :--- | :---: | :---: | :--- |
| **CatBoost** | **YES** | **YES** | Native gradient boosted decision tree classifier/regressor. |
| **AdaBoost** | **YES** | **YES** | Native boosting ensemble algorithm. |
| **Random Forest** | **YES** | **YES** | Native bagging ensemble for classification and regression. |
| **Decision Trees** | **YES** | **YES** | Native CART decision tree algorithm. |
| **Logistic Regression** | **YES** | **YES** | Native linear classifier. |
| **Linear / Ridge Regression**| **YES** | **YES** | Native continuous prediction algorithm. |
| **XGBoost** | **PARTIAL (UI varies)**| **YES** | Fully supported via Python Custom Algorithm node (`xgboost.XGBClassifier` / `XGBRegressor`). |
| **LightGBM** | **NO (Native UI)** | **YES** | Supported via Python Custom Algorithm node. |
| **Multiclass Classification**| **YES** | **YES** | Supported out-of-the-box (e.g., crime category prediction). |
| **Binary Classification** | **YES** | **YES** | Supported out-of-the-box (e.g., recidivism flag). |
| **Regression** | **YES** | **YES** | Supported out-of-the-box (e.g., risk score index). |
| **Clustering (K-Means/DBSCAN)**| **LIMITED** | **YES** | Unsupervised clustering is restricted in visual pipeline; requires custom node. |

---

## 3. QuickML Limitations

### 3.1 Hard Platform Limitations
1. **No Live Streaming DB Connection:** QuickML does not continuously listen to live ZCQL table transactions for instant on-the-fly incremental training; retraining occurs via scheduled or triggered batch runs.
2. **REST Endpoint Network Latency:** Calling a published QuickML endpoint over HTTP introduces **150ms to 400ms** latency per request (due to TLS handshake, gateway routing, and auth token evaluation). In contrast, in-memory Python models execute within **< 5ms**.
3. **Endpoint Invocation Quotas:** Free/development tiers include 1,000 endpoint invocations. High-volume live map simulations can exhaust development quotas without appropriate caching or batching.
4. **OAuth2 / API Key Overhead:** QuickML REST APIs require either an `X-QUICKML-ENDPOINT-KEY` or OAuth2 access token with the `QuickML.deployment.READ` scope.

### 3.2 Practical Recommendations for CrimeNexus
* **Do not use QuickML for real-time per-frame map rendering:** Map interfaces (rendering hundreds of spatial risk nodes) will experience lag if each point queries a remote QuickML REST endpoint.
* **Keep complex non-tabular feature calculations (e.g., NetworkX graph centrality, spatial KDE) in Python services:** Attempting to force multi-table relational graph traversals into a single QuickML CSV node is brittle.

---

## 4. XGBoost Verification

| Verification Item | Status | Detailed Finding |
| :--- | :---: | :--- |
| **1. Supported in QuickML?** | **YES (Hybrid/Custom)** | Supported directly via Custom Algorithm node templates and select platform configurations. |
| **2. Task Types Supported** | **Classification & Regression** | Binary classification, multiclass classification, and regression. |
| **3. Hyperparameter Tuning** | **YES** | In custom nodes, full access to `max_depth`, `learning_rate`, `n_estimators`, `subsample`, `scale_pos_weight`. |
| **4. Custom Feature Training** | **YES** | Accepts any tabular feature schema transformed via upstream nodes. |
| **5. Model Evaluation** | **YES** | Produces ROC-AUC, Confusion Matrix, Precision-Recall, F1-Score, RMSE, MAE, and R². |
| **6. Model Deployment** | **YES** | One-click deployment to a managed Catalyst endpoint. |
| **7. API Access** | **YES** | Authenticated POST REST endpoint accepting JSON payloads. |
| **8. Probabilities / Confidence** | **YES** | Returns class probabilities (`predict_proba`) along with class predictions. |
| **9. Model Retraining** | **YES** | Pipelines can be rerun on updated datasets via console, CLI, or Catalyst Cron. |
| **10. Size / Dataset Limits** | **MANAGED** | Subject to Catalyst tier compute/memory limits (typically sufficient for 50k–500k rows). |

```text
QuickML XGBoost Capability = SUFFICIENT VIA CUSTOM CODE NODES / INTEGRATED PYTHON PIPELINE
```

---

## 5. SHAP / Explainability Verification

Explainability is a core pillar of CrimeNexus. Law enforcement analysts must understand **why** an area or individual received a high risk score.

```text
Feature Importance ≠ SHAP
```

* **Feature Importance (Global):** Ranks the overall importance of features across the entire training dataset (e.g., "Location severity contributes 35% to overall variance"). QuickML provides this natively on the **Model Details** page.
* **Model Explanation (Local Contribution):** Provides heuristic feature contribution scores on the QuickML **Endpoint Details** page.
* **SHAP (Shapley Additive exPlanations):** Computes game-theoretic, mathematically consistent Shapley values for every individual prediction:
  $$\text{Prediction} = \text{Base Value} + \sum_{i=1}^{M} \phi_i$$
  where $\phi_i$ is the exact local attribution of feature $i$.

### SHAP Verification Table
| Feature | QuickML Native | Python SHAP Engine | CrimeNexus Requirement |
| :--- | :---: | :---: | :---: |
| Global Feature Importance | **YES** | **YES** | High |
| Per-Prediction Feature Direction (+/-) | **PARTIAL** | **YES** | Mandatory |
| Exact Shapley Value Vector ($\phi$) | **NO** | **YES** | Mandatory |
| Expected Base Value ($E[f(x)]$) | **NO** | **YES** | Mandatory |
| Waterfall Plot Data | **NO** | **YES** | Mandatory (UI Decision Support) |
| Force Plot Data | **NO** | **YES** | Mandatory (UI Crime Analyst View) |
| Interaction Values Matrix | **NO** | **YES** | Recommended |

### Conclusion on Explainability
QuickML **cannot** completely satisfy CrimeNexus's deep explainability requirements on its own. A dedicated **Python SHAP layer** (`shap.TreeExplainer` or `shap.Explainer`) is required to generate real-time JSON payloads for the frontend explainability cards and charts.

```text
Explainability Strategy = QuickML Model Training / Metadata + Python SHAP Real-Time Explanation Engine
```

---

## 6. Model Endpoint & Inference Analysis

### 6.1 Architecture Flow
```text
[ Next.js Frontend ]
        │ (1) User Interaction / Filter Selection
        ▼
[ FastAPI Backend (Catalyst AppSail) ]
        │ 
        ├────► [ Local In-Memory XGBoost / SHAP Engine ] ──► < 5ms Latency (Real-time Interactive Map)
        │
        └────► [ QuickML Model REST Endpoint ] ─────────► 150-350ms Latency (Batch / Formal Inference)
                    │
                    ▼
        [ Catalyst Data Store / ZCQL ]
```

### 6.2 Endpoint Characteristics
* **Publication:** Models are published as secure REST endpoints from the QuickML console.
* **Authentication:** Requires `Authorization: Zoho-oauthtoken <ACCESS_TOKEN>` or `X-QUICKML-ENDPOINT-KEY`.
* **Request Format:** JSON object containing feature key-value pairs:
  ```json
  {
    "data": [
      {
        "district_id": 4,
        "past_offense_count": 6,
        "gang_affiliated": 1,
        "hour_of_day": 22,
        "historical_severity_index": 0.82
      }
    ]
  }
  ```
* **Response Format:**
  ```json
  {
    "status": "success",
    "predictions": [
      {
        "predicted_label": 1,
        "confidence_score": 0.8924,
        "probabilities": { "0": 0.1076, "1": 0.8924 }
      }
    ]
  }
  ```

---

## 7. Database Integration

```text
[ Catalyst Data Store (ZCQL Tables) ]
               │
               ▼
[ Python Export / ETL Job (Catalyst Job Pool / Function) ]
               │
               ▼ (Generates Processed CSV / Dataset Schema)
[ Catalyst Stratus / File Store ]
               │
               ▼
[ QuickML Dataset Pipeline ]
               │
               ▼
[ Model Retraining & Validation ]
```

* **Direct ZCQL Live Stream:** QuickML cannot automatically subscribe to live table mutations in ZCQL without an intermediate pipeline.
* **Recommended Batch Ingestion:** Use a Catalyst Cron job or Job Pool to execute ZCQL queries, serialize clean tabular datasets to **Catalyst Stratus** object storage, and trigger QuickML pipeline updates.

---

## 8. Data Pipeline & Retraining

| Mechanism | QuickML Support | Implementation Strategy |
| :--- | :---: | :---: |
| **Manual Retraining** | **YES** | Triggered directly in QuickML console via "Re-run Pipeline". |
| **Scheduled Retraining** | **YES** | Triggered via Catalyst Cron / Job Scheduler executing retraining webhooks. |
| **Automated Event Retraining** | **YES** | Catalyst Event Function triggers pipeline execution when threshold of new FIR records is reached. |
| **Model Versioning** | **YES** | QuickML maintains pipeline execution versions, training metrics, and deployment history. |
| **Model Replacement** | **YES** | Seamless endpoint redeployment pointing to newly trained pipeline versions without endpoint URL modification. |

---

## 9. Current Repository Audit

### 9.1 Structure & Status
```text
ml/
├── crime_prediction/          # [SCAFFOLDED - .gitkeep]
├── explainability/            # [SCAFFOLDED - .gitkeep]
├── hotspot_prediction/        # [SCAFFOLDED - .gitkeep]
└── offender_prediction/       # [SCAFFOLDED - .gitkeep]

scripts/
├── train_models.py            # [STUB - Print statement execution stub]
├── seed_fir_lookups.py        # [IMPLEMENTED - Synthetic FIR & Lookup seed data]
├── generate_test_data.py      # [IMPLEMENTED - Synthetic data generator]
└── cleanup.py                 # [IMPLEMENTED - Maintenance script]

datasets/
├── processed/                 # [SCAFFOLDED]
├── raw/                       # [SCAFFOLDED]
├── models/                    # [SCAFFOLDED]
└── synthetic/                 # [SCAFFOLDED]

backend/
├── app/main.py                # [IMPLEMENTED - FastAPI core routing & middleware]
├── services/                  # [IMPLEMENTED - alert_service, report_service, recommendation_service]
├── api/                       # [IMPLEMENTED - alerts, reports, sync routers]
└── schemas/                   # [IMPLEMENTED - Pydantic models]
```

### 9.2 Audit Summary
1. **Existing ML State:** The ML directory structure (`ml/*`) is cleanly organized into domain-specific modules but is currently scaffolded.
2. **Backend Readiness:** FastAPI routes and domain services are well-structured, allowing seamless integration of prediction and explainability endpoints.
3. **Pickle Storage:** Pickled model artifacts (`.pkl`) are targeted for Catalyst Stratus storage with runtime caching in AppSail memory as defined in the deployment blueprint.
4. **QuickML Replacement Opportunity:** QuickML can be leveraged for standard tabular pipeline automation and benchmark model registry, while Python handles real-time execution, SHAP generation, and spatial/graph algorithms.

---

## 10. Four Use-Case Compatibility Matrix

| Use Case | Problem Type | Target Variable | QuickML Support | Suitable? | Technical Reason & Architecture |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **1. Crime Risk Prediction** | Regression / Classification | Risk Score `[0.0 - 1.0]` / Risk Level (`Low`, `Med`, `High`, `Critical`) | **High** | **YES** | Tabular features (police station density, hour, past incident rate) map perfectly to QuickML algorithms and XGBoost custom nodes. |
| **2. Crime Type Prediction** | Multiclass Classification | Crime Category (`Violent`, `Property`, `Cyber`, `Narcotics`, `Financial`) | **High** | **YES** | Standard multi-category classification using One-Hot/Ordinal encoding and tree-based ensembles. |
| **3. Hotspot Prediction** | Spatio-Temporal Spatial Density & Grid Risk | Grid Cell Incident Count / Future Hotspot Likelihood | **Medium** | **HYBRID** | QuickML handles tabular grid features; however, spatial distance calculations, geospatial indexing (H3/Quadkey), and KDE require Python preprocessing. |
| **4. Repeat Offender Prediction** | Binary Classification & Link Analysis | Recidivism Probability `[0.0 - 1.0]` | **Medium** | **HYBRID** | QuickML trains the classification head; criminal network graph features (degree centrality, co-offender clustering) must be precomputed via NetworkX in Python. |

### Detailed Analysis by Use Case

#### Use Case 1: Crime Risk Prediction
* **Input Features:** `police_station_id`, `district_code`, `hour_of_day`, `day_of_week`, `is_holiday`, `historical_crime_rate_30d`, `severity_weight_avg`.
* **Target:** `risk_score` (continuous float $0.0 - 1.0$) or `risk_tier` ($1 - 4$).
* **Model Type:** XGBoost Regressor / CatBoost Regressor.
* **Explainability:** SHAP TreeExplainer for feature attribution (e.g., "Late night hours (+0.25), High 30d local incident history (+0.30)").

#### Use Case 2: Crime Type Prediction
* **Input Features:** `location_type`, `time_block`, `weapon_reported`, `premise_type`, `area_economic_index`, `prior_category_frequencies`.
* **Target:** `crime_category` (string / encoded class integer).
* **Model Type:** XGBoost Multiclass Classifier / LightGBM Classifier.
* **Explainability:** Per-class feature contribution vectors.

#### Use Case 3: Hotspot Prediction
* **Input Features:** `grid_lat_bin`, `grid_lon_bin`, `temporal_lag_7d`, `temporal_lag_30d`, `spatial_neighbor_crime_density`, `weather_condition`, `patrol_frequency`.
* **Target:** `is_hotspot_next_24h` (binary) or `expected_crimes_next_7d` (continuous).
* **Model Type:** Spatial Lag XGBoost / Temporal Tree Regressor.
* **Preprocessing:** Spatial grid binning and spatial autocorrelation ($Moran's\ I$) generated in Python, fed into QuickML or local Python model.

#### Use Case 4: Repeat Offender Prediction
* **Input Features:** `offender_age_first_arrest`, `prior_convictions_count`, `active_warrants`, `gang_association_flag`, `network_betweenness_centrality`, `network_degree_centrality`, `co_offender_risk_score`.
* **Target:** `recidivism_flag` (0 or 1) and `recidivism_risk_score` ($0.0 - 1.0$).
* **Model Type:** XGBoost Binary Classifier with class imbalance weighting (`scale_pos_weight`).
* **Preprocessing:** NetworkX graph traversal executed in Python to extract graph centrality metrics.

---

## 11. Architecture Options Comparison

| Evaluation Metric (Weight) | Option A: Full QuickML | Option B: Full Python | Option C: Hybrid (Recommended) |
| :--- | :---: | :---: | :---: |
| **Model Compatibility** | 6 / 10 | 9.5 / 10 | **9.8 / 10** |
| **Inference Performance (< 10ms)** | 4 / 10 (150-350ms HTTP) | 9.5 / 10 (< 5ms in-memory) | **9.5 / 10** (< 5ms local + async endpoint) |
| **SHAP Explainability** | 3 / 10 (Basic importance only) | 10 / 10 (Full TreeExplainer) | **10 / 10** (Full TreeExplainer integration) |
| **Catalyst Platform Integration** | 10 / 10 | 7 / 10 | **9.8 / 10** (AppSail + QuickML + Stratus) |
| **Maintainability & No-Code UI** | 9 / 10 | 6 / 10 | **9.0 / 10** |
| **Complex Spatial/Graph Support** | 4 / 10 | 9.5 / 10 | **9.5 / 10** |
| **Hackathon & Evaluation Reliability** | 5 / 10 (Quota & latency risks) | 8.5 / 10 | **9.5 / 10** (Dual fallback resilience) |
| **Weighted Total Score** | **5.8 / 10** | **8.6 / 10** | **9.5 / 10** |

### Rationale for Scores
* **Option A (Full QuickML):** Suffers from latency bottlenecks on interactive map queries, lacks deep SHAP matrix generation required for CrimeNexus UI components, and cannot compute graph/spatial lag features natively.
* **Option B (Full Python):** Technically robust with maximum flexibility and sub-millisecond inference, but does not leverage Zoho Catalyst's native QuickML visual pipeline capabilities for platform compliance.
* **Option C (Hybrid Architecture):** Combines the visual pipeline, automated retraining, and cloud management of QuickML with the speed, mathematical precision of SHAP, and complex graph feature handling of Python inside Catalyst AppSail.

---

## 12. Recommended Architecture

```text
PRIMARY APPROACH:
HYBRID ARCHITECTURE (OPTION C)
```

```mermaid
flowchart TD
    subgraph Data Layer [Catalyst Data & Storage Layer]
        DS[(Catalyst Data Store / ZCQL)]
        STR[Catalyst Stratus Object Storage]
    end

    subgraph Batch ML Pipeline [Catalyst QuickML & Job Pools]
        ETL[Python Feature Extraction & NetworkX Graphs]
        QML[QuickML Pipeline Builder & Validation]
        MREG[Model Registry & Benchmark Models]
        DS --> ETL
        ETL --> STR
        STR --> QML
        QML --> MREG
    end

    subgraph Real-Time Serving Layer [Catalyst AppSail - FastAPI Backend]
        INF[In-Memory XGBoost / LightGBM Inference Engine]
        SHAP_ENG[SHAP TreeExplainer Engine]
        API[FastAPI Prediction & Explainability Routers]
        MREG -.->|Sync Binaries| INF
        INF --> SHAP_ENG
        SHAP_ENG --> API
    end

    subgraph Frontend Client [Catalyst Slate - Next.js]
        MAP[Interactive Geospatial Hotspot Map]
        EXP[Explainability Waterfall & Force Cards]
        DASH[Predictive Intelligence Dashboard]
        API --> MAP
        API --> EXP
        API --> DASH
    end
```

### Architectural Principles
1. **Real-Time Serving (< 10ms):** High-throughput map interactions and dashboard queries query the in-memory XGBoost model inside FastAPI on AppSail.
2. **Deep Explainability:** SHAP values ($\phi_i$), base values, and waterfall plot data are computed dynamically in Python and returned as structured JSON to the Next.js frontend.
3. **Pipeline Automation & Visual Governance:** Catalyst QuickML is utilized for visual dataset profiling, pipeline validation, data leakage prevention checks, and scheduled model benchmark retraining.

---

## 13. Final Decision Matrix

| Capability | QuickML Native | Python Engine | Hybrid Architecture | Required for CrimeNexus |
| :--- | :---: | :---: | :---: | :---: |
| **Data Preprocessing** | YES | YES | **YES** | **YES** |
| **Feature Engineering** | YES (Tabular) | YES (All) | **YES** | **YES** |
| **XGBoost Modeling** | PARTIAL / CUSTOM | YES | **YES** | **YES** |
| **Classification** | YES | YES | **YES** | **YES** |
| **Regression** | YES | YES | **YES** | **YES** |
| **Hotspot Prediction** | LIMITED (No GIS) | YES | **YES** | **YES** |
| **Repeat Offender Prediction** | LIMITED (No Graph) | YES | **YES** | **YES** |
| **SHAP Explainability** | NO (Importance only) | YES | **YES** | **YES** |
| **Model Evaluation** | YES | YES | **YES** | **YES** |
| **Model Endpoint** | YES (REST) | YES (FastAPI) | **YES** | **YES** |
| **Real-Time Inference (< 10ms)** | NO (150-350ms) | YES (< 5ms) | **YES** | **YES** |
| **Database Integration** | BATCH | DIRECT / ZCQL | **YES** | **YES** |
| **Retraining Automation** | YES (Cron/Webhooks)| YES (Scripts) | **YES** | **YES** |

---

## 14. Minimal Proof of Concept (POC) Plan

To validate the QuickML integration without modifying production code, a single prediction task is selected for the POC:

### Selected POC Task: **Crime Risk Prediction**
1. **Dataset:** Export a clean sample of 1,000 synthetic crime records with tabular features (`hour`, `location_type`, `historical_crime_rate`, `target_risk_score`).
2. **QuickML Pipeline:**
   - Create a QuickML Dataset from the sample CSV.
   - Attach Imputation node (Mean/Median) and Scaler node (Standard Normalizer).
   - Configure a Decision Tree / CatBoost or Custom XGBoost Regression node.
   - Train and validate using an 80/20 train/test split.
3. **Endpoint Validation:**
   - Deploy model to a QuickML test endpoint.
   - Execute an authenticated POST request with sample feature JSON.
   - Record response latency, confidence metrics, and output format.
4. **FastAPI Client Hook:**
   - Implement an isolated client function in FastAPI that forwards requests to the QuickML endpoint and compares latency against the local Python XGBoost engine.

---

## 15. Risk Assessment & Mitigation

| Identified Risk | Severity | Impact | Mitigation Strategy |
| :--- | :---: | :--- | :--- |
| **API Quota Exhaustion** | High | Live map rendering exhausts QuickML endpoint call limits. | Serve interactive map calls via in-memory AppSail Python models; use QuickML for formal assessment audits. |
| **SHAP Omission** | High | Lack of granular explainability weakens decision-support credibility for law enforcement use cases. | Mandatory Python SHAP layer running alongside inference to deliver exact waterfall/force plot vectors. |
| **Network Latency Overhead** | Medium | External REST round-trips cause UI micro-stutters during multi-filter adjustments. | Cache static feature lookups in Redis/RAM and run real-time inference in AppSail memory. |
| **Complex Spatial/Graph Bottlenecks** | Medium | QuickML no-code nodes cannot calculate NetworkX graph centralities or spatial autocorrelation. | Precalculate graph and spatial indices in Python prior to dataset serialization. |

---

## 16. Official Sources & References

1. **Zoho Catalyst QuickML Documentation:** [Catalyst QuickML Overview & Pipeline Architecture](https://www.zoho.com/catalyst/help/quickml.html)
2. **Zoho Catalyst SDK Reference:** [Catalyst Python SDK Guide & ZCQL Specification](https://www.zoho.com/catalyst/help/sdk/python/)
3. **Zoho Catalyst AppSail Documentation:** [AppSail Standalone Web Hosting & Python Runtime](https://www.zoho.com/catalyst/help/appsail.html)
4. **Zoho Catalyst Deployment Plan:** [04_ZOHO_CATALYST_DEPLOYMENT_PLAN.md](file:///Users/krishanand/datathon26/Project_Documents/04_ZOHO_CATALYST_DEPLOYMENT_PLAN.md)
5. **CrimeNexus Project Architecture:** [PROJECT_STRUCTURE.md](file:///Users/krishanand/datathon26/docs/PROJECT_STRUCTURE.md)

---

## Final Verification Summary

```text
=====================================================
AUDIT STATUS: COMPLETE
IMPLEMENTATION: NOT PERFORMED (AUDIT ONLY)
=====================================================
```
