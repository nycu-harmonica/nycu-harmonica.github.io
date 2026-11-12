## 組 A
一句話總評：品牌主色與首頁內容到位，但深色外觀完全沒有作用，外部資料失敗時行事曆只剩空白框，維護說明與編年史還把內部系統用語直接寫給訪客看，整體像是功能完成、但還沒打磨的版本。
整體分數：6 / 10

| 項目 | 分數 | 證據（頁面／狀態 ID、尺寸、看到的事實） |
|---|---|---|
| 資訊層級 | 6.5 | home_desktop：Hero 有「國立陽明交通大學 竹韻口琴社」大標、「加入 Discord／社團行事曆」兩顆按鈕，主訊息清楚；但 Hero 下方直接接一段置中長文，沒有社課時間、地點、門檻這類一眼可掃的重點，也沒有新生的下一步引導。about_desktop 整頁是連續長文（沿革→支持→聯絡），到約 1130 px 才出現聯絡卡片，主次不夠分明。 |
| 字體排印 | 6 | home_desktop 的置中介紹段每行約 70 字、置中排列，不好閱讀；chronology-error_desktop 的時間軸日期（2026/09/09）與事件字級很小（約 13 px），來源連結更小；join_mobile 的大標「加入陽明交大竹韻口琴社」斷行後「社」單獨落在第二行；site-guide_desktop 正文混入等寬字 `chronology_events`、`YYYY/MM/DD`。 |
| 色彩 | 5 | 藍綠主色＋白色 Logo 有識別度（home_desktop Hero）；但 home-dark、about-dark、chronology-dark、site-guide-dark、portal-dark、join-dark、home-calendar-dark 的截圖與淺色版逐位元相同，深色外觀實際上不存在；反過來 discord_desktop 無論狀態都是深色，主要按鈕還是 Discord 綠（「前往伺服器」），和全站藍綠／白的按鈕系統不同。 |
| 間距與版面 | 6.5 | home_desktop 內容寬約 870 px 置中，1440 寬螢幕兩側大量留白，近期動態三欄卡片尚算整齊；screen-song_screen 標題下方到曲目清單之間有約 450 px 的空白，畫面重心空掉；portal-join_mobile 的「JOIN BAMBOO MELODY」字樣疊在背景 Google 表單的「年級或階段」文字上，可以讀出重疊。 |
| 一致性 | 5.5 | 主站頁首只有「首頁／編年史／關於我們」，Discord 頁頁首卻是「演出 Portal」；Discord 頁深色＋綠色按鈕，join 頁是沒有 Logo、沒有卡片的白底純文字，portal 和 screen 又各有一套；主站按鈕在 Hero 是白底方角（home_desktop），其他地方則是文字連結。 |
| 資訊密度 | 6 | home_desktop 首屏只看得到 Hero，介紹段落、動態、行事曆都在首屏以下；about_desktop 與 site-guide_desktop 文字很密，沒有摘要；home_mobile 首屏的 Logo 圖就佔了約 40% 高度。 |
| 導覽 | 5.5 | 頁首只有 3 項，沒有「行事曆」，也沒有常駐的入社／Discord 按鈕（home_desktop）；目前頁面只用淡色底塊標示（about_desktop「關於我們」）；Discord 頁只能回「演出 Portal」，沒有官網首頁的連結（discord_desktop）。 |
| 狀態與回饋 | 4.5 | home-error_desktop：行事曆區是約 520 px 高的純白空框，沒有任何錯誤說明或替代做法，只剩框外的小字「另開完整行事曆 →」；home-empty_desktop：嵌入的 Google 日曆只顯示「目前顯示 2027年11月12日以前的活動」，下面一大片空白；動態區在錯誤狀態只把小字從「即時資料」換成「上次同步資料」，不容易察覺；discord-error_desktop 用「— 位上線」的破折號頂替數字。about／chronology／site-guide 的五種狀態在手機版都完全相同（雜湊相同），沒有任何狀態提示。 |
| 響應式 | 6.5 | home_mobile 有漢堡選單、Hero 改為置中堆疊，基本合理；但「詢問竹韻」浮動按鈕蓋住第一張動態卡的標題（home_mobile 底部「復社紀念影片」被遮）；site-guide_mobile 的表格在 390 px 寬下直接縮成多欄，字擠；行事曆在手機只能靠嵌入的議程模式。 |
| 文案 | 4.5 | site-guide_desktop 出現「GitHub Pages」「Hugo 輸出的備援內容」「last-good 快照」「Repo 資料備援」「GitHub Actions」「chronology_events」；chronology-error_desktop 開頭寫「由…Google Sheet 的 chronology_events 分頁維護」「Hermes 研究整理」；about_desktop 寫「留在幹部／Hermes 工作區」；discord_desktop 用英文眉標「YOU'VE BEEN INVITED TO JOIN A SERVER」；screen 標題是「陽明交大竹韻口琴社演出投影畫面」，把頁面用途當成給觀眾看的標語。 |
| 無障礙 | 5.5 | screen-song_screen 右下角的鍵盤提示字約 9 px、灰色，在投影上幾乎讀不到；「正在演奏」的徽章極小（約 10 px）；chronology 時間軸的來源連結字很小；Discord 頁說明文字在深底上是低對比的灰字（discord-error_desktop「暫時無法取得即時人數…」）。 |
| 動畫與轉場 | 5 | portal_mobile 頂部有限時動態分段進度條，portal-join 的進度條推進到倒數第二格，能看出播放進度；但 home-loading 看不到載入骨架或載入中說明，discord-loading 也沒有明顯的骨架。線索有限，給保守分數。 |

