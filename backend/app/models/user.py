from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """用户模型 - 存储平台所有用户信息（学生、教师、管理员）"""
    __tablename__ = 'users'  # 数据库表名

    # ========== 基本字段 ==========
    id = db.Column(db.Integer, primary_key=True)  # 用户 ID，主键
    username = db.Column(db.String(80), unique=True, nullable=False)  # 用户名，唯一且必填
    email = db.Column(db.String(120), unique=True, nullable=False)  # 邮箱，唯一且必填
    password_hash = db.Column(db.String(256), nullable=False)  # 密码哈希值，必填
    role = db.Column(db.String(20), nullable=False, default='student')  # 角色：student(学生)、teacher(教师)、admin(管理员)
    
    # ========== 个人信息 ==========
    real_name = db.Column(db.String(50))  # 真实姓名
    phone = db.Column(db.String(20))  # 手机号码
    avatar = db.Column(db.String(255))  # 头像图片 URL
    
    # ========== 账户状态 ==========
    status = db.Column(db.String(20), default='pending')  # 账户状态：pending(待审核)、approved(已通过)、rejected(已拒绝)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # ========== 关联关系 ==========
    enrollments = db.relationship('Enrollment', backref='user', lazy='dynamic')  # 用户的课程注册记录

    def set_password(self, password):
        """设置用户密码 - 将明文密码转换为哈希值"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码 - 检查给定密码是否与哈希值匹配"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """转换为字典格式 - 用于 API 响应，排除敏感信息（如密码）"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'real_name': self.real_name,
            'phone': self.phone,
            'avatar': self.avatar,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
