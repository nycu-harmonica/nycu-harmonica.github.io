## 組 A
一句話總評：參考組三個外部社團網站水準落差很大：Yale Glee Club 版型乾淨，CUMS 與銘傳口琴社則有大片空白、過時版型與系統文字外露，整體只能算可用偏弱。
整體分數：4.5 / 10

| 項目 | 分數 | 證據（頁面／狀態 ID、尺寸、看到的事實） |
|---|---|---|
| 資訊層級 | 5 | ref-yale-glee-home desktop：照片主視覺下接社團介紹，再接 Concerts 清單，主次清楚；ref-cums-home desktop：只有磚牆主視覺、標題與「Upcoming Events」一顆按鈕，下方約 600px 空白，看不出社團能做什麼；ref-mcu-harmonica-home desktop：首屏被左欄主選單與登入表單佔掉一半，主要內容是貼文流，入社資訊不在首屏。 |
| 字體排印 | 5.5 | ref-yale-glee-events desktop：襯線大標配無襯線內文，日期用全大寫字距排，層級分明；ref-mcu-harmonica-home desktop：內文約 11–12px 灰字，夾雜大量顏文字，行距鬆散不一；ref-cums-home desktop：主視覺白字直接壓在磚牆照片上，只靠陰影撐對比。 |
| 色彩 | 5 | Yale 以深藍單色加白底成系統；CUMS 只有灰白加黑色頁尾，沒有品牌色；銘傳是灰底、五線譜橫幅與綠色黑板圖示混搭，沒有統一配色。三站都沒有深色外觀可評。 |
| 間距與版面 | 4 | ref-cums-home desktop：主視覺下方到「Tweets by @CamUniMusSoc」之間約 600px 空白，而且 Twitter 與 Facebook 嵌入重複出現兩次；ref-yale-glee-home desktop：內文只佔左側約 800px，右側整欄空白；ref-mcu-harmonica-home desktop：固定 960px 版心，兩側大片灰色漸層。 |
| 一致性 | 5 | Yale 的首頁與 events 頁共用同一套頁首、按鈕（深藍框線的 Add to Calendar）與頁尾，一致性好；CUMS 的 about 與 home 使用同一套 WordPress 樣板；銘傳的頁籤按鈕、側欄小工具與貼文樣式各自為政。 |
| 資訊密度 | 4.5 | ref-cums-home desktop：首屏幾乎沒有有用資訊；ref-mcu-harmonica-home desktop：每則貼文都重複「語言 Chinese, Traditional」與「發表回應前，請先登入」，雜訊多；Yale 的 events 頁密度適中。 |
| 導覽 | 5.5 | Yale 有校級連結列加社團主選單，結構清楚，但看不出目前所在頁；CUMS 的 Home 用藍字標示目前位置；銘傳同時有頁籤列與左欄主選單，兩套重複。 |
| 狀態與回饋 | 3.5 | ref-cums-home desktop：社群嵌入沒載入，只剩「Tweets by @CamUniMusSoc」文字和空白；ref-mcu-harmonica-home desktop：圖片破圖，只顯示替代文字「可能是一或多人、大家站著和室內的圖像」。參考組沒有載入、讀取失敗、空資料或深色截圖可供比較。 |
| 響應式 | 5 | Yale 與 CUMS 的 mobile 截圖都改成單欄，可以閱讀；銘傳的 mobile 基本上是桌面版的直排，側欄與登入表單照搬，效率低。 |
| 文案 | 4 | ref-yale-glee-events desktop：「Use the Calendar List Block to add a dynamic events feed to your site…」是 CMS 範本的說明文字，被當成正式內容公開；銘傳貼文以顏文字與口語為主，資訊性弱。 |
| 無障礙 | 5 | Yale 的文字對比足、按鈕大；CUMS 的主視覺白字壓在照片上；銘傳的灰色小字對比不足、點擊目標很小，登入欄位只有約 120×16px。 |
| 動畫與轉場 | 3 | 靜態截圖線索很少：CUMS 主視覺有輪播圓點，是唯一的動態線索；其他兩站看不到載入骨架或狀態切換，給保守分數。 |

要保留的優點：
- ref-yale-glee-home／events：襯線大標配全大寫日期的活動清單排版，值得竹韻的行事曆或節目單借鏡。
- ref-yale-glee-events：每個活動都有一致的「Add to Calendar」次要按鈕，行動明確。
- ref-cums-home：Home 以藍字標示目前頁，簡單但有效。
- ref-cums-home 頁尾：把組織資訊（註冊編號、地址、幹部）集中在頁尾，校外人士容易查。

最重要的五個問題（由嚴重到輕微）：
1. [狀態與回饋] [ref-cums-home] [desktop] 社群嵌入讀取失敗後只留標題與約 600px 空白，而且重複兩次 —— 首頁像壞掉一樣 —— 外部嵌入要有讀取失敗時的替代內容，並刪掉重複區塊。
2. [文案] [ref-yale-glee-events] [desktop] CMS 範本說明「Use the Calendar List Block…」直接公開 —— 系統文字外露，損害專業感 —— 換成給觀眾看的活動說明。
3. [資訊層級] [ref-mcu-harmonica-home] [desktop、mobile] 首屏被選單與登入表單佔據，看不到社課時間與入社方式 —— 新生找不到行動入口 —— 把入社與社課資訊放到首屏。
4. [狀態與回饋] [ref-mcu-harmonica-home] [desktop] 圖片破圖只剩替代文字 —— 內容看起來沒人維護 —— 修復圖片來源，或改用站內圖片。
5. [間距與版面] [ref-yale-glee-home] [desktop] 內文只用左側約 800px，右欄全空 —— 1440 寬螢幕浪費空間 —— 右欄可以放近期演出或試唱資訊。

## 組 B
一句話總評：竹韻官網有了品牌色與基本頁面，但深色外觀完全沒有作用，載入中與讀取失敗時大多是空白或系統字，文案充滿 GitHub、Hugo、Repo、Hermes、chronology_events 等內部術語，入社轉址頁也幾乎沒有設計。
整體分數：5.5 / 10

