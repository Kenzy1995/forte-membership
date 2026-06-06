# 部署與手動設定指南

## 一、您必須手動完成（約 15 分鐘）

### 1. Supabase 資料庫（必做）

1. 前往 [https://supabase.com](https://supabase.com) 登入（可用 Google 帳號）
2. **New project** → 名稱 `forte-membership`，Region 選 **Singapore** 或 **Tokyo**
3. 設定 Database Password（請記下）
4. 進入 **SQL Editor** → 貼上 [`supabase/init.sql`](../supabase/init.sql) 全文 → **Run**
5. 進入 **Project Settings → Database** → 複製 **Connection string → URI**
   - 使用 **Transaction pooler**（port **6543**）給 Cloud Run
   - 格式：`postgresql://postgres.xxxx:PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres`
6. 將 URI 設為 GitHub Secret：`DATABASE_URL`（見下方指令）

### 2. LINE 官方帳號（必做，若尚未設定）

1. [LINE Developers Console](https://developers.line.biz/console/) → Messaging API
2. 取得 `Channel Secret`、`Channel Access Token`
3. 建立 2 個 LIFF App（註冊、會員 QR）
4. 部署完成後設定 Webhook：`https://您的CloudRun網址/api/line/webhook`

---

## 二、已由腳本/文件準備的值

| 項目 | 值 |
|------|-----|
| GCP Project | `bl88-risk` |
| GCP 帳號 | `kenzy@dd99.games` |
| 櫃台測試 PIN | `8888`（請上線前更換） |
| QR_SIGNING_SECRET | 見本 repo push 後的 GitHub Secret 或下方本地記錄 |

---

## 三、GitHub Secrets 設定指令

在專案根目錄執行（需已 `gh auth login`）：

```powershell
gh secret set GCP_PROJECT_ID --env staging --repo Kenzy1995/forte-membership --body "bl88-risk"

# Supabase 連線字串（替換成您的）
gh secret set DATABASE_URL --env staging --repo Kenzy1995/forte-membership --body "postgresql://postgres.xxxx:YOUR_PASSWORD@....pooler.supabase.com:6543/postgres"

# LINE（替換成您的）
gh secret set LINE_CHANNEL_SECRET --env staging --repo Kenzy1995/forte-membership --body "YOUR_SECRET"
gh secret set LINE_CHANNEL_ACCESS_TOKEN --env staging --repo Kenzy1995/forte-membership --body "YOUR_TOKEN"
gh secret set LIFF_ID_REGISTER --env staging --repo Kenzy1995/forte-membership --body "YOUR_LIFF_ID"
gh secret set LIFF_ID_MEMBER_QR --env staging --repo Kenzy1995/forte-membership --body "YOUR_LIFF_ID"
```

`GCP_CREDENTIALS`、`CLOUD_RUN_RUNTIME_SA`、`QR_SIGNING_SECRET`、`STAFF_PIN_HASH` 由 GCP 設定腳本或 CI 管理員設定。

---

## 四、部署後驗證

```bash
curl https://YOUR-SERVICE-URL/health
# 預期：{"status":"ok","database_configured":true}

curl https://YOUR-SERVICE-URL/api/members/campaigns/active
# 預期：含 SA-2026-H1 Stay Active
```

- 會員註冊：Cloud Run URL + `/liff/register.html?liffId=您的LIFF_ID`
- 櫃台核銷：Cloud Run URL + `/staff/`

---

## 五、本地開發

```powershell
cd server-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:DATABASE_URL="postgresql://..."
uvicorn app.main:app --reload --port 8080
```
