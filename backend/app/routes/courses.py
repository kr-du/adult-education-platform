from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.course import Course, Category, Lesson, Enrollment, LessonProgress
from app.models.user import User
from app.utils.security import sanitize_search_keyword, sanitize_sort_field, handle_api_error, validate_file_upload, sanitize_filename, generate_safe_filename

courses_bp = Blueprint('courses', __name__)


def get_current_user():
    user_id = int(get_jwt_identity())
    return User.query.get(user_id)


def handle_route_error(f):
    """装饰器：统一处理路由错误"""
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return handle_api_error(e, 400)
        except Exception as e:
            current_app.logger.error(f"Route error: {str(e)}", exc_info=True)
            return handle_api_error("服务器内部错误", 500)
    wrapper.__name__ = f.__name__
    return wrapper


@courses_bp.errorhandler(404)
def not_found_error(error):
    return handle_api_error("资源未找到", 404)


@courses_bp.errorhandler(403)
def forbidden_error(error):
    return handle_api_error("无权限访问", 403)


@courses_bp.route('/', methods=['GET'])
@handle_route_error
def get_courses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword', '')
    teacher_id = request.args.get('teacher_id', type=int)
    status = request.args.get('status')
    sort = request.args.get('sort', 'created_at')

    query = Course.query

    # 如果指定了教师ID，返回该教师的所有课程（包括草稿）
    # 否则只返回已发布的课程
    if not teacher_id:
        query = query.filter_by(status='published')
    elif status:
        query = query.filter_by(status=status)

    if category_id:
        query = query.filter_by(category_id=category_id)
    if keyword:
        try:
            # 清理搜索关键词，防止SQL注入
            safe_keyword = sanitize_search_keyword(keyword)
            if safe_keyword:
                # 同时搜索课程名称和讲师姓名
                query = query.join(User, Course.teacher_id == User.id).filter(
                    db.or_(
                        Course.title.ilike(safe_keyword),
                        User.real_name.ilike(safe_keyword)
                    )
                )
        except ValueError as e:
            current_app.logger.warning(f"Invalid search keyword: {str(e)}")
            # 如果关键词无效，不进行搜索，返回空结果
            query = query.filter(db.false())
    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)

    # 验证和清理排序字段
    try:
        sort = sanitize_sort_field(sort)
    except ValueError as e:
        current_app.logger.warning(f"Invalid sort field: {str(e)}")
        sort = 'created_at'

    # 排序
    if sort == 'price_asc':
        query = query.order_by(Course.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Course.price.desc())
    elif sort == 'student_count':
        # 按学生数量降序排序（通过子查询统计报名数量）
        from sqlalchemy import func
        subquery = db.session.query(
            Enrollment.course_id,
            func.count(Enrollment.id).label('enrollment_count')
        ).group_by(Enrollment.course_id).subquery()
        
        query = query.outerjoin(
            subquery, Course.id == subquery.c.course_id
        ).order_by(
            db.desc(db.func.coalesce(subquery.c.enrollment_count, 0))
        )
    else:
        query = query.order_by(Course.created_at.desc())

    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'courses': [course.to_dict() for course in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()

    # 增加浏览次数
    course.view_count = (course.view_count or 0) + 1
    db.session.commit()

    return jsonify({
        'course': course.to_dict(),
        'lessons': [lesson.to_dict() for lesson in lessons]
    })


@courses_bp.route('/', methods=['POST'])
@jwt_required()
@handle_route_error
def create_course():
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    data = request.get_json()

    # 管理员可以指定教师，教师只能创建自己的课程
    if user.role == 'admin' and data.get('teacher_id'):
        teacher_id = data['teacher_id']
    else:
        teacher_id = user.id

    course = Course(
        title=data['title'],
        description=data.get('description'),
        cover_image=data.get('cover_image'),
        teacher_id=teacher_id,
        category_id=data.get('category_id'),
        price=data.get('price', 0),
        duration=data.get('duration'),
        status=data.get('status', 'draft')
    )

    db.session.add(course)
    db.session.commit()

    return jsonify({
        'message': '课程创建成功',
        'course': course.to_dict()
    }), 201


@courses_bp.route('/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    user = get_current_user()
    course = Course.query.get_or_404(course_id)

    if user.role != 'admin' and course.teacher_id != user.id:
        return jsonify({'error': '无权限'}), 403

    data = request.get_json()
    if 'title' in data:
        course.title = data['title']
    if 'description' in data:
        course.description = data['description']
    if 'cover_image' in data:
        course.cover_image = data['cover_image']
    if 'category_id' in data:
        course.category_id = data['category_id']
    if 'price' in data:
        course.price = data['price']
    if 'status' in data:
        course.status = data['status']

    db.session.commit()

    return jsonify({
        'message': '更新成功',
        'course': course.to_dict()
    })


@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    user = get_current_user()
    course = Course.query.get_or_404(course_id)

    if user.role != 'admin' and course.teacher_id != user.id:
        return jsonify({'error': '无权限'}), 403

    # 删除相关的报名记录
    Enrollment.query.filter_by(course_id=course_id).delete()

    # 删除相关的课时进度记录
    lessons = Lesson.query.filter_by(course_id=course_id).all()
    for lesson in lessons:
        LessonProgress.query.filter_by(lesson_id=lesson.id).delete()

    # 删除相关的课时
    Lesson.query.filter_by(course_id=course_id).delete()

    # 删除相关的评价记录
    from app.models.interaction import Review, Question, Answer, CourseNotice
    from app.models.assignment import Assignment, Submission
    from app.models.announcement import Discussion

    Review.query.filter_by(course_id=course_id).delete()

    # 删除相关的讨论记录
    Discussion.query.filter_by(course_id=course_id).delete()

    # 删除相关的答疑问题和回答
    questions = Question.query.filter_by(course_id=course_id).all()
    for question in questions:
        Answer.query.filter_by(question_id=question.id).delete()
    Question.query.filter_by(course_id=course_id).delete()

    # 删除相关的课程公告
    CourseNotice.query.filter_by(course_id=course_id).delete()

    # 删除相关的作业和提交记录
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    for assignment in assignments:
        Submission.query.filter_by(assignment_id=assignment.id).delete()
    Assignment.query.filter_by(course_id=course_id).delete()

    # 删除课程
    db.session.delete(course)
    db.session.commit()

    return jsonify({'message': '课程删除成功'})


@courses_bp.route('/<int:course_id>/lessons', methods=['POST'])
@jwt_required()
def add_lesson(course_id):
    user = get_current_user()
    course = Course.query.get_or_404(course_id)

    if user.role != 'admin' and course.teacher_id != user.id:
        return jsonify({'error': '无权限'}), 403

    data = request.get_json()
    lesson = Lesson(
        course_id=course_id,
        title=data['title'],
        video_url=data.get('video_url'),
        content=data.get('content'),
        duration=data.get('duration'),
        order=data.get('order', 0)
    )

    db.session.add(lesson)
    db.session.commit()

    return jsonify({
        'message': '课时添加成功',
        'lesson': lesson.to_dict()
    }), 201


@courses_bp.route('/enroll/<int:course_id>', methods=['POST'])
@jwt_required()
def enroll_course(course_id):
    user = get_current_user()
    if user.role != 'student':
        return jsonify({'error': '只有学生可以报名'}), 403

    existing = Enrollment.query.filter_by(
        user_id=user.id,
        course_id=course_id
    ).first()

    if existing:
        return jsonify({'error': '已报名该课程'}), 400

    enrollment = Enrollment(
        user_id=user.id,
        course_id=course_id
    )

    db.session.add(enrollment)
    db.session.commit()

    return jsonify({
        'message': '报名成功',
        'enrollment': enrollment.to_dict()
    }), 201


@courses_bp.route('/my-enrollments', methods=['GET'])
@jwt_required()
def get_my_enrollments():
    user = get_current_user()
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()

    return jsonify({
        'enrollments': [e.to_dict() for e in enrollments]
    })


@courses_bp.route('/progress/<int:lesson_id>', methods=['POST'])
@jwt_required()
def update_progress(lesson_id):
    user = get_current_user()
    data = request.get_json()

    lesson = Lesson.query.get_or_404(lesson_id)
    course_id = lesson.course_id

    progress = LessonProgress.query.filter_by(
        user_id=user.id,
        lesson_id=lesson_id
    ).first()

    if not progress:
        progress = LessonProgress(
            user_id=user.id,
            lesson_id=lesson_id
        )
        db.session.add(progress)

    progress.watched_duration = data.get('watched_duration', progress.watched_duration)
    progress.completed = data.get('completed', progress.completed)

    # 更新课程整体进度
    enrollment = Enrollment.query.filter_by(
        user_id=user.id,
        course_id=course_id
    ).first()

    if enrollment:
        total_lessons = Lesson.query.filter_by(course_id=course_id).count()
        completed_lessons = LessonProgress.query.join(Lesson).filter(
            Lesson.course_id == course_id,
            LessonProgress.user_id == user.id,
            LessonProgress.completed == True
        ).count()
        
        if total_lessons > 0:
            enrollment.progress = round((completed_lessons / total_lessons) * 100, 1)
            if completed_lessons >= total_lessons:
                enrollment.completed = True

    db.session.commit()

    return jsonify({
        'message': '进度更新成功',
        'progress': progress.to_dict(),
        'course_progress': enrollment.progress if enrollment else 0
    })


@courses_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify({
        'categories': [cat.to_dict() for cat in categories]
    })


@courses_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    user = get_current_user()
    if user.role != 'admin':
        return jsonify({'error': '无权限'}), 403

    data = request.get_json()
    category = Category(
        name=data['name'],
        description=data.get('description'),
        parent_id=data.get('parent_id')
    )

    db.session.add(category)
    db.session.commit()

    return jsonify({
        'message': '分类创建成功',
        'category': category.to_dict()
    }), 201


@courses_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    user = get_current_user()
    if user.role != 'admin':
        return jsonify({'error': '无权限'}), 403

    category = Category.query.get_or_404(category_id)
    data = request.get_json()

    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    if 'parent_id' in data:
        category.parent_id = data['parent_id']

    db.session.commit()

    return jsonify({
        'message': '分类更新成功',
        'category': category.to_dict()
    })


@courses_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    user = get_current_user()
    if user.role != 'admin':
        return jsonify({'error': '无权限'}), 403

    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()

    return jsonify({'message': '分类删除成功'})


@courses_bp.route('/teacher/my-courses', methods=['GET'])
@jwt_required()
def get_teacher_courses():
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    status = request.args.get('status')

    query = Course.query.filter_by(teacher_id=user.id)
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Course.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'courses': [course.to_dict() for course in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })