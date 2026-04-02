import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models.user import User

uploads_bp = Blueprint('uploads', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB


def get_current_user():
    user_id = int(get_jwt_identity())
    return User.query.get(user_id)


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_filename(original_filename):
    ext = original_filename.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"


@uploads_bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    user = get_current_user()

    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({'error': '不支持的图片格式，支持：png, jpg, jpeg, gif, webp'}), 400

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_IMAGE_SIZE:
        return jsonify({'error': '图片大小不能超过5MB'}), 400

    filename = generate_filename(file.filename)
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


@uploads_bp.route('/course-image', methods=['POST'])
@jwt_required()
def upload_course_image():
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({'error': '不支持的图片格式'}), 400

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_IMAGE_SIZE:
        return jsonify({'error': '图片大小不能超过5MB'}), 400

    filename = generate_filename(file.filename)
    course_dir = os.path.join(UPLOAD_FOLDER, 'courses')
    os.makedirs(course_dir, exist_ok=True)

    file_path = os.path.join(course_dir, filename)
    file.save(file_path)

    image_url = f'/uploads/courses/{filename}'

    return jsonify({
        'message': '图片上传成功',
        'url': image_url
    })


@uploads_bp.route('/video', methods=['POST'])
@jwt_required()
def upload_video():
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    if not allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        return jsonify({'error': '不支持的视频格式，支持：mp4, webm, ogg'}), 400

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_VIDEO_SIZE:
        return jsonify({'error': '视频大小不能超过500MB'}), 400

    filename = generate_filename(file.filename)
    video_dir = os.path.join(UPLOAD_FOLDER, 'videos')
    os.makedirs(video_dir, exist_ok=True)

    file_path = os.path.join(video_dir, filename)
    file.save(file_path)

    video_url = f'/uploads/videos/{filename}'

    return jsonify({
        'message': '视频上传成功',
        'url': video_url
    })
