# 隨機森林分類結果 PowerPoint 設計

## 目標

建立一份隨機森林專用的兩頁 16:9 PowerPoint，清楚呈現模型準確率、各震度等級命中率與 support，以及完整混淆矩陣。簡報必須能由既有模型產物重跑產生，不依賴手動編輯。

## 輸入資料

產生器讀取以下既有產物：

- `data/model/random_forest_metrics.json`
- `data/model/random_forest_confusion_matrix.png`

metrics JSON 是所有數值與文字結論的唯一資料來源；混淆矩陣 PNG 必須與 metrics JSON 的 8×8 matrix、labels 與 support 一致。輸入不存在、標籤不是 0–7、矩陣尺寸錯誤或 support 不一致時停止產生簡報並回報具體錯誤。

## 第 1 頁：隨機森林分類結果

第 1 頁包含：

- 標題「隨機森林最大震度分類結果」。
- 測試 Accuracy 與 Macro Recall。
- 訓練期間 1995–2023、13,617 筆。
- 測試期間 2024–2026、3,039 筆。
- 最佳參數：`n_estimators=200`、`max_depth=12`、`min_samples_leaf=1`、`max_features=sqrt`、`class_weight=balanced_subsample`、`random_state=42`。
- 震度 0–7 的 recall 與 support；support 為零時顯示 N/A，不顯示 0% 命中率。
- 稀有類別限制：震度 0 僅 1 筆、震度 6 僅 4 筆、震度 7 沒有測試樣本，因此不可將稀有類別 recall 視為穩定結論。
- 明確說明這是最大震度分類，不是地震預測或預報。

版面採上方標題、左側核心指標與期間、右側各類別表格、下方限制說明。沿用目前模型結果簡報的深藍、青綠、琥珀與米白色系，以及 Microsoft JhengHei 中文字體。

## 第 2 頁：混淆矩陣

第 2 頁包含：

- 標題「隨機森林混淆矩陣」。
- 大尺寸嵌入 `random_forest_confusion_matrix.png`，保持原始比例且不得裁掉軸標、刻度或色條。
- 清楚說明縱軸為實際震度、橫軸為預測震度。
- 摘要觀察：主要樣本集中於震度 2–4，這些相鄰類別之間仍有混淆。
- 再次標註震度 0、6、7 的 support 過少，避免誤讀單一格或 recall。

混淆矩陣是頁面主體，摘要文字置於側邊或下方，不壓縮矩陣到難以閱讀。

## 產生器與輸出

新增獨立產生器：

`scripts/create_random_forest_results_powerpoint.py`

預設指令：

```powershell
python scripts/create_random_forest_results_powerpoint.py
```

預設輸出：

`data/model/random-forest-results.pptx`

產生器接受 metrics、matrix PNG 與 output 路徑參數，方便測試使用臨時 fixture。既有決策樹／隨機森林比較 PowerPoint 不被此工作取代或重新命名。

## 測試與驗收

依 TDD 實作，先建立失敗測試再新增產生器。測試至少驗證：

- 產物是可讀取且 ZIP/OpenXML 完整的 PowerPoint。
- 恰好兩頁，比例為 16:9。
- 第 1 頁包含模型名稱、Accuracy、Macro Recall、期間、筆數、最佳參數、震度 0–7 recall/support、稀有類別限制與非預測聲明。
- 第 2 頁包含混淆矩陣標題、實際／預測軸說明、主要混淆觀察與稀有類別提醒。
- 第 2 頁確實嵌入指定 PNG，且圖片在頁面範圍內、尺寸足以作為主體。
- 不相容的 labels、matrix 或 support 會被拒絕，且不留下不完整 PPTX。
- 使用真實產物重建後，PowerPoint 仍是兩頁 16:9，並通過 OpenXML integrity check。

完成後更新 README 重跑指令、`todo.md` 與 `progress.md`，並記錄實際輸出路徑與驗證結果。

