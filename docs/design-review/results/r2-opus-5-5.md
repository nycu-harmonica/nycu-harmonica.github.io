## 組 A
一句話總評：品牌主色與首頁骨架已經成形，但深色外觀完全沒有作用、外部資料失敗時只剩空白，入社轉址頁與 Discord 頁又各自是另一套樣式，整體停在「可用但不完整」。
整體分數：5.8 / 10

| 項目 | 分數 | 證據（頁面／狀態 ID、尺寸、看到的事實） |
|---|---|---|
| 資訊層級 | 6.5 | home desktop：主視覺有「國立陽明交通大學 竹韻口琴社」大標、「加入 Discord／社團行事曆」兩顆按鈕，看得懂是什麼社團；但主視覺沒有社課時間、地點、門檻等關鍵事實，介紹段落置中排成三行長句，「想學口琴嗎？」入社區塊要捲到 2000px 以下才出現。chronology desktop 開頭先放三段資料維護規則（YYYY/MM/DD、Hermes、OCR），真正的時間軸要到約 y=1070 才開始。 |
| 字體排印 | 6.5 | home desktop 標題用粗黑體，層級還算清楚；但 home mobile 介紹文整段置中，換行後每行長短不一，很難讀；chronology desktop 內文行長約 870px、字級偏小（約 14px），時間軸說明文字（↗ 公開活動行事曆）大約只有 11px。日期一律用 2026/08/09 格式，是一致的。 |
| 色彩 | 6 | 有一套藍綠主色（header、hero、CTA 區塊），品牌識別成立；但 home-dark、about-dark、chronology-dark、site-guide-dark 的 desktop 截圖和淺色版逐像素相同，深色外觀根本沒有套用。discord desktop 反過來只有深色；join desktop 是淡藍底配預設藍連結，完全沒有品牌色。 |
| 間距與版面 | 6 | home desktop 內容寬約 1040px，1440 寬的螢幕兩側留白偏多；home-error desktop 的行事曆位置留下約 520px 高的空白白框；home mobile 右下「詢問竹韻」浮動鈕壓在第一張動態卡的標題「復社紀念影片」上。 |
| 一致性 | 5 | 主站（home/about/chronology）、discord（Discord 仿製深色卡片）、join（無樣式純文字）、portal／screen（沉浸式深藍）是四套視覺語言；按鈕在 home 是直角白底，在 discord 是綠色圓角，在 join 是純文字連結。 |
| 資訊密度 | 6 | home desktop 一屏只看得到 hero，加上一段置中文字；chronology desktop 前 900px 都是方法論文字；discord desktop 的卡片在 1440 寬只佔約 720px，資訊量適中。 |
| 導覽 | 6 | 桌面 header 只有「首頁／編年史／關於我們」三項，沒有行事曆，也沒有 Discord 主 CTA；目前頁以淺色底塊標示。home-menu-open mobile 選單只有三項，「詢問竹韻」浮動鈕在選單打開時仍然壓住 hero 的「社團行事曆」按鈕。discord 頁只有「演出 Portal」一個出口，沒有回主站的連結。 |
| 狀態與回饋 | 4.5 | home-error desktop：動態區只把小字改成「上次同步資料：2026/08/14」，行事曆變成完全空白、沒有任何說明的白框，是這輪最嚴重的破圖。about／chronology／site-guide 的 loading、error、empty 三種狀態，desktop 截圖彼此相同，mobile 截圖則和預設完全相同，看不出狀態提示。discord-empty desktop 顯示「0 位上線 0 位成員」，又寫「已連線 Discord，顯示目前的約略上線與成員人數」，容易誤導；discord-error 用「— 位上線」加一行小字，算是合格。 |
| 響應式 | 6 | home-calendar mobile 的行事曆改成議程式，可讀；home mobile hero 把 logo 放大到佔半屏，標題被推到第二屏。join mobile 標題「加入陽明交大竹韻口琴社」折成「…口琴／社」，最後一行只剩一個字。footer mobile 的「Google Sheet 即時讀取：2026/11/13 20:00:0」被浮動鈕截斷。 |
| 文案 | 6 | 主文自然；但 chronology desktop 開頭直接寫「chronology_events 分頁維護」、「Hermes 研究整理」、「YYYY/MM/DD」，都是內部術語。discord 保留英文「YOU'VE BEEN INVITED TO JOIN A SERVER」，描述裡直接貼出網址 https://harmonica.nycu.club。screen 主標「陽明交大竹韻口琴社演出投影畫面」是在描述畫面本身。 |
| 無障礙 | 5.5 | screen 右下的鍵盤說明「按 F 進入全螢幕…」約 8px，在 1920 投影上無法閱讀；時間軸說明約 11px 灰字；portal-join mobile 表單截圖的文字（年級或階段、選項圓圈）透出來，疊在白色大標底下，對比被干擾。主要按鈕的點擊範圍足夠。 |
| 動畫與轉場 | 5 | 可見線索：portal 頂部有分段進度條、播放鍵、「點按兩側或左右滑動」提示；screen-song 用「正在演奏」小標籤加底色標示第 2 首；discord-loading 只把數字換成「讀取中」文字，沒有骨架。主站載入狀態看不到任何過渡線索，所以給保守分數。 |

