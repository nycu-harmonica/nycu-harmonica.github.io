# 竹夢初聲｜交大二餐（女二舍餐廳）電子佈告欄素材

規格依餐廳佈告欄公告：橫式 1920×1080、120 dpi、JPG，檔名為「推播截止日（民國）＋活動名稱」。四張推播到 115/12/08（最後一場）。

| 順序 | 檔案 | 內容 |
|---|---|---|
| 1 | `jpg/1151208竹夢初聲01主視覺.jpg` | 同 /1151/ 首屏：標題、兩社、免費入場、兩社 logo |
| 2 | `jpg/1151208竹夢初聲02三場演出.jpg` | 三場日期、場地、時間 |
| 3 | `jpg/1151208竹夢初聲03演奏曲目.jpg` | 曲目文字雲（字越大＝越多場演出） |
| 4 | `jpg/1151208竹夢初聲04節目資訊QR.jpg` | QR Code → https://harmonica.nycu.club/1151/ ，共同主辦兩社 logo 與 IG |

## 重新產生

`board.html` 以 1280×720 CSS 排版，用 Chrome headless 以 1.5 倍輸出：

```sh
C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$C" --headless=new --hide-scrollbars --allow-file-access-from-files \
  --window-size=1280,720 --force-device-scale-factor=1.5 --virtual-time-budget=10000 \
  --screenshot="$PWD/out2/1.png" "file://$PWD/board.html#s1"   # s1–s4
sips -s format jpeg -s dpiWidth 120 -s dpiHeight 120 out2/1.png --out jpg/<檔名>.jpg
```

## 申請信

- 收件人：wanglangben@yahoo.com.tw
- 主旨：申請女二舍餐廳電子佈告欄
- 附件：上方四張 JPG（以附加檔案寄出，勿貼在信件內文）
- 內文需附申請者姓名、單位、電話
