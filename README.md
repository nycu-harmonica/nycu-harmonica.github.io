# 竹韻口琴社官方網站

國立陽明交通大學竹韻口琴社官網,網址:<https://harmonica.nycu.club/>(DNS 生效前為 GitHub Pages 預設網址)。

- 靜態網站:[Hugo](https://gohugo.io/)(extended)+ GitHub Pages,無付費服務依賴
- 內容來源:社團共用 Google Sheet(公告/精選活動/幹部/相簿資訊/連結)+ 公開 Google Calendar(活動時程)+ repo 內照片目錄(相簿)
- **幹部日常維護不需要碰這個 repo**,只要編輯試算表與行事曆,見 [RUNBOOK.md](RUNBOOK.md)

## 本機預覽

需求:Hugo extended 0.146+(macOS:`brew install hugo`)。

```sh
hugo server          # http://localhost:1313
hugo --gc --minify   # 正式建置,輸出到 public/
```

Fresh checkout 不需執行任何腳本即可建置——所有由試算表產生的內容(`content/announcements/`、`content/gallery/*/index.md`、`data/generated/`)與 CSV 快照(`static/data/`)都已提交在 repo 中。

檢查版面時建議至少看三種寬度:375px(手機)、768px(平板)、1280px(桌面)。

## 資料流

```
Google Sheet(五個工作表,公開可讀)
   │  GitHub Actions 每日同步四次(sync-data.yml,約 08:41/14:41/20:41/02:41 台北時間)
   ▼
scripts/sync_sheet.py ── 下載 CSV → 驗證欄位 → 產生:
   ├── static/data/*.csv              CSV 快照(= Sheet 掛掉時的 fallback)
   ├── content/announcements/*.md     公告頁(每則獨立網址,含 RSS)
   ├── content/gallery/<slug>/index.md 相簿頁資訊
   └── data/generated/*.json          精選活動/幹部/連結/相簿索引/同步時間
   │  有變更才 commit → 觸發 deploy.yml
   ▼
Hugo build → GitHub Pages
```

- 活動完整時程的唯一來源是公開 Google Calendar(活動頁 iframe);Sheet 的 `featured_events` 只負責首頁/活動頁的精選卡片。
- 精選活動的「過期自動下架」以建置當下日期判斷,最多延遲一個同步週期(6 小時)。
- 相簿照片放在 `content/gallery/<slug>/`(WebP/JPG),縮圖與大圖由 Hugo 於建置時自動產生,不需手動處理多種尺寸。

## 資料格式(Google Sheet 五個工作表)

欄位規格的權威定義在 `scripts/sync_sheet.py` 的 `TAB_SPECS`,摘要:

| 工作表 | 欄位(*=必填) | 用途 |
|---|---|---|
| `announcements` | slug*、date*、title*、content*、pinned、link、status | 公告 |
| `featured_events` | title*、start*、end、time_text、location、summary、link、status | 首頁精選活動 |
| `officers` | order*、role*、name*、dept_year、email、photo、status | 幹部名單 |
| `gallery_albums` | slug*、title*、date*、description、cover、drive_folder_id、status | 相簿資訊 |
| `links` | key*、label*、url*、icon、order、show_in | 社群/聯絡連結 |

通則:表頭支援中文別名(如「標題」=`title`);日期格式 `YYYY-MM-DD`;`status` 填 `draft`(或「草稿」)即隱藏;網址僅接受 `https://` 與 `mailto:`。

## 同步腳本

```sh
python3 scripts/test_sync_sheet.py          # 自測(零依賴)
python3 scripts/sync_sheet.py --offline     # 用 repo 內 CSV 快照重建所有生成內容
python3 scripts/sync_sheet.py               # 線上同步(sources.json 需已設定 sheet_id/gid)
python3 scripts/sync_sheet.py --strict      # CI 模式:有錯誤即非零結束
```

`scripts/sources.json` 存 Sheet ID 與各工作表 gid(皆為公開資訊,可入 repo)。`sheet_id` 未設定時自動離線模式。

## 部署

- push 到 `main` → `deploy.yml` 自動建置部署(GitHub Pages 官方流程)。
- baseURL 由 `actions/configure-pages` 自動判斷:設定自訂網域前是 `https://<org>.github.io/<repo>/`,設定後是 `https://harmonica.nycu.club/`,**切換網域不需改 workflow**。
- 自訂網域與 DNS 申請流程:見 [docs/sdc-dns-request.md](docs/sdc-dns-request.md)。

## 相關文件

- [RUNBOOK.md](RUNBOOK.md) — 幹部操作手冊(不需程式背景)
- [docs/google-setup.md](docs/google-setup.md) — 建立共用 Sheet/Calendar/Drive 與最小權限設定
- [docs/sdc-dns-request.md](docs/sdc-dns-request.md) — 給 SDC 的 DNS record 申請範本

## 授權與內容

程式碼以 MIT 授權(見 LICENSE)。網站文字與照片版權屬國立陽明交通大學竹韻口琴社,未經同意請勿轉載。