要保留的優點：
- home desktop 的「竹韻近期動態」三欄卡片：每張都有日期、標題、來源平台，下面附資料時間戳。
- home-calendar mobile 改用議程式的嵌入行事曆，手機上可讀。
- chronology 時間軸「日期在左、事件在右、來源連結在下」的三段結構，每筆都可以回溯來源。
- portal 限時動態式節目單：分段進度條、曲目大標加中文副標、曲目解說，演出現場很好用。
- screen 投影畫面：大 QR Code 加短網址 harmonica.nycu.club/p，節目單兩欄排列清楚。

最重要的五個問題（由嚴重到輕微）：
1. [狀態與回饋] [home-error] [desktop] 行事曆讀取失敗時，顯示的是約 520px 高、沒有任何文字的空白框 —— 訪客會以為網站壞了，也找不到社課時間 —— 失敗時改成說明卡：「Google 日曆暫時載不出來，固定社課是每週二晚上…」，並附開啟 Google 日曆的按鈕。
2. [色彩] [home-dark／about-dark／chronology-dark／site-guide-dark／home-calendar-dark／join-dark] [多者] 深色外觀的截圖和淺色版逐像素相同，深色模式沒有實作 —— 晚上用手機看的學生會被大片白底刺眼，跟 portal／discord 的深色也不一致 —— 用 color token 實作完整的深色主題，嵌入行事曆也要對應。
3. [一致性] [join／discord] [多者] join 頁是無樣式的白底黑字加預設藍連結，discord 頁不論淺色或深色都固定為深色的 Discord 仿製卡，和主站是三套系統 —— 從 QR Code 或社群點進來的人會懷疑是不是同一個網站 —— join 套用品牌卡片（logo、主色按鈕、回官網連結），discord 跟隨系統的明暗設定。
4. [導覽] [home、home-menu-open] [多者] header 沒有「行事曆」和 Discord 主 CTA；「詢問竹韻」浮動鈕在 mobile 壓住卡片標題、hero 按鈕和 footer 文字 —— 最常用的入社動作需要捲動才找得到，被遮住的內容也點不到 —— 在 header 加入行事曆與「加入 Discord」主按鈕，浮動鈕縮成圓形圖示，並為它保留底部安全距離。
5. [文案] [chronology、site-guide、discord、screen] [多者] 頁面直接露出 chronology_events、Hermes、YYYY/MM/DD、英文 Discord 樣板句、裸網址，投影主標寫「演出投影畫面」 —— 對學生與觀眾是噪音，也顯得不專業 —— 把維護規則移到 site-guide 或折疊區，改成讀者語言；投影主標改成演出名稱或「歡迎來到竹韻的演出」。

## 組 B
一句話總評：品牌系統完整、深色外觀成立，首頁把「社課時間、地點、門檻」和「第一次來？」三步驟放到第一屏，外部資料失敗時也有清楚的替代說明；剩下的是內部術語外露、Discord 頁的英文樣板，以及投影畫面的留白與細節。
整體分數：7.6 / 10

