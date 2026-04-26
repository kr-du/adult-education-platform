from werkzeug.security import generate_password_hash, check_password_hash
import re
import bleach
from datetime import datetime, timedelta
from flask import jsonify, current_app

def sanitize_input(input_str, max_length=255):
    """清理和验证用户输入"""
    if not input_str:
        return None
    
    # 去除前后空白
    input_str = input_str.strip()
    
    # 限制长度
    if len(input_str) > max_length:
        raise ValueError(f"输入长度超过最大限制 {max_length} 字符")
    
    # 移除危险字符
    input_str = re.sub(r'[<>"\'%;()&]', '', input_str)
    
    return input_str

def validate_email(email):
    """验证邮箱格式"""
    if not email:
        return False
    
    email = email.strip().lower()
    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_regex.match(email))

def validate_username(username):
    """验证用户名格式"""
    if not username:
        return False
    
    username = username.strip()
    username_regex = re.compile(r'^[a-zA-Z0-9_]{3,50}$')
    return bool(username_regex.match(username))

def validate_password(password):
    """验证密码强度"""
    if not password:
        return False
    
    password = password.strip()
    if len(password) < 8:
        return False
    
    # 检查密码复杂度
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    return has_upper and has_lower and has_digit and has_special

def sanitize_search_keyword(keyword):
    """清理搜索关键词，防止SQL注入"""
    if not keyword:
        return None
    
    # 移除危险字符
    keyword = re.sub(r'[<>"\'%;()&]', '', keyword)
    
    # 限制长度
    if len(keyword) > 100:
        raise ValueError("搜索关键词过长")
    
    return f"%{keyword}%"

def sanitize_sort_field(sort_field):
    """验证和清理排序字段"""
    allowed_fields = ['created_at', 'price_asc', 'price_desc', 'student_count']
    if sort_field not in allowed_fields:
        return 'created_at'
    return sort_field

def handle_api_error(error, status_code=400):
    """统一处理API错误"""
    current_app.logger.error(f"API Error: {str(error)}")
    return jsonify({
        'error': str(error),
        'status': 'error'
    }), status_code

def sanitize_filename(filename):
    """清理文件名，防止路径遍历"""
    if not filename:
        return None
    
    # 使用werkzeug的secure_filename
    filename = secure_filename(filename)
    
    # 限制文件名长度
    if len(filename) > 255:
        raise ValueError("文件名过长")
    
    return filename

def validate_file_upload(file, allowed_extensions, max_size):
    """验证上传的文件"""
    if not file:
        raise ValueError("未提供文件")
    
    # 检查文件扩展名
    if '.' not in file.filename:
        raise ValueError("无效的文件扩展名")
    
    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        raise ValueError(f"不支持的文件类型: {extension}")
    
    # 检查文件大小
    file.seek(0, 2)  # 移动到文件末尾
    file_size = file.tell()
    file.seek(0)  # 重置文件指针
    
    if file_size > max_size:
        raise ValueError(f"文件大小超过限制: {max_size / (1024 * 1024):.1f}MB")
    
    return True

def generate_safe_filename(original_filename):
    """生成安全的文件名"""
    if not original_filename:
        return None
    
    # 获取当前时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 获取文件扩展名
    if '.' in original_filename:
        extension = original_filename.rsplit('.', 1)[1]
        return f"{timestamp}_{secure_filename(original_filename.replace('.' + extension, ''))}.{extension}"
    else:
        return f"{timestamp}_{secure_filename(original_filename)}"

def hash_password(password):
    """安全地哈希密码"""
    return generate_password_hash(password, method='pbkdf2:sha256')

def check_password(hashed_password, password):
    """验证密码"""
    return check_password_hash(hashed_password, password)

def sanitize_html(content):
    """清理HTML内容，防止XSS攻击"""
    if not content:
        return None
    
    # 使用bleach清理HTML
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    allowed_attrs = {}
    
    return bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs)