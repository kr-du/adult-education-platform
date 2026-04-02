#!/bin/bash

# ===========================================
# 教育平台部署脚本 (Linux/Mac)
# ===========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   教育平台部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[错误] 未安装Docker${NC}"
    echo "请访问 https://docs.docker.com/get-docker/ 安装Docker"
    exit 1
fi

# 检查docker-compose是否可用
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}[错误] 未安装docker-compose${NC}"
    exit 1
fi

echo -e "${GREEN}[信息] Docker环境检查通过${NC}"
echo ""

# 检查.env文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}[警告] 未找到.env文件，将使用示例配置${NC}"
    cp .env.example .env
    echo -e "${YELLOW}[提示] 请编辑.env文件修改配置，特别是密码和密钥${NC}"
    echo ""
fi

# 创建必要目录
echo -e "${GREEN}[信息] 创建目录结构...${NC}"
mkdir -p backend/uploads/{avatars,courses,videos}
mkdir -p backend/backups
mkdir -p nginx/{conf.d,ssl}
mkdir -p database/init

# 构建并启动服务
echo -e "${GREEN}[信息] 构建并启动服务...${NC}"
docker-compose down
docker-compose build --no-cache
docker-compose up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] 服务启动失败，请检查日志${NC}"
    docker-compose logs
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "服务访问地址:"
echo "  前端: http://localhost"
echo "  后端API: http://localhost:5000"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo ""
echo -e "${YELLOW}[提示] 首次部署需要初始化数据库，稍等片刻...${NC}"
echo ""

sleep 5

# 初始化数据库
echo -e "${GREEN}[信息] 初始化数据库...${NC}"
docker-compose exec backend python seed_data.py

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   数据库初始化完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "默认管理员账号:"
echo "  用户名: admin"
echo "  密码: 123456"
echo ""
echo -e "${RED}请登录后立即修改密码！${NC}"
echo ""