| 項目 | 分數 | 證據（頁面／狀態 ID、尺寸、看到的事實） |
|---|---|---|
| 資訊層級 | 8.5 | home desktop：hero 有「國立陽明交通大學／竹韻口琴社」、一句「1968 年創社，2026 年夏天復社，零基礎也能…」，下方三格「社課 每週二晚上／地點 學生活動中心 1F 聯誼廳／門檻 零基礎、不限校內」，琥珀色「加入 Discord」主按鈕配外框的「看社團行事曆」，主次清楚；右側「第一次來？」三步驟卡把行動講明白。about desktop 有左側目錄、右側本文，下面是分類聯絡卡。 |
| 字體排印 | 7.5 | 標題、eyebrow（琥珀小字「關於竹韻」）、內文三層清楚；about desktop 內文行長約 640px、行高舒適。site-guide mobile 的資料表第一欄過窄，「首頁竹韻近期動態」被折成四行、每行兩個字；hero 的 eyebrow 用寬字距大寫英文，和中文標題並置略顯生硬。 |
| 色彩 | 8 | 深藍綠搭配琥珀色強調的系統，在 header、CTA、eyebrow、狀態點（綠：最新、橘：備份）一致使用；home-calendar-dark desktop 連嵌入的 Google 日曆都換成深色底，about-dark、site-guide-dark mobile 的對比也正常。portal 和 screen 沿用同一套深藍。 |
| 間距與版面 | 7.5 | home desktop 內容寬約 1140px，左右欄（介紹與「第一次來？」）比例合理；about desktop 用 12 欄格線、目錄側欄對齊。不過 home-error desktop 的行事曆失敗卡維持完整高度（約 600px），訊息只佔中間兩行；screen 的左側中段約 400px 空白；site-guide-error desktop 右下的「詢問竹韻」浮動鈕和 footer 狀態文字「…整理的備份資料」重疊。 |
| 一致性 | 7.5 | header、footer、圓角卡片、琥珀主按鈕在 home、about、chronology、site-guide 一致；join 也用同一套卡片、logo 和琥珀按鈕，並有深色版。discord 改成淺色卡片，會跟隨明暗設定，但仍保留 Discord 綠色主按鈕和英文樣板，和主站按鈕不同色。 |
| 資訊密度 | 7.5 | home desktop 第一屏就有關鍵事實、CTA、新手步驟；chronology 把方法論濃縮成「先知道這兩件事」兩個 bullet，時間軸在約 y=700 開始。site-guide 內容很長而且偏技術，對一般讀者過密。 |
| 導覽 | 8 | header 有「首頁／行事曆／編年史／關於我們」加琥珀「加入 Discord」，目前頁以底線標示；home-menu-open mobile 的選單目前項目有左側琥珀色條，底部是全寬的 Discord 按鈕，點擊範圍大。about、chronology、site-guide 都有「本頁內容」目錄。discord 頁仍然只有「演出 Portal」，沒有回首頁。 |
| 狀態與回饋 | 8 | home-error desktop：動態區下方是橘點加「暫時連不上臺灣口琴觀測站，先顯示 2026/08/14 同步的動態」，行事曆區顯示「Google 日曆暫時載不出來」，並說明每週二社課照常、改開 Google 日曆或到 Discord 問；chronology-error 在時間軸標題下寫「暫時連不上 Google 試算表，先顯示 2026/08/14 整理的備份資料」；discord-error 隱藏人數，改用米黃提示框；discord-loading 用骨架方塊加「正在向 Discord 取得目前人數…」。扣分點：discord-empty 顯示「0 位上線 0 位成員」，並當成正常資料呈現。 |
| 響應式 | 7.5 | home mobile 把三格事實改成堆疊的橫列，hero 按鈕並排；home-calendar mobile 是議程式行事曆，下面有「在 Google 日曆開啟」按鈕；about-contact mobile 卡片單欄。site-guide mobile 的表格欄寬失衡；discord mobile 的「社群伺服器」徽章單獨掉到標題下一行，左側縮排不齊。 |
| 文案 | 7 | 主站用詞親切、精準（「挑一堂社課來看看」、「不確定該找誰的話，寄到這個信箱就對了」）。但 site-guide 仍寫「chronology_events」、「last-good 快照」、「Repo 資料備援」、「GitHub Actions」、「Hermes 工作區」；discord 標題保留「YOU'VE BEEN INVITED TO JOIN A SERVER」，描述貼裸網址；screen 主標「…演出投影畫面」。 |
| 無障礙 | 7 | 主按鈕高度足夠，琥珀底配深色字，對比良好；狀態除了顏色點之外也有文字說明（不只靠顏色）。screen 的鍵盤說明已放大到可讀；但 screen-song 的「正在演奏」標籤仍然很小（約 10px），portal 的「現在」灰字對比偏低，chronology 時間軸來源小字約 11px。 |
| 動畫與轉場 | 6.5 | 可見線索：discord-loading 的骨架方塊、portal 分段進度條和播放鍵、screen-song 的目前曲目高亮加標籤、hero 背景的細橫線紋理。主站 loading 截圖與有資料時相同（因為有內建資料），看不出載入過渡；portal-song 的影像下緣有幾團模糊色塊，像是漸層或模糊轉場殘影。線索有限，給中上的保守分數。 |

