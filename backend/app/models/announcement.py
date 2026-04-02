from datetime import datetime, timezone
from app import db


class Announcement(db.Model):
    """公告模型 - 平台或课程公告"""
    __tablename__ = 'announcements'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True)  # 公告 ID，主键
    title = db.Column(db.String(200), nullable=False)  # 公告标题，必填
    content = db.Column(db.Text, nullable=False)  # 公告内容，必填
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 发布者 ID，必填
    is_pinned = db.Column(db.Boolean, default=False)  # 是否置顶
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 发布时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    # ========== 关联关系 ==========
    author = db.relationship('User', backref='announcements')  # 发布者（关联用户）

    def to_dict(self):
        """转换为字典格式 - 用于 API 响应"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'author_name': self.author.real_name if self.author else None,
            'is_pinned': self.is_pinned,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Discussion(db.Model):
    """讨论模型 - 课程讨论区的帖子和回复"""
    __tablename__ = 'discussions'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True)  # 帖子 ID，主键
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)  # 所属课程 ID，必填
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 发布者 ID，必填
    parent_id = db.Column(db.Integer, db.ForeignKey('discussions.id'))  # 父帖子 ID（用于回复功能）
    content = db.Column(db.Text, nullable=False)  # 帖子内容，必填
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 发布时间

    # ========== 关联关系 ==========
    user = db.relationship('User', backref='discussions')  # 发布者（关联用户）
    course = db.relationship('Course', backref='discussions')  # 所属课程（关联课程）
    replies = db.relationship('Discussion', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')  # 回复列表（自引用）

    def to_dict(self):
        """转换为字典格式 - 用于 API 响应"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'user_id': self.user_id,
            'user_name': self.user.real_name if self.user else None,
            'user_role': self.user.role if self.user else None,
            'parent_id': self.parent_id,
            'content': self.content,
            'status': self.status,
            'reply_count': self.replies.count(),  # 回复数量
            'created_at': self.created_at.replace(tzinfo=timezone.utc).isoformat() if self.created_at else None
        }
