# 05. Feature Analysis

This document details the functional features of the Predictive Guardians dashboard, including their purpose, user input requirements, processing algorithms, and visual outputs.

---

## 1. Crime Pattern Analysis

### A. Temporal Trend Analysis
* **Purpose**: Helps users identify seasonal fluctuations and trends over years, months, and days.
* **Inputs**:
  * District selection (multi-select list, default empty/all).
  * Crime category selection (multi-select list, default empty/all).
  * Time granularity radio buttons (`'Year'`, `'Month'`, `'Day'`).
* **Outputs**: An interactive Plotly bar chart displaying crime counts categorized by time step, grouped by district, and containing crime sub-category tooltips.
* **User Interaction**: Users filter the data using the dropdown controls. Hovering over the bar charts reveals specific crime classifications.
* **Internal Workflow**:
  1. Filter `Crime_Pattern_Analysis_Cleaned.csv` based on district and crime type.
  2. Perform a pandas `groupby` operation on the selected temporal column (`'Year'`, `'Month'`, or `'Day'`) and count the occurrences.
  3. Render the Plotly bar chart.
* **Asset Mapping**:
  * Main Interface: ![Temporal Analysis](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/temporal_analysis.PNG)

### B. Choropleth Map (District-level Drilldown)
* **Purpose**: Provides a high-level view of crime distributions across districts in Karnataka state.
* **Inputs**:
  * Metric Selector (dropdown: `'Crime Incidents'`, `'Total Victim Count'`, or `'Total Accused Count'`).
* **Outputs**: A Mapbox-backed district map colored according to crime volume, with a color scale indicating severity.
* **User Interaction**: Hovering over a district reveals its name and the exact count for the selected metric.
* **Internal Workflow**:
  1. Read geojson boundaries for Karnataka.
  2. Run a pandas aggregation on `Crime_Pattern_Analysis_Cleaned.csv` to compute totals for `FIRNo`, `VICTIM COUNT`, and `Accused Count` by `District_Name`.
  3. Render the choropleth map using `plotly.express.choropleth_mapbox`.
* **Asset Mapping**:
  * Main Interface: ![Choropleth Map](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/choropleth_map.PNG)

### C. Crime Hotspots Detection (Density-based Clustering)
* **Purpose**: Identifies high-density crime coordinates and displays them as heatmap clusters.
* **Inputs**:
  * Date range selection (radio selector: `'All'` or `'Custom Date Range'`).
  * Crime types selection (multi-select dropdown).
* **Outputs**: An interactive Folium map containing a density heatmap (blue to red gradients) and red markers pointing to DBSCAN cluster centers.
* **User Interaction**: Users click "Apply" to run the clustering engine and render the map. Zooming in reveals individual coordinates. Clicking on markers shows cluster labels and crime counts.
* **Internal Workflow**:
  1. Filter records based on selected date ranges and crime types.
  2. Compute coordinates groups to count crime frequencies per location.
  3. Run DBSCAN clustering on coordinates:
     $$\text{DBSCAN}(\text{eps}=0.1, \text{min\_samples}=5)$$
  4. Isolate cluster center coordinates (excluding noise index `-1`) and sum the total crime events in each cluster.
  5. Add `folium.plugins.HeatMap` layer and place `folium.Marker` objects at cluster centers.
* **Asset Mapping**:
  * Hotspot Map: ![Hotspots Map](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/crime_hotspot_map.PNG)

---

## 2. Criminal Profiling

### A. Socio-Demographic Profile Dashboards
* **Purpose**: Analyzes the background profiles of accused offenders to support social rehabilitation and targeted intervention programs.
* **Inputs**: Static selection (reads the cleaned profiling dataset).
* **Outputs**: Four Plotly charts:
  1. **Age Distribution**: Histogram showing the age distribution of offenders.
  2. **Gender Analysis**: Pie chart displaying male/female ratios.
  3. **Caste Analysis**: Vertical bar chart showing the top 10 castes of offenders (excluding "unknown").
  4. **Occupation Analysis**: Horizontal bar chart showing the top 10 offender professions (excluding "unknown" and "Others PI Specify").
* **User Interaction**: Users hover over charts to inspect percentages and values.
* **Internal Workflow**:
  1. Load `Criminal_Profiling_cleaned.csv`.
  2. Compute value distributions for the demographic columns.
  3. Render charts using Plotly.
* **Asset Mapping**:
  * Age Chart: ![Age](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/age.PNG)
  * Caste Chart: ![Caste](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/caste.PNG)
  * Gender Chart: ![Gender](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/gender.PNG)
  * Occupation Chart: ![Occupation](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/occupation.PNG)

### B. Offense Category Analysis
* **Purpose**: Identifies the most common types of crimes and sub-crimes.
* **Inputs**: Tab selection: `'Category'` or `'Sub-Category'`.
* **Outputs**: Bar charts showing the top 5 most frequent crime categories and sub-categories.
* **User Interaction**: Users switch between tabs to toggle views.
* **Internal Workflow**:
  1. Query the counts of `Crime_Group1` (Category) and `Crime_Head2` (Sub-Category) columns.
  2. Slice the top 5 values and render the bar charts.
