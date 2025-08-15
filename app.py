# app.py (V3 - 已解决跨域问题)

from flask import Flask, request, jsonify
from flask_cors import CORS 
import logging
import json
import os
import pandas as pd
from werkzeug.utils import secure_filename
import time
import re
from scripts.utils import inspect_excel_structure
from scripts.data_processor import process_uploaded_data#自己的数据处理函数
# 配置日志
logging.basicConfig(level=logging.INFO) 

# 创建 Flask 应用
app = Flask(__name__)

'''存取上传文件的记录'''
# 定义上传文件夹的路径
UPLOAD_FOLDER = 'uploads'
# 将这个配置项添加到 app 的配置中
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# 更明确地配置CORS，允许所有源访问所有以 /api/ 开头的接口
CORS(app, resources={r"/api/*": {"origins": "*"}})
# app.py
#安全字段辅助函数
def secure_filename_custom(filename):
    """
    一个自定义的版本，允许中文、字母、数字、下划线、点和连字符。
    会移除其他所有不安全的字符。
    """
    # 移除非法字符
    filename = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5_.-]', '', filename)
    # 防止目录遍历攻击
    filename = filename.replace('..', '')
    return filename
# --- ✨✨✨ 我们来重写这个函数 ✨✨✨ ---

# 这是一个辅助函数，一个“数据转换器”
# 它的作用是把一个节点从我们的格式，转换成 el-tree 需要的格式

def transform_node_for_tree(node):
    # 准备一个新的、干净的字典
    new_node = {}
    
    # 1. 把 'data' 里的 'title' 拿出来，放到新字典里，并改名叫 'label'
    if 'data' in node and 'title' in node['data']:
        new_node['label'] = node['data']['title']
    else:
        new_node['label'] = '未命名节点' # 做一个兼容处理

    # 2. 检查这个节点有没有“孩子”（子节点）
    if 'children' in node and node['children']:
        # 如果有，就创建一个空的 children 列表
        new_node['children'] = []
        # 遍历所有的孩子
        for child_node in node['children']:
            # ✨ 最关键的一步：让这个函数自己调用自己，去处理自己的孩子
            # 把处理好的孩子，添加到新节点的 children 列表里
            new_node['children'].append(transform_node_for_tree(child_node))
            
    return new_node

# 定义 /api/search 接口
@app.route('/api/search', methods=['GET'])
def handle_search():
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
# 这句话像是在菜单上写上菜名：/api/outline，并且规定了点菜方式：GET

@app.route('/api/outline', methods=['GET'])
def get_outline():
    search_term = request.args.get('query')
    if not search_term:
        return jsonify({"status": "error", "message": "缺少查询参数"}), 400

    logging.info(f"收到大纲请求: {search_term}")
    file_path = os.path.join('data', f'{search_term}.json')

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                full_data = json.load(f)

            # 我们不再自己手动循环，而是直接调用“数据转换器”
            # 我们假设大纲是从根节点的子节点开始的
            outline_tree = []
            if 'children' in full_data and full_data['children']:
                for top_level_node in full_data['children']:
                    outline_tree.append(transform_node_for_tree(top_level_node))
            
            logging.info(f"成功生成嵌套大纲树: {file_path}")
            # 返回转换好的、带有完整层级的树形数据
            return jsonify({ "status": "success", "data": outline_tree })
        except Exception as e:
            logging.error(f"处理大纲请求时出错 {file_path}: {e}")
            return jsonify({"status": "error", "message": "服务器内部错误"}), 500
    else:
        logging.warning(f"未找到数据文件: {file_path}")
        return jsonify({ "status": "error", "message": f"未找到地址 '{search_term}' 对应的数据文件。" }), 404


# app.py

@app.route('/api/upload', methods=['POST'])
def handle_upload():
    # 1. 文件接收和基础校验 (这部分保持不变)
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "请求中没有文件部分"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "没有选择文件"}), 400
    
    original_filename = file.filename
    if not original_filename.lower().endswith(('.xls', '.xlsx')):
        return jsonify({"status": "error", "message": "不支持的文件类型，请上传Excel文件"}), 400

    # 声明变量，以便在 try...except 的所有地方都能访问
    final_filename_for_upload = "" 
    try:
        # 2. 保存原始文件到 uploads 文件夹作为备份 (不变)
        timestamp_prefix = str(int(time.time()))
        safe_base_filename = secure_filename_custom(original_filename)
        final_filename_for_upload = f"{timestamp_prefix}_{safe_base_filename}"
        upload_file_path = os.path.join(app.config['UPLOAD_FOLDER'], final_filename_for_upload)
        file.save(upload_file_path)

        # 3. 读取所有工作表 (不变)
        all_sheets_df_dict = pd.read_excel(upload_file_path, sheet_name=None, engine='openpyxl')
        
        # 4. --- 关键改动：接收两个返回值 ---
        #    现在我们同时接收到了处理好的数据和用作文件名的核心ID
        final_json_data, core_id = process_uploaded_data(all_sheets_df_dict, original_filename)
        
        # 5. --- 核心功能：保存JSON到data文件夹 ---
        if core_id: # 确保我们得到了一个有效的ID
            # 定义data文件夹的路径
            data_folder_path = 'data'
            # 确保data文件夹存在
            if not os.path.exists(data_folder_path):
                os.makedirs(data_folder_path)
            
            # 使用核心ID来命名最终的JSON文件
            json_filename = f"{core_id}.json"
            json_file_path = os.path.join(data_folder_path, json_filename)
            
            # 使用json.dump()来将Python字典写入文件
            # ensure_ascii=False 保证中文能被正确写入
            # indent=4 让JSON文件格式优美，易于阅读
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(final_json_data, f, ensure_ascii=False, indent=4)
            
            logging.info(f"成功将解析数据保存到: {json_file_path}")
            
            # 6. 返回一个明确的成功信息给前端
            return jsonify({
                "status": "success",
                "message": f"文件上传成功，已入库为 {json_filename}",
                "data": final_json_data # 同时也可以把数据返回给前端预览
            })
        else:
            # 如果没有得到core_id，说明处理失败，主动抛出错误
            raise Exception("无法从文件中提取核心ID (地址或uuid)，入库失败。")

    except Exception as e:
        # 统一的错误处理
        logging.error(f"处理文件 '{final_filename_for_upload}' 时出错: {e}")
        return jsonify({"status": "error", "message": f"处理文件时发生内部错误: {str(e)}"}), 500
    

    
if __name__ == '__main__':
    app.run(port=5000, debug=True)