#!/usr/bin/env python3
"""
AICA-SyS アプリロゴ生成スクリプト
"""

import os

from PIL import Image, ImageDraw, ImageFont


def create_logo():
    # ロゴのサイズ設定
    width, height = 200, 200
    
    # 画像を作成
    img = Image.new('RGB', (width, height), color='#667eea')
    draw = ImageDraw.Draw(img)
    
    # 背景グラデーション効果（簡易版）
    for y in range(height):
        color_value = int(255 * (1 - y / height * 0.3))
        draw.line([(0, y), (width, y)], fill=(color_value, color_value, 255))
    
    # テキストを描画
    try:
        # システムフォントを使用
        font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 32)
        font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
    except:
        # フォールバック
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # テキストの位置を計算
    text1 = "AICA"
    text2 = "SyS"
    text3 = "AI Content System"
    
    # テキストの境界ボックスを取得
    bbox1 = draw.textbbox((0, 0), text1, font=font_large)
    bbox2 = draw.textbbox((0, 0), text2, font=font_large)
    bbox3 = draw.textbbox((0, 0), text3, font=font_small)
    
    text1_width = bbox1[2] - bbox1[0]
    text2_width = bbox2[2] - bbox2[0]
    text3_width = bbox3[2] - bbox3[0]
    
    # 中央揃えでテキストを描画
    x1 = (width - text1_width) // 2
    x2 = (width - text2_width) // 2
    x3 = (width - text3_width) // 2
    
    y1 = height // 2 - 40
    y2 = height // 2 - 5
    y3 = height // 2 + 25
    
    # 白いテキストを描画
    draw.text((x1, y1), text1, fill='white', font=font_large)
    draw.text((x2, y2), text2, fill='white', font=font_large)
    draw.text((x3, y3), text3, fill='white', font=font_small)
    
    # ロゴを保存
    logo_path = 'public/logo.png'
    os.makedirs('public', exist_ok=True)
    img.save(logo_path)
    
    print(f"✅ ロゴを生成しました: {logo_path}")
    return logo_path

if __name__ == "__main__":
    create_logo()
