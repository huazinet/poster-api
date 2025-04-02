# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from pathlib import Path
import random

# 获取当前文件所在目录
CURRENT_DIR = Path(__file__).parent

# 图片和字体目录路径
IMG_DIR = CURRENT_DIR / "img_module"
FONT_DIR = CURRENT_DIR / "ttf_module"

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

def get_random_file(directory: Path, extensions: list) -> Path:
    """从指定目录随机获取指定扩展名的文件"""
    # 确保目录存在
    if not directory.exists():
        raise FileNotFoundError(f"目录不存在: {directory}")
    
    # 获取所有符合扩展名的文件
    files = []
    for ext in extensions:
        files.extend(directory.glob(f"*.{ext}"))
    
    if not files:
        raise FileNotFoundError(f"在 {directory} 中没有找到任何{extensions}文件")
    
    # 随机选择一个文件
    return random.choice(files)

def calculate_font_size(text: str, max_width: int, font_path: str) -> int:
    """计算合适的字体大小"""
    test_size = 200  # 开始的测试大小
    font = ImageFont.truetype(str(font_path), test_size)
    text_width = font.getlength(text)
    
    # 根据文本宽度调整字体大小
    return int(test_size * (max_width / text_width) * 0.95)  # 0.95是为了留一些边距

def create_png_image(text: str) -> bytes:
    """在模板图片上添加文字，大字报风格"""
    try:
        # 随机获取一个图片和字体文件
        template_path = get_random_file(IMG_DIR, ["png", "jpg", "jpeg"])
        font_path = get_random_file(FONT_DIR, ["ttf", "otf"])
        
        print(f"使用模板图片: {template_path.name}")
        print(f"使用字体文件: {font_path.name}")
        
        # 打开模板图片
        image = Image.open(template_path)
        width, height = image.size
        draw = ImageDraw.Draw(image)
        
        # 分割文本并移除空行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 获取模板配置
        template_config = TEMPLATE_CONFIGS.get(template_path.name, DEFAULT_CONFIG)
        config = template_config['two_lines'] if len(lines) == 2 else template_config['three_lines']
        
        # 主标题配置
        main_config = config['main_title']
        main_title_size = calculate_font_size(lines[0], width * main_config['font_size_ratio'], font_path)
        main_font = ImageFont.truetype(str(font_path), main_title_size)
        
        # 计算实际位置
        main_x = int(width * main_config['position'][0])
        main_y = int(height * main_config['position'][1])
        
        # 绘制主标题
        draw.text((main_x, main_y), lines[0], 
                 font=main_font, fill=main_config['color'], anchor="mm")
        
        # 绘制副标题
        if len(lines) > 1:
            subtitle_config = config['subtitle']
            subtitle_size = int(main_title_size * subtitle_config['size_ratio'])
            subtitle_font = ImageFont.truetype(str(font_path), subtitle_size)
            subtitle_x = int(width * subtitle_config['position'][0])
            subtitle_y = int(height * subtitle_config['position'][1])
            draw.text((subtitle_x, subtitle_y), lines[1],
                     font=subtitle_font, fill=subtitle_config['color'], anchor="mm")
        
        # 绘制小标题（如果有）
        if len(lines) > 2:
            small_config = config['small_title']
            small_size = int(main_title_size * small_config['size_ratio'])
            small_font = ImageFont.truetype(str(font_path), small_size)
            small_x = int(width * small_config['position'][0])
            small_y = int(height * small_config['position'][1])
            draw.text((small_x, small_y), lines[2],
                     font=small_font, fill=small_config['color'], anchor="mm")
        
        # 将图像转换为bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()
        
    except Exception as e:
        print(f"创建PNG图片错误: {str(e)}")
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
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())
