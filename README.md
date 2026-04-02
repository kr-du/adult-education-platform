# 成人再教育学习平台

基于 Python Web 的成人再教育学习平台的设计与实现

## 技术栈

### 前端
- Vue 3
- Bootstrap 5
- Element Plus
- JavaScript
- 响应式布局（支持电脑、手机、平板）

### 后端
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- Flask-Migrate

### 数据库
- MySQL

## 项目结构

```
adult-education-platform/
├── backend/                    # Flask后端
│   ├── app/
│   │   ├── models/            # 数据模型
│   │   ├── routes/            # API路由
│   │   └── __init__.py
│   ├── config.py              # 配置文件
│   ├── run.py                 # 启动文件
│   ├── init_db.py             # 数据库初始化
│   └── requirements.txt       # 依赖
├── frontend/                   # Vue3前端
│   ├── src/
│   │   ├── api/               # API接口
│   │   ├── assets/            # 静态资源
│   │   ├── components/        # 组件
│   │   ├── router/            # 路由
│   │   ├── store/             # 状态管理
│   │   └── views/             # 页面视图
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 功能模块

### 学生端
- 登录、注册、密码重置
- 课程浏览、搜索、报名
- 视频课程学习、学习进度跟踪
- 作业查看、提交
- 个人中心（学习记录、成绩查询）

### 教师端
- 课程资源管理（上传、编辑、发布）
- 作业发布与批改
- 学员成绩管理
- 学习数据查看与分析
- 答疑互动

### 管理员端
- 用户管理（学员、教师账号审核与权限分配）
- 课程分类管理
- 系统公告发布
- 全站数据统计与报表生成
- 系统配置与维护

## 安装部署

### 1. 数据库准备

创建 MySQL 数据库：

```sql
CREATE DATABASE adult_education CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 后端部署

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 修改数据库配置
# 编辑 config.py 中的 SQLALCHEMY_DATABASE_URI

# 初始化数据库
python init_db.py

# 启动服务
python run.py
```

后端服务运行在 http://localhost:5000

### 3. 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

前端服务运行在 http://localhost:3000

## 默认账号

管理员账号：
- 用户名: admin
- 密码: admin123

教师账号：
- 用户名: teacher_wang (王伟)
- 密码: teacher123
- 其他教师: teacher_liu, teacher_zhang, teacher_chen 等

学生账号：
- 用户名: student001 (李明)
- 密码: student123
- 其他学生: student002 ~ student020

## API 接口

### 认证相关
- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
- POST /api/auth/reset-password - 重置密码
- GET /api/auth/profile - 获取个人信息
- PUT /api/auth/profile - 更新个人信息

### 课程相关
- GET /api/courses/ - 获取课程列表
- GET /api/courses/:id - 获取课程详情
- POST /api/courses/ - 创建课程
- PUT /api/courses/:id - 更新课程
- DELETE /api/courses/:id - 删除课程
- POST /api/courses/enroll/:id - 报名课程
- GET /api/courses/my-enrollments - 我的报名
- POST /api/courses/progress/:id - 更新学习进度
- GET /api/courses/categories - 获取分类列表
- POST /api/categories/ - 创建分类
- PUT /api/categories/:id - 更新分类
- DELETE /api/categories/:id - 删除分类

### 作业相关
- GET /api/assignments/course/:id - 获取课程作业
- POST /api/assignments/ - 创建作业
- GET /api/assignments/:id - 获取作业详情
- POST /api/assignments/submit/:id - 提交作业
- GET /api/assignments/submissions/:id - 获取提交记录
- POST /api/assignments/grade/:id - 批改作业

### 用户相关
- GET /api/users/learning-records - 学习记录
- GET /api/users/grades - 成绩查询
- GET /api/users/teacher/students - 教师学员列表
- GET /api/users/teacher/statistics - 教师统计数据

### 管理员相关
- GET /api/admin/users - 用户列表
- POST /api/admin/users/:id/approve - 审核通过
- POST /api/admin/users/:id/reject - 审核拒绝
- DELETE /api/admin/users/:id - 删除用户
- GET /api/admin/announcements - 公告列表
- POST /api/admin/announcements - 创建公告
- PUT /api/admin/announcements/:id - 更新公告
- DELETE /api/admin/announcements/:id - 删除公告
- GET /api/admin/statistics - 系统统计
- GET /api/admin/courses - 全部课程

### 讨论相关
- GET /api/discussions/course/:id - 课程讨论
- POST /api/discussions/ - 发布讨论
- GET /api/discussions/:id/replies - 获取回复
- DELETE /api/discussions/:id - 删除讨论
- GET /api/discussions/teacher - 教师讨论列表

## 数据库模型

### User (用户)
- id, username, email, password_hash
- role (student/teacher/admin)
- real_name, phone, avatar
- status (pending/approved/rejected)
- created_at, updated_at

### Course (课程)
- id, title, description, cover_image
- teacher_id, category_id
- price, duration, status
- created_at, updated_at

### Lesson (课时)
- id, course_id, title
- video_url, content, duration, order
- created_at

### Category (分类)
- id, name, description, parent_id
- created_at

### Enrollment (报名)
- id, user_id, course_id
- enrolled_at, completed, progress

### LessonProgress (学习进度)
- id, user_id, lesson_id
- watched_duration, completed
- last_watched

### Assignment (作业)
- id, course_id, title, description
- due_date, max_score
- created_at

### Submission (提交)
- id, assignment_id, student_id
- content, file_url
- score, feedback
- submitted_at, graded_at

### Announcement (公告)
- id, title, content, author_id
- is_pinned
- created_at, updated_at

### Discussion (讨论)
- id, course_id, user_id, parent_id
- content
- created_at

## 响应式设计

平台采用 Bootstrap 5 响应式布局，支持：
- 桌面端（≥1200px）
- 平板端（768px-1199px）
- 移动端（<768px）

## License

MIT
