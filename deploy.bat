@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo    教育平台部署脚本 (Windows)
echo ========================================
echo.

:: 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装Docker，请先安装Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

:: 检查docker-compose是否可用
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装docker-compose
    pause
    exit /b 1
)

echo [信息] Docker环境检查通过
echo.

:: 检查.env文件
if not exist .env (
    echo [警告] 未找到.env文件，将使用示例配置
    copy .env.example .env
    echo [提示] 请编辑.env文件修改配置，特别是密码和密钥
    echo.
)

:: 创建必要目录
echo [信息] 创建目录结构...
if not exist backend\uploads\avatars mkdir backend\uploads\avatars
if not exist backend\uploads\courses mkdir backend\uploads\courses
if not exist backend\uploads\videos mkdir backend\uploads\videos
if not exist backend\backups mkdir backend\backups
if not exist nginx\conf.d mkdir nginx\conf.d
if not exist nginx\ssl mkdir nginx\ssl
if not exist database\init mkdir database\init

:: 构建并启动服务
echo [信息] 构建并启动服务...
docker-compose down
docker-compose build --no-cache
docker-compose up -d

if errorlevel 1 (
    echo [错误] 服务启动失败，请检查日志
    docker-compose logs
    pause
    exit /b 1
)

echo.
echo ========================================
echo    部署完成！
echo ========================================
echo.
echo 服务访问地址:
echo   前端: http://localhost
echo   后端API: http://localhost:5000
echo.
echo 常用命令:
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose down
echo   重启服务: docker-compose restart
echo.
echo [提示] 首次部署需要初始化数据库，稍等片刻...
echo.

timeout /t 5 >nul

:: 初始化数据库
echo [信息] 初始化数据库...
docker-compose exec backend python seed_data.py

echo.
echo ========================================
echo    数据库初始化完成！
echo ========================================
echo.
echo 默认管理员账号:
echo   用户名: admin
echo   密码: 123456
echo.
echo 请登录后立即修改密码！
echo.

pause
