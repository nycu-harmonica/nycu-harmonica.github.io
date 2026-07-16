#!/usr/bin/env python3
"""【預留】從 Google Shared Drive 相簿資料夾下載照片到 content/gallery/。

現況:社團尚未建立 Shared Drive 與 service account,此腳本為介面預留。
      執行時若未設定 GDRIVE_SA_KEY,只會印出設定指引並正常結束(no-op),
      不影響任何 CI 流程。

未來啟用步驟(詳見 docs/google-setup.md):
  1. 建立 Google Cloud 專案與 service account(不需任何專案角色)
  2. 建立社團 Shared Drive,將 service account 的 email 以「檢視者」加入
  3. 將核准的 slug -> 精確子資料夾 ID 映射存為 Actions secret:GALLERY_FOLDER_MAP
  4. 將 service account 金鑰 JSON 存為 GitHub Actions secret:GDRIVE_SA_KEY
  5. 在 sync-data.yml 加一個步驟呼叫本腳本,並補完下方 TODO 實作

預定行為:
  python3 scripts/fetch_gallery_drive.py [--only <slug>] [--dry-run]
  - 讀取 GALLERY_FOLDER_MAP 中核准的相簿 slug 與精確子資料夾 ID
  - 以 Drive API(service account,唯讀 scope)列出資料夾內圖片
  - 僅下載 content/gallery/<slug>/ 內尚無同名檔案者
  - 長邊 > 2000px 的照片縮圖後存檔(WebP),交由 git diff 決定是否 commit
"""

import json
import os
import sys


def main() -> int:
    key = os.environ.get("GDRIVE_SA_KEY", "")
    folder_map_text = os.environ.get("GALLERY_FOLDER_MAP", "")
    if not key or not folder_map_text:
        print("[info] 未設定 GDRIVE_SA_KEY/GALLERY_FOLDER_MAP,略過 Shared Drive 相簿同步(目前為預留功能)。")
        print("[info] 啟用方式見 docs/google-setup.md 的「相簿自動同步(未來)」一節。")
        return 0

    try:
        folder_map = json.loads(folder_map_text)
    except json.JSONDecodeError:
        print("[error] GALLERY_FOLDER_MAP 必須是 JSON object。", file=sys.stderr)
        return 1
    if not isinstance(folder_map, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in folder_map.items()):
        print("[error] GALLERY_FOLDER_MAP 必須是 slug 到 folder ID 的字串映射。", file=sys.stderr)
        return 1
    print(f"[info] 已核准自動同步的相簿:{sorted(folder_map)}")

    # TODO(未來):實作 Drive API 下載。啟用前請先確認:
    #   - 使用唯讀 scope:https://www.googleapis.com/auth/drive.readonly
    #   - 僅存取 GALLERY_FOLDER_MAP 列出的資料夾 id,不掃描其他內容
    print("[error] Drive 下載尚未實作(此腳本目前為介面預留)。", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
