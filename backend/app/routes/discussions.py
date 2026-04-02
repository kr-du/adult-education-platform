from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.announcement import Discussion
from app.models.course import Course
from app.models.user import User


discussions_bp = Blueprint('discussions', __name__)


def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        from flask import abort
        abort(404, description="用户不存在")
    return user


@discussions_bp.route('/course/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_discussions(course_id):
    user = get_current_user()
    
    # 查询已审核通过的讨论
    approved_discussions = Discussion.query.filter_by(
        course_id=course_id,
        parent_id=None,
        status='approved'
    ).all()
    
    # 查询当前用户自己发送的待审核讨论（仅自己可见）
    my_pending_discussions = Discussion.query.filter_by(
        course_id=course_id,
        parent_id=None,
        status='pending',
        user_id=user.id
    ).all()
    
    # 如果是管理员或教师，也显示所有待审核的讨论
    if user.role in ['admin', 'teacher']:
        all_pending_discussions = Discussion.query.filter_by(
            course_id=course_id,
            parent_id=None,
            status='pending'
        ).all()
        # 合并去重
        pending_dict = {d.id: d for d in my_pending_discussions}
        for d in all_pending_discussions:
            pending_dict[d.id] = d
        my_pending_discussions = list(pending_dict.values())
    
    # 合并所有讨论并去重
    all_discussions = {}
    for d in approved_discussions + my_pending_discussions:
        all_discussions[d.id] = d
    
    # 按时间倒序排序
    discussions = sorted(all_discussions.values(), key=lambda x: x.created_at, reverse=True)

    return jsonify({
        'discussions': [d.to_dict() for d in discussions]
    })


@discussions_bp.route('/', methods=['POST'])
@jwt_required()
def create_discussion():
    user = get_current_user()
    data = request.get_json()

    # 验证课程是否存在
    course = Course.query.get(data['course_id'])
    if not course:
        return jsonify({'error': '课程不存在'}), 400

    # 如果是回复，验证父讨论是否存在
    if data.get('parent_id'):
        parent = Discussion.query.get(data['parent_id'])
        if not parent:
            return jsonify({'error': '回复的讨论不存在'}), 400
        # 验证父讨论是否属于同一课程
        if parent.course_id != data['course_id']:
            return jsonify({'error': '回复必须属于同一课程'}), 400

    discussion = Discussion(
        course_id=data['course_id'],
        user_id=user.id,
        parent_id=data.get('parent_id'),
        content=data['content'],
        status='pending'
    )

    db.session.add(discussion)
    db.session.commit()

    return jsonify({
        'message': '发布成功',
        'discussion': discussion.to_dict()
    }), 201


@discussions_bp.route('/<int:discussion_id>/replies', methods=['GET'])
@jwt_required()
def get_replies(discussion_id):
    user = get_current_user()
    
    # 查询已审核通过的回复
    approved_replies = Discussion.query.filter_by(
        parent_id=discussion_id,
        status='approved'
    ).all()
    
    # 查询当前用户自己发送的待审核回复（仅自己可见）
    my_pending_replies = Discussion.query.filter_by(
        parent_id=discussion_id,
        status='pending',
        user_id=user.id
    ).all()
    
    # 如果是管理员或教师，也显示所有待审核的回复
    if user.role in ['admin', 'teacher']:
        all_pending_replies = Discussion.query.filter_by(
            parent_id=discussion_id,
            status='pending'
        ).all()
        # 合并去重
        pending_dict = {r.id: r for r in my_pending_replies}
        for r in all_pending_replies:
            pending_dict[r.id] = r
        my_pending_replies = list(pending_dict.values())
    
    # 合并所有回复并去重
    all_replies = {}
    for r in approved_replies + my_pending_replies:
        all_replies[r.id] = r
    
    # 按时间正序排序
    replies = sorted(all_replies.values(), key=lambda x: x.created_at)

    return jsonify({
        'replies': [r.to_dict() for r in replies]
    })


@discussions_bp.route('/<int:discussion_id>', methods=['DELETE'])
@jwt_required()
def delete_discussion(discussion_id):
    user = get_current_user()
    discussion = Discussion.query.get_or_404(discussion_id)

    if user.role != 'admin' and discussion.user_id != user.id:
        return jsonify({'error': '无权限'}), 403

    # 递归删除所有子回复
    def delete_recursive(disc_id):
        replies = Discussion.query.filter_by(parent_id=disc_id).all()
        for reply in replies:
            delete_recursive(reply.id)
            db.session.delete(reply)
    
    delete_recursive(discussion_id)
    db.session.delete(discussion)
    db.session.commit()

    return jsonify({'message': '删除成功'})


@discussions_bp.route('/teacher', methods=['GET'])
@jwt_required()
def get_teacher_discussions():
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    course_ids = [c.id for c in Course.query.filter_by(teacher_id=user.id).all()]

    discussions = Discussion.query.filter(
        Discussion.course_id.in_(course_ids),
        Discussion.parent_id == None
    ).order_by(Discussion.created_at.desc()).all()

    return jsonify({
        'discussions': [d.to_dict() for d in discussions]
    })
