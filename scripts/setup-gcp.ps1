# 在 bl88-risk 專案建立 Forte Membership 部署資源
# 需已 gcloud auth login kenzy@dd99.games

$ErrorActionPreference = "Stop"
$PROJECT = "bl88-risk"
$REGION = "asia-east1"
$REPO = "forte-membership"
$RUN_SA = "futai-member-run"
$DEPLOY_SA = "forte-membership-deploy"

gcloud config set project $PROJECT

Write-Host "=== Artifact Registry ==="
gcloud artifacts repositories describe $REPO --location=$REGION 2>$null
if ($LASTEXITCODE -ne 0) {
  gcloud artifacts repositories create $REPO --repository-format=docker --location=$REGION --description="Forte membership API"
}

Write-Host "=== Service Accounts ==="
gcloud iam service-accounts describe "${RUN_SA}@${PROJECT}.iam.gserviceaccount.com" 2>$null
if ($LASTEXITCODE -ne 0) {
  gcloud iam service-accounts create $RUN_SA --display-name="Forte Member Cloud Run Runtime"
}
gcloud iam service-accounts describe "${DEPLOY_SA}@${PROJECT}.iam.gserviceaccount.com" 2>$null
if ($LASTEXITCODE -ne 0) {
  gcloud iam service-accounts create $DEPLOY_SA --display-name="Forte Membership GitHub Deploy"
}

$RUN_SA_EMAIL = "${RUN_SA}@${PROJECT}.iam.gserviceaccount.com"
$DEPLOY_SA_EMAIL = "${DEPLOY_SA}@${PROJECT}.iam.gserviceaccount.com"

Write-Host "=== IAM for deploy SA ==="
gcloud projects add-iam-policy-binding $PROJECT --member="serviceAccount:$DEPLOY_SA_EMAIL" --role="roles/run.admin" --quiet
gcloud projects add-iam-policy-binding $PROJECT --member="serviceAccount:$DEPLOY_SA_EMAIL" --role="roles/artifactregistry.writer" --quiet
gcloud projects add-iam-policy-binding $PROJECT --member="serviceAccount:$DEPLOY_SA_EMAIL" --role="roles/iam.serviceAccountUser" --quiet

Write-Host "=== Deploy key (local/deploy-sa.json) ==="
New-Item -ItemType Directory -Force -Path "local" | Out-Null
gcloud iam service-accounts keys create "local/deploy-sa.json" --iam-account=$DEPLOY_SA_EMAIL

Write-Host ""
Write-Host "DONE. Set GitHub secrets:"
Write-Host "  GCP_PROJECT_ID = $PROJECT"
Write-Host "  CLOUD_RUN_RUNTIME_SA = $RUN_SA_EMAIL"
Write-Host "  GCP_CREDENTIALS = contents of local/deploy-sa.json"
Write-Host "  ARTIFACT_REGISTRY_REPOSITORY = $REPO"