要保留的優點：
- home_desktop 的藍綠 Hero 與大型白色 Logo，品牌識別強。
- 近期動態三欄卡片（圖片、日期、標題、來源平台），資訊完整。
- portal 系列的限時動態式播放器：進度條、分享鈕、全幅照片配粗體大標，在現場很有感染力。
- screen_screen 的 QR Code 大而清楚，並附上短網址 harmonica.nycu.club/p。
- about_desktop 的「想入社／捐贈樂器／演出邀約」三張分流聯絡卡。

最重要的五個問題（由嚴重到輕微）：
1. [色彩／狀態與回饋] [home-dark、about-dark、chronology-dark、site-guide-dark、portal-dark、join-dark、home-calendar-dark] [多者] 深色外觀的截圖與淺色版完全相同，深色模式沒有生效 —— 主要讀者多用手機、常開深色模式，一片亮白很刺眼，也表示主題系統沒有接上 —— 為所有頁面定義深色的色彩變數，並讓嵌入的行事曆跟著切換。
2. [狀態與回饋] [home-error、home-empty] [desktop | mobile] 行事曆讀取失敗時只剩空白框，空資料時則是 Google 原生的一行字配大片空白 —— 想看活動的新生會以為網站壞了，而且不知道下一步 —— 在框內顯示錯誤卡片，寫出固定社課時間，並放「到 Google 日曆開啟」「到 Discord 問」的按鈕；空資料時也寫出固定社課。
3. [文案] [site-guide、chronology、about、discord] [多者] 對外文案混入 GitHub Pages、Hugo、last-good、chronology_events、Hermes 工作區、英文 Discord 眉標等內部用語 —— 校外人士與老社員讀不懂，也顯得不專業 —— 改寫成一般讀者懂的說法，把技術細節移到 repo 文件。
4. [一致性／導覽] [discord、join、screen] [多者] Discord 頁（深色＋Discord 綠）、join 頁（無 Logo 的純文字）、主站三套各自為政；主站頁首沒有行事曆，也沒有入社／Discord 按鈕 —— 從 QR Code 或社群進站的人換頁時會失去品牌連續感，入社的轉換路徑也被埋掉 —— 統一按鈕與卡片元件，主站頁首加上常駐的「加入 Discord」。
5. [間距與版面／無障礙] [screen-song] [screen] 投影畫面中段大片空白，「正在演奏」徽章和右下鍵盤提示字非常小 —— 觀眾在遠處看不到現在演到哪一首 —— 把目前曲目做成大卡放在主視覺下方，鍵盤提示只給操作者看或在播放後隱藏。

