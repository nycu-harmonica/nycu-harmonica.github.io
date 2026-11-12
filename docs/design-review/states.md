# 設計評審截圖清單

每一輪都照這份清單截圖，ID 與 `tools/states.mjs` 一致。

| 尺寸 | 視窗 | 像素比 | 截圖高度 |
|---|---|---|---|
| `desktop` | 1440 × 900 | 1 | 從頁首或錨點起，最多 2400 px |
| `mobile` | 390 × 844（觸控） | 2 | 從頁首或錨點起，最多 1688 CSS px |
| `screen` | 1920 × 1080 | 1 | 只截一屏（僅 `/p/screen/`） |

固定條件：

- 瀏覽器時鐘固定在 2026-11-13 20:00（Asia/Taipei），語系 zh-TW，減少動態效果（`prefers-reduced-motion: reduce`）；字型以 Noto Sans TC 補齊。
- 外部資料全部攔截，回 `/tmp/bmhc-review/data` 的凍結 fixture（`tools/fixtures.mjs` 產生，一次 hill climb 只抓一次）：
  - Google Sheet gviz：由 repo 的 last-good CSV（`static/data/*.csv`）轉成 gviz 表格。
  - 觀測站 `/api/source/198.json`：由 `data/generated/observe_updates.json` 轉成 API 格式；貼文圖片快取一份。
  - Google Calendar 嵌入：2026-11-13 錄一次的 HAR 重播；空狀態重播同一份錄製，但把 events API 回應的 `items` 清空（畫面仍是 2026 年 11 月起、沒有活動）。
  - Discord 邀請 API：2026-11-13 抓一次（15 人上線、67 位成員）。
  - `/join/` 轉向的 Google 表單回 204，讓過場頁留在畫面上。
  - 其他對外請求一律中止；不讀寫任何正式資料來源。

## 資料狀態

`data` 一次套用到所有外部來源：

| 狀態 | 重現方式 |
|---|---|
| 有資料 | 回 fixture |
| `-loading` 載入中 | 外部請求永遠不回應；開頁 2.5 秒後截圖 |
| `-error` 錯誤 | Sheet 與行事曆連線被拒；觀測站、Discord 回 500 |
| `-empty` 空 | Sheet 只有表頭、觀測站 `items: []`、行事曆 events 為空、Discord 0 人且無描述 |

## 頁面與狀態

| ID | 頁面 | 狀態 | 尺寸 |
|---|---|---|---|
| `home` | `/` | 有資料 | desktop、mobile |
| `home-dark` | `/` | 深色外觀 | desktop、mobile |
| `home-loading` | `/` | 載入中 | desktop、mobile |
| `home-error` | `/` | 錯誤 | desktop、mobile |
| `home-empty` | `/` | 空 | desktop、mobile |
| `home-calendar` | `/` | 錨點 `#calendar` | desktop、mobile |
| `home-calendar-dark` | `/` | 錨點 `#calendar`、深色 | desktop、mobile |
| `home-menu-open` | `/` | 點 `#nav-toggle`，只截視窗 | mobile |
| `about` 系列（5 種） | `/about/` | 有資料／深色／載入中／錯誤／空 | desktop、mobile |
| `about-contact` | `/about/` | 錨點 `#join` | desktop、mobile |
| `chronology` 系列（5 種） | `/chronology/` | 有資料／深色／載入中／錯誤／空 | desktop、mobile |
| `chronology-timeline` | `/chronology/` | 錨點 `.chronology-timeline` | desktop、mobile |
| `site-guide` 系列（5 種） | `/site-guide/` | 有資料／深色／載入中／錯誤／空（外部資料只影響頁尾） | desktop、mobile |
| `join`、`join-dark` | `/join/` | 轉址過場，只截視窗 | desktop、mobile |
| `discord` 系列（5 種） | `/discord/` | 有資料／深色／載入中／錯誤／空 | desktop、mobile |
| `portal` | `/p/` | 第一則限時動態，只截視窗 | desktop、mobile |
| `portal-dark` | `/p/` | 深色外觀 | desktop、mobile |
| `portal-song` | `/p/` | 點「下一則」到第 1 首曲目 | desktop、mobile |
| `portal-join` | `/p/?story=N` | 入社那一則 | desktop、mobile |
| `screen` | `/p/screen/` | 投影，未標示曲目 | screen |
| `screen-song` | `/p/screen/?song=2` | 標示第 2 首 | screen |

不適用的狀態：`/join/`、`/p/`、`/p/screen/` 不讀外部資料（節目資料在 `data/portal.yaml`，建置時寫進 HTML），所以沒有載入中、錯誤、空狀態；`/join/` 本身只是轉址過場。

## 參考對手

第一輪截一次，之後每輪重用同一組檔案（desktop、mobile）：

| ID | 網址 | 對應的我方頁面 |
|---|---|---|
| `ref-yale-glee-home` | https://gleeclub.yale.edu/ | 首頁 |
| `ref-yale-glee-about` | https://gleeclub.yale.edu/about | 關於 |
| `ref-yale-glee-events` | https://gleeclub.yale.edu/events | 行事曆 |
| `ref-cums-home` | https://cums.org.uk/ | 首頁 |
| `ref-cums-about` | https://cums.org.uk/about | 關於 |
| `ref-mcu-harmonica-home` | http://club.mcu.edu.tw/hc/zh-hant | 同類：大學口琴社官網 |

## 重現

```bash
# 1. 凍結外部資料（每次 hill climb 只做一次）
node docs/design-review/tools/fixtures.mjs . /tmp/bmhc-review/data
# 2. 建置並啟動唯讀預覽（load1 > 10 會先等）
docs/design-review/tools/build.sh baseline origin/main 8411
docs/design-review/tools/build.sh new "$PWD" 8412
# 3. 截圖（tools/node_modules 指向裝有 playwright 的目錄），一次只開一個瀏覽器
node docs/design-review/tools/capture.mjs site http://127.0.0.1:8411 /tmp/bmhc-review/sets/baseline
node docs/design-review/tools/capture.mjs site http://127.0.0.1:8412 /tmp/bmhc-review/sets/rN
node docs/design-review/tools/capture.mjs references /tmp/bmhc-review/sets/reference
# 4. 組一輪盲測
python3 docs/design-review/tools/make_round.py N /tmp/bmhc-review/sets/rN
```

## Fixture 修正紀錄

- 第 1 輪後：空行事曆原本只是 HTML，事件請求不在 HAR 內而變成 Google 錯誤畫面；改錄 2099 年空範圍的完整 HAR。基準 `home-empty` 重拍。
- 第 4 輪後：2099 年的畫面標題會出現「2099」，不像真實的空狀態；改成重播正常錄製並清空 events。基準 `home-empty` 重拍。
- `/join/`：原本以 204 擋表單轉址會讓頁面卡住；改成只移除 HTML 裡的轉址指令，畫面不變。
