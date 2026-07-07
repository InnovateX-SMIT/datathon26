# Zoho Catalyst Deployment & Operations Manual

This guide describes how to deploy the **AI-Powered Crime Intelligence & Decision Support Platform** to the **Zoho Catalyst** production environment.

---

## 1. Directory Structure Mapping

For production-ready deployments, the repository utilizes the standard Zoho Catalyst monorepo structure:
- [catalyst.json](file:///Users/krishanand/datathon26/catalyst.json): Root configuration coordinating client and server targets.
- [backend/app-config.json](file:///Users/krishanand/datathon26/backend/app-config.json): AppSail service properties for Python FastAPI.
- [.catalystrc](file:///Users/krishanand/datathon26/.catalystrc): Metadata binding local files to Zoho Cloud project.

---

## 2. Serverless Component Topology

The platform maps to the following Zoho Catalyst cloud services:
1. **FastAPI Backend Services**: Hosted on **Catalyst AppSail** container microservice running on Python 3.10 stack.
2. **Next.js Single Page App**: Hosted on **Catalyst Web Client Hosting** (static global CDN).
3. **Database Relational Store**: Hosted on **Catalyst Data Store** (ZCQL relational mapping).
4. **Binary Machine Learning Files**: Stored on **Catalyst Stratus** object storage buckets.
5. **Nightly Retraining Tasks**: Triggered via **Catalyst Cron Scheduler**.

---

## 3. Environment Variables Configuration

The following variables must be configured inside the **Catalyst AppSail Console** environment parameters:

| Variable Name | Required | Default Value | Role / Usage |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | Yes | `production` | Switches exception handling, logs level, and middleware strictness |
| `SECRET_KEY` | Yes | *Secure Unique Token* | JWT key. Application will fail to start if default is used in production. |
| `DATABASE_URL` | No | `sqlite:///crime_intel.db` | PostgreSQL target or SQLite location path |
| `ALLOWED_CORS_ORIGINS` | No | `*` | List of allowed CORS origins |

---

## 4. CLI Deployment Commands

Follow these steps to deploy manually from the terminal:

```bash
# 1. Install the global Zoho Catalyst CLI
npm install -g zcatalyst-cli

# 2. Login to your Zoho Account
catalyst login

# 3. Initialize the deployment target mapping
catalyst init

# 4. Run the local development emulator for testing
catalyst serve

# 5. Deploy both AppSail and Web Client targets to Zoho Cloud
catalyst deploy
```

---

## 5. Security & Rate Limiting Controls

The production build includes:
- **Rate Limiting**: Limits incoming IP requests to **100 requests per minute**. Rejects abuses with `HTTP 429 Too Many Requests`.
- **Script Sanitization**: Blocks script tag HTML injections in JSON request bodies (`HTTP 400 Bad Request`).
- **File Upload Limits**: Enforces a strict size boundary of **50MB** per dataset and sanitizes filenames against path traversals.
- **Secure Headers**: Hardens responses with standard secure header policies (`X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`).
