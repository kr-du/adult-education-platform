# 成人再教育学习平台

基于 Python Web 的成人再教育学习平台，支持课程学习、作业管理、答疑互动、AI 学习助手、内容审核等功能。

## 项目简介

本平台是一个面向成人的在线教育系统，提供完整的课程管理、学习跟踪、作业批改、答疑互动等功能。系统采用前后端分离架构，支持多角色（学生、教师、管理员）使用，并集成了 AI 学习助手，提供智能化的学习辅助体验。

## 技术栈

### 前端

| 类型      | 技术                            |
| ------- | ----------------------------- |
| 框架      | Vue 3 + Vite                  |
| 编程范式    | Composition API（script setup） |
| UI 组件   | Element Plus                  |
| 样式框架    | Bootstrap 5                   |
| 状态管理    | Pinia                         |
| HTTP 请求 | Axios                         |
| 代码高亮    | highlight.js + marked         |
| 安全工具    | DOMPurify + 自定义验证模块           |

### 后端

| 类型       | 技术                      |
| -------- | ----------------------- |
| 框架       | Flask                   |
| 数据库 ORM  | Flask-SQLAlchemy        |
| 用户认证     | Flask-JWT-Extended（双令牌） |
| 跨域处理     | Flask-CORS              |
| 数据库迁移    | Flask-Migrate           |
| WSGI 服务器 | Gunicorn                |
| 安全工具     | bleach + 自定义验证模块        |

### 数据库与服务

| 类型      | 技术                      |
| ------- | ----------------------- |
| 数据库     | MySQL 8.0               |
| AI 大模型  | 智谱 AI（GLM-4-Flash）      |
| 容器化部署   | Docker + Docker Compose |
| Web 服务器 | Nginx                   |

## 功能模块

### 学生端

| 功能        | 说明                        |
| --------- | ------------------------- |
| 课程浏览      | 浏览、搜索、分类筛选课程              |
| 课程学习      | 视频播放、倍速、画中画、进度跟踪          |
| 作业管理      | 查看作业、在线提交、查看成绩            |
| 答疑互动      | 提问、回答、参与讨论                |
| 课程评价      | 对已学课程进行评分和评价              |
| **AI 助手** | **智能对话、流式输出、Markdown 渲染** |
| 学习数据      | 查看学习时长、进度、成绩统计            |
| 个人中心      | 编辑资料、修改密码、头像上传            |

### 教师端

| 功能   | 说明                |
| ---- | ----------------- |
| 课程管理 | 创建、编辑、发布、下架课程     |
| 课时管理 | 上传视频、编辑课时内容       |
| 作业管理 | 发布作业、批改作业、评分反馈    |
| 学生管理 | 查看学生列表、学习进度与成绩统计  |
| 内容审核 | 审核评价、提问、回答、讨论     |
| 数据统计 | 课程报名、学习完成率、作业批改统计 |
| 个人中心 | 编辑资料、修改密码、头像上传    |

### 管理员端

| 功能   | 说明               |
| ---- | ---------------- |
| 用户管理 | 审核、编辑、删除用户账号     |
| 课程管理 | 管理所有课程、分类管理      |
| 内容审核 | 审核全站评价、提问、回答、讨论  |
| 公告管理 | 发布系统公告           |
| 数据备份 | 创建备份、恢复数据、下载备份文件 |
| 系统统计 | 用户、课程、学习数据统计     |

## 项目结构

