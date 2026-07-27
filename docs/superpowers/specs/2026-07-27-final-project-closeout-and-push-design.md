# 最終專案收尾與遠端同步設計

## 目的

對目前已完成的台灣地震熱區探索器、最大震度分類模型與隨機森林說明簡報做一次完整、可驗證的最終收尾，將結果記錄在專案文件中，提交至本機 `main`，並推送到 `origin/main`。

本次只做驗證、記錄與同步，不新增功能、不重新部署 Vercel、不建立 Git tag。

## 收尾範圍

收尾內容包括：

- 地震資料處理流程與 1995–2026 資料範圍。
- React、deck.gl 地圖探索 MVP。
- 決策樹與隨機森林最大震度分類比較。
- 隨機森林結果 PowerPoint。
- 隨機森林前三層判斷邏輯 PowerPoint。
- 隨機森林特徵重要度 PowerPoint。

## 驗證

重新執行：

```powershell
python -W error::ResourceWarning -m unittest discover -s tests -p 'test_*.py' -v
npm.cmd test -- --run
npm.cmd run build
```

驗證三份 PowerPoint：

- `data/model/random-forest-results.pptx`
- `data/model/random-forest-three-level-explainer.pptx`
- `data/model/random-forest-feature-importance.pptx`

每份 PowerPoint 至少檢查：

- 檔案存在且大小大於 0。
- ZIP/OpenXML 套件沒有損壞成員。
- 投影片數與預期一致。
- 投影片比例為 16:9。
- 計算 SHA-256。

若任何測試、建置或 PowerPoint 驗證失敗，不得記錄為完成，也不得推送；必須先回報實際失敗。

## 文件更新

### `progress.md`

新增 `2026-07-27 Final Project Close-Out` 章節，記錄：

- 地圖 MVP、資料流程、模型比較與三份簡報已完成。
- 資料範圍為 1995–2026，共 16,691 筆輸出資料。
- 決策樹與隨機森林的最終 chronological test accuracy 與 macro recall。
- 特徵重要度的六項排序，以及空間、時間特徵合計。
- 三份 PowerPoint 的路徑、投影片數、大小與 SHA-256。
- 本次新鮮執行的 Python、Vitest、production build 與 OpenXML 驗證結果。
- 本機收尾 commit。
- 推送完成後的 `main` / `origin/main` 同步狀態。

因 commit SHA 在提交後才會確定、遠端同步狀態在推送後才會確定，允許使用兩筆收尾提交：

1. 第一筆提交記錄驗證與準備推送。
2. 推送後第二筆提交補上最終 commit／同步狀態，再次推送。

不得留下 `TBD`、占位符或聲稱尚未發生的推送結果。

### `todo.md`

新增 `Final Project Close-Out` 區段，全部勾選：

- 重新執行完整 Python 測試。
- 重新執行完整 Vitest。
- 重新執行 production build。
- 驗證三份 PowerPoint。
- 記錄最終成果與限制。
- 將 `main` 推送到 `origin/main`。

最後一項只能在推送成功後勾選。

## Git 與遠端同步

- 工作分支：本機 `main`。
- 遠端目標：`origin/main`。
- 在提交前確認 Git 變更範圍。
- 不加入、不修改、不刪除未追蹤的 `決策樹簡報小白解釋.txt`。
- 不強制推送。
- 推送前先確認遠端狀態；若遠端包含本機沒有的新提交，停止並回報，不自動 rebase 或 merge。
- 使用一般 fast-forward push 將本機 `main` 推送至 `origin/main`。
- 推送後重新抓取或檢查 refs，證明本機 `main` 與 `origin/main` 指向相同 commit。

## 成功標準

- Python 測試全部通過。
- Vitest 全部通過。
- Vite production build 成功；既有大型 chunk 警告可接受。
- 三份 PowerPoint 通過 ZIP/OpenXML、投影片數與 16:9 驗證。
- `progress.md` 與 `todo.md` 記錄完整且無占位符。
- `決策樹簡報小白解釋.txt` 保持未追蹤且未修改。
- 收尾提交已建立。
- 一般 push 成功。
- 最終本機 `main` 與 `origin/main` 指向相同 commit。

