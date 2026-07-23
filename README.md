# 竹韻口琴社官方網站

國立陽明交通大學竹韻口琴社官網:<https://harmonica.nycu.club/>。

- 靜態網站:[Hugo](https://gohugo.io/)(extended)+ GitHub Pages,無付費服務依賴
- 目前內容來源：瀏覽器即時讀取公開 Google Sheet（幹部、相簿資訊與連結）＋公開 Google Calendar（首頁完整活動時程）＋臺灣口琴觀測站公開 API（首頁竹韻公開社群動態）＋ repo 內核准照片
- repo 內公開 CSV 是 last-good 快照,供 Sheet 暫時無法讀取或瀏覽器停用 JavaScript 時 fallback
- 「詢問竹韻」介面仍由 GitHub Pages 靜態提供；只有送出問題時才呼叫隔離的公開問答 endpoint

> **正式 Google Sheet 已於 2026-07-16 接通。** 幹部日常更新幹部、相簿資訊與連結時不需要修改 repo。

## 本機預覽

需求:Hugo extended 0.146+(macOS:`brew install hugo`)。

```sh
hugo server          # http://localhost:1313
hugo --gc --minify   # 正式建置,輸出到 public/
```

Fresh checkout 不需執行任何同步腳本即可建置,因為生成內容與公開 CSV 快照都已提交在 repo 中。

檢查版面時建議至少看三種寬度:375px(手機)、768px(平板)、1280px(桌面)。

## 資料流

```
公開 Google Sheet
   │  訪客開頁立即讀取;頁面停留時每 60 秒重抓;切回分頁時重新確認
   ▼
assets/js/sheet-live.js ── 三個工作表全部下載並驗證成功後,一次更新畫面
   │  任一下載/欄位/內容驗證失敗
   ▼
Hugo 靜態 HTML + repo CSV/JSON last-good 快照(fallback)
```

Google Sheet 不需 API key。前端透過 Google Visualization JSONP 讀取公開工作表,避免跨網域限制；三個 tab 採原子更新,不會顯示只成功一部分的資料。Sheet 修改後,新開頁面會立即讀到；已開啟頁面最慢約 60 秒更新。GitHub Pages 是靜態網站,Google 沒有提供推播給頁面的機制,因此 60 秒輪詢是目前的即時邊界。

首頁也會由訪客的瀏覽器直接讀取臺灣口琴觀測站的竹韻專用公開 API（`/api/source/198.json`），新貼文不需要重新部署官網即可顯示。前端只接受竹韻來源 metadata 與最小必要欄位，成功驗證後才替換卡片；API 失效或資料不合法時，會保留 Hugo 已輸出的 `data/generated/observe_updates.json` 備援內容。

`scripts/sync_observe.py` 只用於網站管理員手動更新 committed fallback，不在定期同步 workflow 內執行。相同貼文不會只因 API 生成時間改變而重寫快照。

- 活動完整時程的來源是公開 Google Calendar，首頁直接顯示完整行事曆。
- 相簿照片放在 `content/gallery/<slug>/`(WebP/JPG),縮圖與大圖由 Hugo 於建置時自動產生,不需手動處理多種尺寸。

## 資料格式（Google Sheet 三個工作表）

欄位規格的權威定義在 `scripts/sync_sheet.py` 的 `TAB_SPECS`,摘要:

| 工作表 | 欄位(*=必填) | 用途 |
|---|---|---|
| `officers` | order*、role*、name*、status | 僅含核准公開的職稱與姓名 |
| `gallery_albums` | slug*、title*、date*、description、cover、status | 相簿資訊 |
| `links` | key*、label*、url*、icon、order、show_in | 社群/聯絡連結 |

通則:表頭支援中文別名(如「標題」=`title`);日期格式 `YYYY-MM-DD`;`status` 填 `draft`(或「草稿」)即隱藏;網址僅接受 `https://` 與 `mailto:`。

## 同步腳本

```sh
python3 scripts/test_sync_sheet.py          # 自測(零依賴)
python3 scripts/test_sync_observe.py        # 觀測站同步與 last-good 自測
node scripts/test_observe_updates.js        # 首頁即時 API 驗證與 fallback 自測
node scripts/test_sheet_live.js             # Sheet 即時讀取、欄位驗證與原子更新自測
python3 scripts/check_public_content.py     # 公開資料隱私與欄位檢查
python3 scripts/sync_sheet.py --offline     # 用 repo 內 CSV 快照重建所有生成內容
python3 scripts/sync_sheet.py               # 手動更新 repo last-good 快照
python3 scripts/sync_sheet.py --strict      # 手動更新快照的嚴格模式
python3 scripts/sync_observe.py             # 手動更新觀測站近期動態 fallback
```

`scripts/sources.json` 存 Sheet ID 與各工作表 gid(皆為公開資訊,可入 repo),Hugo 會把設定放進每頁的公開 JSON config。`sheet_id` 未設定時,手動同步腳本會自動使用離線模式。

## 部署

- Sheet 日常修改不需 commit、Action 或重新部署；訪客瀏覽器會直接讀取。
- push 到 `main` → `deploy.yml` 自動建置部署(GitHub Pages 官方流程),只用於程式、文字、版面或相簿照片變更。
- `Refresh public data fallback` 只供網站管理員手動更新 repo last-good 快照,不設排程。
- 正式 `baseURL` 固定為 `https://harmonica.nycu.club/`,確保 canonical、Open Graph、RSS 與 sitemap 一致。
- DNS、Pages custom domain 與 HTTPS 已啟用;紀錄見 [docs/sdc-dns-request.md](docs/sdc-dns-request.md)。

## Hermes 公開問答

GitHub Pages 不保存模型金鑰，也不直接連完整 Bamboo Hermes。前端只呼叫 `hugo.toml` 中的 `params.websiteAgent.endpoint`；該 endpoint 是一個窄 facade，再轉送到 localhost-only 的獨立 `website` Hermes profile。

`website` profile 固定使用 `ai.kot.gg` 的 `gpt-5.6-luna`，關閉 reasoning 並限制 250 tokens；服務失效時才使用本機 `qwen3.5:9b` fallback。它沒有工具、MCP、內部記憶或寫入權限，上下文只來自本 repo 的公開頁面、公開 Google Sheet 與公開 fallback。前端使用 vendored Deep Chat Web Component，以短對話模式顯示回答與安全來源連結，不在瀏覽器保存對話。架構、安裝與停用方式見 [ops/website-agent/README.md](ops/website-agent/README.md)。

## 相關文件

- [RUNBOOK.md](RUNBOOK.md) — 幹部操作手冊(不需程式背景)
- [docs/google-setup.md](docs/google-setup.md) — 建立共用 Sheet/Calendar/Drive 與最小權限設定
- [docs/sdc-dns-request.md](docs/sdc-dns-request.md) — 給 SDC 的 DNS record 申請範本

## 授權與內容

程式碼以 MIT 授權(見 LICENSE)。網站文字與照片版權屬國立陽明交通大學竹韻口琴社,未經同意請勿轉載。

網站 logo、favicon 與首頁主視覺使用竹韻官方公開社群頭像,由臺灣口琴觀測站的公開來源快取取得;網站只做格式轉換與尺寸衍生,不重新繪製識別圖案。
