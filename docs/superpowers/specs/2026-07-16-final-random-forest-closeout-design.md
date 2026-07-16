# 隨機森林成果最終收尾設計

## 目標

將隨機森林模型比較與兩頁結果 PowerPoint 工作正式結案，使專案紀錄完整、交付物可重跑、Git 工作樹乾淨，且不把無關的二進位重建差異混入收尾提交。

## Git 範圍

- 將 `data/model/decision-tree-results-review.pptx` 恢復為目前 `main` 已提交版本。這個未提交差異來自先前重跑，並非本次隨機森林專用兩頁簡報的交付物。
- 保留並確認 `data/model/random-forest-results.pptx`、產生器、測試、README、todo 與既有 progress 紀錄。
- 最終提交只新增收尾紀錄，不重新產生或修改模型結果與 PowerPoint。

## 收尾紀錄

在 `progress.md` 新增 `2026-07-16 Random-Forest Final Close-Out`，至少記錄：

- 決策樹與隨機森林比較已完成。
- 隨機森林專用兩頁 PowerPoint 已完成。
- 最終 PowerPoint 路徑、大小與 SHA-256。
- Accuracy 43.90%、Macro Recall 40.81%。
- 各震度 recall/support 與稀有類別限制已納入簡報。
- 混淆矩陣由已驗證的 metrics JSON 直接繪製。
- 產生器、重跑指令與自動化測試已保留。
- 完整 Python、Vitest、production build 與 PowerPoint 結構驗證結果。
- 本機 `main` 尚未推送至 GitHub。

`todo.md` 目前所有相關項目已完成，因此不新增重複任務；只確認沒有未勾選項。

## 最終驗證

收尾提交前執行：

- 完整 Python unittest，並將 ResourceWarning 視為錯誤。
- 完整 Vitest。
- production build；既有大型 chunk warning 可接受。
- PowerPoint ZIP/OpenXML、兩頁、16:9、Accuracy、Macro Recall、第二頁矩陣圖片與 SHA-256 檢查。
- `git diff --check`、`git status --short` 與未完成 todo 掃描。

驗證全部通過後，提交 `progress.md` 收尾紀錄，最終工作樹必須乾淨。

