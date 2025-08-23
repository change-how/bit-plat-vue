# app.py - Flask Web 服务器主文件
from scripts.main import run_etl_process_for_file, DB_CONFIG
from scripts.error_handler import ETLError, format_error_for_frontend
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS 
import logging
import json
import os
import pandas as pd
from werkzeug.utils import secure_filename
import time
import re
from scripts.db_queries import get_data_from_db

# 配置日志
logging.basicConfig(level=logging.INFO) 

# 创建 Flask 应用
app = Flask(__name__)

# 定义上传文件夹的路径
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 配置CORS，允许跨域访问
CORS(app, resources={r"/api/*": {"origins": "*"}})

def secure_filename_custom(filename):
    """
    自定义安全文件名处理，允许中文、字母、数字、下划线、点和连字符
    """
    filename = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5_.-]', '', filename)
    filename = filename.replace('..', '')
    return filename

def company_shortname(company_full):
    """将前端公司全名转换为短名称，用于文件命名和模板匹配"""
    company_map = {
        '欧意': 'okx',
        '币安': 'binance', 
        '火币': 'huobi',
        'ImToken': 'imtoken',
        'TokenPocket': 'tokenpocket'
    }
    return company_map.get(company_full, company_full.lower())

def transform_node_for_tree(node):
    """
    数据节点转换器：将节点格式转换为 el-tree 所需的格式
    """
    new_node = {}
    
    if 'data' in node and 'title' in node['data']:
        new_node['label'] = node['data']['title']
    else:
        new_node['label'] = '未命名节点'

    if 'children' in node and node['children']:
        new_node['children'] = []
        for child_node in node['children']:
            new_node['children'].append(transform_node_for_tree(child_node))
            
    return new_node

@app.route('/api/search', methods=['GET'])
def handle_search():
    """搜索指定地址的数据"""
    search_term = request.args.get('query')
    if not search_term:
        return jsonify({"status": "error", "message": "缺少查询参数"}), 400

    logging.info(f"收到查询请求: {search_term}")
    file_path = os.path.join('data', f'{search_term}.json')

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = json.load(f)
            logging.info(f"成功找到并返回文件: {file_path}")
            return jsonify({ "status": "success", "data": file_content })
        except Exception as e:
            logging.error(f"读取文件时出错 {file_path}: {e}")
            return jsonify({"status": "error", "message": "服务器内部错误"}), 500
    else:
        logging.warning(f"未找到数据文件: {file_path}")
        return jsonify({ "status": "error", "message": f"未找到地址 '{search_term}' 对应的数据文件。" }), 404

@app.route('/api/outline', methods=['GET'])
def get_outline():
    """获取数据大纲树形结构"""
    search_term = request.args.get('query')
    if not search_term:
        return jsonify({"status": "error", "message": "缺少查询参数"}), 400

    logging.info(f"收到大纲请求: {search_term}")
    file_path = os.path.join('data', f'{search_term}.json')

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                full_data = json.load(f)

            outline_tree = []
            if 'children' in full_data and full_data['children']:
                for top_level_node in full_data['children']:
                    outline_tree.append(transform_node_for_tree(top_level_node))
            
            logging.info(f"成功生成嵌套大纲树: {file_path}")
            return jsonify({ "status": "success", "data": outline_tree })
        except Exception as e:
            logging.error(f"处理大纲请求时出错 {file_path}: {e}")
            return jsonify({"status": "error", "message": "服务器内部错误"}), 500
    else:
        logging.warning(f"未找到数据文件: {file_path}")
        return jsonify({ "status": "error", "message": f"未找到地址 '{search_term}' 对应的数据文件。" }), 404

