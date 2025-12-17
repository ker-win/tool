# -*- coding: utf-8 -*-
"""
影片畫質提升程式
使用 FFmpeg 進行 CPU 端的影片畫質增強處理

功能：
1. 解析度升級 (Upscale) - 使用 lanczos 高品質演算法
2. 銳化增強 (Sharpen) - 使用 unsharp 濾鏡
3. 降噪處理 (Denoise) - 使用 hqdn3d 濾鏡
4. 高品質編碼輸出
"""

import os
import sys
import io
import subprocess
from pathlib import Path

# 設定 stdout 為 UTF-8 編碼（解決 Windows 終端機 emoji 問題）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 載入設定
from config import (
    INPUT_FOLDER,
    OUTPUT_FOLDER,
    TARGET_WIDTH,
    TARGET_HEIGHT,
    SCALE_ALGORITHM,
    SHARPEN_AMOUNT,
    SHARPEN_LUMA_X,
    SHARPEN_LUMA_Y,
    ENABLE_DENOISE,
    DENOISE_LUMA_STRENGTH,
    DENOISE_CHROMA_STRENGTH,
    VIDEO_CODEC,
    ENCODE_PRESET,
    CRF_VALUE,
    MAX_BITRATE,
    AUDIO_CODEC,
    AUDIO_BITRATE,
    VIDEO_EXTENSIONS,
    OUTPUT_SUFFIX,
    OUTPUT_FORMAT
)


