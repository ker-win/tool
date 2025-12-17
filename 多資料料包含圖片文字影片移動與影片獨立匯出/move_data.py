# -*- coding: utf-8 -*-
"""
資料搬移程式
將 YouTube 分析資料從來源資料夾整理並搬移到目標資料夾

功能：
1. 讀取 analysis_results.json 取得觀看數範圍
2. 在目標資料夾建立 [日期]_[觀看範圍] 格式的資料夾
3. 建立 Video 和 DATA 子資料夾
4. 將影片搬移到 Video，其他檔案搬移到 DATA
5. 清空來源資料夾
"""

import os
import sys
import io
import json
import shutil
from datetime import datetime
from pathlib import Path

# 設定 stdout 為 UTF-8 編碼（解決 Windows 終端機 emoji 問題）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 載入設定
from config import (
    SOURCE_FOLDER,
    TARGET_ROOT_FOLDER,
    DATE_FORMAT,
    VIDEO_EXTENSIONS,
    VIDEO_SUBFOLDER_NAME,
    DATA_SUBFOLDER_NAME,
    CLEAR_SOURCE_AFTER_MOVE,
    ANALYSIS_JSON_FILENAME
)


def format_view_count(count: int) -> str:
    """
    將觀看數轉換為易讀格式
    
    Args:
        count: 觀看數
        
    Returns:
        格式化的字串（如 10K, 1M, 2.1M）
    """
    if count >= 1_000_000:
        value = count / 1_000_000
        if value == int(value):
            return f"{int(value)}M"
        return f"{value:.1f}M".rstrip('0').rstrip('.')  + "M" if '.' in f"{value:.1f}" else f"{int(value)}M"
    elif count >= 1_000:
        value = count / 1_000
        if value == int(value):
            return f"{int(value)}K"
        return f"{int(value)}K"  # 簡化為整數K
    else:
        return str(count)


def format_view_count_simple(count: int) -> str:
    """
    將觀看數轉換為簡化格式（只取整數部分）
    
    Args:
        count: 觀看數
        
    Returns:
        格式化的字串（如 10K, 1M, 2M）
    """
    if count >= 1_000_000:
        return f"{count // 1_000_000}M"
    elif count >= 1_000:
        return f"{count // 1_000}K"
    else:
        return str(count)


def get_view_count_range(json_path: str) -> tuple:
    """
    從 analysis_results.json 讀取觀看數範圍
    
    Args:
        json_path: JSON 檔案路徑
        
    Returns:
        (最小觀看數, 最大觀看數) 的 tuple
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    view_counts = [item['viewCount'] for item in data if 'viewCount' in item]
    
    if not view_counts:
        raise ValueError("JSON 檔案中沒有找到 viewCount 資料")
    
    return min(view_counts), max(view_counts)


def create_target_folder_name(min_views: int, max_views: int) -> str:
    """
    建立目標資料夾名稱
    
    Args:
        min_views: 最小觀看數
        max_views: 最大觀看數
        
    Returns:
        資料夾名稱（如 251217_112K-2M）
    """
    date_str = datetime.now().strftime(DATE_FORMAT)
    min_str = format_view_count_simple(min_views)
    max_str = format_view_count_simple(max_views)
    
    return f"{date_str}_{min_str}-{max_str}"


def is_video_file(filename: str) -> bool:
    """
    檢查檔案是否為影片
    
    Args:
        filename: 檔案名稱
        
    Returns:
        True 如果是影片檔案
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in VIDEO_EXTENSIONS