```
adult-education-platform/
├── backend/                              # Flask 后端
│   ├── app/
│   │   ├── models/                      # 数据模型
│   │   │   ├── user.py                  #   用户模型
│   │   │   ├── course.py                #   课程/分类/课时/报名/进度模型
│   │   │   ├── assignment.py            #   作业/提交模型
│   │   │   ├── interaction.py           #   评价/提问/回答/通知模型
│   │   │   ├── announcement.py          #   公告/讨论模型
│   │   │   └── ai.py                    #   AI 对话/消息模型
│   │   ├── routes/                      # API 路由
│   │   │   ├── auth.py                  #   认证（注册/登录/个人信息/密码）
│   │   │   ├── courses.py               #   课程 CRUD + 分类管理
│   │   │   ├── assignments.py           #   作业管理 + 提交/批改
│   │   │   ├── users.py                 #   学习记录/成绩/教师统计
│   │   │   ├── discussions.py           #   讨论发布/回复/删除
│   │   │   ├── interactions.py          #   评价/提问/回答 + 内容审核
│   │   │   ├── admin.py                 #   管理端用户/课程/统计
│   │   │   ├── backup.py                #   数据备份/恢复/导出
│   │   │   ├── uploads.py               #   文件上传（头像/课程图/视频）
│   │   │   └── ai.py                    #   AI 对话管理
│   │   ├── services/
│   │   │   └── ai_service.py            #   智谱 AI 服务集成
│   │   ├── utils/
│   │   │   ├── auth.py                  #   认证工具（get_current_user + 权限装饰器）
│   │   │   └── security.py              #   安全工具（输入验证/文件校验）
│   │   └── __init__.py                  #   Flask 工厂函数 + 扩展初始化
│   ├── uploads/                         # 上传文件存储目录
│   ├── config.py                        # 多环境配置文件
│   ├── run.py                           # 开发环境启动入口
│   ├── seed_data.py                     # 种子数据（三国教师 + 12 门课程）
│   ├── requirements.txt                 # Python 依赖
│   ├── Dockerfile                       # Docker 镜像
│   └── gunicorn_config.py               # Gunicorn 生产配置
├── frontend/                            # Vue 3 前端
│   ├── src/
│   │   ├── api/
│   │   │   └── index.js                 # Axios 封装 + 拦截器
│   │   ├── assets/
│   │   │   └── css/                     # 全局样式（main.css + mobile.css）
│   │   ├── components/
│   │   │   └── common/                  # 公共组件（Navbar 等）
│   │   ├── composables/
│   │   │   └── useUserProfile.js        # 个人中心共享逻辑
│   │   ├── directives/
│   │   │   └── lazy.js                  # 图片懒加载指令
│   │   ├── router/
│   │   │   └── index.js                 # 路由配置 + 导航守卫
│   │   ├── store/
│   │   │   └── user.js                  # Pinia 用户状态
│   │   ├── utils/
│   │   │   ├── security.js              # 安全工具（验证/错误处理/密码确认）
│   │   │   ├── format.js                # 格式化工具（日期/相对时间）
│   │   │   └── cache.js                 # 页面缓存系统
│   │   └── views/
│   │       ├── auth/                    # 认证页面（登录/注册/密码重置）
│   │       ├── admin/                   # 管理员页面（仪表盘/用户/课程/公告）
│   │       ├── teacher/                 # 教师页面（课程/作业/学生/审核）
│   │       └── student/                 # 学生页面（课程/学习/AI助手/作业）
│   ├── nginx.conf                       # Nginx 反向代理配置
│   ├── Dockerfile                       # Docker 镜像
│   ├── package.json                     # 前端依赖
│   └── vite.config.js                   # Vite 构建配置
├── docker-compose.yml                   # Docker 三服务编排
├── deploy.bat                           # Windows 一键部署脚本
├── deploy.sh                            # Linux 一键部署脚本
├── .env.example                         # 环境变量模板
├── .gitignore
└── README.md
```

## 安装部署

### 方式一：本地开发部署

#### 1. 数据库准备

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

# 配置环境变量（参考 .env.example）
cp ../.env.example ../.env

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

### 方式二：Docker 部署

```bash
# 复制环境变量文件并编辑
cp .env.example .env

# Windows
deploy.bat

# Linux/Mac
chmod +x deploy.sh
./deploy.sh

# 或手动执行
docker-compose up -d --build
docker-compose exec backend python seed_data.py
```

## 默认账号

| 角色  | 用户名        | 密码     |
| --- | ---------- | ------ |
| 管理员 | admin      | 123456 |
| 教师  | zhugeliang | 123456 |
| 学生  | zhangwei   | 123456 |

> 种子数据包含 8 位三国人物教师（诸葛亮、关羽、司马懿等）和 12 门示例课程。

> ⚠️ 首次登录后请立即修改默认密码！

## API 接口

### 认证接口

| 方法   | 路径                        | 说明     |
| ---- | ------------------------- | ------ |
| POST | /api/auth/register        | 用户注册   |
| POST | /api/auth/login           | 用户登录   |
| GET  | /api/auth/profile         | 获取个人信息 |
| PUT  | /api/auth/profile         | 更新个人信息 |
| PUT  | /api/auth/change-password | 修改密码   |
| POST | /api/auth/reset-password  | 重置密码   |

