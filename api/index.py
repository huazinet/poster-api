# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import random
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import traceback

# 颜色方案
COLOR_SCHEMES = [
    {
        'name': 'pink',
        'primary': '#333333',
        'accent': '#FF9EB5',
        'bg_circle': '#FFE6E9'
    },
    {
        'name': 'blue',
        'primary': '#333333',
        'accent': '#40A9FF',
        'bg_circle': '#E8F4FF'
    },
    {
        'name': 'green',
        'primary': '#333333',
        'accent': '#52C41A',
        'bg_circle': '#F0FFE6'
    },
    {
        'name': 'purple',
        'primary': '#333333',
        'accent': '#9254DE',
        'bg_circle': '#F5EDFF'
    },
    {
        'name': 'yellow',
        'primary': '#333333',
        'accent': '#FAAD14',
        'bg_circle': '#FFFBE6'
    }
]

# 表情符号组合
EMOJI_SETS = [
    "🥺 💖 ✨",
    "😊 💓 ✨",
    "🤗 💕 ✨",
    "😍 💝 ✨",
    "🌈 💫 ✨"
]

def hex_to_rgb(hex_color):
    """将十六进制颜色转换为RGB元组"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_font(size):
    """获取字体，如果找不到系统字体则使用默认字体"""
    try:
        # 尝试多个可能的字体路径
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        ]
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
                
        # 如果都失败了，使用默认字体
        return ImageFont.load_default()
    except Exception as e:
        print(f"字体加载错误: {str(e)}")
        return ImageFont.load_default()

def create_png_image(text: str) -> bytes:
    """直接创建PNG图像"""
    try:
        # 创建图像
        width, height = 1080, 1080
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # 随机选择颜色方案和表情符号
        colors = random.choice(COLOR_SCHEMES)
        emojis = random.choice(EMOJI_SETS)
        
        # 分割文本
        lines = text.split('\n')
        if len(lines) < 3:
            lines.extend([''] * (3 - len(lines)))
        
        # 转换颜色
        primary_color = hex_to_rgb(colors['primary'])
        accent_color = hex_to_rgb(colors['accent'])
        bg_circle_color = hex_to_rgb(colors['bg_circle'])
        
        # 绘制背景圆圈
        draw.ellipse([600, -120, 1200, 480], fill=bg_circle_color, width=0)
        
        # 绘制装饰点
        for x in [100, 130, 160]:
            draw.ellipse([x-8, 92, x+8, 108], fill=accent_color)
        
        # 获取字体
        font_large = get_font(80)
        font_medium = get_font(70)
        font_small = get_font(40)
        
        # 绘制文本
        # 第一行文本
        draw.text((540, 350), lines[0], font=font_large, fill=primary_color, anchor="mm")
        
        # 第二行文本背景
        draw.rectangle([270, 420, 810, 520], fill=accent_color + (51,))  # 20% 透明度
        draw.text((540, 490), lines[1], font=font_medium, fill=primary_color, anchor="mm")
        
        # 装饰线
        draw.rectangle([320, 530, 760, 538], fill=accent_color + (179,))  # 70% 透明度
        
        # 第三行文本
        draw.text((540, 620), lines[2], font=font_medium, fill=primary_color, anchor="mm")
        
        # 表情符号
        draw.text((540, 740), emojis, font=font_small, fill=primary_color, anchor="mm")
        
        # 将图像转换为bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()
    except Exception as e:
        print(f"创建PNG图片错误: {str(e)}")
        traceback.print_exc()
        raise

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
            data = json.loads(post_data.decode('utf-8'))

            if 'text' not in data:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "Missing required parameter: text"
                }).encode())
                return

            # 生成PNG图片
            png_data = create_png_image(data['text'])
            
            # 转换为base64
            base64_png = base64.b64encode(png_data).decode('utf-8')
            
            # 返回base64数据
            self._set_headers()
            response_data = {
                "success": True,
                "image_base64": base64_png,
                "content_type": "image/png"
            }
            
            self.wfile.write(json.dumps(response_data).encode())

        except Exception as e:
            print(f"请求处理错误: {str(e)}")
            traceback.print_exc()
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())
