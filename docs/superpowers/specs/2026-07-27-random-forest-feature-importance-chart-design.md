# 隨機森林特徵重要度圖 PowerPoint 設計

## 目的

製作一頁 16:9 PowerPoint，以排序水平長條圖呈現目前隨機森林最大震度分類模型的六項真實特徵重要度，讓非技術觀眾能同時看見模型依據與可解讀的洞見。

本圖解釋模型在分類時對各特徵的相對依賴程度，不宣稱特徵與震度之間存在因果關係，也不暗示模型可以預測地震是否發生。

## 資料來源

- 模型：`data/model/random_forest_model.joblib`
- 特徵順序：
  1. `magnitude`：規模
  2. `depth_km`：深度
  3. `longitude`：經度
  4. `latitude`：緯度
  5. `month`：月份
  6. `hour`：時刻
- 數值來源：模型的 `feature_importances_`。

產生器必須直接讀取現有 `.joblib` 模型，不得在程式中手動寫死重要度。模型必須恰好提供上述六項特徵的重要度，數值須為有限非負數且總和接近 1。

目前模型的實測結果為：

- 規模：31.13%
- 緯度：21.80%
- 深度：15.96%
- 經度：14.06%
- 時刻：9.52%
- 月份：7.53%

## 投影片內容

輸出為一頁 16:9 投影片，標題為：

> 什麼特徵最影響最大震度分類？

副標為：

> 隨機森林特徵重要度｜數值越高，模型越常依賴該特徵做判斷

左側約 70% 顯示由高至低排列的六項水平長條：

- 每一列顯示繁體中文特徵名稱。
- 每一條末端顯示百分比，保留兩位小數。
- 規模使用主色突出，其餘使用同色系深淺。
- 圖表尺度自 0 開始，所有長條共用相同比例。
- 圖表必須包含全部六項特徵，重要度合計為 100%。

右側顯示三張洞見卡，文字由實際模型數值動態產生：

1. `規模是最重要的單一特徵（31.13%）`
2. `經緯度合計 35.86%，顯示地理位置整體影響高於單一規模`
3. `月份與時刻合計 17.05%，時間訊號存在，但不是主要依據`

若未來模型數值改變，洞見文字中的百分比與比較敘述必須跟著更新。若經緯度合計不再高於最高單一特徵，第二張卡不得保留「高於」結論；若時間特徵合計超過事件或空間特徵，第三張卡也必須使用中性描述，避免寫出與數值矛盾的洞見。

頁尾限制說明：

> 重要度代表模型使用程度，不等於因果關係；經緯度也可能共同反映區域差異。本模型是最大震度分類，不是地震預測。

## 視覺方向

- 使用適合投影的淺色背景與高對比深色文字。
- 圖表採水平排列，避免中文特徵名稱旋轉。
- 規模使用醒目的青綠主色；其他長條使用較低彩度的同色系。
- 洞見卡使用一致的卡片結構，以大數字或關鍵詞建立閱讀層級。
- 文字以繁體中文為主。
- 全部文字使用 Microsoft JhengHei，並在 DrawingML 中同時設定 Latin 與 East Asian typeface。
- 所有圖形、文字與連線必須位於投影片安全邊界內，不得重疊或裁切。

## 產物與重跑方式

預計新增：

- PowerPoint 產生器：`scripts/create_random_forest_feature_importance_powerpoint.py`
- PowerPoint：`data/model/random-forest-feature-importance.pptx`
- 自動化測試：`tests/test_create_random_forest_feature_importance_powerpoint.py`

不覆蓋既有的：

- `data/model/random-forest-results.pptx`
- `data/model/random-forest-three-level-explainer.pptx`

重跑命令：

```powershell
python scripts/create_random_forest_feature_importance_powerpoint.py
```

## 錯誤處理

- 模型不存在或無法載入時，回報清楚的路徑與錯誤。
- 模型缺少 `feature_importances_`、特徵數不是六項、包含負值或非有限數值、或總和不接近 1 時，拒絕產生投影片。
- 先寫入同目錄暫存檔，通過 ZIP/OpenXML、一頁與 16:9 驗證後才原子取代正式輸出。
- 產生或驗證失敗時，保留既有正式輸出並清除暫存檔。

## 驗證標準

- PowerPoint ZIP/OpenXML 結構完整。
- 恰好一張投影片，比例為 16:9。
- 包含六條水平長條，順序與模型重要度排名一致。
- 百分比、合計與洞見文字均可由模型 `feature_importances_` 重新計算核對。
- 長條長度使用相同尺度，且與重要度成比例。
- 所有文字 run 同時設定 Microsoft JhengHei Latin 與 East Asian typeface。
- 所有形狀均位於投影片範圍內。
- 原子寫入失敗保護有自動化測試。
- 完整 Python 測試、Vitest 與正式版建置仍通過。

