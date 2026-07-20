# Azure CI/CD Pipeline — Containerized Web App

A small Flask web app that exists mainly as a vehicle to build a **real, working CI/CD pipeline on Azure** — from a `git push` to a live deployment, with zero manual steps in between.

I wanted to actually understand what happens between "I fixed a bug" and "the fix is live," instead of just knowing the buzzwords. This project is that: Azure Pipelines building and testing the code, Azure Container Registry storing the image, and Azure App Service running it.

## What it does

Push to `main` → tests run automatically → app gets containerized → image gets pushed to ACR → App Service pulls the new image and redeploys. The homepage shows the build ID and build time it was deployed with, so I can visually confirm each deployment actually picked up the latest commit instead of silently serving a stale container.

## Architecture

```
GitHub repo
    │  (push to main)
    ▼
Azure Pipelines
    │  Stage 1: run pytest
    │  Stage 2: docker build → push to ACR
    │  Stage 3: deploy image → Azure App Service
    ▼
Azure Container Registry  ──image pull──▶  Azure App Service (live app)
```

Build and deploy are split into separate pipeline stages on purpose. If a deployment fails, I don't need to rebuild the image to retry — I can just re-run the deploy stage against the image that's already sitting in ACR.

## Stack

- **App:** Python (Flask) + Gunicorn
- **Containerization:** Docker
- **CI/CD:** Azure Pipelines (YAML)
- **Registry:** Azure Container Registry (ACR)
- **Hosting:** Azure App Service (Web App for Containers)

## Repo structure

```
.
├── app/
│   ├── main.py              # Flask app
│   ├── test_main.py         # pytest unit tests run in the CI stage
│   ├── requirements.txt
│   ├── templates/index.html
│   └── static/style.css
├── Dockerfile
├── azure-pipelines.yml      # the actual pipeline definition
└── README.md
```

## Running it locally

```bash
cd app
pip install -r requirements.txt
python main.py
# visit http://localhost:8000
```

Or with Docker:

```bash
docker build -t azure-cicd-demo .
docker run -p 8000:8000 azure-cicd-demo
```

## Setting up the pipeline yourself

If you're cloning this to reproduce the setup:

1. **Create the Azure resources**
   - An Azure Container Registry (`az acr create ...`)
   - An App Service plan + Web App configured for containers (`az webapp create ... --deployment-container-image-name ...`)

2. **Create an Azure DevOps project** and import this repo (or connect it via GitHub).

3. **Set up two service connections** (Project Settings → Service connections):
   - `acr-service-connection` — Docker Registry type, pointing at your ACR
   - `azure-subscription-connection` — Azure Resource Manager type, pointing at your subscription

4. **Add pipeline variables** (Pipelines → Edit → Variables):
   - `acrName` — your ACR name (without `.azurecr.io`)
   - `webAppName` — your App Service name
   - `resourceGroup` — the resource group both live in

5. **Create a new pipeline**, point it at `azure-pipelines.yml`, and run it.

6. Push a commit to `main` and watch the three stages (Test → Build & Push → Deploy) run in sequence.

## Things I ran into while building this

- **Service connections are the part nobody warns you about.** The pipeline YAML is the easy 20%; getting Azure DevOps and Azure to actually trust each other (RBAC roles, ACR admin access, the AzureRM connection scope) is where most of the actual debugging happened.
- **Splitting build/push from deploy into separate stages** made failures way less painful — a bad App Service config no longer means rebuilding the whole image to test a fix.
- **Tagging images with `$(Build.BuildId)`** instead of just `latest` was the single most useful decision — it means every deployment is traceable back to an exact pipeline run and commit, which matters the moment something breaks in production and you need to know what actually shipped.
- **`/health` endpoint** exists because App Service and any future monitoring needs something machine-checkable, not just "does the homepage render."

## What I'd add next

- A staging slot on App Service with slot-swap deployment instead of deploying straight to production
- Azure Monitor / Application Insights wired in for real telemetry instead of just checking the DevOps dashboard manually
- Branch policies requiring the Test stage to pass before merging to `main`
