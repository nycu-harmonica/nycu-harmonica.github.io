# 給 SDC 的 DNS 設定申請

`harmonica.nycu.club` 的 DNS 由 SDC 管理。本文件是申請 record 的範本與操作順序。

## 需要的兩筆 record

(組織名為 `nycu-harmonica`;TXT 驗證碼要先做完下方步驟 1–2 才會拿到)

```
1) 網站指向
   名稱(Host):harmonica.nycu.club
   類型:CNAME
   值:nycu-harmonica.github.io.
   TTL:3600

2) GitHub Pages 網域驗證(防止網域被他人 Pages 佔用,建議長期保留)
   名稱(Host):_github-pages-challenge-nycu-harmonica.harmonica.nycu.club
   類型:TXT
   值:「<GitHub 顯示的驗證碼,見下方步驟 2>」
   TTL:3600
```

## 操作順序

1. 建立 GitHub organization `nycu-harmonica`(需先完成,org 名稱決定上面兩筆 record 的值)。
2. Org 首頁 → **Settings → Pages → Verified domains → Add a domain**,輸入 `harmonica.nycu.club`。GitHub 會顯示 TXT record 的完整主機名稱與驗證碼——把它填進上面第 2 筆。
3. 把兩筆 record **一次**寄給 SDC(避免來回)。
4. DNS 生效後確認:
   ```sh
   dig +short CNAME harmonica.nycu.club
   dig +short TXT _github-pages-challenge-nycu-harmonica.harmonica.nycu.club
   ```
5. 回到步驟 2 的頁面按 **Verify**。
6. 網站 repo → **Settings → Pages → Custom domain** 填 `harmonica.nycu.club`,等 HTTPS 憑證簽發完成後勾選 **Enforce HTTPS**。
7. 完成後,原 `https://nycu-harmonica.github.io/` 會自動導向新網域;deploy workflow 不需修改(baseURL 自動切換)。

## 寄給 SDC 的信件範本

> 主旨:申請 harmonica.nycu.club DNS record 設定(竹韻口琴社網站)
>
> 您好,竹韻口琴社已於 GitHub Pages 建置社團官網,煩請協助設定以下兩筆 DNS record:
>
> 1. `harmonica.nycu.club` CNAME `nycu-harmonica.github.io.`(TTL 3600)
> 2. `_github-pages-challenge-nycu-harmonica.harmonica.nycu.club` TXT `"<驗證碼>"`(TTL 3600)
>
> 第 2 筆為 GitHub Pages 的網域所有權驗證,建議長期保留。若有任何問題再麻煩告知,謝謝!
