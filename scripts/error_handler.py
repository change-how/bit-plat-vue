# error_handler.py - 统一错误处理和用户友好消息
from enum import Enum
from typing import Dict, Any, Tuple
import pandas as pd

class ErrorType(Enum):
    """错误类型枚举"""
    # 文件相关错误
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_FORMAT_ERROR = "FILE_FORMAT_ERROR"
    FILE_ENCODING_ERROR = "FILE_ENCODING_ERROR"
    FILE_EMPTY = "FILE_EMPTY"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    
    # 数据库相关错误
    DB_CONNECTION_ERROR = "DB_CONNECTION_ERROR"
    DB_WRITE_ERROR = "DB_WRITE_ERROR"
    DB_READ_ERROR = "DB_READ_ERROR"
    DB_TIMEOUT = "DB_TIMEOUT"
    
    # 数据处理相关错误
    TEMPLATE_NOT_FOUND = "TEMPLATE_NOT_FOUND"
    TEMPLATE_FORMAT_ERROR = "TEMPLATE_FORMAT_ERROR"
    COMPANY_NOT_RECOGNIZED = "COMPANY_NOT_RECOGNIZED"
    COLUMN_MISSING = "COLUMN_MISSING"
    DATA_VALIDATION_ERROR = "DATA_VALIDATION_ERROR"
    DATA_TRANSFORMATION_ERROR = "DATA_TRANSFORMATION_ERROR"
    WORKSHEET_MISSING = "WORKSHEET_MISSING"
    TEMPLATE_MISMATCH = "TEMPLATE_MISMATCH"
    
    # 网络和系统错误
    NETWORK_ERROR = "NETWORK_ERROR"
    PERMISSION_ERROR = "PERMISSION_ERROR"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

class ETLError(Exception):
    """自定义ETL处理错误类"""
    
    def __init__(self, error_type: ErrorType, message: str, details: str = None, suggestions: list = None):
        self.error_type = error_type
        self.message = message
        self.details = details
        self.suggestions = suggestions or []
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于前端显示"""
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "details": self.details,
            "suggestions": self.suggestions
        }

# 用户友好的错误消息映射
ERROR_MESSAGES = {
    ErrorType.FILE_NOT_FOUND: {
        "message": "文件未找到",
        "suggestions": ["请检查文件是否存在", "确认文件路径是否正确"]
    },
    ErrorType.FILE_FORMAT_ERROR: {
        "message": "文件格式不正确",
        "suggestions": ["请确保文件是Excel(.xlsx/.xls)或CSV格式", "检查文件是否损坏", "尝试重新导出文件"]
    },
    ErrorType.FILE_ENCODING_ERROR: {
        "message": "文件编码错误",
        "suggestions": ["建议使用UTF-8编码保存文件", "尝试用Excel重新保存文件"]
    },
    ErrorType.FILE_EMPTY: {
        "message": "文件是空的",
        "suggestions": ["请检查文件是否包含数据", "确认工作表中有内容"]
    },
    ErrorType.DB_CONNECTION_ERROR: {
        "message": "数据库连接失败",
        "suggestions": ["检查数据库服务是否运行", "确认数据库连接配置", "检查网络连接"]
    },
    ErrorType.DB_WRITE_ERROR: {
        "message": "数据写入数据库失败",
        "suggestions": ["检查数据库空间是否足够", "确认数据格式是否正确", "检查数据库权限"]
    },
    ErrorType.TEMPLATE_NOT_FOUND: {
        "message": "找不到对应的数据模板",
        "suggestions": ["检查文件名是否包含正确的平台标识", "支持的平台：欧意(OKX)、币安、火币、ImToken、TokenPocket"]
    },
    ErrorType.COMPANY_NOT_RECOGNIZED: {
        "message": "无法识别数据平台",
        "suggestions": ["请在文件名中包含平台名称", "支持的平台：欧意(OKX)、币安、火币、ImToken、TokenPocket", "或使用CSV格式的通用模板"]
    },
    ErrorType.COLUMN_MISSING: {
        "message": "缺少必需的数据列",
        "suggestions": ["检查Excel表格是否包含所有必需的列", "确认列名是否正确", "参考平台的标准导出格式"]
    },
    ErrorType.DATA_VALIDATION_ERROR: {
        "message": "数据格式验证失败",
        "suggestions": ["检查数据格式是否正确", "确认日期、金额等字段格式", "删除空行或无效数据"]
    },
    ErrorType.DATA_TRANSFORMATION_ERROR: {
        "message": "数据转换失败",
        "suggestions": ["检查数据格式，确保符合系统要求", "确认数据类型正确", "删除特殊字符或无效数据"]
    },
    ErrorType.WORKSHEET_MISSING: {
        "message": "Excel文件中缺少必要的工作表",
        "suggestions": ["请确保Excel文件包含所有必要的工作表", "检查工作表名称是否正确", "参考平台的标准导出格式"]
    },
    ErrorType.TEMPLATE_MISMATCH: {
        "message": "文件结构与所选公司模板不匹配",
        "suggestions": ["请检查所选公司是否正确", "确保文件符合相应的模板格式", "检查工作表是否完整"]
    },
    ErrorType.NETWORK_ERROR: {
        "message": "网络连接错误",
        "suggestions": ["检查网络连接", "稍后重试"]
    },
    ErrorType.UNKNOWN_ERROR: {
        "message": "未知错误",
        "suggestions": ["请联系技术支持", "提供错误详情以便排查"]
    }
}

def create_user_friendly_error(error_type: ErrorType, details: str = None, custom_suggestions: list = None) -> ETLError:
    """创建用户友好的错误对象"""
    error_info = ERROR_MESSAGES.get(error_type, ERROR_MESSAGES[ErrorType.UNKNOWN_ERROR])
    
    suggestions = custom_suggestions or error_info["suggestions"]
    
    return ETLError(
        error_type=error_type,
        message=error_info["message"],
        details=details,
        suggestions=suggestions
    )

def handle_exception(func):
    """装饰器：统一异常处理"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ETLError:
            # 重新抛出ETL错误
            raise
        except FileNotFoundError as e:
            raise create_user_friendly_error(
                ErrorType.FILE_NOT_FOUND,
                details=str(e)
            )
        except PermissionError as e:
            raise create_user_friendly_error(
                ErrorType.PERMISSION_ERROR,
                details=str(e),
                custom_suggestions=["检查文件权限", "确认文件未被其他程序占用"]
            )
        except pd.errors.EmptyDataError as e:
            raise create_user_friendly_error(
                ErrorType.FILE_EMPTY,
                details=str(e)
            )
        except Exception as e:
            # 捕获所有其他异常
            raise create_user_friendly_error(
                ErrorType.UNKNOWN_ERROR,
                details=str(e)
            )
    
    return wrapper

def format_error_for_frontend(error: ETLError) -> Dict[str, Any]:
    """格式化错误信息供前端显示"""
    # 生成简洁的用户消息
    user_message = error.message
    
    # 对于特定错误类型，提供更简洁的消息
    if error.error_type == ErrorType.DATA_VALIDATION_ERROR and error.details:
        details_lower = error.details.lower()
        if "缺少工作表" in error.details:
            # 如果错误详情已经很简洁，直接使用
            user_message = error.message
        elif "worksheet_name" in details_lower or "keyerror" in details_lower:
            user_message = "文件格式与所选平台不匹配"
        elif "不存在" in error.details:
            user_message = error.message
    
    return {
        "success": False,
        "error": {
            "type": error.error_type.value,
            "title": error.message,
            "details": error.details,
            "suggestions": error.suggestions,
            "user_message": user_message
        }
    }
