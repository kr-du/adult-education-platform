# 成人再教育学习平台

基于 Python Web 的成人再教育学习平台，支持课程学习、作业管理、答疑互动、内容审核等功能。

## 项目简介

本平台是一个面向成人的在线教育系统，提供完整的课程管理、学习跟踪、作业批改、答疑互动等功能。系统采用前后端分离架构，支持多角色（学生、教师、管理员）使用。

## 技术栈

### 前端
- **框架**：Vue 3 + Vite
- **UI组件**：Element Plus
- **样式**：Bootstrap 5
- **状态管理**：Pinia
- **HTTP请求**：Axios

### 后端
- **框架**：Flask
- **数据库ORM**：Flask-SQLAlchemy
- **用户认证**：Flask-JWT-Extended
- **跨域处理**：Flask-CORS
- **数据库迁移**：Flask-Migrate
- **WSGI服务器**：Gunicorn

### 数据库
- MySQL 8.0

## 功能模块

### 学生端
| 功能 | 说明 |
|------|------|
| 课程浏览 | 浏览、搜索、分类筛选课程 |
| 课程学习 | 视频播放、倍速、画中画、进度跟踪 |
| 作业管理 | 查看作业、在线提交、查看成绩 |
| 答疑互动 | 提问、回答、查看讨论 |
| 课程评价 | 对已学课程进行评分和评价 |
| 学习数据 | 查看学习时长、进度、成绩统计 |
| 消息通知 | 接收系统通知和课程公告 |

### 教师端
| 功能 | 说明 |
|------|------|
| 课程管理 | 创建、编辑、发布、下架课程 |
| 课时管理 | 上传视频、编辑课时内容 |
| 作业管理 | 发布作业、批改作业、评分反馈 |
| 学生管理 | 查看学生列表、学习进度 |
| 内容审核 | 审核评价、提问、讨论 |
| 数据统计 | 课程报名、学习完成率统计 |

### 管理员端
| 功能 | 说明 |
|------|------|
| 用户管理 | 审核、编辑、删除用户账号 |
| 课程管理 | 管理所有课程、分类管理 |
| 内容审核 | 审核全站评价、提问、讨论 |
| 公告管理 | 发布系统公告 |
| 数据备份 | 创建备份、恢复数据、下载备份 |
| 系统统计 | 用户、课程、学习数据统计 |

## 项目结构

```
adult-education-platform/
├── backend/                        # Flask后端
│   ├── app/
│   │   ├── models/                # 数据模型
│   │   │   ├── user.py           # 用户模型
│   │   │   ├── course.py         # 课程模型
│   │   │   ├── assignment.py     # 作业模型
│   │   │   ├── interaction.py    # 互动模型（评价、问答）
│   │   │   ├── announcement.py   # 公告、讨论模型
│   │   │   └── ai.py             # AI对话模型
│   │   ├── routes/               # API路由
│   │   │   ├── auth.py           # 认证接口
│   │   │   ├── courses.py        # 课程接口
│   │   │   ├── assignments.py    # 作业接口
│   │   │   ├── users.py          # 用户接口
│   │   │   ├── admin.py          # 管理员接口
│   │   │   ├── discussions.py    # 讨论接口
│   │   │   ├── interactions.py   # 互动接口
│   │   │   ├── backup.py         # 备份接口
│   │   │   └── uploads.py        # 上传接口
│   │   └── __init__.py
│   ├── uploads/                   # 上传文件目录
│   ├── config.py                  # 配置文件
│   ├── run.py                     # 启动文件
│   ├── seed_data.py               # 种子数据
│   ├── requirements.txt           # 依赖
│   ├── Dockerfile                 # Docker配置
│   └── gunicorn_config.py         # Gunicorn配置
├── frontend/                       # Vue3前端
│   ├── src/
│   │   ├── api/                   # API接口
│   │   ├── assets/                # 静态资源
│   │   ├── components/            # 公共组件
│   │   ├── directives/            # 自定义指令
│   │   ├── router/                # 路由配置
│   │   ├── store/                 # Pinia状态管理
│   │   ├── utils/                 # 工具函数
│   │   └── views/                 # 页面视图
│   │       ├── admin/            # 管理员页面
│   │       ├── teacher/          # 教师页面
│   │       └── student/          # 学生页面
│   ├── nginx.conf                 # Nginx配置
│   ├── Dockerfile                 # Docker配置
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml              # Docker编排
├── deploy.bat                      # Windows部署脚本
├── deploy.sh                       # Linux部署脚本
├── .env.example                    # 环境变量示例
├── .gitignore                      # Git忽略文件
└── README.md
```

