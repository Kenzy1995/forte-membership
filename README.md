# 福泰會員系統（Forte Membership）

集團級會員優惠平台 — LINE 註冊、Supabase PostgreSQL、Cloud Run 核銷。

- Repo: [Kenzy1995/forte-membership](https://github.com/Kenzy1995/forte-membership)
- 測試 GCP: `kenzy@dd99.games` / `bl88-risk`
- 資料庫: **Supabase PostgreSQL**（非 Google Sheet）

## 快速部署

1. **Supabase**：建立專案 → 執行 [`supabase/init.sql`](supabase/init.sql) → 複製 `DATABASE_URL`
2. **GCP**：`gcloud auth login` 後執行 [`scripts/setup-gcp.ps1`](scripts/setup-gcp.ps1)
3. **GitHub Secrets**：依 [`docs/SETUP-MANUAL.md`](docs/SETUP-MANUAL.md) 補齊 staging Environment
4. **push main** → GitHub Actions 自動部署 `futai-member-api`

## 本地開發

```powershell
cd server-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:DATABASE_URL="postgresql://..."
uvicorn app.main:app --reload --port 8080
```

## 端點

| 路徑 | 說明 |
|------|------|
| `/health` | 健康檢查 |
| `/liff/register.html` | 會員註冊 |
| `/liff/member-qr.html` | 會員 QR |
| `/staff/` | 櫃台核銷 |
| `/api/line/webhook` | LINE Webhook |

完整環境變數清單：[`docs/ENV-MANIFEST.txt`](docs/ENV-MANIFEST.txt)