* **Asset Mapping**:
  * Category View: ![Crime Category](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/crime_Category.PNG)
  * Sub-Category View: ![Crime Sub-Category](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/crime_sub_category.PNG)

---

## 3. Predictive Modeling (Repeat Offense Prediction)

* **Purpose**: Estimates the likelihood of a previously accused individual committing a crime again.
* **Inputs**:
  * Age (numeric input, range 7-100).
  * Caste (dropdown list).
  * Profession (dropdown list).
  * Crime District (dropdown list).
  * Criminal Present City (dropdown list).
* **Outputs**: A banner showing either a blue success message (*"The person is not likely to repeat the crime."*) or a red warning message (*"The person is likely to repeat the crime."*).
* **User Interaction**: Users enter suspect parameters and click the "Predict" button.
* **Internal Workflow**:
  1. Initialize H2O JVM.
  2. Load H2O Stacked Ensemble MOJO model zip and scikit-learn standardizer pickle.
  3. Load `frequency_encoding.json` to map categorical strings (caste, profession, district, city) to their frequency ratios.
  4. Standardize the features using the scaler.
  5. Load features into an `H2OFrame` and run prediction:
     $$\text{Prediction} = \text{Model.predict}(\text{Scaled Input})$$
  6. Display warning or success banner.
* **Asset Mapping**:
  * Prediction Form: ![Recidivism Form](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/repeat_offense_prediction.PNG)

---

## 4. Police Resource Allocation

* **Purpose**: Allocates sanctioned police personnel to beats based on crime severity.
* **Inputs**:
  * District selection (dropdown list).
  * Sanctioned ASI, CHC, and CPC strengths (numeric inputs, restricted to $\pm 10\%$ of default values for safety).
  * Police Unit selection (multi-select list).
* **Outputs**: An optimized allocation table showing village areas, beats, crime severity, and calculated officer counts for each rank.
* **User Interaction**: Users select a district, adjust officer strengths, select beats, and click "Show Allocation".
* **Internal Workflow**:
  1. Read `Resource_Allocation_Cleaned.csv` and get the default sanctioned strengths for the district.
  2. Define the Linear Programming (LP) optimization problem using PuLP:
     $$\text{Maximize } \sum (\text{Normalised Severity}_{\text{beat}} \times \text{Total Officers}_{\text{beat}})$$
  3. Solve the optimization problem and round values to integers.
  4. Filter the optimized table based on user selections and display it.
* **Asset Mapping**:
  * Parameters Input: ![Resource Input](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/input_Res_Allocation.PNG)
  * Allocation Output: ![Allocation Table](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/tab_coln_Res_alloc.PNG)

---

## 5. Continuous Learning and Feedback

### A. Dynamic Resource Strength Updates
* **Purpose**: Allows administrators to update sanctioned personnel strengths based on operational experience.
* **Inputs**: Unit selection, and new count values for ASI, CHC, and CPC.
* **Outputs**: A success message confirming updates to the datasets.
* **User Interaction**: Users select the checkbox, modify counts, and click "Confirm Update".
* **Internal Workflow**: Updates the corresponding rows in `Resource_Allocation_Cleaned.csv` and saves the file.
* **Asset Mapping**:
  * Form: ![Resource Update Form](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/police-resource-allocation.PNG)

### B. User Feedback and Alert Meter
* **Purpose**: Tracks system performance and triggers developer notifications when rating metrics drop.
* **Inputs**: Rating slider (1 to 5), Feedback Type dropdown, and comments text box.
* **Outputs**: Banners showing system rating status and a live progress meter.
* **User Interaction**: Users rate the system and submit comments.
* **Internal Workflow**:
  1. Save ratings to `Feedback.csv`.
  2. Compute the average rating and negative feedback counts (ratings < 3).
  3. Render progress bars.
  4. If the average rating is below 3.5 or negative feedback count exceeds 20, trigger `send_alert()`:
     * Connect to `smtp.gmail.com:587` via TLS.
     * Authenticate using the `EMAIL_PASSWORD` environment variable.
     * Attach `Feedback.csv` and email the technical lead.
* **Asset Mapping**:
  * Alert Meter: ![Alert Meter](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/live-feedback.PNG)
  * Email Alert: ![Email Alert Detail](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/alert-2.PNG)

### C. Feedback Session Scheduling
* **Purpose**: Schedules follow-up meetings with stakeholders to discuss system performance.
* **Inputs**: Date, Time, and Stakeholders list.
* **Outputs**: Invitation emails containing the feedback CSV file as an attachment.
* **User Interaction**: Users select stakeholders, set a date and time, and click "Send Invitation mail".
* **Internal Workflow**: Sends emails to the selected stakeholders with `Feedback.csv` attached.
* **Asset Mapping**:
  * Session Manager: ![Session UI](file:///d:/Workplace/Hackathons/Datathon/Predictive_Guardians/Predictive_Guardians-main/assets/feedback-sessions.PNG)
