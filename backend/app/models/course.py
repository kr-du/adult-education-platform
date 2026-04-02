from datetime import datetime
from app import db


class Category(db.Model):
    """课程分类模型 - 支持多级分类结构"""
    __tablename__ = 'categories'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True)  # 分类 ID，主键
    name = db.Column(db.String(100), nullable=False)  # 分类名称，必填
    description = db.Column(db.Text)  # 分类描述
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  # 父分类 ID，用于实现多级分类
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间

    # ========== 关联关系 ==========
    courses = db.relationship('Course', backref='category', lazy='dynamic')  # 该分类下的所有课程
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))  # 子分类（自引用）

    def to_dict(self):
        """转换为字典格式 - 用于 API 响应"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'course_count': self.courses.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Course(db.Model):
    """课程模型 - 存储课程基本信息"""
    __tablename__ = 'courses'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True)  # 课程 ID，主键
    title = db.Column(db.String(200), nullable=False)  # 课程标题，必填
    description = db.Column(db.Text)  # 课程描述
    cover_image = db.Column(db.String(255))  # 封面图片 URL
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 授课教师 ID，必填
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  # 所属分类 ID
    price = db.Column(db.Numeric(10, 2), default=0)  # 课程价格，最多 10 位数，其中 2 位小数
    duration = db.Column(db.Integer)  # 课程总时长（分钟）
    view_count = db.Column(db.Integer, default=0)  # 浏览次数
    status = db.Column(db.String(20), default='draft')  # 课程状态：draft(草稿)、published(已发布)、archived(已归档)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    # ========== 关联关系 ==========
    teacher = db.relationship('User', backref='courses_teaching')  # 授课教师
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic', order_by='Lesson.order')  # 课程包含的所有课时
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic')  # 课程的所有注册记录
    assignments = db.relationship('Assignment', backref='course', lazy='dynamic')  # 课程的所有作业

    def to_dict(self):
        """转换为字典格式 - 用于 API 响应，包含关联信息"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'cover_image': self.cover_image,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.real_name if self.teacher else None,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'price': float(self.price) if self.price else 0,
            'duration': self.duration,
            'view_count': self.view_count or 0,  # 浏览次数
            'status': self.status,
            'student_count': self.enrollments.count(),  # 注册学生数量
            'lesson_count': self.lessons.count(),  # 课时数量
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Lesson(db.Model):
    """课时模型 - 课程的单个学习单元"""
    __tablename__ = 'lessons'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True)  # 课时 ID，主键
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)  # 所属课程 ID，必填
    title = db.Column(db.String(200), nullable=False)  # 课时标题，必填
    video_url = db.Column(db.String(500))  # 教学视频 URL
    content = db.Column(db.Text)  # 课时文本内容
    duration = db.Column(db.Integer)  # 课时时长（分钟）
    order = db.Column(db.Integer, default=0)  # 课时在课程中的顺序
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间

    # ========== 关联关系 ==========
    progress = db.relationship('LessonProgress', backref='lesson', lazy='dynamic')  # 学生的学习进度记录

    def to_dict(self):
        """转换为字典格式 - 用于 API 响应"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'video_url': self.video_url,
            'content': self.content,
            'duration': self.duration,
            'order': self.order
        }


class Enrollment(db.Model):
    """课程注册模型 - 记录学生选课信息"""
    __tablename__ = 'enrollments'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True)  # 注册记录 ID，主键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 学生 ID，必填
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)  # 课程 ID，必填
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)  # 注册时间
    completed = db.Column(db.Boolean, default=False)  # 是否已完成课程
    progress = db.Column(db.Float, default=0)  # 学习进度百分比（0-100）

    def to_dict(self):
        """转换为字典格式 - 用于 API 响应"""
        course_data = None
        if self.course:
            course_data = {
                'id': self.course.id,
                'title': self.course.title,
                'cover_image': self.course.cover_image,
                'teacher_name': self.course.teacher.real_name if self.course.teacher else None,
                'duration': self.course.duration or 0,
                'lesson_count': self.course.lessons.count()
            }

        # 获取学生信息
        student_name = None
        student_email = None
        if self.user:
            student_name = self.user.real_name or self.user.username
            student_email = self.user.email

        return {
            'id': self.id,
            'user_id': self.user_id,
            'student_id': self.user_id,
            'student_name': student_name,
            'student_email': student_email,
            'course_id': self.course_id,
            'course_title': self.course.title if self.course else None,
            'course': course_data,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'completed': self.completed,
            'progress': self.progress or 0
        }


class LessonProgress(db.Model):
    """课时进度模型 - 跟踪学生学习进度"""
    __tablename__ = 'lesson_progress'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True)  # 进度记录 ID，主键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 学生 ID，必填
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)  # 课时 ID，必填
    watched_duration = db.Column(db.Integer, default=0)  # 已观看时长（秒）
    completed = db.Column(db.Boolean, default=False)  # 是否已完成该课时
    last_watched = db.Column(db.DateTime, default=datetime.utcnow)  # 最后观看时间

    def to_dict(self):
        """转换为字典格式 - 用于 API 响应"""
        return {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'watched_duration': self.watched_duration,
            'completed': self.completed,
            'last_watched': self.last_watched.isoformat() if self.last_watched else None
        }
