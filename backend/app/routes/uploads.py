import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.utils.security import validate_file_upload, sanitize_filename, generate_safe_filename, handle_api_error

uploads_bp = Blueprint('uploads', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg'}


def get_current_user():
    user_id = int(get_jwt_identity())
    return User.query.get(user_id)


def handle_upload_error(f):
    """装饰器：统一处理上传错误"""
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return handle_api_error(e, 400)
        except Exception as e:
            db.session.rollback()
            return handle_api_error(f"上传失败: {str(e)}", 500)
    wrapper.__name__ = f.__name__
    return wrapper


@uploads_bp.route('/avatar', methods=['POST'])
@jwt_required()
@handle_upload_error
def upload_avatar():
    user = get_current_user()

    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    try:
        # 验证文件上传
        validate_file_upload(file, ALLOWED_IMAGE_EXTENSIONS, 5 * 1024 * 1024)
        
        # 生成安全文件名
        filename = generate_safe_filename(file.filename)
        avatar_dir = os.path.join(UPLOAD_FOLDER, 'avatars')
        os.makedirs(avatar_dir, exist_ok=True)

        file_path = os.path.join(avatar_dir, filename)
        file.save(file_path)

        avatar_url = f'/uploads/avatars/{filename}'
        user.avatar = avatar_url
        db.session.commit()

        return jsonify({
            'message': '头像上传成功',
            'url': avatar_url
        })
    except ValueError as e:
        return handle_api_error(e, 400)
    except Exception as e:
        db.session.rollback()
        return handle_api_error(f"头像上传失败: {str(e)}", 500)


@uploads_bp.route('/course-image', methods=['POST'])
@jwt_required()
@handle_upload_error
def upload_course_image():
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    try:
        # 验证文件上传
        validate_file_upload(file, ALLOWED_IMAGE_EXTENSIONS, 5 * 1024 * 1024)
        
        # 生成安全文件名
        filename = generate_safe_filename(file.filename)
        course_dir = os.path.join(UPLOAD_FOLDER, 'courses')
        os.makedirs(course_dir, exist_ok=True)

        file_path = os.path.join(course_dir, filename)
        file.save(file_path)

        image_url = f'/uploads/courses/{filename}'

        return jsonify({
            'message': '图片上传成功',
            'url': image_url
        })
    except ValueError as e:
        return handle_api_error(e, 400)
    except Exception as e:
        db.session.rollback()
        return handle_api_error(f"课程图片上传失败: {str(e)}", 500)


@uploads_bp.route('/video', methods=['POST'])
@jwt_required()
@handle_upload_error
def upload_video():
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    try:
        # 验证文件上传
        validate_file_upload(file, ALLOWED_VIDEO_EXTENSIONS, 500 * 1024 * 1024)
        
        # 生成安全文件名
        filename = generate_safe_filename(file.filename)
        video_dir = os.path.join(UPLOAD_FOLDER, 'videos')
        os.makedirs(video_dir, exist_ok=True)

        file_path = os.path.join(video_dir, filename)
        file.save(file_path)

        video_url = f'/uploads/videos/{filename}'

        return jsonify({
            'message': '视频上传成功',
            'url': video_url
        })
    except ValueError as e:
        return handle_api_error(e, 400)
    except Exception as e:
        db.session.rollback()
        return handle_api_error(f"视频上传失败: {str(e)}", 500)