要保留的優點：
- home hero 的「社課／地點／門檻」三格事實列，加上琥珀「加入 Discord」主按鈕。
- home 右側的「第一次來？」1-2-3 步驟卡，把新生的下一步講清楚。
- 外部資料失敗時的處理：橘點狀態行、行事曆失敗說明卡、chronology「先顯示 2026/08/14 整理的備份資料」，都是讀者語言，也給了下一步。
- 深色外觀完整，連嵌入的 Google 日曆都轉成深色（home-calendar-dark desktop）。
- join 轉址頁用品牌卡片、琥珀主按鈕，附「回竹韻官網」，也有深色版。
- about 的聯絡區：社團信箱主卡，加上「想入社／捐贈樂器／演出邀約」三張分流卡。

最重要的五個問題（由嚴重到輕微）：
1. [文案] [site-guide、discord、screen] [多者] site-guide 大量內部術語（chronology_events、last-good、Repo 資料備援、GitHub Actions、Hermes），discord 保留英文「YOU'VE BEEN INVITED TO JOIN A SERVER」和裸網址，screen 主標是「演出投影畫面」 —— 讀者語氣在這幾頁突然斷掉，投影主標直接對觀眾說「這是投影畫面」 —— site-guide 分成「給訪客」與「給幹部」兩層，技術細節折疊；discord 改成中文「你被邀請加入竹韻 Discord」，網址做成連結；投影主標改成演出名稱。
2. [狀態與回饋] [discord-empty] [多者] 空資料時顯示「0 位上線 0 位成員」，並當作正常資料呈現 —— 看起來像社團沒人，會直接勸退新生 —— 人數為 0 或缺值時隱藏人數列，改顯示「歡迎成為第一批成員」或只保留社課資訊。
3. [間距與版面] [home-error、screen] [desktop、screen] 行事曆失敗卡維持約 600px 高，訊息只佔中間；screen 左側中段約 400px 空白，節目單擠在底部 —— 失敗狀態浪費一整屏，投影時資訊重心偏低 —— 失敗卡縮成內容高度，並附按鈕；screen 把節目單上移，或放大曲目字級填滿中段。
4. [響應式] [site-guide、discord] [mobile] site-guide mobile 的表格第一欄窄到「首頁竹韻近期動態」折成四行；discord mobile 的「社群伺服器」徽章掉到下一行，左側縮排不齊 —— 手機是主要讀者的設備 —— 小螢幕把表格改成卡片堆疊；徽章和標題同行，或改放在 eyebrow 位置。
5. [間距與版面／無障礙] [site-guide-error、home] [desktop、mobile] 「詢問竹韻」浮動鈕與 footer 狀態文字重疊（site-guide-error desktop 右下）；screen-song 的「正在演奏」標籤只有約 10px —— 狀態訊息被遮住，現場觀眾看不到目前曲目 —— 為浮動鈕保留 footer 底部安全距離；「正在演奏」標籤放大到至少 20px，並加上左側色條。

## 組 C
一句話總評：參考組水準落差很大：Yale Glee Club 的排印和導覽穩重成熟，但 CUMS 首頁大片空白、about 在手機上沒有響應式，MCU 口琴社則是過時的 Drupal 部落格版型；整體只能算是「可用到過時」。
整體分數：4.7 / 10

