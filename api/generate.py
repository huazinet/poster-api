from flask import Flask, request, jsonify
from http.server import BaseHTTPRequestHandler
import requests
import random
import json

# 颜色方案 - 对应不同的模板
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

def create_svg_image(text):
    """创建SVG图像"""
    # 随机选择颜色方案
    colors = random.choice(COLOR_SCHEMES)
    
    # 随机选择表情符号
    emojis = random.choice(EMOJI_SETS)
    
    # 分割文本
    lines = text.split('\n')
    if len(lines) < 3:
        lines.extend([''] * (3 - len(lines)))
    
    # 构建SVG图像
    svg_content = f"""
    <svg width="1080" height="1080" xmlns="http://www.w3.org/2000/svg">
        <rect width="1080" height="1080" fill="white"/>
        
        <!-- 右上角装饰圆 -->
        <circle cx="900" cy="180" r="300" fill="{colors['bg_circle']}" opacity="0.7"/>
        
        <!-- 装饰点 -->
        <circle cx="100" cy="100" r="8" fill="{colors['accent']}" opacity="0.8"/>
        <circle cx="130" cy="100" r="8" fill="{colors['accent']}" opacity="0.8"/>
        <circle cx="160" cy="100" r="8" fill="{colors['accent']}" opacity="0.8"/>
        
        <!-- 第一行文本 -->
        <text x="540" y="350" font-family="'Noto Sans SC', sans-serif" font-size="80" font-weight="bold" fill="{colors['primary']}" text-anchor="middle">{lines[0]}</text>
        
        <!-- 第二行文本 -->
        <g>
            <rect x="270" y="420" width="540" height="100" rx="10" fill="{colors['accent']}" opacity="0.2"/>
            <text x="540" y="490" font-family="'Noto Sans SC', sans-serif" font-size="70" font-weight="bold" fill="{colors['primary']}" text-anchor="middle">{lines[1]}</text>
            <rect x="320" y="530" width="440" height="8" fill="{colors['accent']}" opacity="0.7"/>
        </g>
        
        <!-- 第三行文本 -->
        <text x="540" y="620" font-family="'Noto Sans SC', sans-serif" font-size="70" font-weight="bold" fill="{colors['primary']}" text-anchor="middle">{lines[2]}</text>
        
        <!-- 表情符号 -->
        <text x="540" y="740" font-family="'Noto Sans SC', sans-serif" font-size="40" fill="{colors['primary']}" text-anchor="middle">{emojis}</text>
    </svg>
    """
    
    return svg_content

def upload_to_imgbb(svg_content):
    """将SVG上传到ImgBB并返回URL"""
    imgbb_api_key = "44b4d3a8024b4abd4b7a94139dcfcf0f"  # 免费API密钥
    
    # 向imgbb发送请求
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        params={"key": imgbb_api_key},
        data={"image": svg_content}
    )
    
    if response.status_code != 200:
        raise Exception(f"ImgBB API错误: {response.status_code}")
    
    result = response.json()
    if not result.get("success"):
        raise Exception(f"ImgBB上传失败")
    
    # 返回图片URL
    return result["data"]["url"]

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        if 'text' not in data:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Missing required parameter: text"}).encode())
            return
        
        try:
            # 创建SVG并上传
            svg_content = create_svg_image(data['text'])
            image_url = upload_to_imgbb(svg_content)
            
            # 返回成功结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
            self.end_headers()
            
            response_data = {
                "success": True,
                "image_url": image_url
            }
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        self.end_headers()
