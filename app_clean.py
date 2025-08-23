# app.py - Flask Web 服务器主文件
from scripts.main import run_etl_process_for_file, DB_CONFIG
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
    """处理文件上传并执行ETL流程"""
    # 文件接收和基础校验
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "请求中没有文件部分"}), 400
    
    file = request.files['file']
    company_full = request.form.get('company')
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "没有选择文件"}), 400
    
    original_filename = file.filename
    if not original_filename.lower().endswith(('.xls', '.xlsx', '.csv')):
        return jsonify({"status": "error", "message": "不支持的文件类型，请上传Excel或CSV文件"}), 400

    final_filename_for_upload = "" 
    try:
        # 保存文件到uploads文件夹
        timestamp_prefix = str(int(time.time()))
        safe_base_filename = secure_filename_custom(original_filename)
        final_filename_for_upload = f"{timestamp_prefix}_{company_shortname(company_full)}_{safe_base_filename}"
        print(f'保存文件：{final_filename_for_upload}')
        upload_file_path = os.path.join(app.config['UPLOAD_FOLDER'], final_filename_for_upload)
        file.save(upload_file_path)

        # 执行ETL流程
        success, message = run_etl_process_for_file(Path(upload_file_path))
        if success:
            return jsonify({"status": "success", "message": message})
        else:
            return jsonify({"status": "error", "message": f"文件入库失败: {message}"}), 500

    except Exception as e:
        logging.error(f"处理文件 '{final_filename_for_upload}' 时出错: {e}")
        return jsonify({"status": "error", "message": f"处理文件时发生内部错误: {str(e)}"}), 500

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