| 項目 | 分數 | 證據（頁面／狀態 ID、尺寸、看到的事實） |
|---|---|---|
| 資訊層級 | 6 | home desktop：主視覺有校名、社名、標語與「加入 Discord／社團行事曆」兩顆按鈕，身分清楚；但社課時間、地點與零基礎這些新生最需要的資訊埋在下方一段置中的長文裡。chronology desktop／mobile：時間軸之前有四段方法論長文，mobile 要捲超過 1688px 才看得到第一個事件。 |
| 字體排印 | 5.5 | home desktop／mobile：首頁介紹是約 10 行的置中段落，行尾參差難讀；chronology desktop：內文夾雜 `chronology_events`、`YYYY/MM/DD` 等等寬程式字；時間軸的日期只有約 11px 粗體，事件文字約 13px，偏小；join mobile：大標「加入陽明交大竹韻口琴社」斷行後只剩「社」一字在第二行。 |
| 色彩 | 4.5 | 淺色以藍綠色加白底，品牌一致；但 home-dark、about-dark、chronology-dark、site-guide-dark、join-dark、portal-dark、home-calendar-dark 與淺色版逐像素相同，深色外觀不存在。discord desktop 反過來，淺色狀態也是深藍底，主按鈕用 Discord 綠，和官網其他頁不同色系。 |
| 間距與版面 | 5.5 | about／site-guide desktop：內容寬約 1020px，左對齊、間距一致；home-loading／home-error desktop：行事曆位置是約 520px 高的空白框；screen screen：主標下方到曲目清單之間約 450px 的空白中段；portal-join mobile：背景 Google 表單的「年級或階段 *」與單選圈和「JOIN BAMBOO MELODY」等字疊在一起。 |
| 一致性 | 4.5 | 官網用白底按鈕（hero 白色實心）與深金色按鈕（「想學口琴嗎？」區塊）兩套 CTA 樣式；discord 頁改用綠色主按鈕與英文眉標「YOU'VE BEEN INVITED TO JOIN A SERVER」；join 頁沒有社徽、卡片與按鈕，只有一行藍字連結；screen 與 portal 的眉標多為英文（WELCOME TO OUR PERFORMANCE、TODAY'S PROGRAM），和官網的中文調性不同。 |
| 資訊密度 | 5.5 | home desktop：近期動態三張卡片加 Google 行事曆，一屏資訊量尚可；chronology、site-guide desktop：大段方法論與工程說明擠在使用者需要的內容之前；about desktop：聯絡區的三張情境卡（入社／捐贈／演出邀約）密度好。 |
| 導覽 | 5 | home desktop：頁首只有「首頁／編年史／關於我們」三項，沒有行事曆與 Discord 入口，但有目前頁的底色標示；home-menu-open mobile：展開後只有三個純文字連結，沒有主要行動按鈕，浮動「詢問竹韻」還壓在主視覺的「社團行事曆」按鈕上；discord desktop 右上只有「演出 Portal」，沒有回官網的連結。 |
| 狀態與回饋 | 3.5 | home-loading／home-error desktop：行事曆是完全空白的白框，沒有載入提示，也沒有讀取失敗的說明或下一步；home-empty desktop：只有 Google 自己的「目前顯示 2027年11月12日以前的活動」；home／about／chronology 的 mobile 五種狀態逐像素相同，看不出任何狀態差異；chronology-error desktop：時間軸排序悄悄改變，沒有任何提示；discord-loading mobile 顯示「讀取中 位上線」，語句不通；discord-error desktop 以「— 位上線」加小字說明，是少數處理得體的狀態。 |
| 響應式 | 5.5 | home mobile、about-contact mobile：單欄重排合理，聯絡卡片好點；home-calendar mobile：Google 嵌入改成議程模式，可用，但標題被截成「活動中心一樓聯…」；home mobile：浮動「詢問竹韻」按鈕蓋住第一張動態卡的標題；home-calendar mobile：頁尾「Google Sheet 即時讀取：2026/11/13 20:00:0…」被浮動按鈕截斷。 |
| 文案 | 3.5 | site-guide desktop：「本網站為 GitHub Pages 上的靜態網站」「不需要等待 GitHub Actions 或重新部署」「last-good 快照」「Hugo 輸出的備援內容」「Repo 資料備援」；about desktop：「留在幹部／Hermes 工作區」；chronology desktop：「2026/08/12 的 Hermes 研究整理」「Google Sheet 的 chronology_events 分頁維護」；頁尾「Google Sheet 即時讀取：…（Asia/Taipei）」、about-error 頁尾「Repo 資料備援：…」；screen 主標是「陽明交大竹韻口琴社演出投影畫面」，等於把頁面用途寫給觀眾看。 |
| 無障礙 | 5.5 | 主要文字對比足；chronology desktop 的來源連結「↗ Club Portal」約 10px 灰字，點擊範圍很小；screen-song screen：正在演奏只靠一個約 50×14px 的「正在演奏」小標籤與底色，投影距離難以辨識；home-menu-open mobile 的選單項目間距足夠，但看不出焦點樣式。 |
| 動畫與轉場 | 4.5 | portal mobile：頂部有 16 段進度條、播放鍵與「點按兩側或左右滑動」提示，限時動態式播放器的線索完整；但 home-loading 沒有骨架或載入指示，discord-loading 只把數字換成「讀取中」文字；screen-song 沒有明顯的切換提示（例如正在演奏的大卡片）。 |

要保留的優點：
- about desktop／about-contact mobile：「社團信箱」主卡片加上「想入社／捐贈樂器／演出邀約」三張情境卡，各附對應的聯絡連結，校外人士一眼知道該找誰。
- portal mobile：限時動態式節目單（進度條、播放、分享、劇照加圖片出處）體驗完整，很適合掃 QR Code 的觀眾。
- discord-error desktop：拿不到人數時用「—」佔位，並說明「邀請連結仍可正常使用」，不擋住主要行動。
- screen screen：右側大 QR Code 加短網址 harmonica.nycu.club/p，投影時一眼就能掃。
- home desktop：近期動態卡片有日期、標題與來源平台，並附「前往觀測站來源頁」連結。