## 安装部署

### 方式一：本地开发部署

#### 1. 数据库准备

创建 MySQL 数据库：
```sql
CREATE DATABASE adult_education CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 2. 后端部署

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

# 初始化数据库表
flask db upgrade

# 填充种子数据
python seed_data.py

# 启动服务
python run.py
```

后端服务运行在 http://localhost:5000

#### 3. 前端部署

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

### 方式二：Docker部署

#### 1. 复制环境变量文件

```bash
cp .env.example .env
```

编辑 `.env` 文件，修改数据库密码和密钥。

#### 2. 运行部署脚本

**Windows**：
```bash
deploy.bat
```

**Linux/Mac**：
```bash
chmod +x deploy.sh
./deploy.sh
```

#### 3. 手动Docker部署

```bash
# 构建并启动服务
docker-compose up -d --build

# 初始化数据库
docker-compose exec backend python seed_data.py
```

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | 123456 |
| 教师 | zhugeliang | 123456 |
| 学生 | zhangwei | 123456 |

> ⚠️ **安全提示**：首次登录后请立即修改默认密码！

## API 接口

### 认证接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| GET | /api/auth/profile | 获取个人信息 |
| PUT | /api/auth/profile | 更新个人信息 |

### 课程接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/courses/ | 获取课程列表 |
| GET | /api/courses/:id | 获取课程详情 |
| POST | /api/courses/ | 创建课程 |
| PUT | /api/courses/:id | 更新课程 |
| DELETE | /api/courses/:id | 删除课程 |
| POST | /api/courses/enroll/:id | 报名课程 |
| GET | /api/courses/my-enrollments | 我的报名 |

### 作业接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/assignments/course/:id | 获取课程作业 |
| POST | /api/assignments/ | 创建作业 |
| POST | /api/assignments/submit/:id | 提交作业 |
| POST | /api/assignments/grade/:id | 批改作业 |

### 管理员接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/admin/users | 用户列表 |
| POST | /api/admin/users/:id/approve | 审核通过 |
| DELETE | /api/admin/users/:id | 删除用户 |
| GET | /api/admin/statistics | 系统统计 |
| POST | /api/backup/export | 创建备份 |
| POST | /api/backup/restore | 恢复数据 |

## 数据库模型

### 核心模型

**User（用户）**
- id, username, email, password_hash
- role (student/teacher/admin)
- real_name, phone, avatar
- status (pending/approved/rejected)

**Course（课程）**
- id, title, description, cover_image
- teacher_id, category_id
- price, duration, status

**Lesson（课时）**
- id, course_id, title
- video_url, content, duration, order

**Assignment（作业）**
- id, course_id, title, description
- due_date, max_score

**Review（评价）**
- id, course_id, user_id
- rating, content, status

**Question（提问）**
- id, course_id, user_id
- title, content, is_resolved, status

**Discussion（讨论）**
- id, course_id, user_id, parent_id
- content, status

## 响应式设计

平台支持多设备访问：
- **桌面端**：≥992px
- **平板端**：768px-991px
- **移动端**：<768px

## 视频播放器功能

- 倍速播放（0.5x ~ 2x）
- 画中画模式
- 快进/快退（10秒）
- 音量调节
- 全屏播放
- 快捷键支持

## 内容审核机制

- 用户提交的内容需审核后才能显示
- 学生可看到自己待审核的内容（显示"审核中"标签）
- 教师可审核自己课程的内容
- 管理员可审核全站内容

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue 或 Pull Request。
