# Google 資源建立指南(最小權限)

建立網站所需的社團共用 Google 資源。原則:

- **一律用社團共用帳號或多位幹部共同管理**,不要綁在任何人的個人帳號上。
- 對外只開「檢視」;編輯權限只給現任幹部。
- 網站只需要「公開可讀」,不需要任何 Google API 金鑰(相簿自動同步除外,見最後一節)。

## 1. 資料試算表(Google Sheet)

1. 以社團帳號建立試算表,命名如「竹韻口琴社網站資料」。
2. 建立五個工作表(分頁),名稱與表頭如下(表頭也可用中文別名,見 README):

   | 工作表 | 表頭(第 1 列) |
   |---|---|
   | `announcements` | `slug,date,title,content,pinned,link,status` |
   | `featured_events` | `title,start,end,time_text,location,summary,link,status` |
   | `officers` | `order,role,name,dept_year,email,photo,status` |
   | `gallery_albums` | `slug,title,date,description,cover,drive_folder_id,status` |
   | `links` | `key,label,url,icon,order,show_in` |

   起手內容可直接複製 repo 內 `static/data/*.csv`(範例資料)。
3. 共用設定:「知道連結的任何人」=**檢視者**(這是同步能運作的關鍵;不要開放編輯)。
4. 把現任幹部(至少 2 位)加為**編輯者**。
5. 取得識別碼填入 repo 的 `scripts/sources.json`:
   - `sheet_id`:試算表網址 `https://docs.google.com/spreadsheets/d/<這一段>/edit` 
   - 各工作表 `gid`:點該工作表時網址結尾 `#gid=<數字>`
6. (選填)把試算表編輯網址填入 `hugo.toml` 的 `sheetEditUrl`。
7. 完成後到 GitHub Actions 手動跑一次 **Sync data from Google Sheet** 驗證。

## 2. 活動行事曆(Google Calendar)

1. 以社團帳號建立日曆,命名如「竹韻口琴社活動」。
2. 設定 → 「存取權限」→ 勾選**公開提供**,詳細程度選「顯示所有活動詳細資料」。
3. 設定 → 「整合日曆」→ 複製**日曆 ID**(形如 `xxxx@group.calendar.google.com`)。
4. 填入 repo `hugo.toml` 的 `calendarId`,commit 後活動頁即顯示行事曆。
5. 把現任幹部(至少 2 位)加為「變更活動」權限。

## 3. 相簿照片(現行做法)

照片放在 repo 的 `content/gallery/<相簿代號>/`,由網站管理員整理上傳(流程見 RUNBOOK 第 4 節)。**不要**使用 Google Drive 的公開圖片直連網址——Drive 不是圖床,連結會失效且載入慢。

## 4. 相簿自動同步(未來,尚未啟用)

目標:幹部把照片丟進 Shared Drive 資料夾,網站自動抓取。啟用前置條件與步驟:

1. **建立 Shared Drive**(共用雲端硬碟,非個人「我的雲端硬碟」):所有權屬於團隊,不隨個人帳號畢業而消失。內建「網站相簿」資料夾,底下一本相簿一個子資料夾。
2. **建立 Google Cloud 專案**(社團帳號):啟用 Google Drive API。
3. **建立 service account**:
   - 不授予任何專案層級角色(權限最小化)
   - 產生金鑰(JSON)。**金鑰絕不放進 repo**
4. 把 service account 的 email 以**檢視者**加入該 Shared Drive(或僅「網站相簿」資料夾)。
5. GitHub repo → Settings → Secrets and variables → Actions → 新增 secret `GDRIVE_SA_KEY`,值為金鑰 JSON 全文。
6. 在 `gallery_albums` 工作表為每本相簿填 `drive_folder_id`(開啟該資料夾時網址的最後一段)。
7. 補完 `scripts/fetch_gallery_drive.py` 的下載實作(介面與行為已在該檔案開頭定義;僅用唯讀 scope `drive.readonly`),並在 `sync-data.yml` 加一個步驟呼叫它。

> 在完成以上設定前,`fetch_gallery_drive.py` 執行時會自動跳過,不影響既有流程。