最重要的五個問題（由嚴重到輕微）：
1. [色彩／狀態與回饋] [home-dark、about-dark、chronology-dark、site-guide-dark、join-dark、portal-dark、home-calendar-dark] [desktop、mobile] 深色截圖與淺色逐像素相同，深色外觀完全沒有作用 —— 夜間使用的學生與演出現場的觀眾會被白底刺眼，也代表主題系統沒有接上 —— 為官網各頁建立深色 token，並確實套用到所有頁面。
2. [狀態與回饋] [home-loading、home-error、home-empty] [desktop、mobile] 行事曆載入中與讀取失敗時是約 520px 的空白框，空資料時只有 Google 的系統字；mobile 的五種狀態完全一樣 —— 使用者會以為網站壞了，也拿不到下一步 —— 載入時放骨架與文字提示；讀取失敗時說明「每週二晚上照常社課」並附「開啟 Google 日曆」的按鈕。
3. [文案] [site-guide、chronology、about、全站頁尾] [desktop、mobile] GitHub Pages、GitHub Actions、Hugo、last-good、Repo 資料備援、Hermes 工作區、chronology_events、YYYY/MM/DD 格式規則等內部術語直接公開 —— 老社員、校外人士看不懂，也洩漏維運細節 —— 改寫成「資料多久更新、讀不到時會怎樣」這類白話，工程細節移到 repo 文件。
4. [一致性] [join、discord] [desktop、mobile] 入社轉址頁沒有社徽、卡片與按鈕，只有一行藍字；Discord 頁改用綠色按鈕、英文眉標與「演出 Portal」字樣，像別的網站 —— 入社是最重要的轉換路徑，風格斷裂會降低信任 —— 套用官網的卡片、社徽、金色主按鈕與中文用語，並附「回竹韻官網」。
5. [導覽] [home、home-menu-open] [desktop、mobile] 頁首缺少「行事曆」與常駐的「加入 Discord」主按鈕，手機選單只有三個純文字連結，浮動「詢問竹韻」按鈕會蓋住主視覺按鈕與卡片標題 —— 手機使用者的主要行動被藏起來或遮住 —— 導覽補上行事曆與 Discord 按鈕，浮動按鈕縮小並避開內容。

## 組 C
一句話總評：竹韻官網的完成度明顯較高：品牌色與金色主按鈕貫穿官網、Discord、入社、節目單與投影畫面，深色外觀成立，載入中、讀取失敗與空資料都有白話說明；剩下的是行事曆讀取失敗時大片空白、時間軸字小、浮動按鈕遮擋等細節。
整體分數：8 / 10

