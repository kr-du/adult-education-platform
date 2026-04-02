from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.course import Course, Enrollment
from app.models.assignment import Submission

users_bp = Blueprint('users', __name__)


def get_current_user():
    user_id = int(get_jwt_identity())
    return User.query.get(user_id)


@users_bp.route('/learning-records', methods=['GET'])
@jwt_required()
def get_learning_records():
    user = get_current_user()
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()

    records = []
    for enrollment in enrollments:
        course = Course.query.get(enrollment.course_id)
        if course:
            records.append({
                'course_id': course.id,
                'course_title': course.title,
                'teacher_name': course.teacher.real_name if course.teacher else None,
                'progress': enrollment.progress,
                'completed': enrollment.completed,
                'enrolled_at': enrollment.enrolled_at.isoformat()
            })

    return jsonify({'records': records})


@users_bp.route('/grades', methods=['GET'])
@jwt_required()
def get_grades():
    user = get_current_user()
    submissions = Submission.query.filter_by(student_id=user.id).all()

    grades = []
    for sub in submissions:
        if sub.score is not None:
            grades.append({
                'assignment_title': sub.assignment.title if sub.assignment else None,
                'course_title': sub.assignment.course.title if sub.assignment and sub.assignment.course else None,
                'score': sub.score,
                'max_score': sub.assignment.max_score if sub.assignment else 100,
                'feedback': sub.feedback,
                'graded_at': sub.graded_at.isoformat() if sub.graded_at else None
            })

    return jsonify({'grades': grades})


@users_bp.route('/teacher/students', methods=['GET'])
@jwt_required()
def get_teacher_students():
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    from app.models.assignment import Assignment
    from app.models.course import Lesson, LessonProgress

    courses = Course.query.filter_by(teacher_id=user.id).all()
    result = []

    for course in courses:
        enrollments = Enrollment.query.filter_by(course_id=course.id).all()
        total_lessons = Lesson.query.filter_by(course_id=course.id).count()
        
        for enrollment in enrollments:
            student = User.query.get(enrollment.user_id)
            if not student:
                continue
            
            # 计算学生在该课程的已完成课时数
            completed_lessons = LessonProgress.query.join(Lesson).filter(
                Lesson.course_id == course.id,
                LessonProgress.user_id == student.id,
                LessonProgress.completed == True
            ).count()
            
            # 计算学生在该课程的平均成绩
            submissions = Submission.query.join(Assignment).filter(
                Assignment.course_id == course.id,
                Submission.student_id == student.id,
                Submission.score.isnot(None)
            ).all()
            
            avg_score = None
            if submissions:
                total_score = sum(s.score for s in submissions)
                avg_score = round(total_score / len(submissions), 1)
            
            result.append({
                'student_id': student.id,
                'student_name': student.real_name or student.username,
                'student_email': student.email,
                'student_avatar': student.avatar,
                'course_id': course.id,
                'course_title': course.title,
                'progress': enrollment.progress or 0,
                'enrolled_at': enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
                'completed_lessons': completed_lessons,
                'total_lessons': total_lessons,
                'avg_score': avg_score
            })

    return jsonify({'students': result})


@users_bp.route('/teacher/statistics', methods=['GET'])
@jwt_required()
def get_teacher_statistics():
    user = get_current_user()
    if user.role not in ['teacher', 'admin']:
        return jsonify({'error': '无权限'}), 403

    courses = Course.query.filter_by(teacher_id=user.id).all()

    total_students = 0
    total_submissions = 0
    graded_submissions = 0

    for course in courses:
        total_students += Enrollment.query.filter_by(course_id=course.id).count()
        for assignment in course.assignments:
            subs = Submission.query.filter_by(assignment_id=assignment.id).all()
            total_submissions += len(subs)
            graded_submissions += len([s for s in subs if s.score is not None])

    return jsonify({
        'statistics': {
            'course_count': len(courses),
            'total_students': total_students,
            'total_submissions': total_submissions,
            'graded_submissions': graded_submissions,
            'pending_submissions': total_submissions - graded_submissions
        }
    })
