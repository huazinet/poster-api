# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import random
import requests
from pathlib import Path
import os

# GitHub 仓库信息
GITHUB_REPO = "huazinet/dazibao-assets"  # 请替换成你实际的 GitHub 仓库地址
GITHUB_BRANCH = "main"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}"

def get_github_file_list(path):
    """获取 GitHub 仓库中指定路径下的文件列表"""
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    response = requests.get(api_url)
    if response.status_code == 200:
        files = response.json()
        return [f for f in files if f['type'] == 'file']
    return []

def get_random_file_url(path, extensions):
    """获取随机文件的 URL"""
    files = get_github_file_list(path)
    valid_files = [f for f in files if any(f['name'].lower().endswith(ext) for ext in extensions)]
    if not valid_files:
        return None
    chosen_file = random.choice(valid_files)
    return f"{GITHUB_RAW_URL}/{path}/{chosen_file['name']}"

def get_font():
    """获取字体"""
    try:
        # 首先尝试使用系统字体
        system_fonts = [
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.otf",
            "/System/Library/Fonts/PingFang.ttc",
            "C:\\Windows\\Fonts\\msyh.ttc",
        ]
        
        for font_path in system_fonts:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size=1)

        # 如果系统字体都不可用，尝试从 GitHub 获取字体
        font_url = f"{GITHUB_RAW_URL}/fonts/NotoSansSC-Bold.otf"
        response = requests.get(font_url)
        if response.status_code == 200:
            font_data = io.BytesIO(response.content)
            return ImageFont.truetype(font_data, size=1)  # size会在后面重新设置
    except Exception as e:
        print(f"字体加载错误: {str(e)}")
        
    # 如果都失败了，使用默认字体
    return ImageFont.load_default()

def calculate_font_size(text: str, max_width: int, font) -> int:
    """计算合适的字体大小"""
    try:
        test_size = 100
        font = font.font_variant(size=test_size)
        text_width = font.getlength(text)
        return int(test_size * (max_width / text_width) * 0.95)
    except Exception as e:
        print(f"计算字体大小错误: {str(e)}")
        return 50

def create_png_image(text: str) -> bytes:
    """创建图片"""
    try:
        # 确保文本是 UTF-8 编码
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        
        # 获取随机背景图片
        img_url = get_random_file_url('images', ['png', 'jpg', 'jpeg'])
        if img_url:
            response = requests.get(img_url)
            if response.status_code == 200:
                img_data = io.BytesIO(response.content)
                with Image.open(img_data) as template:
                    template = template.convert('RGB')
                    # 调整图片大小以减少内存使用
                    template.thumbnail((800, 600), Image.Resampling.LANCZOS)
                    image = template
            else:
                image = Image.new('RGB', (800, 600), color='white')
        else:
            image = Image.new('RGB', (800, 600), color='white')

        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # 获取字体
        base_font = get_font()
        
        # 分割文本并处理特殊字符
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                # 移除不可见字符和控制字符
                line = ''.join(char for char in line if ord(char) >= 32)
                lines.append(line)
        
        if len(lines) == 2:
            # 两行文字
            main_title_size = min(calculate_font_size(lines[0], width * 0.8, base_font), 100)
            main_font = base_font.font_variant(size=main_title_size)
            subtitle_size = min(int(main_title_size * 0.7), 70)
            subtitle_font = base_font.font_variant(size=subtitle_size)
            
            draw.text((width/2, height*0.4), lines[0], 
                     font=main_font, fill="#000000", anchor="mm")
            draw.text((width/2, height*0.65), lines[1], 
                     font=subtitle_font, fill="#000000", anchor="mm")
        else:
            # 三行文字
            main_title_size = min(calculate_font_size(lines[0], width * 0.8, base_font), 80)
            main_font = base_font.font_variant(size=main_title_size)
            subtitle_size = min(int(main_title_size * 0.6), 60)
            subtitle_font = base_font.font_variant(size=subtitle_size)
            small_title_size = min(int(main_title_size * 0.4), 40)
            small_font = base_font.font_variant(size=small_title_size)
            
            draw.text((width/2, height*0.3), lines[0], 
                     font=main_font, fill="#000000", anchor="mm")
            if len(lines) > 1:
                draw.text((width/2, height*0.5), lines[1], 
                         font=subtitle_font, fill="#000000", anchor="mm")
            if len(lines) > 2:
                draw.text((width/2, height*0.7), lines[2], 
                         font=small_font, fill="#000000", anchor="mm")
        
        # 优化内存使用
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG', optimize=True, quality=85)
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()
    
    except Exception as e:
        print(f"创建图片错误: {str(e)}")
        # 创建错误提示图片
        error_img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(error_img)
        font = ImageFont.load_default()
        draw.text((400, 300), f"Error: {str(e)}", fill="black", anchor="mm", font=font)
        
        img_byte_arr = io.BytesIO()
        error_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({"status": "API is running"}).encode())

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # 确保 JSON 解码使用 UTF-8
            data = json.loads(post_data.decode('utf-8'))

            if 'text' not in data:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "Missing required parameter: text"
                }).encode())
                return

            # 生成图片
            png_data = create_png_image(data['text'])
            
            # 转换为 base64
            base64_data = base64.b64encode(png_data).decode('utf-8')
            
            self._set_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "data": base64_data
            }).encode('utf-8'))  # 确保使用 UTF-8 编码

        except Exception as e:
            print(f"处理请求错误: {str(e)}")
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode('utf-8'))  # 确保使用 UTF-8 编码
