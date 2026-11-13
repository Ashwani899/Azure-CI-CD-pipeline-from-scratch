# Azure CI/CD Pipeline — Containerized Flask Application

A small Flask application used to demonstrate an Azure DevOps delivery pipeline: run tests, build a Docker image, push it to Azure Container Registry (ACR), and deploy the tagged image to Azure App Service.

## Pipeline flow

```text
Git push
   |
Azure Pipelines
   |-- Test (pytest)
   |-- Build Docker image and tag with Build.BuildId
   |-- Push image to ACR
   '-- Deploy image to Azure App Service
```

Build and deployment are separate stages so a deployment can be retried against an already-built image. Use immutable build identifiers for traceability; do not rely only on a mutable `latest` tag.

## Stack

- Python / Flask / Gunicorn
- Docker
- Azure Pipelines YAML
- Azure Container Registry
- Azure App Service for Containers
- pytest

## Repository layout

```text
app/
  main.py
  test_main.py
  requirements.txt
  templates/
  static/
Dockerfile
azure-pipelines.yml
```

## Run locally

```bash
cd app
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Open `http://localhost:8000`.

## Run with Docker

From the repository root:

```bash
docker build -t azure-cicd-demo .
docker run --rm -p 8000:8000 azure-cicd-demo
```

## Configure Azure DevOps

The pipeline expects Azure resources and service connections to be configured in your own subscription:

1. Create an Azure Container Registry and an App Service configured for a container image.
2. Connect the repository to an Azure DevOps project.
3. Create the Docker Registry service connection referenced by the YAML.
4. Create an Azure Resource Manager service connection referenced by the YAML.
5. Configure the variable names used by `azure-pipelines.yml` (registry name, App Service name, resource group, and service-connection identifiers).
6. Run the pipeline and verify the Test, Build/Push, and Deploy stages in Azure DevOps.

Exact service-connection and variable names must match the checked-in pipeline. Never commit service principal secrets, publish profiles, registry passwords, or subscription credentials.

## Operational considerations

- Restrict service connections to the required project and resource scope.
- Prefer managed identity and least-privilege RBAC where supported.
- Add a staging slot and health-gated slot swap before using this pattern for a production workload.
- Pin base images and dependency versions, scan container images, and retain a rollback image.
- Confirm that the deployed App Service image tag matches the pipeline build ID.

## Evidence and status

This repository contains the pipeline definition and application code. A successful deployment depends on external Azure resources, service connections, and variables; no live endpoint is claimed by this README. Add sanitized run links or screenshots only after a real pipeline run has succeeded.

## Next steps

- Add branch protection and require tests before merging to `main`.
- Add container vulnerability scanning and artifact retention.
- Add a staging environment and rollback procedure.
