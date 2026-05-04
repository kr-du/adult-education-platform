from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.course import Course


def get_current_user():
    user_id = int(get_jwt_identity())
    return User.query.get(user_id)


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or user.role != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        return fn(*args, **kwargs)
    return wrapper


def teacher_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or user.role not in ['teacher', 'admin']:
            return jsonify({'error': '需要教师权限'}), 403
        return fn(*args, **kwargs)
    return wrapper


def course_owner_or_admin(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if user.role == 'admin':
            return fn(*args, **kwargs)
        course_id = kwargs.get('course_id')
        if not course_id:
            course_id = request.view_args.get('course_id')
        if course_id:
            course = Course.query.get(course_id)
            if course and course.teacher_id == user.id:
                return fn(*args, **kwargs)
        return jsonify({'error': '无权限'}), 403
    return wrapper


def review_owner_or_admin(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if user.role == 'admin':
            return fn(*args, **kwargs)
        if user.role == 'teacher':
            review_id = kwargs.get('review_id')
            if review_id:
                from app.models.interaction import Review
                review = Review.query.get(review_id)
                if review:
                    course = Course.query.get(review.course_id)
                    if course and course.teacher_id == user.id:
                        return fn(*args, **kwargs)
        return jsonify({'error': '无权限'}), 403
    return wrapper


def get_pagination_params(default_per_page=20):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default_per_page, type=int)
    return page, per_page
