from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.course import Course, Category, Enrollment, LessonProgress
from app.models.assignment import Submission
from app.models.announcement import Announcement
from app.models.interaction import Review, Message, Question, Answer, CourseNotice
from app.models.ai import AiConversation

admin_bp = Blueprint('admin', __name__)


def get_current_user():
    """获取当前登录用户"""
    user_id = int(get_jwt_identity())
    return User.query.get(user_id)


def admin_required(fn):
    """管理员权限装饰器"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or user.role != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        return fn(*args, **kwargs)
    return wrapper


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    role = request.args.get('role')
    status = request.args.get('status')
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    query = User.query

    if role:
        query = query.filter_by(role=role)
    if status:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{keyword}%'),
                User.email.ilike(f'%{keyword}%'),
                User.real_name.ilike(f'%{keyword}%')
            )
        )

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'users': [u.to_dict() for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@admin_bp.route('/users/<int:user_id>/approve', methods=['POST'])
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'approved'
    db.session.commit()

    return jsonify({
        'message': '用户已通过审核',
        'user': user.to_dict()
    })


@admin_bp.route('/users/<int:user_id>/reject', methods=['POST'])
@admin_required
def reject_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'rejected'
    db.session.commit()

    return jsonify({
        'message': '用户已被拒绝',
        'user': user.to_dict()
    })


@admin_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
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
        role=data.get('role', 'student'),
        status='approved'  # 管理员创建的用户直接通过
    )
    user.set_password(data.get('password', '123456'))

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': '用户创建成功',
        'user': user.to_dict()
    }), 201


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if 'username' in data:
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user.id:
            return jsonify({'error': '用户名已存在'}), 400
        user.username = data['username']

    if 'email' in data:
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user.id:
            return jsonify({'error': '邮箱已被注册'}), 400
        user.email = data['email']

    if 'real_name' in data:
        user.real_name = data['real_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'role' in data:
        user.role = data['role']
    if 'status' in data:
        user.status = data['status']
    if 'password' in data and data['password']:
        user.set_password(data['password'])

    db.session.commit()

    return jsonify({
        'message': '用户更新成功',
        'user': user.to_dict()
    })


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    from sqlalchemy import text
    
    # 先检查用户是否存在
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 清除 session 缓存，避免自动关联更新
    db.session.expire_all()
    db.session.close()
    
    # 使用原始 SQL 删除所有关联数据
    uid = str(user_id)
    
    try:
        # 1. 删除作业提交记录
        db.session.execute(text(f'DELETE FROM submissions WHERE student_id = {uid}'))
        db.session.commit()
        
        # 2. 删除课程评价
        db.session.execute(text(f'DELETE FROM reviews WHERE user_id = {uid}'))
        db.session.commit()
        
        # 3. 删除消息通知
        db.session.execute(text(f'DELETE FROM messages WHERE user_id = {uid}'))
        db.session.commit()
        
        # 4. 删除答疑回答
        db.session.execute(text(f'DELETE FROM answers WHERE user_id = {uid}'))
        db.session.commit()
        
        # 5. 删除答疑问题
        db.session.execute(text(f'DELETE FROM questions WHERE user_id = {uid}'))
        db.session.commit()
        
        # 6. 删除课程讨论
        db.session.execute(text(f'DELETE FROM discussions WHERE user_id = {uid}'))
        db.session.commit()
        
        # 7. 删除学习进度
        db.session.execute(text(f'DELETE FROM lesson_progress WHERE user_id = {uid}'))
        db.session.commit()
        
        # 8. 删除课程报名
        db.session.execute(text(f'DELETE FROM enrollments WHERE user_id = {uid}'))
        db.session.commit()
        
        # 9. 删除公告
        db.session.execute(text(f'DELETE FROM announcements WHERE author_id = {uid}'))
        db.session.commit()
        
        # 10. 删除课程公告
        db.session.execute(text(f'DELETE FROM course_notices WHERE teacher_id = {uid}'))
        db.session.commit()
        
        # 11. 删除AI消息和对话
        conv_ids = db.session.execute(text(f'SELECT id FROM ai_conversations WHERE user_id = {uid}')).fetchall()
        if conv_ids:
            conv_id_list = ','.join(str(c[0]) for c in conv_ids)
            db.session.execute(text(f'DELETE FROM ai_messages WHERE conversation_id IN ({conv_id_list})'))
            db.session.commit()
        db.session.execute(text(f'DELETE FROM ai_conversations WHERE user_id = {uid}'))
        db.session.commit()
        
        # 12. 如果是教师，先删除其创建的课程的所有关联数据，再删除课程
        course_ids = db.session.execute(text(f'SELECT id FROM courses WHERE teacher_id = {uid}')).fetchall()
        for (cid,) in course_ids:
            # 删除课程相关的所有数据（注意外键顺序）
            # 先删除 lesson_progress（依赖 lessons）
            db.session.execute(text(f'DELETE lp FROM lesson_progress lp INNER JOIN lessons l ON lp.lesson_id = l.id WHERE l.course_id = {cid}'))
            db.session.commit()
            
            # 删除 lessons
            db.session.execute(text(f'DELETE FROM lessons WHERE course_id = {cid}'))
            db.session.commit()
            
            # 先删除 submissions（依赖 assignments）
            db.session.execute(text(f'DELETE s FROM submissions s INNER JOIN assignments a ON s.assignment_id = a.id WHERE a.course_id = {cid}'))
            db.session.commit()
            
            # 删除 assignments
            db.session.execute(text(f'DELETE FROM assignments WHERE course_id = {cid}'))
            db.session.commit()
            
            # 先删除 answers（依赖 questions）- 使用子查询
            db.session.execute(text(f'DELETE FROM answers WHERE question_id IN (SELECT q.id FROM (SELECT id FROM questions WHERE course_id = {cid}) q)'))
            db.session.commit()
            
            # 删除 questions
            db.session.execute(text(f'DELETE FROM questions WHERE course_id = {cid}'))
            db.session.commit()
            
            # 先删除 discussions 的回复（自引用）- 删除有 parent_id 的记录
            db.session.execute(text(f'DELETE FROM discussions WHERE course_id = {cid} AND parent_id IS NOT NULL'))
            db.session.commit()
            
            # 删除 discussions 主帖
            db.session.execute(text(f'DELETE FROM discussions WHERE course_id = {cid}'))
            db.session.commit()
            
            # 删除 reviews
            db.session.execute(text(f'DELETE FROM reviews WHERE course_id = {cid}'))
            db.session.commit()
            
            # 删除 course_notices
            db.session.execute(text(f'DELETE FROM course_notices WHERE course_id = {cid}'))
            db.session.commit()
            
            # 删除 enrollments
            db.session.execute(text(f'DELETE FROM enrollments WHERE course_id = {cid}'))
            db.session.commit()
        
        # 13. 删除该教师创建的所有课程
        db.session.execute(text(f'DELETE FROM courses WHERE teacher_id = {uid}'))
        db.session.commit()
        
        # 14. 最后删除用户
        db.session.execute(text(f'DELETE FROM users WHERE id = {uid}'))
        db.session.commit()
        
        return jsonify({'message': '用户已删除'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


@admin_bp.route('/teachers', methods=['GET'])
@admin_required
def get_teachers():
    teachers = User.query.filter_by(role='teacher', status='approved').all()
    return jsonify({
        'teachers': [t.to_dict() for t in teachers]
    })


@admin_bp.route('/announcements', methods=['GET'])
@jwt_required()
def get_announcements():
    announcements = Announcement.query.order_by(
        Announcement.is_pinned.desc(),
        Announcement.created_at.desc()
    ).all()

    return jsonify({
        'announcements': [a.to_dict() for a in announcements]
    })


@admin_bp.route('/announcements', methods=['POST'])
@admin_required
def create_announcement():
    data = request.get_json()
    user = get_current_user()

    announcement = Announcement(
        title=data['title'],
        content=data['content'],
        author_id=user.id,
        is_pinned=data.get('is_pinned', False)
    )

    db.session.add(announcement)
    db.session.commit()

    return jsonify({
        'message': '公告发布成功',
        'announcement': announcement.to_dict()
    }), 201


@admin_bp.route('/announcements/<int:announcement_id>', methods=['PUT'])
@admin_required
def update_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    data = request.get_json()

    if 'title' in data:
        announcement.title = data['title']
    if 'content' in data:
        announcement.content = data['content']
    if 'is_pinned' in data:
        announcement.is_pinned = data['is_pinned']

    db.session.commit()

    return jsonify({
        'message': '公告更新成功',
        'announcement': announcement.to_dict()
    })


@admin_bp.route('/announcements/<int:announcement_id>', methods=['DELETE'])
@admin_required
def delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()

    return jsonify({'message': '公告已删除'})


@admin_bp.route('/statistics', methods=['GET'])
@admin_required
def get_statistics():
    from datetime import datetime, timedelta
    from sqlalchemy import func

    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 用户统计
    total_users = User.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_admins = User.query.filter_by(role='admin').count()
    pending_users = User.query.filter_by(status='pending').count()

    # 课程统计
    total_courses = Course.query.count()
    published_courses = Course.query.filter_by(status='published').count()
    draft_courses = Course.query.filter_by(status='draft').count()
    archived_courses = Course.query.filter_by(status='archived').count()

    # 报名统计
    total_enrollments = Enrollment.query.count()

    # 提交统计
    total_submissions = Submission.query.count()
    graded_submissions = Submission.query.filter(Submission.score.isnot(None)).count()
    pending_submissions = Submission.query.filter(Submission.score.is_(None)).count()
    avg_score = db.session.query(func.avg(Submission.score)).filter(Submission.score.isnot(None)).scalar()
    avg_score = round(float(avg_score), 1) if avg_score else 0

    # 本月新增
    monthly_new_users = User.query.filter(User.created_at >= month_start).count()
    monthly_new_courses = Course.query.filter(Course.created_at >= month_start).count()
    monthly_new_enrollments = Enrollment.query.filter(Enrollment.enrolled_at >= month_start).count()

    # 热门课程 Top 5（按报名人数排序）
    top_courses_query = db.session.query(
        Course,
        func.count(Enrollment.id).label('enrollment_count')
    ).outerjoin(Enrollment).filter(
        Course.status == 'published'
    ).group_by(Course.id).order_by(
        func.count(Enrollment.id).desc()
    ).limit(5).all()

    top_courses_data = []
    for course, count in top_courses_query:
        course_dict = course.to_dict()
        course_dict['student_count'] = count
        top_courses_data.append(course_dict)

    return jsonify({
        'total_users': total_users,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_submissions': total_submissions,
        'user_stats': {
            'students': total_students,
            'teachers': total_teachers,
            'admins': total_admins,
            'pending': pending_users
        },
        'course_stats': {
            'published': published_courses,
            'draft': draft_courses,
            'archived': archived_courses
        },
        'submission_stats': {
            'total': total_submissions,
            'graded': graded_submissions,
            'pending': pending_submissions,
            'avg_score': avg_score
        },
        'top_courses': top_courses_data,
        'monthly': {
            'new_users': monthly_new_users,
            'new_courses': monthly_new_courses,
            'new_enrollments': monthly_new_enrollments
        }
    })

# 课程列表
@admin_bp.route('/courses', methods=['GET'])
@admin_required
def get_all_courses():
    page = request.args.get('page', 1, type=int) # 当前页码
    per_page = request.args.get('per_page', 20, type=int) # 每页显示数量
    status = request.args.get('status') # 课程状态
    category_id = request.args.get('category_id', type=int) # 课程分类
    keyword = request.args.get('keyword', '') # 课程关键字

    query = Course.query # 课程查询对象
    if status:
        query = query.filter_by(status=status)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if keyword:
        query = query.filter(Course.title.ilike(f'%{keyword}%'))

    # 分页
    pagination = query.order_by(Course.created_at.desc()).paginate(# 按创建时间降序排列
        page=page, per_page=per_page, error_out=False
    )
    # 返回课程列表
    return jsonify({
        'courses': [c.to_dict() for c in pagination.items], # 课程列表
        'total': pagination.total, # 总数
        'pages': pagination.pages, # 页数
        'current_page': page # 当前页码
    })