def move_data(source_folder: str, target_root: str) -> dict:
    """
    執行資料搬移
    
    Args:
        source_folder: 來源資料夾路徑
        target_root: 目標根資料夾路徑
        
    Returns:
        包含統計資訊的字典
    """
    stats = {
        'videos_moved': 0,
        'data_folders_moved': 0,
        'files_moved': 0,
        'target_folder': ''
    }
    
    # 確認來源資料夾存在
    if not os.path.exists(source_folder):
        raise FileNotFoundError(f"來源資料夾不存在: {source_folder}")
    
    # 確認目標根資料夾存在
    if not os.path.exists(target_root):
        raise FileNotFoundError(f"目標資料夾不存在: {target_root}")
    
    # 讀取 JSON 取得觀看數範圍
    json_path = os.path.join(source_folder, ANALYSIS_JSON_FILENAME)
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"找不到 {ANALYSIS_JSON_FILENAME}: {json_path}")
    
    min_views, max_views = get_view_count_range(json_path)
    print(f"📊 觀看數範圍: {min_views:,} ~ {max_views:,}")
    
    # 建立目標資料夾
    folder_name = create_target_folder_name(min_views, max_views)
    target_folder = os.path.join(target_root, folder_name)
    
    if os.path.exists(target_folder):
        print(f"⚠️  目標資料夾已存在，將繼續使用: {target_folder}")
    else:
        os.makedirs(target_folder)
        print(f"📁 建立目標資料夾: {target_folder}")
    
    stats['target_folder'] = target_folder
    
    # 建立 Video 和 DATA 子資料夾
    video_folder = os.path.join(target_folder, VIDEO_SUBFOLDER_NAME)
    data_folder = os.path.join(target_folder, DATA_SUBFOLDER_NAME)
    
    os.makedirs(video_folder, exist_ok=True)
    os.makedirs(data_folder, exist_ok=True)
    print(f"📁 建立子資料夾: {VIDEO_SUBFOLDER_NAME}, {DATA_SUBFOLDER_NAME}")
    
    # 遍歷來源資料夾
    for item in os.listdir(source_folder):
        item_path = os.path.join(source_folder, item)
        
        # 如果是 analysis_results.json，搬移到 DATA
        if item == ANALYSIS_JSON_FILENAME:
            dest_path = os.path.join(data_folder, item)
            shutil.move(item_path, dest_path)
            print(f"📄 搬移 {item} -> DATA/")
            stats['files_moved'] += 1
            continue
        
        # 如果是資料夾，處理其內容
        if os.path.isdir(item_path):
            # 在 DATA 中建立對應的子資料夾
            data_subfolder = os.path.join(data_folder, item)
            os.makedirs(data_subfolder, exist_ok=True)
            
            # 遍歷子資料夾中的檔案
            for file in os.listdir(item_path):
                file_path = os.path.join(item_path, file)
                
                if os.path.isfile(file_path):
                    if is_video_file(file):
                        # 影片搬移到 Video 資料夾
                        dest_path = os.path.join(video_folder, file)
                        shutil.move(file_path, dest_path)
                        print(f"🎬 搬移影片: {file} -> Video/")
                        stats['videos_moved'] += 1
                    else:
                        # 其他檔案搬移到 DATA 對應子資料夾
                        dest_path = os.path.join(data_subfolder, file)
                        shutil.move(file_path, dest_path)
                        stats['files_moved'] += 1
            
            stats['data_folders_moved'] += 1
            
            # 刪除空的來源子資料夾
            if not os.listdir(item_path):
                os.rmdir(item_path)
    
    print(f"\n✅ 搬移完成!")
    print(f"   - 影片: {stats['videos_moved']} 個")
    print(f"   - 資料夾: {stats['data_folders_moved']} 個")
    print(f"   - 其他檔案: {stats['files_moved']} 個")
    
    return stats


def main():
    """主程式"""
    print("=" * 60)
    print("📦 YouTube 分析資料搬移程式")
    print("=" * 60)
    print(f"\n來源: {SOURCE_FOLDER}")
    print(f"目標: {TARGET_ROOT_FOLDER}\n")
    
    try:
        stats = move_data(SOURCE_FOLDER, TARGET_ROOT_FOLDER)
        
        if CLEAR_SOURCE_AFTER_MOVE:
            # 確認來源資料夾已清空
            remaining = os.listdir(SOURCE_FOLDER)
            if remaining:
                print(f"\n⚠️  來源資料夾中仍有 {len(remaining)} 個項目未搬移")
            else:
                print(f"\n🧹 來源資料夾已清空")
        
        print(f"\n📍 目標資料夾: {stats['target_folder']}")
        
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