| 項目 | 分數 | 證據（頁面／狀態 ID、尺寸、看到的事實） |
|---|---|---|
| 資訊層級 | 8.5 | home desktop：主視覺有「國立陽明交通大學／竹韻口琴社」、創社與復社年份、「加入 Discord／看社團行事曆」，再加上社課（每週二晚上）、地點（學生活動中心 1F 聯誼廳）、門檻（零基礎、不限校內）三格事實；右側「第一次來？」三步驟卡片直接回答新生的下一步。home mobile：同樣的資訊依序排成單欄，首屏就看得到。 |
| 字體排印 | 8 | home desktop：大標、眉標（「關於竹韻」「近期動態」金色小字）、內文三層清楚；site-guide desktop：表格欄位標題粗體、內文約 15px，行長控制在約 770px；portal-song mobile：英文曲名大字、中文說明行高寬鬆；chronology desktop：時間軸日期與事件約 12–13px，偏小，「2026/05/15 前後」的補充字更小。 |
| 色彩 | 8.5 | 藍綠主色加金色主按鈕在 home、discord、join、screen 各處一致；home-dark、site-guide-dark、discord-dark、join-dark desktop／mobile 都是完整的深藍黑配色，表格、卡片與頁尾都重新上色；狀態點用綠（最新）、藍（同步中）、琥珀（備份），並附文字。 |
| 間距與版面 | 7.5 | home desktop：版心約 1140px，左文右卡的雙欄善用寬螢幕；site-guide desktop：左側目錄加右側內文的雙欄；home-error desktop：行事曆讀取失敗的說明卡只約 370px 寬，周圍是 400px 以上的灰色空白；chronology desktop：時間軸只用中間約 640px，左側目錄下方大片空白。 |
| 一致性 | 8.5 | discord desktop／mobile：金色「前往伺服器」與淺色「複製邀請連結」和官網按鈕同一套；join desktop／mobile：白卡、社徽、金色膠囊按鈕加「回竹韻官網」；screen 與 portal 共用同一套藍綠漸層、社徽與「現場演出」膠囊標籤。小瑕疵：portal 的眉標仍有英文「JOIN BAMBOO MELODY」「NYCU BAMBOO MELODY HARMONICA CLUB」。 |
| 資訊密度 | 8 | home desktop：一屏內有身分、行動、事實與三步驟；site-guide mobile：桌面的表格在手機改成一張張卡片，易讀但很長；screen screen：上方「即將開始・共 4 首」大卡片加下方 2×2 曲目清單加 QR Code，投影一屏資訊完整不擁擠。 |
| 導覽 | 8.5 | home desktop：頁首有「首頁／行事曆／編年史／關於我們」加常駐金色「加入 Discord」，目前頁有底線；home-menu-open mobile：目前頁「首頁」以金色左邊條加底色標示，選單最後是滿版的「加入 Discord」；discord desktop：右上有「官網首頁／演出節目單」；site-guide 與 chronology desktop 都有「本頁內容」目錄。 |
| 狀態與回饋 | 8 | home-loading desktop：動態下方顯示「正在讀取觀測站的最新動態…」，行事曆有骨架線條加「正在載入 Google 日曆…」；home-error desktop：顯示「暫時連不上臺灣口琴觀測站，先顯示 2026/08/14 同步的動態」，行事曆有「Google 日曆暫時載不出來」說明卡，提醒社課照常並指向下一步；home-empty desktop：顯示「觀測站目前沒有新的公開貼文…」；discord-loading 是數字骨架，discord-error 是琥珀色提示框，discord-empty 是「伺服器已開放加入，進去和大家打聲招呼吧！」；site-guide-error 頁尾顯示「Google 試算表的資料暫時無法使用，先顯示 2026/08/14 整理的備份資料」。扣分：home-empty 的行事曆仍是 Google 自己的「目前顯示 2027年11月12日以前的活動」，沒有站方說明。 |
| 響應式 | 7.5 | home mobile：主視覺、按鈕與事實列都重排為單欄；site-guide mobile：表格改成卡片；discord mobile：按鈕上下排列、滿版好點；但 site-guide mobile 的浮動「詢問竹韻」按鈕蓋住「頁尾的小圓點會告訴你目前的…」這段內文；home desktop 的行事曆嵌入中，地點欄被截成「Daxue R…」。 |
| 文案 | 8 | 用語自然親切：「第一次來？」「竹韻最近在做什麼」「下一段旋律，換你加入」「沒有自動跳轉？開啟入社表單」；site-guide 用「資料從哪裡來／多久更新一次／讀不到資料時」白話說明，沒有工程術語。小問題：chronology 時間軸的來源標籤「Club Portal」沒有解釋。 |
| 無障礙 | 7.5 | 金色按鈕配深色字、白字配藍綠底，對比良好；狀態不只靠顏色，每個狀態點都附文字；home-menu-open mobile 的選單項目高度約 48px；但 chronology 的來源連結與日期補充字約 10–11px，點擊範圍小；截圖看不出焦點樣式。 |
| 動畫與轉場 | 7.5 | home-loading desktop：行事曆的骨架線條加膠囊狀載入提示；discord-loading desktop／mobile：數字位置是灰色骨架塊；portal mobile：16 段進度條、播放鍵與「點按兩側或左右滑動」；screen-song screen：正在演奏的曲目同時出現在上方大卡片（金色左邊條加「正在演奏」）與清單中的高亮底色。實際動態看不到，依線索給分。 |

要保留的優點：
- home desktop／mobile：社課、地點、門檻三格事實列，加上「第一次來？」三步驟卡片，新生在首屏就知道下一步。
- 全站頁尾的狀態點：「社團公開資料已是最新（20:00 讀取）」「正在同步社團公開資料…」「暫時連不上…先顯示 2026/08/14 整理的備份資料」，同時用顏色與文字傳達狀態。
- home-error desktop：行事曆讀取失敗時的說明卡，先告訴使用者「每週二晚上社課照常」，再給替代行動。
- discord 各狀態：骨架、琥珀色提示框、空資料的鼓勵文案，三種狀態都有設計，主按鈕始終可用。
- screen-song screen：上方大卡片標出「正在演奏 02 風之丘」，清單同步高亮，投影距離也看得清。
- join desktop／mobile 與 site-guide-dark：轉址頁與深色外觀都和官網同一套設計。

