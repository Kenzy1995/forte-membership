# GCP 測試環境設定（kenzy@dd99.games）

## 1. 登入

```bash
gcloud auth login kenzy@dd99.games
gcloud config set project YOUR_PROJECT_ID
```

## 2. 啟用 API

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com sheets.googleapis.com
```

## 3. 建立 Artifact Registry（若尚未建立）

```bash
gcloud artifacts repositories create forte-membership \
  --repository-format=docker \
  --location=asia-east1
```

## 4. 建立 Service Account

```bash
gcloud iam service-accounts create futai-member-sheets \
  --display-name="Forte Membership Sheets"

# Cloud Run 執行身分（可與部署 SA 分開）
gcloud iam service-accounts create futai-member-run \
  --display-name="Forte Membership Cloud Run"
```

分享 Google 試算表編輯權給：`futai-member-run@YOUR_PROJECT_ID.iam.gserviceaccount.com`

## 5. 部署用 SA 金鑰（給 GitHub GCP_CREDENTIALS）

```bash
gcloud iam service-accounts keys create deploy-sa.json \
  --iam-account=YOUR_DEPLOY_SA@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

將 JSON 內容貼至 GitHub → Environment `staging` → Secret `GCP_CREDENTIALS`

## 6. GitHub staging Secrets

依 `docs/ENV-MANIFEST.txt` 逐項設定。設定後將 manifest 中 staging 欄改為 ✅。

## 7. LINE Webhook

部署完成取得 Cloud Run URL 後：

```
https://YOUR-SERVICE-URL/api/line/webhook
```

## 產生 STAFF_PIN_HASH

```bash
python -c "import bcrypt; print(bcrypt.hashpw(b'1234', bcrypt.gensalt()).decode())"
```

將輸出存入 GitHub Secret `STAFF_PIN_HASH`（請改用正式 PIN）。