| 項目 | 分數 | 證據（頁面／狀態 ID、尺寸、看到的事實） |
|---|---|---|
| 資訊層級 | 5 | ref-yale-glee-home desktop：大合照加創立於 1861 的介紹，再接 Concerts 清單，層級清楚；ref-cums-home desktop：輪播只有「Cambridge University Musical Society」和「Upcoming Events」，下方約 600px 空白；ref-mcu-harmonica-home desktop：首屏左側是「使用者登入」表單，主欄是 2022 年的舊貼文，看不出現在能做什麼。 |
| 字體排印 | 6 | Yale 的襯線標題、小型大寫日期（NOVEMBER 13, 2026 7:30 PM）和內文行長都很講究；ref-cums-about desktop 用細體 Raleway 灰字，粗體字距不一致；MCU 混用 11–12px 小字、顏文字與日文。 |
| 色彩 | 4.5 | Yale 只用深藍一色，品牌識別成立但偏保守；CUMS 首頁是磚牆照片配灰白，about 是淺藍連結配白底；MCU 是灰色漸層，頁首有五線譜圖，整體灰階、沒有系統；三站都沒有深色外觀。 |
| 間距與版面 | 5 | Yale 版面整齊，但 1440 寬的內容只用到左側約 800px，右側大片留白（ref-yale-glee-about desktop）；ref-cums-home desktop 的社群嵌入沒載入，留下兩段「Tweets by @CamUniMusSoc」和大片空白；MCU 側欄加主欄的版型擁擠，圖文間距不一。 |
| 一致性 | 4.5 | Yale 內部一致（按鈕、標題、分隔線）；CUMS 首頁（WordPress Divi 版型）和 about 頁（舊版 logo、全大寫導覽）像兩個不同網站；MCU 是單一舊模板，但貼文格式各自不同。 |
| 資訊密度 | 5 | Yale events 一屏可看到三場演出，各有日期與「Add to Calendar」；CUMS 首頁幾乎沒有內容；MCU 首頁塞滿舊貼文與「語言 Chinese, Traditional」等系統欄位，過擠又沒有重點。 |
| 導覽 | 6 | Yale 有完整的下拉主選單（About、Concerts、Auditions…）加麵包屑「Home / About」，mobile 用漢堡選單；CUMS mobile 是「Select Page」下拉，about 有左側子選單；MCU 有分頁籤和側欄兩套重複的選單。 |
| 狀態與回饋 | 3 | ref-cums-home desktop／mobile：嵌入內容失敗後留下空白區和「Tweets by…」字樣，沒有說明；ref-mcu-harmonica-home：圖片失效，只剩替代文字「可能是一或多人、大家站著和室內的圖像」；ref-yale-glee-events 的頁面說明直接露出 CMS 範本文字。 |
| 響應式 | 4 | Yale mobile 正常重排；ref-cums-about mobile 只是把桌面版縮小，字小到無法閱讀；ref-cums-home mobile 輪播文字壓在照片上、對比差，下方約 1000px 空白；ref-mcu-harmonica-home mobile 完全沒有響應式，是整頁縮小。 |
| 文案 | 5 | Yale 的介紹文案專業；但 ref-yale-glee-events 直接顯示範本說明「Use the Calendar List Block to add a dynamic events feed…」，是 CMS 文字外露；MCU 用語隨性（顏文字、「發表回應前，請先登入」）；CUMS 只有贊助、董事等機構資訊。 |
| 無障礙 | 5 | Yale 的按鈕與連結對比良好，Add to Calendar 外框按鈕夠大；CUMS 輪播白字壓在照片上、對比不足，cookie 橫幅遮住底部；MCU 的小字與灰字對比偏低，連結很小。 |
| 動畫與轉場 | 3 | 只看得到 CUMS 的輪播點點與左右箭頭（mobile 截圖中輪播正在過場、文字半透明）；Yale 只有下拉箭頭；MCU 沒有任何線索。看不到載入或狀態轉場的設計，給保守低分。 |

要保留的優點：
- Yale 的襯線字標與小型大寫日期，建立了學術、正式的品牌氣質（ref-yale-glee-home desktop）。
- Yale 演出列表每筆都有「日期時間＋形式（IN-PERSON）＋Add to Calendar」（ref-yale-glee-events）。
- Yale 的麵包屑和完整的下拉主選單（ref-yale-glee-about desktop）。
- CUMS about 左側子選單把十幾個子頁分好類（ref-cums-about desktop）。
- MCU 首頁以活動紀錄為主，有社團生活感（ref-mcu-harmonica-home）。