最重要的五個問題（由嚴重到輕微）：
1. [間距與版面] [home-error] [desktop] 行事曆讀取失敗的說明卡只約 370px 寬，周圍保留原嵌入高度，形成 400px 以上的灰色空白 —— 錯誤狀態看起來像版面壞掉 —— 讀取失敗時縮短容器高度，或在空白處列出固定社課與「開啟 Google 日曆」按鈕。
2. [狀態與回饋] [home-empty] [desktop、mobile] 動態區已有站方說明，但行事曆空資料時仍只有 Google 的「目前顯示 2027年11月12日以前的活動」 —— 和其他狀態的處理不一致，使用者不知道是沒活動還是讀取失敗 —— 偵測到空資料時，加上站方的「近期沒有排定活動，每週二社課照常」說明。
3. [響應式] [site-guide、home] [mobile] 浮動「詢問竹韻」按鈕蓋住段落文字與卡片內容 —— 手機是主要使用情境，遮字會影響閱讀 —— 頁面底部留出安全距離，或捲動時把按鈕收成小圓鈕。
4. [字體排印／無障礙] [chronology、chronology-timeline] [desktop、mobile] 時間軸的日期、事件與「↗ 官方 Instagram 貼文」等來源連結只有約 10–13px，點擊範圍小，左側目錄下方大片空白 —— 編年史是老社員的核心頁面，閱讀不舒服 —— 把字級提高到 15–16px，來源連結做成較大的點擊區，桌面版可以讓時間軸更寬或加年代分段。
5. [一致性／文案] [portal、portal-join、screen] [mobile、desktop] 節目單與投影畫面仍有英文眉標（JOIN BAMBOO MELODY、NYCU BAMBOO MELODY HARMONICA CLUB）；chronology 的來源標籤「Club Portal」沒有解釋 —— 和官網全中文的語氣不一致，觀眾也看不懂 —— 改成中文眉標，為「Club Portal」加上說明或改名。

```json
{"A": {"overall": 4.5, "scores": {"資訊層級": 5, "字體排印": 5.5, "色彩": 5, "間距與版面": 4, "一致性": 5, "資訊密度": 4.5, "導覽": 5.5, "狀態與回饋": 3.5, "響應式": 5, "文案": 4, "無障礙": 5, "動畫與轉場": 3}, "issues": ["ref-cums-home desktop 社群嵌入讀取失敗後留下約 600px 空白並重複兩次", "ref-yale-glee-events desktop CMS 範本說明文字直接公開", "ref-mcu-harmonica-home 首屏被選單與登入表單佔據，看不到入社資訊", "ref-mcu-harmonica-home desktop 圖片破圖只剩替代文字", "ref-yale-glee-home desktop 右欄全空，未善用寬螢幕"]}, "B": {"overall": 5.5, "scores": {"資訊層級": 6, "字體排印": 5.5, "色彩": 4.5, "間距與版面": 5.5, "一致性": 4.5, "資訊密度": 5.5, "導覽": 5, "狀態與回饋": 3.5, "響應式": 5.5, "文案": 3.5, "無障礙": 5.5, "動畫與轉場": 4.5}, "issues": ["所有 -dark 截圖與淺色逐像素相同，深色外觀完全沒有作用", "home-loading/error 行事曆是約 520px 空白框，empty 只有 Google 系統字；mobile 五種狀態完全一樣", "site-guide、chronology、about、頁尾外露 GitHub、Hugo、Repo、Hermes、chronology_events 等內部術語", "join 頁沒有設計，discord 頁用綠色按鈕與英文眉標，和官網風格斷裂", "頁首缺少行事曆與 Discord 主按鈕，手機選單只有三個連結，浮動按鈕遮住內容"]}, "C": {"overall": 8, "scores": {"資訊層級": 8.5, "字體排印": 8, "色彩": 8.5, "間距與版面": 7.5, "一致性": 8.5, "資訊密度": 8, "導覽": 8.5, "狀態與回饋": 8, "響應式": 7.5, "文案": 8, "無障礙": 7.5, "動畫與轉場": 7.5}, "issues": ["home-error desktop 行事曆說明卡周圍有 400px 以上的灰色空白", "home-empty 行事曆仍只有 Google 的空資料系統字，沒有站方說明", "mobile 浮動「詢問竹韻」按鈕蓋住 site-guide 與 home 的內文", "chronology 時間軸字級約 10–13px，來源連結點擊範圍小，左側空白", "portal、screen 仍有英文眉標，chronology 的「Club Portal」沒有解釋"]}}
```
