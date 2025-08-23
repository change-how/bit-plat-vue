#!/usr/bin/env python
# simple_flask_test.py - 简单的Flask错误测试

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/upload', methods=['POST'])
def test_upload():
    """测试错误响应格式"""
    print("收到测试上传请求")
    
    # 模拟一个错误响应
    error_response = {
        "success": False,
        "error": {
            "type": "COMPANY_NOT_RECOGNIZED",
            "title": "无法识别数据平台",
            "details": "无法从文件名 'test_huobi.xlsx' 识别数据平台",
            "suggestions": [
                "请在文件名中包含平台标识，如: okx_data.xlsx, binance_交易记录.csv",
                "支持的平台关键词: okx, binance, huobi, imtoken, tokenpocket",
                "或直接使用 .csv 格式让系统自动处理"
            ],
            "user_message": "无法识别数据平台: 无法从文件名 'test_huobi.xlsx' 识别数据平台"
        }
    }
    
    print("返回错误响应:", error_response)
    return jsonify(error_response), 500

if __name__ == '__main__':
    print("启动简单Flask测试服务器...")
    app.run(port=5000, debug=True, host='0.0.0.0')