## 組 B
一句話總評：參考組水準落差很大：Yale Glee Club 版面成熟、字體講究；CUMS 首頁大段空白、外嵌內容沒載入；銘傳口琴社是過時的入口網站樣板。整體只能算普通。
整體分數：5.5 / 10

| 項目 | 分數 | 證據（頁面／狀態 ID、尺寸、看到的事實） |
|---|---|---|
| 資訊層級 | 6 | ref-yale-glee-home_desktop：校名列→社名→7 個導覽→合唱照→介紹→Concerts 清單，主次清楚；ref-cums-home_desktop 只有一張磚牆圖、社名和「Upcoming Events」，下面約 600 px 空白；ref-mcu-harmonica-home_mobile 直接是一長串部落格貼文與登入框，看不出能做什麼。 |
| 字體排印 | 6.5 | Yale 用襯線社名搭配無襯線內文，活動標題用粗襯線、日期用小型大寫字母，非常講究（ref-yale-glee-home_desktop「NOVEMBER 13, 2026 7:30 PM」）；CUMS 是系統預設的 Arial 風格；銘傳在手機上字級極小，夾雜顏文字。 |
| 色彩 | 6 | Yale 以耶魯藍＋白，系統化但保守；CUMS 幾乎只有白底加深灰頁尾；銘傳是 2000 年代的灰色分頁樣板。三站都沒有深色外觀。 |
| 間距與版面 | 5.5 | Yale 內文只用到約 800 px，右側大片空白，但節奏工整；CUMS 首頁在輪播圖和推文區之間有約 600 px 空白；銘傳左側邊欄＋右側貼文的版型在手機上沒有重排，左右都很擠（ref-mcu-harmonica-home_mobile）。 |
| 一致性 | 6.5 | Yale 的 home、about、events 三頁頁首、按鈕（藍底白字方角、藍框「Add to Calendar ↗」）一致；CUMS 的 home 與 about 一致但很陽春；銘傳只有單頁。 |
| 資訊密度 | 5.5 | Yale 首屏有照片、介紹與導覽，密度適中；CUMS 首屏幾乎沒有內容；銘傳整頁塞滿貼文，資訊過載。 |
| 導覽 | 6.5 | Yale 有 7 個下拉選單，手機改成漢堡選單（ref-yale-glee-home_mobile）；CUMS 有 7 個下拉選單，目前頁以藍字標示；銘傳的分頁標籤很小，手機上很難點。 |
| 狀態與回饋 | 4 | ref-cums-home_desktop：「Tweets by @CamUniMusSoc」下面完全空白，Facebook 外掛重複出現兩次且第二個被截成「Cambridge Univ…」，外嵌失敗沒有任何替代內容；銘傳的貼文圖片顯示成破圖的替代文字。 |
| 響應式 | 5.5 | Yale 手機版合理（ref-yale-glee-home_mobile 單欄，行距舒適）；銘傳手機版只是把桌面版縮小，字小到看不清；CUMS 手機版尚可，但空白問題一樣存在。 |
| 文案 | 6.5 | Yale 的文案成熟，引用媒體評論；CUMS 文案很少；銘傳的貼文大量使用顏文字，「發表回應・請先登入」這類系統字直接外露。 |
| 無障礙 | 6 | Yale 對比良好、按鈕夠大；CUMS 頁尾的灰字「Privacy Policy」對比低；銘傳的手機點擊目標極小。 |
| 動畫與轉場 | 4.5 | CUMS 輪播有分頁點（ref-cums-home_desktop 圖下方的小白點）；其他站看不到載入或轉場線索，給保守分數。 |

要保留的優點：
- Yale 的襯線社名與活動標題、小型大寫字母日期，排印質感高。
- Yale 活動清單每筆都有「Add to Calendar ↗」，行動明確。
- Yale 的 Mission／Solidarity 用手風琴收合，縮短長頁。
- CUMS 頁尾整理了慈善登記號、地址與指揮名單，對校外人士很實用。