### 课程接口

| 方法     | 路径                              | 说明     |
| ------ | ------------------------------- | ------ |
| GET    | /api/courses/                   | 获取课程列表 |
| GET    | /api/courses/:id                | 获取课程详情 |
| POST   | /api/courses/                   | 创建课程   |
| PUT    | /api/courses/:id                | 更新课程   |
| DELETE | /api/courses/:id                | 删除课程   |
| POST   | /api/courses/enroll/:id         | 报名课程   |
| GET    | /api/courses/my-enrollments     | 我的报名   |
| GET    | /api/courses/teacher/my-courses | 教师课程列表 |

### 作业接口

| 方法     | 路径                          | 说明     |
| ------ | --------------------------- | ------ |
| GET    | /api/assignments/course/:id | 获取课程作业 |
| POST   | /api/assignments/           | 创建作业   |
| PUT    | /api/assignments/:id        | 更新作业   |
| DELETE | /api/assignments/:id        | 删除作业   |
| POST   | /api/assignments/submit/:id | 提交作业   |
| POST   | /api/assignments/grade/:id  | 批改作业   |

### 互动接口

| 方法   | 路径                           | 说明     |
| ---- | ---------------------------- | ------ |
| GET  | /api/discussions/course/:id  | 获取课程讨论 |
| POST | /api/discussions/            | 创建讨论   |
| GET  | /api/discussions/:id/replies | 获取讨论回复 |
| POST | /api/reviews                 | 提交课程评价 |
| POST | /api/questions               | 提交提问   |
| POST | /api/questions/:id/answers   | 提交回答   |

### 审核接口

| 方法  | 路径                                 | 说明     |
| --- | ---------------------------------- | ------ |
| GET | /api/admin/reviews                 | 评价审核列表 |
| GET | /api/admin/questions               | 提问审核列表 |
| GET | /api/admin/answers                 | 回答审核列表 |
| GET | /api/admin/discussions             | 讨论审核列表 |
| PUT | /api/admin/reviews/:id/approve     | 通过评价   |
| PUT | /api/admin/reviews/:id/reject      | 拒绝评价   |
| PUT | /api/admin/discussions/:id/approve | 通过讨论   |
| PUT | /api/admin/discussions/:id/reject  | 拒绝讨论   |

### 管理端接口

| 方法     | 路径                           | 说明     |
| ------ | ---------------------------- | ------ |
| GET    | /api/admin/users             | 用户列表   |
| POST   | /api/admin/users/:id/approve | 审核用户通过 |
| DELETE | /api/admin/users/:id         | 删除用户   |
| GET    | /api/admin/statistics        | 系统统计   |
| GET    | /api/admin/courses           | 全部课程管理 |

### AI 接口

| 方法     | 路径                        | 说明           |
| ------ | ------------------------- | ------------ |
| GET    | /api/ai/conversations     | 获取对话列表       |
| POST   | /api/ai/chat              | 发送消息（SSE 流式） |
| DELETE | /api/ai/conversations/:id | 删除对话         |

### 备份接口

| 方法     | 路径                         | 说明   |
| ------ | -------------------------- | ---- |
| POST   | /api/backup/export         | 创建备份 |
| POST   | /api/backup/import         | 导入恢复 |
| GET    | /api/backup/list           | 备份列表 |
| GET    | /api/backup/download/:name | 下载备份 |
| DELETE | /api/backup/delete/:name   | 删除备份 |

### 文件上传

| 方法   | 路径                        | 说明    |
| ---- | ------------------------- | ----- |
| POST | /api/uploads/avatar       | 上传头像  |
| POST | /api/uploads/course-image | 上传课程图 |
| POST | /api/uploads/video        | 上传视频  |

## 数据库模型

### 核心模型

**User（用户）**

| 字段            | 类型  | 说明                             |
| ------------- | --- | ------------------------------ |
| id            | int | 主键                             |
| username      | str | 用户名（唯一）                        |
| email         | str | 邮箱（唯一）                         |
| password_hash | str | 密码哈希                           |
| role          | str | 角色：student / teacher / admin   |
| real_name     | str | 真实姓名                           |
| phone         | str | 手机号                            |
| avatar        | str | 头像 URL                         |
| bio           | str | 个人简介                           |
| status        | str | 状态：pending / active / inactive |

