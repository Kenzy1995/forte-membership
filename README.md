# 福泰會員優惠活動（Forte Membership）

集團級會員優惠平台：LINE 會員註冊、櫃台 QR 核銷、Google Sheet 資料管理。  
首波活動：**Stay Active 帥！先行動**（`SA-2026-H1`）。

- GitHub：[Kenzy1995/forte-membership](https://github.com/Kenzy1995/forte-membership)
- 測試 GCP：`kenzy@dd99.games`（不另開新 Project）
- 與接駁車系統完全獨立（不共用 API / Sheet）

## 專案結構

```
server-api/     FastAPI 後端 + Docker
web/            LIFF 註冊、會員 QR、櫃台核銷頁
docs/           ENV-MANIFEST.txt、Sheet 欄位說明
gas/            Google Apps Script（試算表報表）
.github/        GitHub Actions 部署
```

## 快速開始（本地）

```bash
cd server-api
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
set SPREADSHEET_ID=your-sheet-id
set GOOGLE_APPLICATION_CREDENTIALS=path\to\sa.json
uvicorn app.main:app --reload --app-dir . --port 8080
```

- 健康檢查：http://localhost:8080/health
- 會員註冊頁：http://localhost:8080/liff/register.html
- 櫃台核銷：http://localhost:8080/staff/

## 環境變數

**所有 Secrets 存放在 GitHub Actions Environment（staging / production）。**  
變數清單與遷移 checklist 見 [docs/ENV-MANIFEST.txt](docs/ENV-MANIFEST.txt)。

## 部署（staging）

1. 在 GitHub repo → Settings → Environments → 建立 `staging`
2. 依 ENV-MANIFEST 填入 Secrets
3. push 至 `main` 觸發 `.github/workflows/deploy-staging.yml`
4. 部署完成後，至 LINE Console 設定 Webhook：`{BASE_URL}/api/line/webhook`

## Google Sheet

依 [docs/SHEET-SCHEMA.md](docs/SHEET-SCHEMA.md) 建立四個工作表，並分享編輯權給 Cloud Run Service Account。

## API 摘要

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/health` | 健康檢查 |
| POST | `/api/members/register` | 會員註冊 |
| GET | `/api/members/{id}/qr` | 取得會員 QR |
| POST | `/api/staff/redeem` | 櫃台核銷 |
| POST | `/api/line/webhook` | LINE Webhook |