最重要的五個問題（由嚴重到輕微）：
1. [狀態與回饋] [ref-cums-home] [desktop | mobile] Twitter 外嵌沒載入，留下大片空白，Facebook 外掛又重複出現 —— 首頁看起來像壞掉 —— 移除外嵌，或在讀不到時改顯示靜態的最新消息。
2. [響應式] [ref-mcu-harmonica-home] [mobile] 桌面版直接縮放到手機，字級極小、點擊目標過小 —— 主要讀者是手機用戶 —— 改用響應式單欄版型。
3. [資訊層級] [ref-cums-home、ref-mcu-harmonica-home] [多者] 首頁沒有說明社團是什麼、怎麼參加 —— 新生找不到入口 —— 首屏放社團簡介與主要行動按鈕。
4. [色彩] [三站] [多者] 沒有深色外觀，CUMS 與銘傳的配色缺乏個性 —— 品牌記憶點弱 —— 建立品牌色系並支援深色。
5. [間距與版面] [ref-yale-glee-home] [desktop] 內文只用到約 800 px，1440 寬螢幕右側大片空白 —— 寬螢幕的空間沒有用上 —— 在右側放即將到來的演出或甄選資訊。

## 組 C
一句話總評：完成度高且成體系：頁首導覽、Hero 重點資訊、新手三步驟、各種載入／錯誤／空狀態、深色外觀、投影畫面的目前曲目都處理到位；剩下的是空狀態的行事曆留白、浮動按鈕遮擋，以及 Discord 和節目單子站的頁首與主站不一致。
整體分數：8 / 10