最重要的五個問題（由嚴重到輕微）：
1. [響應式] [ref-cums-about、ref-mcu-harmonica-home] [mobile] 手機版是整頁縮小，字級小到無法閱讀 —— 主要讀者用手機，等於無法使用 —— 改用響應式版型。
2. [狀態與回饋] [ref-cums-home] [desktop、mobile] 社群嵌入失敗後留下大片空白和「Tweets by…」殘字 —— 首頁看起來像壞掉 —— 失敗時隱藏區塊或顯示替代連結。
3. [資訊層級] [ref-mcu-harmonica-home] [desktop] 首屏是登入表單和 2022 年的舊貼文，沒有入社、社課資訊 —— 新生不知道社團是否還在運作 —— 首屏改放社團介紹、社課時間與入社入口。
4. [文案] [ref-yale-glee-events] [desktop、mobile] CMS 範本說明「Use the Calendar List Block…」直接顯示在頁面上 —— 內部文字外露，降低專業感 —— 換成真正的演出季說明。
5. [色彩／間距] [ref-yale-glee-about、ref-cums-home] [desktop] Yale 在 1440 寬只用左側約 800px；CUMS 的輪播文字壓在照片上，對比不足 —— 空間浪費、可讀性差 —— 善用寬螢幕兩欄，文字加遮罩或改到照片外。

```json
{"A": {"overall": 5.8, "scores": {"資訊層級": 6.5, "字體排印": 6.5, "色彩": 6, "間距與版面": 6, "一致性": 5, "資訊密度": 6, "導覽": 6, "狀態與回饋": 4.5, "響應式": 6, "文案": 6, "無障礙": 5.5, "動畫與轉場": 5}, "issues": ["home-error 行事曆讀取失敗時顯示約 520px 空白框，沒有任何說明", "深色外觀未實作：home/about/chronology/site-guide/home-calendar/join 的 dark 截圖與淺色版逐像素相同", "join 是無樣式白底純文字頁，discord 固定深色，和主站是三套視覺系統", "header 缺行事曆與 Discord 主 CTA；「詢問竹韻」浮動鈕在 mobile 遮住卡片標題、hero 按鈕與 footer", "chronology/site-guide/discord/screen 露出 chronology_events、Hermes、YYYY/MM/DD、英文樣板句與裸網址"]}, "B": {"overall": 7.6, "scores": {"資訊層級": 8.5, "字體排印": 7.5, "色彩": 8, "間距與版面": 7.5, "一致性": 7.5, "資訊密度": 7.5, "導覽": 8, "狀態與回饋": 8, "響應式": 7.5, "文案": 7, "無障礙": 7, "動畫與轉場": 6.5}, "issues": ["site-guide 內部術語外露（chronology_events、last-good、Repo 資料備援、GitHub Actions、Hermes），discord 保留英文樣板與裸網址，screen 主標為「演出投影畫面」", "discord-empty 把「0 位上線 0 位成員」當正常資料顯示，可能勸退新生", "home-error 行事曆失敗卡維持約 600px 高；screen 左側中段約 400px 空白、節目單擠在底部", "site-guide mobile 表格第一欄過窄，文字折成每行兩字；discord mobile 徽章掉行、縮排不齊", "「詢問竹韻」浮動鈕與 footer 狀態文字重疊；screen-song「正在演奏」標籤過小"]}, "C": {"overall": 4.7, "scores": {"資訊層級": 5, "字體排印": 6, "色彩": 4.5, "間距與版面": 5, "一致性": 4.5, "資訊密度": 5, "導覽": 6, "狀態與回饋": 3, "響應式": 4, "文案": 5, "無障礙": 5, "動畫與轉場": 3}, "issues": ["CUMS about 與 MCU 首頁在手機上只是整頁縮小，無法閱讀", "CUMS 首頁社群嵌入失敗後留下大片空白和「Tweets by…」殘字", "MCU 首屏是登入表單與 2022 年舊貼文，缺入社與社課資訊", "Yale events 頁直接顯示 CMS 範本說明文字", "Yale 在 1440 寬只用左側約 800px；CUMS 輪播文字壓在照片上，對比不足"]}}
```
