from datetime import datetime
from app import db


class Assignment(db.Model):
    """作业模型 - 教师布置的课程作业"""
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)  # 作业描述
    attachment_url = db.Column(db.String(500))  # 教师上传的附件
    due_date = db.Column(db.DateTime)  # 截止日期
    max_score = db.Column(db.Integer, default=100)  # 满分
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联
    submissions = db.relationship('Submission', backref='assignment', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'course_title': self.course.title if self.course else None,
            'title': self.title,
            'description': self.description,
            'attachment_url': self.attachment_url,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'max_score': self.max_score,
            'submission_count': self.submissions.count(),
            'pending_count': self.submissions.filter_by(score=None).count(),
            'created_at': self.created_at.isoformat()
        }


class Submission(db.Model):
    """作业提交模型 - 学生提交的作业"""
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text)  # 作业内容
    file_url = db.Column(db.String(500))  # 学生上传的附件
    score = db.Column(db.Integer)  # 得分
    feedback = db.Column(db.Text)  # 教师评语
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    graded_at = db.Column(db.DateTime)

    # 关联
    student = db.relationship('User', backref='submissions')

    def to_dict(self):
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'assignment_title': self.assignment.title if self.assignment else None,
            'assignment_max_score': self.assignment.max_score if self.assignment else 100,
            'student_id': self.student_id,
            'student_name': self.student.real_name if self.student else None,
            'student_username': self.student.username if self.student else None,
            'content': self.content,
            'file_url': self.file_url,
            'score': self.score,
            'feedback': self.feedback,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None
        }
