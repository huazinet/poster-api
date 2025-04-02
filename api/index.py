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
GITHUB_REPO = "huazinet/dazibao-assets"
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
    print("开始加载字体...")
    
    # 首先尝试从 GitHub 获取字体
    try:
        print("尝试从 GitHub 获取字体...")
        font_url = f"{GITHUB_RAW_URL}/fonts/NotoSansSC-Bold.otf"
        response = requests.get(font_url)
        if response.status_code == 200:
            print("成功从 GitHub 获取字体")
            font_data = io.BytesIO(response.content)
            try:
                font = ImageFont.truetype(font_data, size=50)  # 使用更大的初始大小
                # 测试字体是否可用
                test_text = "测试文字"
                font.getlength(test_text)
                print("GitHub 字体加载成功并通过测试")
                return font
            except Exception as e:
                print(f"GitHub 字体测试失败: {str(e)}")
    except Exception as e:
        print(f"从 GitHub 获取字体失败: {str(e)}")

    # 尝试使用系统字体
    print("尝试使用系统字体...")
    system_fonts = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.otf",
        "/System/Library/Fonts/PingFang.ttc",
        "C:\\Windows\\Fonts\\msyh.ttc",
    ]
    
    for font_path in system_fonts:
        try:
            if os.path.exists(font_path):
                print(f"尝试加载系统字体: {font_path}")
                font = ImageFont.truetype(font_path, size=50)
                # 测试字体是否可用
                test_text = "测试文字"
                font.getlength(test_text)
                print(f"系统字体 {font_path} 加载成功并通过测试")
                return font
        except Exception as e:
            print(f"系统字体 {font_path} 加载失败: {str(e)}")
    
    print("所有字体加载尝试都失败，使用默认字体")
    return ImageFont.load_default()

def calculate_font_size(text: str, max_width: int, font) -> int:
    """计算合适的字体大小"""
    try:
        test_size = 100
        font = font.font_variant(size=test_size)
        text_width = font.getlength(text)
        calculated_size = int(test_size * (max_width / text_width) * 0.95)
        print(f"计算字体大小: 文本='{text}', 最大宽度={max_width}, 计算结果={calculated_size}")
        return calculated_size
    except Exception as e:
        print(f"计算字体大小错误: {str(e)}")
        return 50

def create_png_image(text: str) -> bytes:
    """创建图片"""
    try:
        print(f"开始处理文本: {text}")
        
        # 确保文本是 UTF-8 编码
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        print(f"文本编码处理后: {text}")
        
        # 创建白色背景图片
        image = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # 获取字体
        base_font = get_font()
        print(f"使用字体: {type(base_font)}")
        
        # 分割文本并处理特殊字符
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                # 移除不可见字符和控制字符
                line = ''.join(char for char in line if ord(char) >= 32)
                lines.append(line)
        print(f"处理后的文本行: {lines}")
        
        if len(lines) == 2:
            print("处理两行文字布局")
            # 两行文字
            main_title_size = min(calculate_font_size(lines[0], width * 0.8, base_font), 100)
            main_font = base_font.font_variant(size=main_title_size)
            subtitle_size = min(int(main_title_size * 0.7), 70)
            subtitle_font = base_font.font_variant(size=subtitle_size)
            
            print(f"主标题大小: {main_title_size}, 副标题大小: {subtitle_size}")
            
            draw.text((width/2, height*0.4), lines[0], 
                     font=main_font, fill="#000000", anchor="mm")
            draw.text((width/2, height*0.65), lines[1], 
                     font=subtitle_font, fill="#000000", anchor="mm")
        else:
            print("处理三行文字布局")
            # 三行文字
            main_title_size = min(calculate_font_size(lines[0], width * 0.8, base_font), 80)
            main_font = base_font.font_variant(size=main_title_size)
            subtitle_size = min(int(main_title_size * 0.6), 60)
            subtitle_font = base_font.font_variant(size=subtitle_size)
            small_title_size = min(int(main_title_size * 0.4), 40)
            small_font = base_font.font_variant(size=small_title_size)
            
            print(f"主标题大小: {main_title_size}, 副标题大小: {subtitle_size}, 小标题大小: {small_title_size}")
            
            draw.text((width/2, height*0.3), lines[0], 
                     font=main_font, fill="#000000", anchor="mm")
            if len(lines) > 1:
                draw.text((width/2, height*0.5), lines[1], 
                         font=subtitle_font, fill="#000000", anchor="mm")
            if len(lines) > 2:
                draw.text((width/2, height*0.7), lines[2], 
                         font=small_font, fill="#000000", anchor="mm")
        
        print("图片生成完成，准备保存")
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
        error_text = f"Error: {str(e)}"
        print(f"生成错误图片: {error_text}")
        draw.text((400, 300), error_text, fill="black", anchor="mm", font=font)
        
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
            print(f"收到POST请求数据: {post_data[:200]}")  # 只打印前200个字符
            
            # 确保 JSON 解码使用 UTF-8
            data = json.loads(post_data.decode('utf-8'))
            print(f"解析后的数据: {data}")

            if 'text' not in data:
                print("缺少必要的text参数")
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "Missing required parameter: text"
                }).encode('utf-8'))
                return

            # 生成图片
            png_data = create_png_image(data['text'])
            
            # 转换为 base64
            base64_data = base64.b64encode(png_data).decode('utf-8')
            print("图片生成和编码完成")
            
            self._set_headers()
            response_data = {
                "success": True,
                "data": base64_data
            }
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

        except Exception as e:
            print(f"处理请求错误: {str(e)}")
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode('utf-8'))