| 項目 | 分數 | 證據（頁面／狀態 ID、尺寸、看到的事實） |
|---|---|---|
| 資訊層級 | 8.5 | home_desktop：Hero 有「國立陽明交通大學／竹韻口琴社」、「1968 年創社，2026 年夏天復社，零基礎也能從第一個音開始」，還有「社課 每週二晚上／地點 學生活動中心 1F 聯誼廳／門檻 零基礎、不限校內」三格重點，以及右側「第一次來？」三步驟卡＋「加入 Discord」，一屏內就說清楚是什麼、怎麼加入；各區都有「關於竹韻／近期動態／行事曆」眉標＋大標。 |
| 字體排印 | 8 | site-guide_desktop 的內文行長控制在約 770 px、行高寬鬆，中英混排（Google 試算表、60 秒）間距自然；日期統一用 2026/09/09 格式（chronology-dark_mobile）；portal-song 的 Tradition／Matchmaker 大字有力。小缺點：home 的 Hero 重點格子字偏小，chronology-dark_mobile 的時間軸日期與內文字級差異不大。 |
| 色彩 | 8.5 | 藍綠主色＋琥珀色主要按鈕（加入 Discord）貫穿 home、join、discord、portal；深色外觀成立：site-guide-dark_desktop 的深藍底、淺藍標題、琥珀眉標，join-dark_mobile 的深色卡片，discord-dark_desktop 的深色卡片，都不是單純反色。 |
| 間距與版面 | 7.5 | home_desktop 內容寬約 1140 px，左文右卡片的兩欄善用寬螢幕；site-guide_desktop 左側目錄＋右側內文。缺點：home-error_desktop 的行事曆框約 540 px 高，錯誤卡下方約 280 px 空白；home-empty_desktop 的 Google 日曆只有一行字，下面大片空白；portal-song_mobile 照片下方有一段模糊的色塊過渡（約 750–1000 px），顯得髒。 |
| 一致性 | 7.5 | 主站頁首、眉標＋大標、圓角卡片、琥珀膠囊按鈕在 home／site-guide／chronology 一致；join_desktop 也用同一套 Logo、卡片與琥珀按鈕。但 discord_desktop 的頁首換成只有「官網首頁／演出節目單」的小型樣式，背景是霧面漸層；portal 是全黑的限時動態式介面，視覺語彙與主站差距大。 |
| 資訊密度 | 8 | home_desktop 首屏就有簡介、重點、新手步驟與 CTA；site-guide_mobile 把表格改成卡片，一屏約 3 張；略冗的是 home 的行事曆列表，每列都重複很長的英文地址。 |
| 導覽 | 8.5 | 頁首有「首頁／行事曆／編年史／關於我們」，加上常駐的琥珀色「加入 Discord」，目前頁用底線＋底色標示（home_desktop「首頁」）；site-guide 與 chronology 有「本頁內容」錨點目錄；頁尾分「網站／社群」兩欄。Discord 頁回得了「官網首頁」。 |
| 狀態與回饋 | 8 | home-loading_desktop：動態區顯示「正在讀取觀測站的最新動態…」，行事曆用骨架列＋「正在載入 Google 日曆…」；home-error_desktop：「暫時連不上臺灣口琴觀測站，先顯示 2026/08/14 同步的動態」，行事曆錯誤卡寫出「每週二晚上的定期社課照常…」並引導用下方按鈕；home-empty_desktop：「觀測站目前沒有新的公開貼文，先顯示…」；discord-loading_mobile 人數骨架＋「正在向 Discord 取得目前人數…」，discord-error_mobile 琥珀提示框「邀請連結照常可以使用」，discord-empty_mobile 隱藏人數並改成「伺服器已開放加入」。扣分：home-empty 的行事曆仍是 Google 原生空畫面。 |
| 響應式 | 8 | site-guide_mobile 把表格改成卡片；discord_mobile 兩顆按鈕改成上下滿寬；join-dark_mobile 的卡片置中合理。但「詢問竹韻」浮動按鈕蓋住正文（site-guide_mobile、chronology-dark_mobile 底部都壓在文字上）。 |
| 文案 | 8.5 | 文案口語又精準：「下一段旋律，換你加入」「先進 Discord 潛水看看也可以」「沒有自動跳轉？開啟入社表單」「人數由 Discord 即時提供，為約略值。」；site-guide 改寫成「你打開網頁時…不會出現只更新一半的畫面」。小瑕疵：site-guide 仍提到「版本歷史」，行事曆列中的英文地址是外部資料。 |
| 無障礙 | 7.5 | 按鈕大且對比足（琥珀底深字）；狀態圓點有搭配文字，不只靠顏色；screen-song_screen 的目前曲目同時用「正在演奏」文字、琥珀色條和放大卡片表示。扣分：home 的 Hero 重點格子標籤字小；portal-join 背景的模糊表單文字會干擾閱讀；看不到焦點樣式。 |
| 動畫與轉場 | 7.5 | portal 系列有分段進度條（portal-song 在第 1 格、portal-join 推進到倒數第二格），並提示「點按兩側或左右滑動」；行事曆與 Discord 人數有骨架載入；screen-song 能看出從「即將開始・共 4 首」切換到「正在演奏 02 風之丘」。動態本身無法驗證。 |

要保留的優點：
- home_desktop 的 Hero 三格重點（社課／地點／門檻）與「第一次來？」三步驟卡，新生一屏就知道怎麼開始。
- 完整的狀態設計：載入骨架、錯誤時「先顯示 2026/08/14 同步的動態」、Discord 錯誤的琥珀提示框，每種狀態都有說明與下一步。
- screen-song_screen：目前曲目做成大卡＋清單中標示「正在演奏」，加上大 QR Code 與短網址，投影效果好。
- 成立的深色外觀（site-guide-dark、discord-dark、join-dark），色彩不是單純反轉。
- site-guide_mobile 把表格改成卡片的手機版處理。
- 自然、有溫度的文案：「下一段旋律，換你加入」「先進 Discord 潛水看看也可以」。

