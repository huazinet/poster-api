# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from pathlib import Path
import random
import os
import sys

# 获取当前文件所在目录
CURRENT_DIR = Path(__file__).parent

# 图片和字体目录路径
IMG_DIR = CURRENT_DIR / "img_module"
FONT_DIR = CURRENT_DIR / "ttf_module"

# 确保目录存在
IMG_DIR.mkdir(exist_ok=True)
FONT_DIR.mkdir(exist_ok=True)

# 模板配置
TEMPLATE_CONFIGS = {
    # 这里添加特定模板的配置
    # 'template1.png': {
    #     'two_lines': {  # 两行文字的配置
    #         'main_title': {
    #             'position': (0.5, 0.3),  # 相对位置 (x, y)
    #             'font_size_ratio': 0.8,  # 字体大小占图片宽度的比例
    #             'color': '#000000'
    #         },
    #         'subtitle': {
    #             'position': (0.5, 0.6),
    #             'size_ratio': 0.7,  # 相对于主标题的大小
    #             'color': '#000000'
    #         }
    #     },
    #     'three_lines': {  # 三行文字的配置
    #         'main_title': {
    #             'position': (0.5, 0.2),
    #             'font_size_ratio': 0.8,
    #             'color': '#000000'
    #         },
    #         'subtitle': {
    #             'position': (0.5, 0.5),
    #             'size_ratio': 0.6,
    #             'color': '#000000'
    #         },
    #         'small_title': {
    #             'position': (0.5, 0.8),
    #             'size_ratio': 0.4,
    #             'color': '#000000'
    #         }
    #     }
    # }
}

# 默认配置
DEFAULT_CONFIG = {
    'two_lines': {
        'main_title': {
            'position': (0.5, 0.4),  # 中间偏上
            'font_size_ratio': 0.8,
            'color': '#000000'
        },
        'subtitle': {
            'position': (0.5, 0.65),
            'size_ratio': 0.7,
            'color': '#000000'
        }
    },
    'three_lines': {
        'main_title': {
            'position': (0.5, 0.3),
            'font_size_ratio': 0.8,
            'color': '#000000'
        },
        'subtitle': {
            'position': (0.5, 0.5),
            'size_ratio': 0.6,
            'color': '#000000'
        },
        'small_title': {
            'position': (0.5, 0.7),
            'size_ratio': 0.4,
            'color': '#000000'
        }
    }
}

def get_system_font():
    """获取系统字体"""
    system_fonts = [
        # Linux
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.otf",
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        # Windows
        "C:\\Windows\\Fonts\\msyh.ttc",
    ]
    
    for font_path in system_fonts:
        if os.path.exists(font_path):
            return font_path
            
    # 如果找不到系统字体，使用默认字体
    return str(FONT_DIR / "NotoSansSC-Bold.otf")

def get_random_file(directory: Path, extensions: list) -> Path:
    """从指定目录随机获取指定扩展名的文件"""
    try:
        files = []
        for ext in extensions:
            files.extend(directory.glob(f"*.{ext}"))
        
        if not files:
            # 如果没有找到文件，创建一个空白图片
            img = Image.new('RGB', (800, 600), color='white')
            temp_path = directory / "default.png"
            img.save(str(temp_path))
            return temp_path
        
        return random.choice(files)
    except Exception as e:
        print(f"获取文件错误: {str(e)}")
        # 创建一个空白图片作为后备方案
        img = Image.new('RGB', (800, 600), color='white')
        temp_path = directory / "default.png"
        img.save(str(temp_path))
        return temp_path

def calculate_font_size(text: str, max_width: int, font_path: str) -> int:
    """计算合适的字体大小"""
    try:
        test_size = 100  # 减小初始测试大小以节省内存
        font = ImageFont.truetype(font_path, test_size)
        text_width = font.getlength(text)
        
        return int(test_size * (max_width / text_width) * 0.95)
    except Exception as e:
        print(f"计算字体大小错误: {str(e)}")
        return 50  # 返回一个安全的默认值

def create_png_image(text: str) -> bytes:
    """在模板图片上添加文字，大字报风格"""
    try:
        # 获取模板图片
        template_path = get_random_file(IMG_DIR, ["png", "jpg", "jpeg"])
        font_path = get_system_font()
        
        print(f"使用模板图片: {template_path}")
        print(f"使用字体文件: {font_path}")
        
        # 创建新的图片对象
        with Image.new('RGB', (800, 600), color='white') as image:
            draw = ImageDraw.Draw(image)
            
            # 分割文本并移除空行
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # 根据行数调整布局
            if len(lines) == 2:
                # 两行文字的情况
                main_title_size = min(calculate_font_size(lines[0], 600, font_path), 100)
                main_font = ImageFont.truetype(font_path, main_title_size)
                subtitle_size = min(int(main_title_size * 0.7), 70)
                subtitle_font = ImageFont.truetype(font_path, subtitle_size)
                
                # 绘制文字
                draw.text((400, 240), lines[0], 
                         font=main_font, fill="#000000", anchor="mm")
                draw.text((400, 360), lines[1], 
                         font=subtitle_font, fill="#000000", anchor="mm")
            else:
                # 三行文字的情况
                main_title_size = min(calculate_font_size(lines[0], 600, font_path), 80)
                main_font = ImageFont.truetype(font_path, main_title_size)
                subtitle_size = min(int(main_title_size * 0.6), 60)
                subtitle_font = ImageFont.truetype(font_path, subtitle_size)
                small_title_size = min(int(main_title_size * 0.4), 40)
                small_font = ImageFont.truetype(font_path, small_title_size)
                
                # 绘制文字
                draw.text((400, 180), lines[0], 
                         font=main_font, fill="#000000", anchor="mm")
                if len(lines) > 1:
                    draw.text((400, 300), lines[1], 
                             font=subtitle_font, fill="#000000", anchor="mm")
                if len(lines) > 2:
                    draw.text((400, 420), lines[2], 
                             font=small_font, fill="#000000", anchor="mm")
            
            # 优化内存使用：直接将图像保存到字节流
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG', optimize=True, quality=85)
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()
        
    except Exception as e:
        print(f"创建PNG图片错误: {str(e)}")
        # 创建一个带有错误信息的图片
        error_img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(error_img)
        draw.text((400, 300), f"Error: {str(e)}", fill="black", anchor="mm")
        
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
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())
