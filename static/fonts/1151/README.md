# /1151/ 字型子集

兩個檔案都只含頁面實際用到的字（皆為 SIL OFL 1.1）：

| 檔案 | 來源字型 | 用途 |
|---|---|---|
| `concert-title.woff2` | Noto Serif TC Black | 主標「竹夢初聲」，照海報定稿 |
| `concert-serif.woff2` | Noto Serif TC Bold | 副標、各區標題、社團名稱、製作名單姓名 |

改了 `data/concert1151.yaml`（新場次、名單、贊助單位）之後，執行腳本重新產生；它會保留舊子集的字並補上新的字：

```sh
uv run --with fonttools --with brotli --with pyyaml \
  python scripts/subset_concert_fonts.py --sources /path/to/font/dir
```

來源字型下載位置寫在 `scripts/subset_concert_fonts.py` 開頭。
