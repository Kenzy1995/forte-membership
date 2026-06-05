# Google Sheet 工作表結構

建立新試算表後，建立以下 4 個工作表（Sheet tab 名稱需完全一致）：

## Members（會員主檔）

| 欄位 | 說明 |
|------|------|
| member_id | UUID |
| line_user_id | LINE User ID（唯一） |
| 姓名 | |
| 電話 | 唯一性檢查 |
| email | |
| 性別 | |
| 出生年月日 | YYYY-MM-DD |
| 首次參加館別 | 翡翠灣 / 汐止 / 彰化 |
| 註冊時間 | ISO8601 |
| 狀態 | active / blocked |

## Campaigns（活動）

| 欄位 | 說明 |
|------|------|
| campaign_id | 如 SA-2026-H1 |
| 活動名稱 | |
| 活動類型 | stay_active / birthday / seasonal / custom |
| 適用館別 | 逗號分隔 |
| 開始日期 | YYYY-MM-DD |
| 結束日期 | YYYY-MM-DD |
| 獎勵類型 | physical / digital_coupon / both |
| 獎勵描述 | |
| 每人限領次數 | 預設 1 |
| 兌換條件說明 | |
| 狀態 | active / ended |

首筆範例：

```
SA-2026-H1,Stay Active 帥！先行動,stay_active,汐止,翡翠灣,彰化,2026-01-01,2026-12-31,both,精美禮品,1,完成 Strava 路線+社群打卡,active
```

## Redemptions（兌換紀錄）

| 欄位 | 說明 |
|------|------|
| redemption_id | UUID |
| member_id | |
| campaign_id | |
| 兌換館別 | |
| 兌換時間 | ISO8601 |
| 核銷人員 | |
| 社群平台 | FB / IG / Google |
| 審核備註 | |
| 獎勵類型 | physical / coupon / both |
| 券碼 | |
| 狀態 | completed / cancelled |

## Coupons（數位券碼池）

| 欄位 | 說明 |
|------|------|
| coupon_code | 唯一 |
| campaign_id | |
| member_id | 派發後填入 |
| 派發時間 | |
| 使用狀態 | unused / used / expired |
| 有效期限 | YYYY-MM-DD |

試算表需分享編輯權給 Cloud Run 使用的 Service Account。
