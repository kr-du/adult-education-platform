# 导入所有路由蓝图，用于在应用初始化时注册
from app.routes.auth import auth_bp
from app.routes.courses import courses_bp
from app.routes.assignments import assignments_bp
from app.routes.users import users_bp
from app.routes.admin import admin_bp