@app.route('/api/upload', methods=['POST'])
def handle_upload():
    """处理文件上传并执行ETL流程，带有完整的错误处理"""
    print("\n" + "+"*80)
    print("📥 收到新的文件上传请求")
    print("+"*80)
    
    try:
        # 文件接收和基础校验
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": {
                    "type": "INVALID_REQUEST",
                    "title": "请求格式错误",
                    "user_message": "请求中没有文件部分",
                    "suggestions": ["请确保选择了文件后再上传"]
                }
            }), 400
        
        file = request.files['file']
        company_full = request.form.get('company')
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": {
                    "type": "INVALID_REQUEST",
                    "title": "文件选择错误",
                    "user_message": "没有选择文件",
                    "suggestions": ["请选择一个文件后重试"]
                }
            }), 400
        
        original_filename = file.filename
        if not original_filename.lower().endswith(('.xls', '.xlsx', '.csv')):
            return jsonify({
                "success": False,
                "error": {
                    "type": "FILE_FORMAT_ERROR",
                    "title": "文件格式不支持",
                    "user_message": f"文件格式 '{original_filename.split('.')[-1]}' 不受支持",
                    "suggestions": [
                        "请上传Excel文件(.xlsx, .xls)或CSV文件",
                        "确认文件未损坏",
                        "尝试重新导出文件"
                    ]
                }
            }), 400

        print(f"📋 原始文件名: {original_filename}")
        print(f"🏢 选择平台: {company_full}")
        
        final_filename_for_upload = "" 
        try:
            print("\n" + "~"*60)
            print("💾 文件保存处理")
            print("~"*60)
            
            # 保存文件到uploads文件夹
            timestamp_prefix = str(int(time.time()))
            safe_base_filename = secure_filename_custom(original_filename)
            final_filename_for_upload = f"{timestamp_prefix}_{company_shortname(company_full)}_{safe_base_filename}"
            print(f"📁 保存文件名: {final_filename_for_upload}")
            
            upload_file_path = os.path.join(app.config['UPLOAD_FOLDER'], final_filename_for_upload)
            
            # 检查文件大小（可选）
            file.seek(0, 2)  # 移动到文件末尾
            file_size = file.tell()
            file.seek(0)  # 重置到文件开头
            
            # 限制文件大小为100MB
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                return jsonify({
                    "success": False,
                    "error": {
                        "type": "FILE_TOO_LARGE",
                        "title": "文件过大",
                        "user_message": f"文件大小 {file_size / (1024*1024):.1f}MB 超过限制",
                        "suggestions": [
                            f"文件大小不能超过 {max_size / (1024*1024)}MB",
                            "请删除不必要的数据后重试",
                            "考虑分批上传数据"
                        ]
                    }
                }), 400
            
            file.save(upload_file_path)
            print(f"✅ 文件已保存到: {upload_file_path}")

            # 执行ETL流程
            print("\n" + "~"*60)
            print("🚀 开始ETL数据处理")
            print("~"*60)
            
            success, result = run_etl_process_for_file(Path(upload_file_path), company_full)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": result,
                    "data": {
                        "filename": final_filename_for_upload,
                        "original_filename": original_filename,
                        "platform": company_full,
                        "processed_at": timestamp_prefix
                    }
                })
            else:
                # result是ETLError对象
                if isinstance(result, ETLError):
                    error_response = format_error_for_frontend(result)
                    return jsonify(error_response), 500
                else:
                    # 兼容旧格式
                    return jsonify({
                        "success": False,
                        "error": {
                            "type": "PROCESSING_ERROR",
                            "title": "处理失败",
                            "user_message": str(result),
                            "suggestions": ["请检查文件格式和内容", "联系技术支持"]
                        }
                    }), 500

        except ETLError as e:
            # 处理我们自定义的ETL错误
            print(f"\n❌ ETL处理错误: {e.message}")
            if e.details:
                print(f"详细信息: {e.details}")
            
            error_response = format_error_for_frontend(e)
            return jsonify(error_response), 500
            
        except Exception as e:
            # 处理所有其他未预期的错误
            logging.error(f"处理文件 '{final_filename_for_upload}' 时发生未知错误: {e}")
            return jsonify({
                "success": False,
                "error": {
                    "type": "UNKNOWN_ERROR",
                    "title": "系统错误",
                    "user_message": "处理文件时发生未知错误",
                    "details": str(e),
                    "suggestions": [
                        "请稍后重试",
                        "如果问题持续存在，请联系技术支持",
                        "提供完整的错误信息以便排查"
                    ]
                }
            }), 500

    except Exception as e:
        # 最外层异常捕获
        logging.error(f"处理上传请求时发生严重错误: {e}")
        return jsonify({
            "success": False,
            "error": {
                "type": "SERVER_ERROR",
                "title": "服务器错误",
                "user_message": "服务器处理请求时发生错误",
                "suggestions": ["请稍后重试", "联系技术支持"]
            }
        }), 500

@app.route('/api/mindmap_data', methods=['GET'])
def get_mindmap_data():
    """获取指定用户的思维导图数据"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "缺少 user_id 参数"}), 400
    
    data_df = get_data_from_db(DB_CONFIG, user_id)
    if data_df is not None:
        data_dict = data_df.to_dict(orient='records')
        return jsonify({"status": "success", "data": data_dict})
    else:
        return jsonify({"status": "error", "message": "无法从数据库获取数据或数据为空"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
