from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'error': '用户名已存在'}), 400

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': '邮箱已被注册'}), 400

    user = User(
        username=data['username'],
        email=data['email'],
        real_name=data.get('real_name'),
        phone=data.get('phone'),
        role=data.get('role', 'student')
    )
    user.set_password(data['password'])

    if user.role == 'student':
        user.status = 'approved'
    else:
        user.status = 'pending'

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': '注册成功',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if not user or not user.check_password(data.get('password')):
        return jsonify({'error': '用户名或密码错误'}), 401

    if user.status == 'pending':
        return jsonify({'error': '账号正在审核中'}), 403

    if user.status == 'rejected':
        return jsonify({'error': '账号已被拒绝'}), 403

    # 使用user.id作为identity（必须是字符串）
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'message': '登录成功',
        'access_token': access_token,
        'user': user.to_dict()
    })


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if not user:
        return jsonify({'error': '邮箱不存在'}), 404

    user.set_password(data['new_password'])
    db.session.commit()

    return jsonify({'message': '密码重置成功'})


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': '用户不存在'}), 404

    return jsonify({'user': user.to_dict()})


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.get_json()

    if data.get('real_name'):
        user.real_name = data['real_name']
    if data.get('phone'):
        user.phone = data['phone']
    if data.get('avatar'):
        user.avatar = data['avatar']

    db.session.commit()

    return jsonify({
        'message': '更新成功',
        'user': user.to_dict()
    })
