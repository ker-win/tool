"""
影片分割程式
掃描資料夾中大於 200MB 的影片，並自動分割成 2 部分
分割後的影片留在原位置，原始大檔案移動到專用資料夾
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

# 設定
TARGET_FOLDER = r"D:\紫薇"  # 目標資料夾
SIZE_LIMIT_MB = 200  # 檔案大小限制 (MB)
ARCHIVE_FOLDER_NAME = "原檔_超過200MB"  # 存放原始大檔案的資料夾名稱
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}


def get_file_size_mb(file_path: Path) -> float:
    """取得檔案大小 (MB)"""
    return file_path.stat().st_size / (1024 * 1024)


def get_video_duration(file_path: Path) -> float:
    """使用 ffprobe 取得影片時長 (秒)"""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(file_path)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"  ❌ 無法取得影片時長: {e}")
        return 0


def split_video(file_path: Path, output_dir: Path = None) -> bool:
    """
    將影片分割成 2 部分，並將原始檔案移動到專用資料夾
    
    Args:
        file_path: 原始影片路徑
        output_dir: 輸出目錄 (預設為原始影片所在目錄)
    
    Returns:
        bool: 分割是否成功
    """
    if output_dir is None:
        output_dir = file_path.parent
    
    # 取得影片時長
    duration = get_video_duration(file_path)
    if duration <= 0:
        return False
    
    # 計算分割點 (一半)
    split_point = duration / 2
    
    # 準備輸出檔名
    stem = file_path.stem
    suffix = file_path.suffix
    
    part1_path = output_dir / f"{stem}_part1{suffix}"
    part2_path = output_dir / f"{stem}_part2{suffix}"
    
    print(f"  📎 影片時長: {duration:.2f} 秒")
    print(f"  ✂️ 分割點: {split_point:.2f} 秒")
    print(f"  📁 輸出:")
    print(f"      - {part1_path.name}")
    print(f"      - {part2_path.name}")
    
    # 分割第一部分 (從開始到分割點)
    cmd1 = [
        'ffmpeg', '-y', '-i', str(file_path),
        '-t', str(split_point),
        '-c', 'copy',  # 使用複製模式，不重新編碼，速度快
        str(part1_path)
    ]
    
    # 分割第二部分 (從分割點到結束)
    cmd2 = [
        'ffmpeg', '-y', '-i', str(file_path),
        '-ss', str(split_point),
        '-c', 'copy',
        str(part2_path)
    ]
    
    try:
        print("  ⏳ 正在分割第 1 部分...")
        subprocess.run(cmd1, capture_output=True, check=True)
        
        print("  ⏳ 正在分割第 2 部分...")
        subprocess.run(cmd2, capture_output=True, check=True)
        
        # 顯示分割後的檔案大小
        size1 = get_file_size_mb(part1_path)
        size2 = get_file_size_mb(part2_path)
        print(f"  ✅ 分割完成!")
        print(f"      - Part 1: {size1:.2f} MB")
        print(f"      - Part 2: {size2:.2f} MB")
        
        # 建立存放原始檔案的資料夾
        archive_folder = file_path.parent / ARCHIVE_FOLDER_NAME
        archive_folder.mkdir(exist_ok=True)
        
        # 移動原始檔案到專用資料夾
        archive_path = archive_folder / file_path.name
        shutil.move(str(file_path), str(archive_path))
        print(f"  📦 原始檔案已移動至: {ARCHIVE_FOLDER_NAME}/{file_path.name}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 分割失敗: {e}")
        # 清理可能產生的不完整檔案
        if part1_path.exists():
            part1_path.unlink()
        if part2_path.exists():
            part2_path.unlink()
        return False


def scan_and_split(folder_path: str, size_limit_mb: float = 200):
    """
    掃描資料夾並分割大於限制的影片
    
    Args:
        folder_path: 目標資料夾路徑
        size_limit_mb: 檔案大小限制 (MB)
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ 資料夾不存在: {folder}")
        return
    
    print(f"🔍 掃描資料夾: {folder}")
    print(f"📏 檔案大小限制: {size_limit_mb} MB")
    print("-" * 50)
    
    # 掃描所有影片檔案
    large_videos = []
    for file_path in folder.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
            size_mb = get_file_size_mb(file_path)
            if size_mb > size_limit_mb:
                large_videos.append((file_path, size_mb))
    
    if not large_videos:
        print("✅ 沒有發現大於限制的影片檔案")
        return
    
    print(f"📊 發現 {len(large_videos)} 個大於 {size_limit_mb} MB 的影片:\n")
    
    for i, (file_path, size_mb) in enumerate(large_videos, 1):
        print(f"[{i}/{len(large_videos)}] 處理: {file_path.name}")
        print(f"  📦 檔案大小: {size_mb:.2f} MB")
        
        success = split_video(file_path)
        
        if success:
            print()
        else:
            print("  ⚠️ 跳過此檔案\n")
    
    print("-" * 50)
    print("🎉 處理完成!")


def check_ffmpeg():
    """檢查 ffmpeg 是否已安裝"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    print("=" * 50)
    print("🎬 影片分割程式")
    print("=" * 50)
    
    # 檢查 ffmpeg
    if not check_ffmpeg():
        print("❌ 錯誤: 找不到 ffmpeg")
        print("   請先安裝 ffmpeg: https://ffmpeg.org/download.html")
        print("   或使用 winget: winget install ffmpeg")
        sys.exit(1)
    
    print("✅ ffmpeg 已安裝\n")
    
    # 執行掃描與分割
    scan_and_split(TARGET_FOLDER, SIZE_LIMIT_MB)


if __name__ == "__main__":
    main()
