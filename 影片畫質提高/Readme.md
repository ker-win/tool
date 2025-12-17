# 影片畫質提升程式 (CPU 版)

## 功能說明

此程式使用 FFmpeg 在 CPU 上進行影片畫質提升，適合沒有 GPU 的使用者。

### 主要功能

- 🎯 **解析度升級**: 將低解析度影片升級至 1080x1920 (短影音標準)
- ✨ **銳化增強**: 使用 unsharp 濾鏡提升影像清晰度
- 🔇 **降噪處理**: 使用 hqdn3d 濾鏡減少影像雜訊
- 📦 **高品質編碼**: 使用 H.264 編碼器和較低的 CRF 值確保畫質

## 系統需求

- Python 3.6+
- **FFmpeg** (必須安裝)

### 安裝 FFmpeg

```powershell
# 方法1: 使用 winget (推薦)
winget install ffmpeg

# 方法2: 使用 chocolatey
choco install ffmpeg
```

或從 [FFmpeg 官網](https://ffmpeg.org/download.html) 下載並加入系統 PATH。

## 檔案結構

```
影片畫質提高/
├── config.py          # 設定檔
├── enhance_video.py   # 主程式
├── Readme.md          # 說明文件
├── input/             # 放入原始影片
└── output/            # 輸出處理後的影片
```

## 使用方式

### 1. 放入影片

將要處理的影片放入 `input` 資料夾（首次執行會自動建立）

### 2. 執行程式

```powershell
cd c:\Users\qpalz\Desktop\Tool\影片畫質提高
python enhance_video.py
```

### 3. 取得結果

處理完成的影片會輸出到 `output` 資料夾，檔名加上 `_enhanced` 後綴

## 設定說明

編輯 `config.py` 可調整以下參數：

### 解析度設定
```python
TARGET_WIDTH = 1080    # 目標寬度
TARGET_HEIGHT = 1920   # 目標高度 (9:16 短影音)
```

### 銳化設定
```python
SHARPEN_AMOUNT = 1.0   # 銳化強度 (0.5-1.5)
```

### 降噪設定
```python
ENABLE_DENOISE = True           # 是否啟用降噪
DENOISE_LUMA_STRENGTH = 3       # 降噪強度 (0-10)
```

### 編碼品質
```python
CRF_VALUE = 18         # 品質值 (18=視覺無損, 23=標準)
ENCODE_PRESET = "slower"  # 編碼速度 (slower=高品質但慢)
```

## 輸出範例

```
==================================================
🎬 影片畫質提升程式 (CPU 版)
==================================================
✅ FFmpeg 已安裝

📊 找到 1 個影片待處理

🎯 目標解析度: 1080 x 1920
🔧 縮放算法: lanczos
✨ 銳化強度: 1.0
🔇 降噪: 啟用
📦 編碼品質 (CRF): 18
--------------------------------------------------

[1/1] 處理: video.mp4
  📐 原始解析度: 704 x 1280
  📊 原始位元率: 3644 kbps
  📁 輸出: video_enhanced.mp4
  ⏳ 正在處理中...
  ✅ 處理完成!
     輸出解析度: 1080 x 1920
     輸出位元率: 6500 kbps

==================================================
🎉 處理完成!
   成功: 1 個

📂 輸出資料夾: c:\Users\qpalz\Desktop\Tool\影片畫質提高\output
```

## 支援的影片格式

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WebM (.webm)
- WMV (.wmv)
- FLV (.flv)
- M4V (.m4v)

## 注意事項

1. **CPU 處理**: 由於使用 CPU 運算，處理時間較長，請耐心等待
2. **磁碟空間**: 輸出影片檔案較大，請確保有足夠空間
3. **原始檔案**: 原始影片不會被修改或刪除

---

## 更新紀錄

### 2025-12-17
- 新增 `config.py` 設定檔
- 新增 `enhance_video.py` 主程式
- 支援 lanczos 高品質縮放
- 支援 unsharp 銳化濾鏡
- 支援 hqdn3d 降噪濾鏡
- 支援 H.264 高品質編碼