def check_ffmpeg() -> bool:
    """檢查 ffmpeg 是否已安裝"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_video_info(file_path: Path) -> dict:
    """
    使用 ffprobe 取得影片資訊
    
    Args:
        file_path: 影片檔案路徑
        
    Returns:
        包含影片資訊的字典
    """
    cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,duration,bit_rate',
        '-of', 'json',
        str(file_path)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        data = json.loads(result.stdout)
        if data.get('streams'):
            stream = data['streams'][0]
            return {
                'width': int(stream.get('width', 0)),
                'height': int(stream.get('height', 0)),
                'duration': float(stream.get('duration', 0)),
                'bitrate': int(stream.get('bit_rate', 0)) // 1000  # 轉換為 kbps
            }
    except Exception as e:
        print(f"  ⚠️ 無法取得影片資訊: {e}")
    return {}


def build_filter_chain() -> str:
    """
    建立 FFmpeg 濾鏡鏈
    
    Returns:
        濾鏡鏈字串
    """
    filters = []
    
    # 1. 縮放濾鏡 - 升級解析度
    scale_filter = f"scale={TARGET_WIDTH}:{TARGET_HEIGHT}:flags={SCALE_ALGORITHM}"
    filters.append(scale_filter)
    
    # 2. 銳化濾鏡
    sharpen_filter = f"unsharp={SHARPEN_LUMA_X}:{SHARPEN_LUMA_Y}:{SHARPEN_AMOUNT}:{SHARPEN_LUMA_X}:{SHARPEN_LUMA_Y}:0"
    filters.append(sharpen_filter)
    
    # 3. 降噪濾鏡 (可選)
    if ENABLE_DENOISE:
        denoise_filter = f"hqdn3d={DENOISE_LUMA_STRENGTH}:{DENOISE_CHROMA_STRENGTH}:{DENOISE_LUMA_STRENGTH}:{DENOISE_CHROMA_STRENGTH}"
        filters.append(denoise_filter)
    
    return ",".join(filters)


def enhance_video(input_path: Path, output_path: Path) -> bool:
    """
    執行影片畫質提升
    
    Args:
        input_path: 輸入影片路徑
        output_path: 輸出影片路徑
        
    Returns:
        bool: 處理是否成功
    """
    # 建立濾鏡鏈
    filter_chain = build_filter_chain()
    
    # 建立 FFmpeg 命令
    cmd = [
        'ffmpeg', '-y',  # 覆蓋已存在的檔案
        '-i', str(input_path),
        '-vf', filter_chain,
        '-c:v', VIDEO_CODEC,
        '-preset', ENCODE_PRESET,
        '-crf', str(CRF_VALUE),
        '-c:a', AUDIO_CODEC,
        '-b:a', AUDIO_BITRATE,
    ]
    
    # 如果設定了位元率上限
    if MAX_BITRATE > 0:
        cmd.extend(['-maxrate', f'{MAX_BITRATE}k', '-bufsize', f'{MAX_BITRATE * 2}k'])
    
    cmd.append(str(output_path))
    
    try:
        print(f"  ⏳ 正在處理中...")
        print(f"     濾鏡: {filter_chain}")
        
        # 執行 FFmpeg（顯示進度）
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if process.returncode == 0:
            return True
        else:
            print(f"  ❌ FFmpeg 錯誤:")
            print(process.stderr[-500:] if len(process.stderr) > 500 else process.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 處理失敗: {e}")
        return False


def get_output_filename(input_path: Path) -> Path:
    """
    產生輸出檔案名稱
    
    Args:
        input_path: 輸入檔案路徑
        
    Returns:
        輸出檔案路徑
    """
    stem = input_path.stem
    ext = OUTPUT_FORMAT if OUTPUT_FORMAT else input_path.suffix
    return Path(OUTPUT_FOLDER) / f"{stem}{OUTPUT_SUFFIX}{ext}"


def scan_and_enhance():
    """掃描並處理所有影片"""
    input_folder = Path(INPUT_FOLDER)
    output_folder = Path(OUTPUT_FOLDER)
    
    # 確保資料夾存在
    if not input_folder.exists():
        input_folder.mkdir(parents=True)
        print(f"📁 已建立輸入資料夾: {input_folder.absolute()}")
        print(f"   請將要處理的影片放入此資料夾後重新執行程式")
        return
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # 掃描影片檔案
    videos = []
    for file_path in input_folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
            videos.append(file_path)
    
    if not videos:
        print(f"⚠️ 輸入資料夾中沒有找到影片檔案")
        print(f"   路徑: {input_folder.absolute()}")
        print(f"   支援格式: {', '.join(VIDEO_EXTENSIONS)}")
        return
    
    print(f"📊 找到 {len(videos)} 個影片待處理\n")
    print(f"🎯 目標解析度: {TARGET_WIDTH} x {TARGET_HEIGHT}")
    print(f"🔧 縮放算法: {SCALE_ALGORITHM}")
    print(f"✨ 銳化強度: {SHARPEN_AMOUNT}")
    print(f"🔇 降噪: {'啟用' if ENABLE_DENOISE else '停用'}")
    print(f"📦 編碼品質 (CRF): {CRF_VALUE}")
    print("-" * 50)
    
    success_count = 0
    fail_count = 0
    
    for i, video_path in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}] 處理: {video_path.name}")
        
        # 取得原始影片資訊
        info = get_video_info(video_path)
        if info:
            print(f"  📐 原始解析度: {info.get('width', '?')} x {info.get('height', '?')}")
            if info.get('bitrate'):
                print(f"  📊 原始位元率: {info['bitrate']} kbps")
        
        # 產生輸出路徑
        output_path = get_output_filename(video_path)
        print(f"  📁 輸出: {output_path.name}")
        
        # 執行畫質提升
        if enhance_video(video_path, output_path):
            # 取得輸出影片資訊
            output_info = get_video_info(output_path)
            if output_info:
                print(f"  ✅ 處理完成!")
                print(f"     輸出解析度: {output_info.get('width', '?')} x {output_info.get('height', '?')}")
                if output_info.get('bitrate'):
                    print(f"     輸出位元率: {output_info['bitrate']} kbps")
            else:
                print(f"  ✅ 處理完成!")
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 處理完成!")
    print(f"   成功: {success_count} 個")
    if fail_count > 0:
        print(f"   失敗: {fail_count} 個")
    print(f"\n📂 輸出資料夾: {output_folder.absolute()}")


def main():
    print("=" * 50)
    print("🎬 影片畫質提升程式 (CPU 版)")
    print("=" * 50)
    
    # 檢查 FFmpeg
    if not check_ffmpeg():
        print("\n❌ 錯誤: 找不到 ffmpeg")
        print("   請先安裝 ffmpeg:")
        print("   方法1: winget install ffmpeg")
        print("   方法2: 從 https://ffmpeg.org/download.html 下載")
        print("   安裝後請確保 ffmpeg 在系統 PATH 中")
        sys.exit(1)
    
    print("✅ FFmpeg 已安裝\n")
    
    # 執行掃描與處理
    scan_and_enhance()


if __name__ == "__main__":
    main()