最重要的五個問題（由嚴重到輕微）：
1. [狀態與回饋／間距與版面] [home-empty、home-error] [desktop | mobile] 空資料時行事曆是 Google 原生「目前顯示 2027年11月12日以前的活動」配大片空白；錯誤卡下方也留有約 280 px 空框 —— 想看活動的人會覺得沒東西或像壞掉 —— 空資料時改用自家的空狀態卡（寫出固定社課，並附「到 Discord 問」），錯誤時把框高度收到內容高度。
2. [響應式／無障礙] [site-guide、chronology-dark、home] [mobile] 「詢問竹韻」浮動按鈕蓋住正文最後一兩行 —— 手機讀者讀到一半被遮，還可能誤觸 —— 頁面底部加上足夠的安全留白，或在捲動時把按鈕縮成圖示。
3. [一致性] [discord、portal] [多者] Discord 頁的頁首、霧面漸層背景，以及節目單的黑底介面，都和主站的頁首、卡片語彙不同 —— 從 QR Code 或社群進站時品牌感會斷掉 —— 至少統一頁首的 Logo 與字型，按鈕與卡片的圓角、陰影共用主站的設計變數。
4. [間距與版面] [portal-song、portal-join] [mobile | desktop] 曲目照片下方有模糊的色塊過渡，入社頁的背景是模糊的 Google 表單截圖，文字像鬼影 —— 顯得粗糙，也干擾閱讀 —— 改用乾淨的漸層遮罩，入社頁換成品牌插圖或照片。
5. [資訊密度] [home、home-calendar] [desktop] 行事曆每一列都重複很長的英文地址「National Chiao Tung University Student Activity Center, No. 1001號…」並被截斷 —— 雜訊多，重要的活動名稱反而不顯眼 —— 在日曆源頭把地點改成短名「活動中心 1F 聯誼廳」。

```json
{"A": {"overall": 6, "scores": {"資訊層級": 6.5, "字體排印": 6, "色彩": 5, "間距與版面": 6.5, "一致性": 5.5, "資訊密度": 6, "導覽": 5.5, "狀態與回饋": 4.5, "響應式": 6.5, "文案": 4.5, "無障礙": 5.5, "動畫與轉場": 5}, "issues": ["深色外觀截圖與淺色版逐位元相同，深色模式未生效（home/about/chronology/site-guide/portal/join/home-calendar）", "home-error 行事曆只剩空白框、home-empty 只剩 Google 原生一行字，沒有說明與下一步", "site-guide/chronology/about/discord 外露 GitHub Pages、Hugo、last-good、chronology_events、Hermes、英文 Discord 眉標等內部用語", "Discord（深色＋綠鈕）、join（無 Logo 純文字）、主站三套樣式不一致；主站頁首缺行事曆與入社 CTA", "screen-song 中段大片空白，正在演奏徽章與鍵盤提示字過小"]}, "B": {"overall": 5.5, "scores": {"資訊層級": 6, "字體排印": 6.5, "色彩": 6, "間距與版面": 5.5, "一致性": 6.5, "資訊密度": 5.5, "導覽": 6.5, "狀態與回饋": 4, "響應式": 5.5, "文案": 6.5, "無障礙": 6, "動畫與轉場": 4.5}, "issues": ["CUMS 首頁 Twitter 外嵌沒載入，留下大片空白，Facebook 外掛重複出現", "銘傳口琴社手機版只是桌面縮放，字與點擊目標過小", "CUMS 與銘傳首頁沒有說明社團是什麼、怎麼參加", "三站都沒有深色外觀，CUMS 與銘傳配色缺乏個性", "Yale 內文只用到約 800 px，寬螢幕右側大片空白"]}, "C": {"overall": 8, "scores": {"資訊層級": 8.5, "字體排印": 8, "色彩": 8.5, "間距與版面": 7.5, "一致性": 7.5, "資訊密度": 8, "導覽": 8.5, "狀態與回饋": 8, "響應式": 8, "文案": 8.5, "無障礙": 7.5, "動畫與轉場": 7.5}, "issues": ["home-empty 行事曆是 Google 原生空畫面加大片空白，home-error 錯誤卡下方留空框", "手機版「詢問竹韻」浮動按鈕蓋住正文（site-guide、chronology-dark）", "Discord 頁與 portal 的頁首、背景、元件和主站不一致", "portal-song 照片下方有模糊色塊，portal-join 的模糊表單背景像鬼影", "行事曆每列重複冗長的英文地址並被截斷"]}}
```
