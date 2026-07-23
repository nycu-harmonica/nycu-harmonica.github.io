# 竹韻官網 Hermes 問答服務

官網仍是完整的 Hugo + GitHub Pages 靜態網站。只有訪客送出問題時，瀏覽器才呼叫一個獨立 HTTPS endpoint：

```text
GitHub Pages -> public facade /ask -> localhost Hermes API -> ai.kot.gg gpt-5.6-luna
                                                        `-> local Qwen fallback
```

安全邊界：

- `website` 是獨立 Hermes profile，不共用 Bamboo Discord session 或工具。
- 主模型是 `gpt-5.6-luna`，固定 `reasoning_effort: none` 與 250-token 輸出上限；`ai.kot.gg` 無法使用時才回退本機 `qwen3.5:9b`。
- Hermes API 只監聽 `127.0.0.1:8643`，bearer key 不會傳給瀏覽器。
- 公開 facade 只監聽 `127.0.0.1:8788`，只提供 `POST /ask` 與 `GET /health`。
- facade 只讀官網 repo 中的公開頁面、公開 Google Sheet 及 repo last-good fallback。
- 不讀 `shared/`、`private/`、Discord、Gmail、Drive、Hermes 記憶或任何 OAuth/token 檔案。
- 每題最多 500 字、回答最多 250 tokens；單 IP 與全站每日都有上限。
- 前端使用 vendored Deep Chat 2.5.0 Web Component（MIT），只在訪客開啟問答時載入；最多帶入最近 4 則短訊息，不使用瀏覽器儲存。

## 安裝與啟動

需求：Hermes、Ollama、本機 `qwen3.5:9b`，以及 Bamboo profile 既有的 `AI_KOT_GG_API_KEY`。

```sh
python3 ops/website-agent/install.py
curl -fsS http://127.0.0.1:8788/health
```

安裝腳本會：

1. 把 `hermes-config.yaml` 與 `SOUL.md` 安裝到 `~/.hermes/profiles/website/`。
2. 產生只存在本機 profile 的隨機 API key。
3. 安裝並啟動專用的 `club.nycu.harmonica.website-hermes` gateway。它刻意不使用 Hermes 的 secondary-profile multiplexer，讓 localhost API 可以獨立綁定 `8643`。
4. 把 façade 程式與其必要的公開頁面、Sheet 設定、公開 fallback 複製到隔離 profile 的 runtime snapshot；這是為了避開 macOS 對 LaunchAgent 讀取 `~/Documents` 的背景權限限制，不包含 `shared/`、`private/` 或憑證。
5. 安裝 `club.nycu.harmonica.website-agent` launchd 服務。網站程式或公開靜態文字變更後需重跑 installer；Google Sheet 內容仍由 façade 即時讀取，不需重裝。

## 本機測試

```sh
python3 -m unittest discover -s ops/website-agent -p 'test_*.py'
curl -sS -X POST http://127.0.0.1:8788/ask \
  -H 'Origin: http://127.0.0.1:1313' \
  -H 'Content-Type: application/json' \
  --data '{"question":"我要怎麼加入竹韻？"}'
```

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
