# 隨機森林最大震度分類與模型比較設計

## 目標

保留既有決策樹最大震度分類器，新增可重跑的隨機森林分類流程，並在完全相同的資料、特徵、時間切分與評估指標下比較兩個模型。比較結果必須忠實呈現實測表現，不預設隨機森林一定優於決策樹。

## 範圍

本次工作包含：

- 抽出決策樹與隨機森林共用的資料載入、特徵建立、時間切分、評估與產物輸出邏輯。
- 保留現有決策樹訓練入口、輸出名稱與可重跑行為。
- 新增隨機森林訓練入口與獨立產物。
- 產生兩模型的比較表。
- 更新一頁模型結果 PowerPoint 與結案報告中的模型比較內容。
- 更新自動化測試、README、todo 與 progress。

本次不增加新特徵、不更換目標標籤定義、不改成隨機資料切分，也不擴充為即時預測服務。

## 資料與特徵

兩個模型共用目前處理完成的 `data/processed/earthquakes.csv`。

最大震度標籤延續既有正規化規則：數字 0–7 保持原類別，`5弱` 與 `5強` 合併為 5，`6弱` 與 `6強` 合併為 6。缺少或無法正規化最大震度的資料列排除於模型訓練與評估之外，並在 metrics 中保留排除筆數。

兩個模型使用完全相同的六項特徵：

1. magnitude
2. depth_km
3. longitude
4. latitude
5. event month
6. event hour

為避免輸入順序影響可重現性，共用資料層須先依穩定鍵排序，再交給模型選擇與訓練流程。

## 時間切分與模型選擇

最終訓練期間固定為 1995–2023，最終測試期間固定為 2024–2026。測試資料不得參與參數選擇。

隨機森林的參數選擇沿用決策樹的時間序列原則：使用訓練期間內的 2021–2023 作驗證集，較早年份作參數搜尋的擬合集。選出參數後，再用完整 1995–2023 資料重新擬合，最後只在 2024–2026 測試一次。

候選參數網格如下：

- `n_estimators`: 200、500
- `max_depth`: 12、20、`None`
- `min_samples_leaf`: 1、3、5
- `max_features`: `sqrt`
- `class_weight`: `balanced_subsample`
- `random_state`: 42

主要選模指標為 validation macro recall。若候選模型的 macro recall 相同，依 validation accuracy 排序；若仍相同，優先選擇較簡單且計算量較低的模型，排序依序為較少樹、較淺深度、較大的 `min_samples_leaf`。選模摘要須記錄驗證期間、所有最終選定參數、macro recall 與 accuracy。

## 程式架構

新增一個共用模型模組，集中負責以下工作：

- 讀取與驗證處理後 CSV。
- 正規化最大震度標籤。
- 建立六項特徵。
- 建立訓練、驗證與測試時間切分。
- 計算 accuracy、macro recall、各類別 recall、support 與 0–7 完整混淆矩陣。
- 寫出 metrics JSON、class report CSV、confusion matrix CSV／PNG 與 joblib 模型。

`scripts/train_intensity_classifier.py` 保留為決策樹入口，改用共用模組但維持既有公開函式與產物名稱，避免破壞既有測試與重跑指令。

新增獨立的隨機森林入口。它只負責隨機森林的候選模型建立、參數選擇與呼叫共用輸出流程，使模型特有邏輯與共用評估邏輯保持分離。

新增比較產物產生器，讀取兩份已完成的 metrics JSON，驗證資料期間、測試筆數、標籤與 support 相容後才寫出比較表。若任一模型產物缺失或比較基準不同，應以清楚錯誤停止，不產生可能誤導的比較結果。

## 輸出產物

既有決策樹產物維持不變：

- `decision_tree_metrics.json`
- `decision_tree_class_report.csv`
- `decision_tree_confusion_matrix.csv`
- `decision_tree_confusion_matrix.png`
- `decision_tree_model.joblib`（本機產物、Git 忽略）

新增隨機森林產物：

- `random_forest_metrics.json`
- `random_forest_class_report.csv`
- `random_forest_confusion_matrix.csv`
- `random_forest_confusion_matrix.png`
- `random_forest_model.joblib`（本機產物、Git 忽略）

新增 `model_comparison.csv`，至少包含兩個模型的 test accuracy、test macro recall，以及震度 0–7 的 recall 與 support。support 理論上應一致；產生器仍須顯式驗證並拒絕不一致輸入。

模型結果 PowerPoint 更新為同頁比較兩個模型，包含：訓練／測試期間、樣本筆數、accuracy、macro recall、各震度 recall 與 support、混淆矩陣或其可讀摘要、最佳參數、勝出指標及稀有類別限制。結案報告只更新與模型名稱及比較結論直接相關的內容，不重新設計其他頁面。

## 錯誤處理與產物安全

遇到下列情況時流程必須停止並提供具體訊息：

- 輸入 CSV 不存在或缺少必要欄位。
- 沒有可用訓練列、驗證列或測試列。
- 模型 metrics 缺少比較所需欄位。
- 兩模型使用不同測試期間、測試筆數、標籤或 support。
- 輸出目錄不可建立或產物不可寫入。

隨機森林訓練失敗時不得覆蓋既有決策樹產物。各模型先完成評估，再寫入各自命名空間；比較表只在兩份 metrics 均可驗證後產生。

## 測試策略

所有行為變更依 TDD 進行，先新增會失敗的測試並確認失敗原因，再寫最小實作。

測試至少涵蓋：

- 決策樹與隨機森林取得相同的資料列、特徵欄位與時間切分。
- 隨機森林固定 `random_state=42`，且反轉輸入資料順序後仍選出相同參數與摘要。
- 驗證資料僅來自 2021–2023，測試資料僅來自 2024–2026。
- 0–7 全部類別固定出現在 metrics、class report 與混淆矩陣，即使某類 support 為零。
- 隨機森林 joblib 模型重新載入後得到相同混淆矩陣與 support。
- `model_comparison.csv` 的值與兩份 metrics JSON 一致。
- 比較產生器拒絕期間、測試筆數、標籤或 support 不相容的 metrics。
- PowerPoint 包含兩個模型名稱、主要指標、比較結論與稀有類別警告。
- 既有決策樹測試仍全部通過，確認重構未改變其外部行為。

## 驗收條件

完成時必須能證明：

- 決策樹與隨機森林均可由獨立指令重跑。
- 兩者使用相同資料、特徵、時間切分與 0–7 評估定義。
- 隨機森林依 2021–2023 validation macro recall 選模，未接觸 2024–2026 測試資料。
- 所有隨機森林產物與 `model_comparison.csv` 已產生且內容互相一致。
- 結果簡報與結案報告忠實反映實測比較，不誇大稀有類別指標。
- Python 全套測試、前端測試與 production build 通過。
- `README.md`、`todo.md` 與 `progress.md` 已記錄重跑方式、結果與限制。

