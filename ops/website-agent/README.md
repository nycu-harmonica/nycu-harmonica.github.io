# 竹韻官網 Hermes 問答服務

官網仍是完整的 Hugo + GitHub Pages 靜態網站。只有訪客送出問題時，瀏覽器才呼叫一個獨立 HTTPS endpoint：

```text
GitHub Pages -> public facade /ask -> localhost Hermes API -> local AI gateway (127.0.0.1:8317) `sky-fast`
```

安全邊界：

- `website` 是獨立 Hermes profile，不共用 Bamboo Discord session 或工具。
- 主模型是本機 AI gateway（CLIProxyAPI，`127.0.0.1:8317`）的 `sky-fast` 別名，使用 `custom:ai-gateway-sky-fast` 與 250-token 輸出上限；別名對應的實際模型由 `~/Projects/ai-gateway/model-policy.json` 管理。Hermes profile `.env` 需要 `AI_GATEWAY_API_KEY`（`~/.config/ai-gateway/clients.env` 的 `harmonica` client key，不進 repo）。上限同時放在 provider 的 `extra_body.max_tokens`，因為目前 Hermes gateway 不會轉傳 facade 的 `max_tokens`。
- 新版 Hermes 要求至少 64,000-token context，profile 設為 65,536。本機不使用任何本地模型（2026-11-20 起移除原本的 Ollama `qwen3.5:9b` 路線，它在主機負載高時會逾時）。
- facade 每次請求都送新的 `X-Hermes-Session-Id`。否則 Hermes 依訊息內容推導 session，相同問題的訪客會共用 session，一次失敗就讓該 session 被暫停（HTTP 409），之後同一句問題永遠失敗。
- `ai-kot-gg-luna` 因既有憑證回傳 401 而保留但停用，`fallback_providers` 為空；不再重試該遠端或取得其他 profile 的憑證。gateway 失敗仍回傳 HTTP 503 `agent_unavailable`，公開資料直接回答仍可使用。
- Hermes API 只監聽 `127.0.0.1:8643`，bearer key 不會傳給瀏覽器。
- 公開 facade 只監聽 `127.0.0.1:8788`，只提供 `POST /ask`、`GET /challenge` 與 `GET /health`。
- facade 只讀官網 repo 中的公開頁面、公開 Google Sheet 及 repo last-good fallback。
- facade 也會讀取公開 Google Calendar 的 ICS，展開重複活動與例外，只保留活動名稱、日期時間與地點；不把活動描述或行政細節送進模型。
- 不讀 `shared/`、`private/`、Discord、Gmail、Drive、Hermes 記憶或任何 OAuth/token 檔案。
- 記憶與使用者偏好注入明確停用；`no_mcp`、停用工具清單、standalone gateway 與單一並行請求維持隔離。provider request/stale timeout 為 55 秒，停用自動復原循環，facade 的 75 秒等待上限不變。
- 每題最多 500 字、回答最多 250 tokens；單 IP 與全站每日都有上限。
- 會呼叫模型的問題需要 ALTCHA 相容的 proof-of-work：瀏覽器開啟問答時先向 `GET /challenge` 取得 HMAC 簽章的題目並在背景解題，送出時把結果放在 `altcha` 欄位。每個解答只能用一次、10 分鐘過期；簽章金鑰只存在記憶體，服務重啟後舊題目失效，前端會自動重拿一次。直接回答的常見問題不需要。這只提高大量自動請求的成本，擋不住刻意的攻擊者，真正的額度上限是下一項。
- 每日 token 預算（`DAILY_TOKEN_BUDGET`，預設 500,000，依臺北時間換日）。用量以 Hermes 回傳的 `usage.total_tokens` 累計，沒有回傳就以送出字數估算；逾時的請求也照估算扣，連不上或被拒的請求不扣。累計值寫在 runtime 目錄的 `daily-usage.json`，重啟不歸零。用完後回傳 HTTP 429 `budget_exhausted`，直接回答的常見問題仍可使用。
- 前端使用 vendored Deep Chat 2.5.0 Web Component（MIT），只在訪客開啟問答時載入；最多帶入最近 4 則短訊息，不使用瀏覽器儲存。
- 「如何加入／社課時間地點／近期活動」由公開資料直接產生回答，不呼叫模型；其他問題才轉給 Hermes，並帶入相同的近期公開活動摘要。

## 安裝與啟動

需求：**Python >= 3.11**（使用標準庫 `tomllib`）、同一 Python 環境中的 **python-dateutil**、Hermes，以及本機 AI gateway 的 `harmonica` client key（`~/.config/ai-gateway/clients.env`；沒有的話先加一行並執行 `~/Projects/ai-gateway/apply.py`）。Installer 會把它寫進 profile `.env` 的 `AI_GATEWAY_API_KEY`。建議使用已有 dateutil 的 Hermes venv；macOS 內建 `python3` 可能仍是 3.9，不能用來執行本服務。Installer 會在修改任何檔案前檢查版本、依賴與 gateway key。

```sh
"$HOME/.hermes/bamboo-runtime/bin/python" ops/website-agent/install.py
curl -fsS http://127.0.0.1:8788/health
```

安裝腳本會：

1. 把 `hermes-config.yaml` 與 `SOUL.md` 安裝到 `~/.hermes/profiles/website/`。
2. 產生只存在本機 profile 的隨機 API key。
3. 移除舊的 `club.nycu.harmonica.website-ollama` 服務（若仍存在），接著啟動專用的 `club.nycu.harmonica.website-hermes` gateway。它刻意不使用 Hermes 的 secondary-profile multiplexer，讓 localhost API 可以獨立綁定 `8643`。
4. 把 façade 程式與其必要的公開頁面、Sheet 設定、公開 fallback 複製到隔離 profile 的 runtime snapshot；這是為了避開 macOS 對 LaunchAgent 讀取 `~/Documents` 的背景權限限制，不包含 `shared/`、`private/` 或憑證。
5. 安裝 `club.nycu.harmonica.website-agent` launchd 服務。網站程式或公開靜態文字變更後需重跑 installer；Google Sheet 內容仍由 façade 即時讀取，不需重裝。

Hermes backend 與 facade 都使用執行 installer 時的 Python 與該環境的 Hermes 安裝，不再固定到舊 core 目錄。LaunchAgent 保留 venv Python 路徑，以便服務也能載入相同依賴。`--no-start` 仍會更新本機檔案與設定，只是不啟動服務；它不是 dry run。

### 公開行事曆與社課回答

- 查詢範圍為現在起 180 天，包含仍在進行中的活動；最多保留 128 筆，近期活動摘要最多顯示 8 筆。
- 支援每日、每週、每月、每年 `RRULE`（含 `COUNT` / `UNTIL`）、`RDATE`、`EXDATE`、依 `UID` / `RECURRENCE-ID` 修改或取消的單次活動，以及整個系列取消。依原始 `TZID` 展開後轉為臺北時間，保留全天活動。
- 高於每日頻率、`BYHOUR` / `BYMINUTE` / `BYSECOND`、`EXRULE`、`DURATION`、`RDATE;VALUE=PERIOD`、`RANGE=THISANDFUTURE` 等未支援格式會略過該系列並記錄警告，不沿用可能失效的時間。
- 社課回答列出查詢結果中標題含「社課」的近期日期、時間與地點，不推論永久固定課表。查無資料、缺少地點或無法讀取 Calendar 時，會保留相應的不確定性並提供公開來源與聯絡入口。
- Calendar 讀取失敗後不把上次快取的活動當成目前確認的安排；網站內嵌公開行事曆仍可直接查閱。

## 本機測試

```sh
"$HOME/.hermes/bamboo-runtime/bin/python" -B -m unittest discover -s ops/website-agent -p 'test_*.py'
curl -sS -X POST http://127.0.0.1:8788/ask \
  -H 'Origin: http://127.0.0.1:1313' \
  -H 'Content-Type: application/json' \
  --data '{"question":"我要怎麼加入竹韻？"}'
```

健康檢查與入社／社課直接回答不代表模型可用；還要以 plist `ALLOWED_ORIGINS` 中的 Origin 呼叫 `/ask`，例如問「請用一句話說明竹韻這個社團的特色。」並確認收到實質回答。新版 Hermes 可能以 HTTP 200 搭配 `finish_reason: error` 或 `hermes.failed` 回傳失敗；facade 會將其轉成一般訪客可讀的 HTTP 503，不把 provider 診斷文字當成回答。

## 公開入口

目前採 Tailscale Funnel，只把 facade 的 `8788` port 對外，不公開 Hermes `8643`：

```sh
tailscale funnel --bg --https=8443 8788
tailscale funnel status
```

這台主機的 `443` 已由既有 Caddy 使用，因此 Funnel 採 Tailscale 支援的 `8443` HTTPS port。官網的 endpoint 設於 `hugo.toml` 的 `params.websiteAgent.endpoint`。若遷移到社團持有的 VPS 或 Cloudflare Tunnel，只需更換這個 URL；GitHub Pages 架構不需改變。

## 停用

先把 `hugo.toml` 的 `params.websiteAgent.enabled` 改成 `false` 並重新部署，再停服務：

```sh
tailscale funnel reset
launchctl bootout "gui/$(id -u)/club.nycu.harmonica.website-agent"
launchctl bootout "gui/$(id -u)/club.nycu.harmonica.website-hermes"
```
