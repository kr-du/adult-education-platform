"""数据备份与恢复API"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.course import Course, Category, Enrollment, Lesson
from app.models.assignment import Assignment, Submission
from app.models.interaction import Review, Question, Answer, Message, CourseNotice
from app.models.announcement import Announcement, Discussion
import json
import os
from datetime import datetime
from sqlalchemy import text

backup_bp = Blueprint('backup', __name__)

# 备份文件存储目录
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backups')
os.makedirs(BACKUP_DIR, exist_ok=True)


def admin_required(fn):
    """管理员权限装饰器"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        return fn(*args, **kwargs)
    return wrapper


@backup_bp.route('/export', methods=['POST'])
@jwt_required()
def export_data():
    """导出数据备份"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': '需要管理员权限'}), 403
    
    data = request.get_json() or {}
    tables = data.get('tables', 'all')  # all 或 指定表名列表
    
    try:
        backup_data = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'created_by': user.username,
            'data': {}
        }
        
        # 定义所有可备份的表
        all_tables = {
            'users': User,
            'categories': Category,
            'courses': Course,
            'lessons': Lesson,
            'enrollments': Enrollment,
            'assignments': Assignment,
            'submissions': Submission,
            'reviews': Review,
            'questions': Question,
            'answers': Answer,
            'messages': Message,
            'course_notices': CourseNotice,
            'announcements': Announcement,
            'discussions': Discussion
        }
        
        # 确定要备份的表
        if tables == 'all':
            tables_to_backup = all_tables.keys()
        else:
            tables_to_backup = [t for t in tables if t in all_tables]
        
        # 导出数据
        for table_name in tables_to_backup:
            model = all_tables[table_name]
            records = model.query.all()
            backup_data['data'][table_name] = [record.to_dict() for record in records]
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_{timestamp}.json'
        filepath = os.path.join(BACKUP_DIR, filename)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
        
        return jsonify({
            'message': '备份创建成功',
            'filename': filename,
            'filepath': filepath,
            'tables': list(tables_to_backup),
            'record_count': sum(len(v) for v in backup_data['data'].values())
        })
        
    except Exception as e:
        return jsonify({'error': f'备份失败: {str(e)}'}), 500


@backup_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_backup(filename):
    """下载备份文件"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': '需要管理员权限'}), 403
    
    filepath = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': '备份文件不存在'}), 404
    
    return send_file(filepath, as_attachment=True, download_name=filename)


@backup_bp.route('/list', methods=['GET'])
@jwt_required()
def list_backups():
    """获取备份列表"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': '需要管理员权限'}), 403
    
    backups = []
    for filename in os.listdir(BACKUP_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(BACKUP_DIR, filename)
            stat = os.stat(filepath)
            backups.append({
                'filename': filename,
                'size': stat.st_size,
                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
    
    # 按创建时间倒序排序
    backups.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({'backups': backups})


@backup_bp.route('/delete/<filename>', methods=['DELETE'])
@jwt_required()
def delete_backup(filename):
    """删除备份文件"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': '需要管理员权限'}), 403
    
    filepath = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': '备份文件不存在'}), 404
    
    os.remove(filepath)
    return jsonify({'message': '备份已删除'})


@backup_bp.route('/restore', methods=['POST'])
@jwt_required()
def restore_data():
    """从备份恢复数据"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': '需要管理员权限'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': '请上传备份文件'}), 400
    
    file = request.files['file']
    if not file.filename.endswith('.json'):
        return jsonify({'error': '请上传JSON格式的备份文件'}), 400
    
    try:
        # 读取备份文件
        backup_data = json.loads(file.read().decode('utf-8'))
        
        # 验证备份格式
        if 'data' not in backup_data:
            return jsonify({'error': '无效的备份文件格式'}), 400
        
        # 获取恢复选项
        mode = request.form.get('mode', 'merge')  # merge 或 replace
        
        # 恢复数据
        restored_counts = {}
        
        # 按依赖顺序恢复
        restore_order = [
            'users', 'categories', 'courses', 'lessons', 'enrollments',
            'assignments', 'submissions', 'reviews', 'questions', 'answers',
            'messages', 'course_notices', 'announcements', 'discussions'
        ]
        
        for table_name in restore_order:
            if table_name not in backup_data['data']:
                continue
            
            records = backup_data['data'][table_name]
            model_map = {
                'users': User,
                'categories': Category,
                'courses': Course,
                'lessons': Lesson,
                'enrollments': Enrollment,
                'assignments': Assignment,
                'submissions': Submission,
                'reviews': Review,
                'questions': Question,
                'answers': Answer,
                'messages': Message,
                'course_notices': CourseNotice,
                'announcements': Announcement,
                'discussions': Discussion
            }
            
            model = model_map.get(table_name)
            if not model:
                continue
            
            count = 0
            for record_data in records:
                try:
                    record_id = record_data.get('id')
                    if not record_id:
                        continue
                    
                    if mode == 'replace':
                        # 替换模式：删除现有数据
                        existing = model.query.get(record_id)
                        if existing:
                            db.session.delete(existing)
                    
                    # 检查记录是否存在
                    existing = model.query.get(record_id)
                    if existing:
                        # 更新现有记录
                        for key, value in record_data.items():
                            if hasattr(existing, key) and key != 'id':
                                setattr(existing, key, value)
                    else:
                        # 创建新记录
                        new_record = model(**{k: v for k, v in record_data.items() if hasattr(model, k)})
                        db.session.add(new_record)
                    
                    count += 1
                except Exception as e:
                    print(f'恢复记录失败 {table_name}: {e}')
                    continue
            
            restored_counts[table_name] = count
        
        db.session.commit()
        
        return jsonify({
            'message': '数据恢复成功',
            'restored': restored_counts,
            'mode': mode
        })
        
    except json.JSONDecodeError:
        return jsonify({'error': '无效的JSON文件'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'恢复失败: {str(e)}'}), 500


@backup_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """获取数据库统计信息"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': '需要管理员权限'}), 403
    
    stats = {
        'users': User.query.count(),
        'categories': Category.query.count(),
        'courses': Course.query.count(),
        'lessons': Lesson.query.count(),
        'enrollments': Enrollment.query.count(),
        'assignments': Assignment.query.count(),
        'submissions': Submission.query.count(),
        'reviews': Review.query.count(),
        'questions': Question.query.count(),
        'answers': Answer.query.count(),
        'messages': Message.query.count(),
        'course_notices': CourseNotice.query.count(),
        'announcements': Announcement.query.count(),
        'discussions': Discussion.query.count()
    }
    
    return jsonify({'statistics': stats})
