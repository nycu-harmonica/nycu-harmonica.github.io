# 幹部操作手冊(RUNBOOK)

這份文件寫給**不需要程式背景**的社團幹部:如何更新網站內容、誰該有哪些權限、出問題怎麼辦。

網站長期維護模式＝社團共用 Google Sheet＋公開 Google Calendar＋臺灣口琴觀測站公開動態＋核准公開的相簿照片。

> **目前狀態:**公開 Calendar 與正式公開 Google Sheet 均已連結。試算表編輯網址只留在幹部交接資料,網站與公開文件不提供編輯入口。

## 0. 「詢問竹韻」公開問答

- 官網本身仍完全部署在 GitHub Pages。問答服務離線時，只會顯示暫時無法回答；其他頁面、Sheet、Calendar 和相簿不受影響。
- 問答只讀已核准的公開網站內容與公開 Sheet，不會讀取 `shared/`、`private/`、Discord、Gmail、Drive 或社員個資。
- 不要在問答視窗輸入學號、電話或私人聯絡資料。
- 若回答內容不正確，先以官網、公開 Calendar 或 Instagram 為準，並由網站管理員檢查 `club.nycu.harmonica.website-agent` 與 `website` Hermes profile。
- 緊急停用時，把 `hugo.toml` 的 `params.websiteAgent.enabled` 設為 `false` 後部署；網站其他功能仍會正常運作。

## 1. 竹韻近期動態

首頁的「竹韻近期動態」由臺灣口琴觀測站整理自竹韻公開社群，並連回原始貼文。官網不另設公告頁，幹部不需要維護公告工作表。

訪客開啟首頁時，瀏覽器會直接讀取觀測站的竹韻專用公開 API，因此新貼文不需要重新部署官網。若 API 暫時無法使用，首頁會安靜地保留網站內建的上次同步資料，不影響其他內容。

`Sync public site data` 不會為觀測站貼文建立自動 commit。只有需要更新網站內建備援資料時，才由網站管理員手動執行 `python3 scripts/sync_observe.py`，檢查後 commit。

## 2. 首頁行事曆

- **所有活動**加進社團的公開 Google Calendar，首頁會直接顯示完整行事曆。
- 官網不另設活動頁，也不需要維護精選活動工作表。

## 3. 更新幹部名單/社群連結

- `officers` 工作表只接受 order(排序)、role(職稱)、name(經核准的公開姓名)、status。不可加入 email、系級或其他個資。
- `links` 工作表只放官方公開入口。icon 可填 `instagram / facebook / youtube / email / line / link`,不得填個人聯絡資料。
- 儲存 Sheet 後不需要執行 GitHub Action 或等待部署。新開網站會立即讀取最新公開資料；已開啟的頁面最慢約 60 秒更新。
- 網站會等三個工作表全部讀取且驗證成功才一次換成新資料。編輯到一半、表頭錯誤或 Google 暫時失效時,訪客會繼續看到 last-good 備援,不會看到半套內容。

## 4. 新增相簿

照片目前需要一位會用 GitHub 的幹部(網站管理員)協助:

1. 幹部把選好的照片交給網站管理員(挑 10–30 張精華即可)。
2. 網站管理員:
   - 在 repo 的 `content/gallery/` 開新資料夾,名稱=相簿代號(例:`2026-12-year-end-concert`)
   - 照片縮圖後放入(建議 WebP、長邊 ≤1600px、單張 <300KB)。Mac 一行指令:
     `for f in *.jpg; do cwebp -q 82 -resize 1600 0 "$f" -o "${f%.jpg}.webp"; done`
     (`cwebp` 會自動去除照片的 GPS 等隱私資訊)
   - commit + push
3. 在 `gallery_albums` 工作表加一列:slug(=資料夾名)、title、date 必填;cover 填封面檔名(留空=第一張)。

> 未來若建好社團 Shared Drive 與自動同步(見 docs/google-setup.md),步驟 2 會簡化成「把照片丟進指定雲端資料夾」。

## 5. 手動更新 last-good 備援

日常 Sheet 更新不需要做這一步。只有網站管理員想把目前 Sheet 內容保存成 Google 失效時的 repo 備援時才執行:

1. 開啟 GitHub repo → **Actions** 頁籤。
2. 左側選 **Refresh public data fallback** → 右側 **Run workflow** → 綠色按鈕。
3. 有內容變更時會 commit 並重新部署,把目前內容保存為新的 last-good fallback。

正常開啟網站後,頁尾應在數秒內從「Repo 資料備援」變成「Google Sheet 即時讀取」並顯示讀取時間。若沒有變化,先檢查 Sheet 是否仍維持「知道連結的任何人:檢視者」。

## 6. 同步失敗怎麼辦

同步失敗時,系統會自動在 repo 開一個標籤為 `sync-failure` 的 issue(有 watch repo 的幹部會收到 email)。常見原因:

| 症狀 | 原因 | 處理 |
|---|---|---|
| 「回應不是 CSV」 | 試算表的共用設定被改掉 | 把試算表改回「知道連結的任何人:檢視者」 |
| 「缺少必要欄位」 | 有人改了表頭列 | 把表頭改回文件規格(見 README 資料格式) |
| 「slug 重複」 | 兩列用了同一個 slug | 改掉其中一個 |
| 「第 N 列…已跳過」 | 該列格式錯誤（日期或網址等） | 照錯誤訊息修正該列 |

修好後重跑「手動觸發同步」,成功後把 issue 關閉。

即時讀取沒有 GitHub 排程,因此不受 GitHub 60 天停用 scheduled workflow 的限制。

## 7. 內容出錯想回復

所有內容變更都有 Git 歷史。請網站管理員:

```sh
git log --oneline -- static/data content   # 找到出錯前的 commit
git revert <commit>                         # 回復該次變更
```

若錯誤來自試算表,記得同時把試算表改回來,否則下次同步又會蓋回去。

## 8. 權限與交接清單

每屆交接必查,**任何資源都不可只有一個人(或已畢業學長姊的個人帳號)能管理**:

| 資源 | 應有權限 |
|---|---|
| GitHub organization(nycu-harmonica) | 至少 2 位現任幹部為 **Owner** |
| 網站 repo | 由 organization 持有(不放個人帳號下) |
| 資料試算表 | 至少 2 位現任幹部為「編輯者」;共用設定維持「知道連結的任何人:檢視者」 |
| Google Calendar | 至少 2 位現任幹部可「變更活動」;維持公開 |
| 社團 Google 帳號(若有) | 密碼與備援信箱交接給現任社長與一位幹部 |

新幹部上任時:舊幹部在 GitHub org 加入新幹部(Owner)、試算表與行事曆加編輯權限;確認後再移除已卸任者。