**Course（课程）**

| 字段          | 类型    | 说明                           |
| ----------- | ----- | ---------------------------- |
| id          | int   | 主键                           |
| title       | str   | 课程标题                         |
| description | str   | 课程描述                         |
| cover_image | str   | 封面图 URL                      |
| teacher_id  | int   | 外键 → User                    |
| category_id | int   | 外键 → Category                |
| price       | float | 价格                           |
| status      | str   | draft / published / archived |

**Lesson（课时）**

| 字段        | 类型  | 说明          |
| --------- | --- | ----------- |
| id        | int | 主键          |
| course_id | int | 外键 → Course |
| title     | str | 课时标题        |
| video_url | str | 视频 URL      |
| content   | str | 课时文字内容      |
| duration  | int | 时长（秒）       |
| order     | int | 排序序号        |

**Assignment（作业）**

| 字段          | 类型       | 说明          |
| ----------- | -------- | ----------- |
| id          | int      | 主键          |
| course_id   | int      | 外键 → Course |
| title       | str      | 作业标题        |
| description | str      | 作业描述        |
| due_date    | datetime | 截止日期        |
| max_score   | int      | 满分值         |

**Review（评价）**

| 字段        | 类型  | 说明                            |
| --------- | --- | ----------------------------- |
| id        | int | 主键                            |
| course_id | int | 外键 → Course                   |
| user_id   | int | 外键 → User                     |
| rating    | int | 评分（1-5）                       |
| content   | str | 评价内容                          |
| status    | str | pending / approved / rejected |

**Question（提问）**

| 字段          | 类型   | 说明                            |
| ----------- | ---- | ----------------------------- |
| id          | int  | 主键                            |
| course_id   | int  | 外键 → Course                   |
| user_id     | int  | 外键 → User                     |
| title       | str  | 问题标题                          |
| content     | str  | 问题内容                          |
| is_resolved | bool | 是否已解决                         |
| status      | str  | pending / approved / rejected |

**Discussion（讨论）**

| 字段        | 类型  | 说明                            |
| --------- | --- | ----------------------------- |
| id        | int | 主键                            |
| course_id | int | 外键 → Course                   |
| user_id   | int | 外键 → User                     |
| parent_id | int | 父讨论 ID（NULL 表示主帖）             |
| content   | str | 讨论内容                          |
| status    | str | pending / approved / rejected |

## 架构亮点

### 后端

- **共享认证模块**：`get_current_user` 提取至 `app/utils/auth.py`，8 个路由文件统一引用
- **权限装饰器体系**：`admin_required` / `teacher_required` / `course_owner_or_admin` 统一权限校验
- **分页工具函数**：`get_pagination_params` 消除 15+ 处分页参数重复代码
- **统一错误处理**：`handle_route_error` / `handle_upload_error` 装饰器统一响应格式
- **双令牌机制**：Access Token + Refresh Token，安全与体验兼顾
- **内容审核三态**：pending → approved / rejected 流转，角色分级管理

### 前端

- **组合函数复用**：`useUserProfile` 将 Student/Teacher Profile 共享逻辑提升为组合函数
- **安全工具模块**：`createConfirmValidator` 工厂函数、`formatDate` 等统一管理
- **自定义指令**：`v-lazy` 基于 IntersectionObserver 的图片懒加载
- **缓存系统**：`PageCache` 带 TTL 过期机制的页面级缓存
- **响应式设计**：桌面端 / 平板端 / 移动端三端适配

## 视频播放器功能

- 倍速播放（0.5x ~ 2x）
- 画中画模式
- 快进/快退（10 秒）
- 音量调节
- 全屏播放
- 快捷键支持

## AI 学习助手

- 基于智谱 AI（GLM-4-Flash）大语言模型
- 支持流式输出（SSE），实时显示 AI 回复
- Markdown 渲染（代码高亮、表格、列表）
- 多轮对话管理，对话历史持久化
- 学习场景定制系统提示词

## 内容审核机制

- 用户提交的内容需审核后才能公开展示
- 学生可看到自己待审核的内容（显示"审核中"标签）
- 教师可审核自己课程下的评价、提问、讨论
- 管理员可审核全站所有内容
- 统一的三态审核流转：pending → approved / rejected

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue 或 Pull Request。
