# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import random
import base64
from playwright.sync_api import sync_playwright
import os

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

def create_html(text: str, colors: dict) -> str:
    """创建HTML内容"""
    lines = text.split('\n')
    if len(lines) < 3:
        lines.extend([''] * (3 - len(lines)))
    
    emojis = random.choice(EMOJI_SETS)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');
            
            body {{
                margin: 0;
                padding: 0;
                width: 1080px;
                height: 1080px;
                background: white;
                font-family: 'Noto Sans SC', sans-serif;
                overflow: hidden;
                position: relative;
            }}
            
            .background-circle {{
                position: absolute;
                top: -120px;
                right: -120px;
                width: 600px;
                height: 600px;
                border-radius: 50%;
                background: {colors['bg_circle']};
                opacity: 0.7;
            }}
            
            .dots {{
                position: absolute;
                top: 92px;
                left: 92px;
                display: flex;
                gap: 30px;
            }}
            
            .dot {{
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: {colors['accent']};
                opacity: 0.8;
            }}
            
            .content {{
                position: relative;
                width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 40px;
                box-sizing: border-box;
            }}
            
            .line1 {{
                font-size: 80px;
                font-weight: bold;
                color: {colors['primary']};
                margin-bottom: 40px;
                text-align: center;
                max-width: 900px;
                line-height: 1.2;
            }}
            
            .line2-container {{
                background: {colors['accent']};
                opacity: 0.2;
                padding: 20px 40px;
                border-radius: 10px;
                margin-bottom: 20px;
            }}
            
            .line2 {{
                font-size: 70px;
                font-weight: bold;
                color: {colors['primary']};
                text-align: center;
                max-width: 800px;
                line-height: 1.2;
            }}
            
            .decoration-line {{
                width: 440px;
                height: 8px;
                background: {colors['accent']};
                opacity: 0.7;
                margin: 20px 0;
            }}
            
            .line3 {{
                font-size: 70px;
                font-weight: bold;
                color: {colors['primary']};
                text-align: center;
                max-width: 800px;
                line-height: 1.2;
                margin-bottom: 40px;
            }}
            
            .emojis {{
                font-size: 40px;
                color: {colors['primary']};
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="background-circle"></div>
        <div class="dots">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
        <div class="content">
            <div class="line1">{lines[0]}</div>
            <div class="line2-container">
                <div class="line2">{lines[1]}</div>
            </div>
            <div class="decoration-line"></div>
            <div class="line3">{lines[2]}</div>
            <div class="emojis">{emojis}</div>
        </div>
    </body>
    </html>
    """

def create_png_image(text: str) -> bytes:
    """使用HTML生成PNG图片"""
    try:
        # 随机选择颜色方案
        colors = random.choice(COLOR_SCHEMES)
        
        # 生成HTML内容
        html_content = create_html(text, colors)
        
        # 使用playwright生成图片
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1080, 'height': 1080})
            
            # 设置HTML内容
            page.set_content(html_content)
            
            # 等待字体加载
            page.wait_for_load_state('networkidle')
            
            # 截图
            screenshot = page.screenshot(type='png')
            
            # 关闭浏览器
            browser.close()
            
            return screenshot
            
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
