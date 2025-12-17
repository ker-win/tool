# 多資料包含圖片文字影片移動與影片獨立匯出

## 功能說明

此程式用於將 YouTube 分析資料從來源資料夾整理並搬移到目標資料夾。

### 主要功能

1. 讀取 `analysis_results.json` 取得觀看數範圍
2. 在目標資料夾自動建立 `[日期]_[觀看範圍]` 格式的資料夾（如 `251217_112K-2M`）
3. 建立 `Video` 和 `DATA` 子資料夾
4. 將影片檔案(.mp4等)搬移到 `Video` 資料夾
5. 將其他檔案（圖片、文字等）保持原有子資料夾結構搬移到 `DATA` 資料夾
6. 完成後清空來源資料夾

## 檔案結構

```
├── config.py      # 設定檔（可修改來源/目標路徑、日期格式等）
├── move_data.py   # 主程式
└── Readme.md      # 說明文件
```

## 使用方式

### 1. 修改設定

編輯 `config.py` 設定以下參數：

```python
# 來源資料夾路徑
SOURCE_FOLDER = r"C:\來源路徑"

# 目標根資料夾路徑
TARGET_ROOT_FOLDER = r"D:\目標路徑"

# 日期格式（%y%m%d = 251217, %Y%m%d = 20251217）
DATE_FORMAT = "%y%m%d"
```

### 2. 執行程式

```powershell
cd c:\Users\qpalz\Desktop\Tool\多資料料包含圖片文字影片移動與影片獨立匯出
python move_data.py
```

## 輸出範例

執行後會在目標資料夾建立如下結構：

```
重逢狗狗系列/
└── 251217_112K-2M/
    ├── Video/
    │   ├── video1.mp4
    │   └── video2.mp4
    └── DATA/
        ├── analysis_results.json
        ├── videoId1/
        │   ├── image1.png
        │   └── title.txt
        └── videoId2/
            ├── image2.png
            └── description.txt
```

---

## 更新紀錄

### 2025-12-17
- 新增 `config.py` 設定檔
- 新增 `move_data.py` 資料搬移主程式
- 支援自動計算觀看數範圍並格式化（K/M）
- 支援自動建立日期資料夾
