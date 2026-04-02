from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# 上传文件目录
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    jwt.init_app(app)

    # 静态文件服务 - 上传的文件
    @app.route('/uploads/avatars/<filename>')
    def serve_avatar(filename):
        return send_from_directory(os.path.join(UPLOAD_FOLDER, 'avatars'), filename)

    @app.route('/uploads/courses/<filename>')
    def serve_course_image(filename):
        return send_from_directory(os.path.join(UPLOAD_FOLDER, 'courses'), filename)

    @app.route('/uploads/videos/<filename>')
    def serve_video(filename):
        return send_from_directory(os.path.join(UPLOAD_FOLDER, 'videos'), filename)

    # JWT 错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"JWT过期: {jwt_payload}")
        return jsonify({'error': 'Token已过期', 'msg': 'token_expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"JWT无效: {error}")
        return jsonify({'error': 'Token无效', 'msg': str(error)}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"JWT缺失: {error}")
        return jsonify({'error': '未提供Token', 'msg': str(error)}), 401

    # 调试路由
    @app.route('/api/test-token', methods=['GET'])
    @jwt_required()
    def test_token():
        user_id = int(get_jwt_identity())
        return jsonify({'msg': 'Token有效', 'user_id': user_id})

    @app.route('/api/test-login', methods=['POST'])
    def test_login():
        data = request.get_json()
        print(f"收到登录请求: {data}")
        return jsonify({'msg': '收到请求', 'data': data})

    from app.routes.auth import auth_bp
    from app.routes.courses import courses_bp
    from app.routes.assignments import assignments_bp
    from app.routes.users import users_bp
    from app.routes.admin import admin_bp
    from app.routes.discussions import discussions_bp
    from app.routes.uploads import uploads_bp
    from app.routes.interactions import interactions_bp
    from app.routes.ai import ai_bp
    from app.routes.backup import backup_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(assignments_bp, url_prefix='/api/assignments')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(discussions_bp, url_prefix='/api/discussions')
    app.register_blueprint(uploads_bp, url_prefix='/api/uploads')
    app.register_blueprint(interactions_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(backup_bp, url_prefix='/api/backup')

    return app
