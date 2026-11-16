# concert-serif.woff2

`/1151/` 標題用的 Noto Serif TC Bold（SIL OFL 1.1）子集，只含頁面上以襯線字顯示的字：
h1／h2、場次名稱、場次標籤、主辦社團名稱，以及製作名單（Credits）的標題與姓名。

新增字時，保留舊子集的所有字並加入新字，重新產生：

```sh
curl -fsSL -o /tmp/NotoSerifTC-Bold.otf \
  https://github.com/notofonts/noto-cjk/raw/main/Serif/SubsetOTF/TC/NotoSerifTC-Bold.otf
uv run --with fonttools --with brotli python -c "
from fontTools.ttLib import TTFont
cm = TTFont('static/fonts/1151/concert-serif.woff2').getBestCmap()
open('/tmp/subset-text.txt', 'w').write(''.join(map(chr, cm)) + '新增的字')"
uv run --with fonttools --with brotli pyftsubset /tmp/NotoSerifTC-Bold.otf \
  --text-file=/tmp/subset-text.txt --flavor=woff2 \
  --output-file=static/fonts/1151/concert-serif.woff2
```
