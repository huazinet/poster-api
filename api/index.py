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

def create_png_image(text: str) -> bytes:
    """在模板图片上添加文字"""
    try:
        # 随机获取一个图片和字体文件
        template_path = get_random_file(IMG_DIR, ["png", "jpg", "jpeg"])
        font_path = get_random_file(FONT_DIR, ["ttf", "otf"])
        
        print(f"使用模板图片: {template_path.name}")
        print(f"使用字体文件: {font_path.name}")
        
        # 打开模板图片
        image = Image.open(template_path)
        draw = ImageDraw.Draw(image)
        
        # 加载字体
        font_large = ImageFont.truetype(str(font_path), 80)
        font_medium = ImageFont.truetype(str(font_path), 70)
        
        # 分割文本
        lines = text.split('\n')
        if len(lines) < 3:
            lines.extend([''] * (3 - len(lines)))
        
        # 绘制文本
        # 第一行文本
        draw.text((540, 350), lines[0], font=font_large, fill="#333333", anchor="mm")
        
        # 第二行文本
        draw.text((540, 490), lines[1], font=font_medium, fill="#333333", anchor="mm")
        
        # 第三行文本
        draw.text((540, 620), lines[2], font=font_medium, fill="#333333", anchor="mm")
        
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
