# app.py (V3 - 已解决跨域问题)

from flask import Flask, request, jsonify
from flask_cors import CORS 
import logging
import json
import os

# 配置日志
logging.basicConfig(level=logging.INFO) 

# 创建 Flask 应用
app = Flask(__name__)

CORS(app) 

# app.py

# ... (Flask, CORS, logging, json, os 的 import 语句保持不变) ...
# ... (app = Flask(__name__) 和 CORS(app) 保持不变) ...
# ... (handle_search 函数保持不变) ...

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


# 启动服务器
if __name__ == '__main__':
    app.run(port=5000, debug=True)