from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.course import Course
from app.models.interaction import Review, Message, Question, Answer, CourseNotice
from app.models.announcement import Discussion
from app.utils.auth import get_current_user, teacher_required, get_pagination_params

interactions_bp = Blueprint('interactions', __name__)


# ==================== Reviews (课程评价) ====================

@interactions_bp.route('/reviews/course/<int:course_id>', methods=['GET'])
def get_course_reviews(course_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # 查询已审核通过的评价
    approved_reviews = Review.query.filter_by(course_id=course_id, status='approved').all()
    
    # 查询当前用户自己发送的待审核评价（仅自己可见）
    try:
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
    except:
        user_id = None
    
    my_pending_reviews = []
    if user_id:
        my_pending_reviews = Review.query.filter_by(
            course_id=course_id,
            status='pending',
            user_id=user_id
        ).all()
    
    # 如果是管理员或教师，也显示所有待审核的评价
    if user_id and current_user.role in ['admin', 'teacher']:
        all_pending_reviews = Review.query.filter_by(course_id=course_id, status='pending').all()
        pending_dict = {r.id: r for r in my_pending_reviews}
        for r in all_pending_reviews:
            pending_dict[r.id] = r
        my_pending_reviews = list(pending_dict.values())
    
    # 合并所有评价并去重
    all_reviews_dict = {}
    for r in approved_reviews + my_pending_reviews:
        all_reviews_dict[r.id] = r
    
    # 按时间倒序排序
    all_reviews = sorted(all_reviews_dict.values(), key=lambda x: x.created_at, reverse=True)
    
    # 手动分页
    total = len(all_reviews)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_reviews = all_reviews[start:end]

    reviews = [review.to_dict() for review in paginated_reviews]

    # 计算平均评分（只计算已审核通过的）
    ratings = [r.rating for r in approved_reviews]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    return jsonify({
        'reviews': reviews,
        'average_rating': round(avg_rating, 1),
        'total': total,
        'pages': (total + per_page - 1) // per_page if total > 0 else 1,
        'current_page': page
    })


@interactions_bp.route('/reviews/', methods=['POST'])
@jwt_required()
def create_review():
    user = get_current_user()
    if user.role != 'student':
        return jsonify({'error': '只有学生可以评价'}), 403

    data = request.get_json()
    course_id = data.get('course_id')
    rating = data.get('rating')

    if not course_id or not rating:
        return jsonify({'error': '课程ID和评分不能为空'}), 400

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': '评分必须是1-5之间的整数'}), 400

    enrollment = Enrollment.query.filter_by(user_id=user.id, course_id=course_id).first()
    if not enrollment:
        return jsonify({'error': '未报名该课程，无法评价'}), 403

    existing = Review.query.filter_by(user_id=user.id, course_id=course_id).first()
    if existing:
        return jsonify({'error': '已评价过该课程'}), 400

    review = Review(
        course_id=course_id,
        user_id=user.id,
        rating=rating,
        content=data.get('content'),
        status='pending'
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({
        'message': '提交成功，内容审核通过后将显示',
        'review': review.to_dict()
    }), 201


@interactions_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    user = get_current_user()
    review = Review.query.get_or_404(review_id)

    if review.user_id != user.id:
        return jsonify({'error': '只能删除自己的评价'}), 403

    db.session.delete(review)
    db.session.commit()

    return jsonify({'message': '评价删除成功'})


# ==================== Messages (消息通知) ====================

@interactions_bp.route('/messages/', methods=['GET'])
@jwt_required()
def get_messages():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    message_type = request.args.get('type')

    query = Message.query.filter_by(user_id=user.id)
    if message_type:
        query = query.filter_by(message_type=message_type)

    pagination = query.order_by(Message.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'messages': [msg.to_dict() for msg in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@interactions_bp.route('/messages/<int:message_id>/read', methods=['PUT'])
@jwt_required()
def mark_message_read(message_id):
    user = get_current_user()
    message = Message.query.get_or_404(message_id)

    if message.user_id != user.id:
        return jsonify({'error': '无权限'}), 403

    message.is_read = True
    db.session.commit()

    return jsonify({
        'message': '已标记为已读',
        'data': message.to_dict()
    })


@interactions_bp.route('/messages/read-all', methods=['PUT'])
@jwt_required()
def mark_all_messages_read():
    user = get_current_user()

    Message.query.filter_by(user_id=user.id, is_read=False).update({'is_read': True})
    db.session.commit()

    return jsonify({'message': '已全部标记为已读'})


@interactions_bp.route('/messages/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    user = get_current_user()
    count = Message.query.filter_by(user_id=user.id, is_read=False).count()

    return jsonify({'unread_count': count})


# ==================== Questions & Answers (答疑互动) ====================

@interactions_bp.route('/questions/course/<int:course_id>', methods=['GET'])
def get_course_questions(course_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    resolved = request.args.get('resolved', type=str)

    # 只返回已审核通过的问题
    query = Question.query.filter_by(course_id=course_id, status='approved')

    if resolved is not None:
        query = query.filter_by(is_resolved=(resolved.lower() == 'true'))

    pagination = query.order_by(Question.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'questions': [q.to_dict() for q in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@interactions_bp.route('/questions/', methods=['POST'])
@jwt_required()
def create_question():
    user = get_current_user()
    data = request.get_json()

    course_id = data.get('course_id')
    title = data.get('title')
    content = data.get('content')

    if not course_id or not title or not content:
        return jsonify({'error': '课程ID、标题和内容不能为空'}), 400

    course = Course.query.get_or_404(course_id)

    question = Question(
        course_id=course_id,
        user_id=user.id,
        title=title,
        content=content,
        status='pending'
    )

    db.session.add(question)
    db.session.commit()

    return jsonify({
        'message': '提问成功，内容审核通过后将显示',
        'question': question.to_dict()
    }), 201


@interactions_bp.route('/questions/<int:question_id>/answers', methods=['GET'])
def get_question_answers(question_id):
    question = Question.query.get_or_404(question_id)
    # 只返回已审核通过的回答
    answers = Answer.query.filter_by(question_id=question_id, status='approved').order_by(
        Answer.created_at.asc()
    ).all()

    return jsonify({
        'question': question.to_dict(),
        'answers': [a.to_dict() for a in answers]
    })


@interactions_bp.route('/questions/<int:question_id>/answers', methods=['POST'])
@jwt_required()
def create_answer(question_id):
    user = get_current_user()
    question = Question.query.get_or_404(question_id)

    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({'error': '回答内容不能为空'}), 400

    is_teacher = user.role == 'teacher'

    answer = Answer(
        question_id=question_id,
        user_id=user.id,
        content=content,
        is_teacher=is_teacher,
        status='pending'
    )

    db.session.add(answer)
    db.session.commit()

    return jsonify({
        'message': '回答成功，内容审核通过后将显示',
        'answer': answer.to_dict()
    }), 201


@interactions_bp.route('/questions/<int:question_id>/resolve', methods=['PUT'])
@jwt_required()
def resolve_question(question_id):
    user = get_current_user()
    question = Question.query.get_or_404(question_id)

    course = Course.query.get(question.course_id)
    if question.user_id != user.id and (not course or course.teacher_id != user.id):
        return jsonify({'error': '无权限'}), 403

    question.is_resolved = True
    db.session.commit()

    return jsonify({
        'message': '问题已标记为已解决',
        'question': question.to_dict()
    })


# ==================== Course Notices (课程公告) ====================

@interactions_bp.route('/notices/course/<int:course_id>', methods=['GET'])
def get_course_notices(course_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = CourseNotice.query.filter_by(course_id=course_id).order_by(
        CourseNotice.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'notices': [notice.to_dict() for notice in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@interactions_bp.route('/notices/', methods=['POST'])
@jwt_required()
def create_notice():
    user = get_current_user()
    if user.role != 'teacher':
        return jsonify({'error': '只有教师可以发布公告'}), 403

    data = request.get_json()
    course_id = data.get('course_id')
    title = data.get('title')
    content = data.get('content')

    if not course_id or not title or not content:
        return jsonify({'error': '课程ID、标题和内容不能为空'}), 400

    course = Course.query.get_or_404(course_id)
    if course.teacher_id != user.id:
        return jsonify({'error': '只能在自己教授的课程中发布公告'}), 403

    notice = CourseNotice(
        course_id=course_id,
        teacher_id=user.id,
        title=title,
        content=content
    )

    db.session.add(notice)
    db.session.commit()

    return jsonify({
        'message': '公告发布成功',
        'notice': notice.to_dict()
    }), 201


@interactions_bp.route('/notices/<int:notice_id>', methods=['DELETE'])
@jwt_required()
def delete_notice(notice_id):
    user = get_current_user()
    notice = CourseNotice.query.get_or_404(notice_id)

    if user.role != 'admin' and notice.teacher_id != user.id:
        return jsonify({'error': '无权限'}), 403

    db.session.delete(notice)
    db.session.commit()

    return jsonify({'message': '公告删除成功'})


# ==================== Teacher Statistics (教师统计) ====================

@interactions_bp.route('/teacher/course/<int:course_id>/students', methods=['GET'])
@jwt_required()
def get_course_students(course_id):
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    course = Course.query.get_or_404(course_id)
    if user.role != 'admin' and course.teacher_id != user.id:
        return jsonify({'error': '无权限'}), 403

    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    students = []

    for enrollment in enrollments:
        student = User.query.get(enrollment.user_id)
        if not student:
            continue

        lessons = Lesson.query.filter_by(course_id=course_id).all()
        total_lessons = len(lessons)
        completed_lessons = 0

        for lesson in lessons:
            progress = LessonProgress.query.filter_by(
                user_id=student.id, lesson_id=lesson.id, completed=True
            ).first()
            if progress:
                completed_lessons += 1

        progress_pct = round((completed_lessons / total_lessons) * 100, 1) if total_lessons > 0 else 0

        students.append({
            'user_id': student.id,
            'username': student.username,
            'real_name': student.real_name,
            'avatar': student.avatar,
            'enrolled_at': enrollment.enrolled_at.isoformat(),
            'completed': enrollment.completed,
            'progress': progress_pct,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons
        })

    return jsonify({'students': students})


@interactions_bp.route('/teacher/course/<int:course_id>/statistics', methods=['GET'])
@jwt_required()
def get_course_statistics(course_id):
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    course = Course.query.get_or_404(course_id)
    if user.role != 'admin' and course.teacher_id != user.id:
        return jsonify({'error': '无权限'}), 403

    total_students = Enrollment.query.filter_by(course_id=course_id).count()
    completed_students = Enrollment.query.filter_by(course_id=course_id, completed=True).count()

    reviews = Review.query.filter_by(course_id=course_id).all()
    ratings = [r.rating for r in reviews]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0

    total_lessons = Lesson.query.filter_by(course_id=course_id).count()

    lesson_stats = []
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
    for lesson in lessons:
        completed_count = LessonProgress.query.filter_by(lesson_id=lesson.id, completed=True).count()
        lesson_stats.append({
            'lesson_id': lesson.id,
            'title': lesson.title,
            'completed_count': completed_count,
            'completion_rate': round((completed_count / total_students) * 100, 1) if total_students > 0 else 0
        })

    return jsonify({
        'course_id': course_id,
        'course_title': course.title,
        'total_students': total_students,
        'completed_students': completed_students,
        'completion_rate': round((completed_students / total_students) * 100, 1) if total_students > 0 else 0,
        'review_count': len(reviews),
        'average_rating': avg_rating,
        'total_lessons': total_lessons,
        'lesson_statistics': lesson_stats
    })


# ==================== 审核管理 ====================

@interactions_bp.route('/admin/reviews', methods=['GET'])
@jwt_required()
def get_admin_reviews():
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403

    page, per_page = get_pagination_params(default_per_page=20)
    status = request.args.get('status', 'pending')
    course_id = request.args.get('course_id', type=int)
    
    query = Review.query
    if status:
        query = query.filter_by(status=status)
    if course_id:
        query = query.filter_by(course_id=course_id)
    # 教师只能审核自己课程的评价
    if user.role == 'teacher':
        teacher_course_ids = [c.id for c in Course.query.filter_by(teacher_id=user.id).all()]
        query = query.filter(Review.course_id.in_(teacher_course_ids))
    
    pagination = query.order_by(Review.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    reviews = []
    for review in pagination.items:
        review_dict = review.to_dict()
        review_dict['course_title'] = review.course.title if review.course else None
        reviews.append(review_dict)
    
    return jsonify({
        'reviews': reviews,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@interactions_bp.route('/admin/reviews/<int:review_id>/approve', methods=['PUT'])
@jwt_required()
def approve_review(review_id):
    """审核通过评价"""
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    review = Review.query.get_or_404(review_id)
    
    # 教师只能审核自己课程的评价
    if user.role == 'teacher':
        course = Course.query.get(review.course_id)
        if not course or course.teacher_id != user.id:
            return jsonify({'error': '无权限'}), 403
    
    review.status = 'approved'
    db.session.commit()
    
    return jsonify({'message': '评价已通过审核', 'review': review.to_dict()})


@interactions_bp.route('/admin/reviews/<int:review_id>/reject', methods=['PUT'])
@jwt_required()
def reject_review(review_id):
    """审核拒绝评价"""
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    review = Review.query.get_or_404(review_id)
    
    # 教师只能审核自己课程的评价
    if user.role == 'teacher':
        course = Course.query.get(review.course_id)
        if not course or course.teacher_id != user.id:
            return jsonify({'error': '无权限'}), 403
    
    review.status = 'rejected'
    db.session.commit()
    
    return jsonify({'message': '评价已拒绝', 'review': review.to_dict()})


@interactions_bp.route('/admin/questions', methods=['GET'])
@jwt_required()
def get_admin_questions():
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403

    page, per_page = get_pagination_params(default_per_page=20)
    status = request.args.get('status', 'pending')
    course_id = request.args.get('course_id', type=int)
    
    query = Question.query
    if status:
        query = query.filter_by(status=status)
    if course_id:
        query = query.filter_by(course_id=course_id)
    # 教师只能审核自己课程的问题
    if user.role == 'teacher':
        teacher_course_ids = [c.id for c in Course.query.filter_by(teacher_id=user.id).all()]
        query = query.filter(Question.course_id.in_(teacher_course_ids))
    
    pagination = query.order_by(Question.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    questions = []
    for q in pagination.items:
        q_dict = q.to_dict()
        q_dict['course_title'] = q.course.title if q.course else None
        questions.append(q_dict)
    
    return jsonify({
        'questions': questions,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@interactions_bp.route('/admin/questions/<int:question_id>/approve', methods=['PUT'])
@jwt_required()
def approve_question(question_id):
    """审核通过问题"""
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    question = Question.query.get_or_404(question_id)
    
    # 教师只能审核自己课程的问题
    if user.role == 'teacher':
        course = Course.query.get(question.course_id)
        if not course or course.teacher_id != user.id:
            return jsonify({'error': '无权限'}), 403
    
    question.status = 'approved'
    db.session.commit()
    
    return jsonify({'message': '问题已通过审核', 'question': question.to_dict()})


@interactions_bp.route('/admin/questions/<int:question_id>/reject', methods=['PUT'])
@jwt_required()
def reject_question(question_id):
    """审核拒绝问题"""
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    question = Question.query.get_or_404(question_id)
    
    # 教师只能审核自己课程的问题
    if user.role == 'teacher':
        course = Course.query.get(question.course_id)
        if not course or course.teacher_id != user.id:
            return jsonify({'error': '无权限'}), 403
    
    question.status = 'rejected'
    db.session.commit()
    
    return jsonify({'message': '问题已拒绝', 'question': question.to_dict()})


@interactions_bp.route('/admin/answers', methods=['GET'])
@jwt_required()
def get_admin_answers():
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403

    page, per_page = get_pagination_params(default_per_page=20)
    status = request.args.get('status', 'pending')
    
    query = Answer.query
    if status:
        query = query.filter_by(status=status)
    # 教师只能审核自己课程的回答
    if user.role == 'teacher':
        teacher_course_ids = [c.id for c in Course.query.filter_by(teacher_id=user.id).all()]
        query = query.join(Question).filter(Question.course_id.in_(teacher_course_ids))
    
    pagination = query.order_by(Answer.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    answers = []
    for a in pagination.items:
        a_dict = a.to_dict()
        if a.question:
            a_dict['question_title'] = a.question.title
            a_dict['course_id'] = a.question.course_id
            a_dict['course_title'] = a.question.course.title if a.question.course else None
        answers.append(a_dict)
    
    return jsonify({
        'answers': answers,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@interactions_bp.route('/admin/answers/<int:answer_id>/approve', methods=['PUT'])
@jwt_required()
def approve_answer(answer_id):
    """审核通过回答"""
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    answer = Answer.query.get_or_404(answer_id)
    
    # 教师只能审核自己课程的回答
    if user.role == 'teacher' and answer.question:
        course = Course.query.get(answer.question.course_id)
        if not course or course.teacher_id != user.id:
            return jsonify({'error': '无权限'}), 403
    
    answer.status = 'approved'
    db.session.commit()
    
    return jsonify({'message': '回答已通过审核', 'answer': answer.to_dict()})


@interactions_bp.route('/admin/answers/<int:answer_id>/reject', methods=['PUT'])
@jwt_required()
def reject_answer(answer_id):
    """审核拒绝回答"""
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    answer = Answer.query.get_or_404(answer_id)
    
    # 教师只能审核自己课程的回答
    if user.role == 'teacher' and answer.question:
        course = Course.query.get(answer.question.course_id)
        if not course or course.teacher_id != user.id:
            return jsonify({'error': '无权限'}), 403
    
    answer.status = 'rejected'
    db.session.commit()
    
    return jsonify({'message': '回答已拒绝', 'answer': answer.to_dict()})


@interactions_bp.route('/admin/discussions', methods=['GET'])
@jwt_required()
def get_admin_discussions():
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403

    page, per_page = get_pagination_params(default_per_page=20)
    status = request.args.get('status', 'pending')
    course_id = request.args.get('course_id', type=int)
    
    query = Discussion.query.filter(Discussion.parent_id.is_(None))  # 只查主帖
    if status:
        query = query.filter_by(status=status)
    if course_id:
        query = query.filter_by(course_id=course_id)
    # 教师只能审核自己课程的讨论
    if user.role == 'teacher':
        teacher_course_ids = [c.id for c in Course.query.filter_by(teacher_id=user.id).all()]
        query = query.filter(Discussion.course_id.in_(teacher_course_ids))
    
    pagination = query.order_by(Discussion.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    discussions = []
    for d in pagination.items:
        d_dict = d.to_dict()
        d_dict['course_title'] = d.course.title if d.course else None
        discussions.append(d_dict)
    
    return jsonify({
        'discussions': discussions,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@interactions_bp.route('/admin/discussions/<int:discussion_id>/approve', methods=['PUT'])
@jwt_required()
def approve_discussion(discussion_id):
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    discussion = Discussion.query.get_or_404(discussion_id)
    
    # 教师只能审核自己课程的讨论
    if user.role == 'teacher':
        course = Course.query.get(discussion.course_id)
        if not course or course.teacher_id != user.id:
            return jsonify({'error': '无权限'}), 403
    
    discussion.status = 'approved'
    db.session.commit()
    
    return jsonify({'message': '讨论已通过审核', 'discussion': discussion.to_dict()})


@interactions_bp.route('/admin/discussions/<int:discussion_id>/reject', methods=['PUT'])
@jwt_required()
def reject_discussion(discussion_id):
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    discussion = Discussion.query.get_or_404(discussion_id)
    
    # 教师只能审核自己课程的讨论
    if user.role == 'teacher':
        course = Course.query.get(discussion.course_id)
        if not course or course.teacher_id != user.id:
            return jsonify({'error': '无权限'}), 403
    
    discussion.status = 'rejected'
    db.session.commit()
    
    return jsonify({'message': '讨论已拒绝', 'discussion': discussion.to_dict()})


@interactions_bp.route('/reviews/statistics', methods=['GET'])
@jwt_required()
def get_admin_statistics():
    """获取审核统计数据"""
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    # 如果是教师，只统计自己课程的数据
    if user.role == 'teacher':
        teacher_course_ids = [c.id for c in Course.query.filter_by(teacher_id=user.id).all()]
        pending_reviews = Review.query.filter(Review.course_id.in_(teacher_course_ids), Review.status == 'pending').count()
        pending_questions = Question.query.filter(Question.course_id.in_(teacher_course_ids), Question.status == 'pending').count()
        pending_answers = Answer.query.join(Question).filter(Question.course_id.in_(teacher_course_ids), Answer.status == 'pending').count()
        pending_discussions = Discussion.query.filter(Discussion.course_id.in_(teacher_course_ids), Discussion.parent_id.is_(None), Discussion.status == 'pending').count()
    else:
        pending_reviews = Review.query.filter_by(status='pending').count()
        pending_questions = Question.query.filter_by(status='pending').count()
        pending_answers = Answer.query.filter_by(status='pending').count()
        pending_discussions = Discussion.query.filter(Discussion.parent_id.is_(None), Discussion.status == 'pending').count()
    
    return jsonify({
        'pending_reviews': pending_reviews,
        'pending_questions': pending_questions,
        'pending_answers': pending_answers,
        'pending_discussions': pending_discussions,
        'total_pending': pending_reviews + pending_questions + pending_answers + pending_discussions
    })


# ==================== 删除内容接口 ====================

@interactions_bp.route('/admin/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review_admin(review_id):
    """管理员删除评价"""
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    review = Review.query.get_or_404(review_id)
    
    if user.role == 'teacher':
        course = Course.query.get(review.course_id)
        if not course or course.teacher_id != user.id:
            return jsonify({'error': '无权限'}), 403
    
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': '评价已删除'})


@interactions_bp.route('/admin/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question_admin(question_id):
    """管理员删除问题"""
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    question = Question.query.get_or_404(question_id)
    
    if user.role == 'teacher':
        course = Course.query.get(question.course_id)
        if not course or course.teacher_id != user.id:
            return jsonify({'error': '无权限'}), 403
    
    Answer.query.filter_by(question_id=question_id).delete()
    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': '问题已删除'})


@interactions_bp.route('/admin/answers/<int:answer_id>', methods=['DELETE'])
@jwt_required()
def delete_answer_admin(answer_id):
    """管理员删除回答"""
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    answer = Answer.query.get_or_404(answer_id)
    
    if user.role == 'teacher' and answer.question:
        course = Course.query.get(answer.question.course_id)
        if not course or course.teacher_id != user.id:
            return jsonify({'error': '无权限'}), 403
    
    db.session.delete(answer)
    db.session.commit()
    return jsonify({'message': '回答已删除'})


@interactions_bp.route('/admin/discussions/<int:discussion_id>', methods=['DELETE'])
@jwt_required()
def delete_discussion_admin(discussion_id):
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    discussion = Discussion.query.get_or_404(discussion_id)
    
    if user.role == 'teacher':
        course = Course.query.get(discussion.course_id)
        if not course or course.teacher_id != user.id:
            return jsonify({'error': '无权限'}), 403
    
    Discussion.query.filter_by(parent_id=discussion_id).delete()
    db.session.delete(discussion)
    db.session.commit()
    return jsonify({'message': '讨论已删除'})


@interactions_bp.route('/admin/reviews/delete-all-approved', methods=['DELETE'])
@jwt_required()
def delete_all_approved_reviews():
    """删除所有已通过的评价"""
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    query = Review.query.filter_by(status='approved')
    if user.role == 'teacher':
        teacher_course_ids = [c.id for c in Course.query.filter_by(teacher_id=user.id).all()]
        query = query.filter(Review.course_id.in_(teacher_course_ids))
    
    count = query.delete()
    db.session.commit()
    return jsonify({'message': f'已删除 {count} 条评价'})


@interactions_bp.route('/admin/questions/delete-all-approved', methods=['DELETE'])
@jwt_required()
def delete_all_approved_questions():
    """删除所有已通过的问题"""
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    query = Question.query.filter_by(status='approved')
    if user.role == 'teacher':
        teacher_course_ids = [c.id for c in Course.query.filter_by(teacher_id=user.id).all()]
        query = query.filter(Question.course_id.in_(teacher_course_ids))
    
    questions = query.all()
    for q in questions:
        Answer.query.filter_by(question_id=q.id).delete()
        db.session.delete(q)
    db.session.commit()
    return jsonify({'message': f'已删除 {len(questions)} 条问题'})


@interactions_bp.route('/admin/answers/delete-all-approved', methods=['DELETE'])
@jwt_required()
def delete_all_approved_answers():
    """删除所有已通过的回答"""
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    query = Answer.query.filter_by(status='approved')
    if user.role == 'teacher':
        teacher_course_ids = [c.id for c in Course.query.filter_by(teacher_id=user.id).all()]
        query = query.join(Question).filter(Question.course_id.in_(teacher_course_ids))
    
    count = query.delete()
    db.session.commit()
    return jsonify({'message': f'已删除 {count} 条回答'})


@interactions_bp.route('/admin/discussions/delete-all-approved', methods=['DELETE'])
@jwt_required()
def delete_all_approved_discussions():
    user = get_current_user()
    if user.role not in ['admin', 'teacher']:
        return jsonify({'error': '无权限'}), 403
    
    query = Discussion.query.filter_by(status='approved', parent_id=None)
    if user.role == 'teacher':
        teacher_course_ids = [c.id for c in Course.query.filter_by(teacher_id=user.id).all()]
        query = query.filter(Discussion.course_id.in_(teacher_course_ids))
    
    discussions = query.all()
    for d in discussions:
        Discussion.query.filter_by(parent_id=d.id).delete()
        db.session.delete(d)
    db.session.commit()
    return jsonify({'message': f'已删除 {len(discussions)} 条讨论'})
