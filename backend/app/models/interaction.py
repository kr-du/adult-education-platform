from datetime import datetime, timezone
from app import db


class Review(db.Model):
    """课程评价模型"""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 星评分
    content = db.Column(db.Text)  # 评价内容
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 创建时间（UTC）
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # 更新时间（UTC）

    course = db.relationship('Course', backref='reviews')
    user = db.relationship('User', backref='reviews')

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'user_id': self.user_id,
            'user_name': self.user.real_name or self.user.username if self.user else None,
            'user_avatar': self.user.avatar if self.user else None,
            'rating': self.rating,
            'content': self.content,
            'status': self.status,
            'created_at': self.created_at.replace(tzinfo=timezone.utc).isoformat() if self.created_at else None,
            'updated_at': self.updated_at.replace(tzinfo=timezone.utc).isoformat() if self.updated_at else None
        }


class Message(db.Model):
    """消息通知模型"""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 接收者
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    message_type = db.Column(db.String(50))  # system, course, assignment, announcement
    is_read = db.Column(db.Boolean, default=False)
    related_id = db.Column(db.Integer)  # 关联的 ID（课程 ID、作业 ID 等）
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 创建时间（UTC）

    user = db.relationship('User', backref='messages')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'message_type': self.message_type,
            'is_read': self.is_read,
            'related_id': self.related_id,
            'created_at': self.created_at.replace(tzinfo=timezone.utc).isoformat() if self.created_at else None
        }


class Question(db.Model):
    """答疑问题模型"""
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 提问者
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 创建时间（UTC）

    course = db.relationship('Course', backref='questions')
    user = db.relationship('User', backref='questions')
    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'course_title': self.course.title if self.course else None,
            'user_id': self.user_id,
            'user_name': self.user.real_name or self.user.username if self.user else None,
            'title': self.title,
            'content': self.content,
            'is_resolved': self.is_resolved,
            'status': self.status,
            'answer_count': self.answers.count(),
            'created_at': self.created_at.replace(tzinfo=timezone.utc).isoformat() if self.created_at else None
        }


class Answer(db.Model):
    """答疑回答模型"""
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_teacher = db.Column(db.Boolean, default=False)  # 是否是教师回答
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 创建时间（UTC）

    user = db.relationship('User', backref='answers')

    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'user_id': self.user_id,
            'user_name': self.user.real_name or self.user.username if self.user else None,
            'user_avatar': self.user.avatar if self.user else None,
            'is_teacher': self.is_teacher,
            'content': self.content,
            'status': self.status,
            'created_at': self.created_at.replace(tzinfo=timezone.utc).isoformat() if self.created_at else None
        }


class CourseNotice(db.Model):
    """课程公告模型"""
    __tablename__ = 'course_notices'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 创建时间（UTC）

    course = db.relationship('Course', backref='notices')
    teacher = db.relationship('User', backref='course_notices')

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'course_title': self.course.title if self.course else None,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.real_name or self.teacher.username if self.teacher else None,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.replace(tzinfo=timezone.utc).isoformat() if self.created_at else None
        }
