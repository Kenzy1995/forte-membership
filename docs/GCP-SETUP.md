# GCP 設定（bl88-risk / kenzy@dd99.games）

Cloud Run 只跑 API；**資料在 Supabase**，Runtime SA 不需 Sheets 權限。

## 一、重新登入（若 token 過期）

```powershell
gcloud auth login kenzy@dd99.games
gcloud config set project bl88-risk
```

## 二、一鍵建立資源

```powershell
cd 專案根目錄
.\scripts\setup-gcp.ps1
```

會建立：
- Artifact Registry：`asia-east1/forte-membership`
- Runtime SA：`futai-member-run@bl88-risk.iam.gserviceaccount.com`
- Deploy SA：`forte-membership-deploy@bl88-risk.iam.gserviceaccount.com`
- 金鑰：`local/deploy-sa.json`（給 GitHub `GCP_CREDENTIALS`）

## 三、寫入 GitHub Secrets

```powershell
gh secret set GCP_CREDENTIALS --env staging --repo Kenzy1995/forte-membership < local/deploy-sa.json
gh secret set CLOUD_RUN_RUNTIME_SA --env staging --repo Kenzy1995/forte-membership --body "futai-member-run@bl88-risk.iam.gserviceaccount.com"
```

## 四、部署

push `main` 或 Actions → Run workflow **Deploy Staging**。

## 五、部署後

```powershell
gcloud run services describe futai-member-api --region asia-east1 --format="value(status.url)"
```

將 URL 用於 LINE Webhook 與 LIFF Endpoint。
