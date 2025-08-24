# app.py - Flask Web 服务器主文件
from scripts.main import run_etl_process_for_file, DB_CONFIG
from scripts.error_handler import ETLError, format_error_for_frontend
from scripts.file_metadata import insert_file_metadata, create_file_metadata_table
from pathlib import Path
from flask import Flask, request, jsonify, send_file
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

@app.route('/api/search_uid', methods=['GET'])
def search_uid():
    """通过模糊查找获取用户ID列表"""
    search_term = request.args.get('query')
    if not search_term:
        return jsonify({"status": "error", "message": "缺少查询参数"}), 400

    logging.info(f"收到模糊查找请求: {search_term}")
    
    try:
        from scripts.db_queries import search_users_by_fuzzy_term
        results = search_users_by_fuzzy_term(DB_CONFIG, search_term)
        
        if results and len(results) > 0:
            logging.info(f"找到 {len(results)} 个匹配的用户")
            return jsonify({
                "status": "success", 
                "users": results,  # 修改为 users 以匹配前端期望
                "count": len(results)
            })
        else:
            logging.warning(f"未找到匹配的用户: {search_term}")
            return jsonify({
                "status": "error", 
                "message": f"未找到匹配 '{search_term}' 的用户信息"
            }), 404
            
    except Exception as e:
        logging.error(f"模糊查找时出错: {e}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500

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
            
            # 记录文件元信息到数据库
            try:
                insert_file_metadata(
                    DB_CONFIG, 
                    upload_file_path, 
                    original_filename=original_filename,
                    platform=company_full
                )
                print(f"📝 文件元信息已记录到数据库")
            except Exception as meta_error:
                print(f"⚠️ 记录文件元信息失败: {meta_error}")
                # 不中断主流程，仅记录警告

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

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """安全的文件下载接口"""
    try:
        # 安全检查：防止路径遍历攻击
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({"status": "error", "message": "非法文件名"}), 400
        
        # 构建完整文件路径
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "文件不存在"}), 404
        
        # 检查是否在允许的目录内
        if not os.path.abspath(file_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
            return jsonify({"status": "error", "message": "访问被拒绝"}), 403
        
        # 返回文件
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        logging.error(f"文件下载失败: {e}")
        return jsonify({"status": "error", "message": "下载失败"}), 500

@app.route('/api/mindmap_data', methods=['GET'])
def get_mindmap_data():
    """获取指定用户的原始数据 - 由前端转换为思维导图格式"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "缺少 user_id 参数"}), 400
    
    # 获取包含所有表数据的字典
    all_data = get_data_from_db(DB_CONFIG, user_id)
    if all_data is not None:
        # 直接返回原始数据，让前端处理转换
        return jsonify({"status": "success", "data": all_data})
    else:
        return jsonify({"status": "error", "message": "无法从数据库获取数据或数据为空"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
