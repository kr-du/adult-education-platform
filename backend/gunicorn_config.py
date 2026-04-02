# Gunicorn配置文件

# 绑定地址和端口
bind = "0.0.0.0:5000"

# 工作进程数（推荐为 CPU核心数 * 2 + 1）
workers = 4

# 工作进程类型
worker_class = "sync"

# 超时时间（秒）
timeout = 120

# 保持连接时间
keepalive = 2

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

# 日志配置
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 进程名称
proc_name = "education_platform"

# 守护进程模式（Docker中不需要）
daemon = False

# 临时目录
tmp_upload_dir = None
