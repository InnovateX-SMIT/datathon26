# Predictive Guardians

## AI-Powered Crime Intelligence & Decision Support Platform

An advanced intelligence and decision support platform engineered for law enforcement agencies, police SPs, SHOs, and platform administrators. Built on clean architecture principles to aggregate incident history, map geospatial hotspots (DBSCAN), predict recidivism risks (H2O Stacked Ensembles), outline criminal networks (NetworkX & React Flow), and optimize police patrol strength allocations (Linear Programming Solver).

---

## 🏗️ Architecture Design & Engine Separation

The project is structured into modular layers implementing:
- **Presentation Layer**: Next.js App Router, TypeScript, and TailwindCSS.
- **Backend API Layer**: FastAPI with SQLAlchemy ORM and JWT role authorization.
- **Computation / Analytics Layer**: Python modules powered by Pandas, NumPy, and SciPy.
- **ML & Network Modeling Layer**: Scikit-Learn classifiers, H2O MOJO scoring runtimes, SHAP explanations, and NetworkX relational graphs.

For a detailed mapping of files and folders, see [PROJECT_STRUCTURE.md](file:///d:/Workplace/Hackathons/Datathon/datathon26/docs/PROJECT_STRUCTURE.md).

---

## 🚀 Getting Started

Follow the steps in [DEVELOPMENT_SETUP.md](file:///d:/Workplace/Hackathons/Datathon/datathon26/docs/DEVELOPMENT_SETUP.md) to initialize:
1. Local database container via Docker Compose
2. Python virtual environments and FastAPI server
3. Next.js local development package installation and visual interface dev server

---

## 🛡️ Sandbox Simulation Roles

For testing and review, the frontend Navbar includes a **Demo Role Selector** to toggle access between:
1. **OFFICER**: Basic incident review and threat alerts.
2. **SUPERINTENDENT**: Active resource allocation solver and executive report generators.
3. **ADMIN**: Platform settings and user account role management.