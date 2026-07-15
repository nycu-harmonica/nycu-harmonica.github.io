# 幹部操作手冊(RUNBOOK)

這份文件寫給**不需要程式背景**的社團幹部:如何更新網站內容、誰該有哪些權限、出問題怎麼辦。

網站內容 = 社團共用 Google Sheet + 公開 Google Calendar + 相簿照片。改好資料後,網站**每天自動更新四次**(約 08:41、14:41、20:41、02:41);急件見「手動觸發同步」。

## 1. 發公告

開啟社團資料試算表(網址見社團幹部交接文件)→ `announcements` 工作表,新增一列:

| 欄位 | 填法 |
|---|---|
| slug | 網址代號,小寫英數與 `-`,例:`2026-09-01-recruit`(不可與其他列重複) |
| date | `2026-09-01` 格式 |
| title | 公告標題 |
| content | 內文,可用 Markdown(`**粗體**`、`[文字](網址)`、`- 條列`);儲存格內換行就是分段(Mac:`⌥+Enter`,Windows:`Alt+Enter`) |
| pinned | 要置頂填 `TRUE`,否則留空 |
| link | 相關連結(報名表等),須為 `https://` 開頭 |
| status | 留空=發布;填 `draft` =先隱藏 |

刪掉一列,網站上該公告就會消失(歷史版本仍可從 GitHub 找回)。

## 2. 活動時程與精選

- **所有活動**加進社團的公開 Google Calendar(活動頁的行事曆直接顯示它)。
- 想在**首頁露出**的活動,另外在 `featured_events` 工作表加一列(title、start 必填)。活動結束日過後會自動從首頁消失,不用手動刪。

## 3. 更新幹部名單/社群連結

- `officers` 工作表:order(排序,小的在前)、role(職稱)、name 必填。照片先把檔案交給網站管理員放進 repo 的 `assets/images/officers/`,再於 photo 欄填檔名。
- `links` 工作表:Instagram、信箱等。icon 可填 `instagram / facebook / youtube / email / line / link`。

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

## 5. 手動觸發同步(急件)

1. 開啟 GitHub repo → **Actions** 頁籤
2. 左側選 **Sync data from Google Sheet** → 右側 **Run workflow** → 綠色按鈕
3. 約 2–3 分鐘後網站更新(接著會自動跑 **Deploy to GitHub Pages**)

## 6. 同步失敗怎麼辦

同步失敗時,系統會自動在 repo 開一個標籤為 `sync-failure` 的 issue(有 watch repo 的幹部會收到 email)。常見原因:

| 症狀 | 原因 | 處理 |
|---|---|---|
| 「回應不是 CSV」 | 試算表的共用設定被改掉 | 把試算表改回「知道連結的任何人:檢視者」 |
| 「缺少必要欄位」 | 有人改了表頭列 | 把表頭改回文件規格(見 README 資料格式) |
| 「slug 重複」 | 兩列用了同一個 slug | 改掉其中一個 |
| 「第 N 列…已跳過」 | 該列格式錯(日期/網址/布林) | 照錯誤訊息修正該列 |

修好後重跑「手動觸發同步」,成功後把 issue 關閉。

**排程停擺**:GitHub 對 60 天沒有任何 commit 的 repo 會自動停用排程。若收到「scheduled workflow disabled」通知,到 Actions 頁點該 workflow 的 **Enable workflow** 即可。

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
