from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.assignment import Assignment, Submission
from app.models.course import Course, Enrollment
from app.models.user import User

assignments_bp = Blueprint('assignments', __name__)


def get_current_user():
    user_id = int(get_jwt_identity())
    return User.query.get(user_id)


# ========== 教师端 API ==========

@assignments_bp.route('/', methods=['POST'])
@jwt_required()
def create_assignment():
    """教师创建作业"""
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    data = request.get_json()
    course = Course.query.get_or_404(data['course_id'])

    if user.role != 'admin' and course.teacher_id != user.id:
        return jsonify({'error': '无权限'}), 403

    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except:
            due_date = None

    assignment = Assignment(
        course_id=data['course_id'],
        title=data['title'],
        description=data.get('description'),
        attachment_url=data.get('attachment_url'),
        due_date=due_date,
        max_score=data.get('max_score', 100)
    )

    db.session.add(assignment)
    db.session.commit()

    return jsonify({
        'message': '作业创建成功',
        'assignment': assignment.to_dict()
    }), 201


@assignments_bp.route('/<int:assignment_id>', methods=['PUT'])
@jwt_required()
def update_assignment(assignment_id):
    """教师更新作业"""
    user = get_current_user()
    assignment = Assignment.query.get_or_404(assignment_id)
    course = Course.query.get(assignment.course_id)

    if user.role != 'admin' and course.teacher_id != user.id:
        return jsonify({'error': '无权限'}), 403

    data = request.get_json()

    if 'title' in data:
        assignment.title = data['title']
    if 'description' in data:
        assignment.description = data['description']
    if 'attachment_url' in data:
        assignment.attachment_url = data['attachment_url']
    if 'due_date' in data and data['due_date']:
        try:
            assignment.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except:
            pass
    if 'max_score' in data:
        assignment.max_score = data['max_score']

    db.session.commit()

    return jsonify({
        'message': '作业更新成功',
        'assignment': assignment.to_dict()
    })


@assignments_bp.route('/<int:assignment_id>', methods=['DELETE'])
@jwt_required()
def delete_assignment(assignment_id):
    """教师删除作业"""
    user = get_current_user()
    assignment = Assignment.query.get_or_404(assignment_id)
    course = Course.query.get(assignment.course_id)

    if user.role != 'admin' and course.teacher_id != user.id:
        return jsonify({'error': '无权限'}), 403

    db.session.delete(assignment)
    db.session.commit()

    return jsonify({'message': '作业删除成功'})


@assignments_bp.route('/teacher', methods=['GET'])
@jwt_required()
def get_teacher_assignments():
    """获取教师的所有作业"""
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    courses = Course.query.filter_by(teacher_id=user.id).all()
    course_ids = [c.id for c in courses]

    assignments = Assignment.query.filter(
        Assignment.course_id.in_(course_ids)
    ).order_by(Assignment.created_at.desc()).all()

    return jsonify({
        'assignments': [a.to_dict() for a in assignments]
    })


@assignments_bp.route('/course/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_assignments(course_id):
    """获取课程的作业列表"""
    assignments = Assignment.query.filter_by(course_id=course_id).order_by(
        Assignment.created_at.desc()
    ).all()

    return jsonify({
        'assignments': [a.to_dict() for a in assignments]
    })


@assignments_bp.route('/<int:assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment(assignment_id):
    """获取作业详情"""
    assignment = Assignment.query.get_or_404(assignment_id)
    return jsonify({'assignment': assignment.to_dict()})


# ========== 学生端 API ==========

@assignments_bp.route('/student', methods=['GET'])
@jwt_required()
def get_student_assignments():
    """获取学生的作业列表"""
    user = get_current_user()
    if user.role != 'student':
        return jsonify({'error': '无权限'}), 403

    enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    course_ids = [e.course_id for e in enrollments]

    assignments = Assignment.query.filter(
        Assignment.course_id.in_(course_ids)
    ).order_by(Assignment.due_date.asc()).all()

    result = []
    for assignment in assignments:
        assignment_dict = assignment.to_dict()
        submission = Submission.query.filter_by(
            assignment_id=assignment.id,
            student_id=user.id
        ).first()
        assignment_dict['submitted'] = submission is not None
        assignment_dict['submission'] = submission.to_dict() if submission else None
        result.append(assignment_dict)

    return jsonify({'assignments': result})


@assignments_bp.route('/submit/<int:assignment_id>', methods=['POST'])
@jwt_required()
def submit_assignment(assignment_id):
    """学生提交作业"""
    user = get_current_user()
    if user.role != 'student':
        return jsonify({'error': '只有学生可以提交'}), 403

    existing = Submission.query.filter_by(
        assignment_id=assignment_id,
        student_id=user.id
    ).first()

    data = request.get_json()

    if existing:
        if 'content' in data:
            existing.content = data['content']
        if 'file_url' in data:
            existing.file_url = data['file_url']
        existing.submitted_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': '作业更新成功',
            'submission': existing.to_dict()
        })

    submission = Submission(
        assignment_id=assignment_id,
        student_id=user.id,
        content=data.get('content'),
        file_url=data.get('file_url')
    )

    db.session.add(submission)
    db.session.commit()

    return jsonify({
        'message': '作业提交成功',
        'submission': submission.to_dict()
    }), 201


@assignments_bp.route('/my-submissions', methods=['GET'])
@jwt_required()
def get_my_submissions():
    """获取学生的提交记录"""
    user = get_current_user()
    if user.role != 'student':
        return jsonify({'error': '无权限'}), 403

    submissions = Submission.query.filter_by(student_id=user.id).order_by(
        Submission.submitted_at.desc()
    ).all()

    return jsonify({
        'submissions': [s.to_dict() for s in submissions]
    })


# ========== 批改 API ==========

@assignments_bp.route('/submissions/<int:assignment_id>', methods=['GET'])
@jwt_required()
def get_submissions(assignment_id):
    """获取作业的提交记录"""
    user = get_current_user()
    assignment = Assignment.query.get_or_404(assignment_id)
    course = Course.query.get(assignment.course_id)

    if user.role == 'student':
        submissions = Submission.query.filter_by(
            assignment_id=assignment_id,
            student_id=user.id
        ).all()
    else:
        if user.role != 'admin' and course.teacher_id != user.id:
            return jsonify({'error': '无权限'}), 403
        submissions = Submission.query.filter_by(assignment_id=assignment_id).all()

    return jsonify({
        'submissions': [s.to_dict() for s in submissions]
    })


@assignments_bp.route('/grade/<int:submission_id>', methods=['POST'])
@jwt_required()
def grade_submission(submission_id):
    """教师批改作业"""
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    submission = Submission.query.get_or_404(submission_id)
    data = request.get_json()

    submission.score = data.get('score')
    submission.feedback = data.get('feedback')
    submission.graded_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'message': '批改成功',
        'submission': submission.to_dict()
    })
