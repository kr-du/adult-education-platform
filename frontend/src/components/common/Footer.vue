<template>
  <footer class="footer">
    <div class="container">
      <div class="row">
        <div class="col-md-4 mb-3 mb-md-0">
          <h5 class="footer-title">
            <el-icon class="me-2"><Reading /></el-icon>成人再教育学习平台
          </h5>
          <p class="footer-desc">致力于为成人学习者提供优质在线教育资源，助力终身学习与职业发展</p>
          <div class="footer-social">
            <el-icon :size="20"><ChatDotRound /></el-icon>
            <el-icon :size="20"><Promotion /></el-icon>
            <el-icon :size="20"><VideoCamera /></el-icon>
          </div>
        </div>
        <div class="col-md-4 mb-3 mb-md-0">
          <h6 class="footer-subtitle">快速链接</h6>
          <ul class="list-unstyled footer-links">
            <li><router-link to="/">首页</router-link></li>
            <li><router-link to="/courses">课程中心</router-link></li>
            <li><router-link to="/register">免费注册</router-link></li>
          </ul>
        </div>
        <div class="col-md-4">
          <h6 class="footer-subtitle">联系我们</h6>
          <p class="footer-contact"><el-icon class="me-1"><Message /></el-icon>support@edu-platform.com</p>
          <p class="footer-contact"><el-icon class="me-1"><Phone /></el-icon>400-888-9999</p>
          <p class="footer-contact"><el-icon class="me-1"><Location /></el-icon>北京市海淀区中关村科技园</p>
        </div>
      </div>
      <hr class="footer-divider">
      <div class="footer-bottom">
        <p class="footer-copyright">&copy; 2025-{{ currentYear }} 成人再教育学习平台 版权所有</p>
        <div class="footer-links-bottom">
          <a href="#">用户协议</a>
          <span class="divider">|</span>
          <a href="#">隐私政策</a>
          <span class="divider">|</span>
          <a href="#">帮助中心</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { Reading, Message, Phone, Location, ChatDotRound, Promotion, VideoCamera } from '@element-plus/icons-vue'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.footer {
  background: #1a1a2e;
  color: #e0e0e0;
  padding: 40px 0 20px;
  margin-top: auto;
}

.footer-title {
  color: #ffffff;
  font-weight: 600;
  margin-bottom: 12px;
}

.footer-desc {
  color: #a0a0a0;
  font-size: 14px;
  margin: 0 0 16px;
}

.footer-social {
  display: flex;
  gap: 16px;
  color: #a0a0a0;
}

.footer-social .el-icon {
  cursor: pointer;
  transition: color 0.2s;
}

.footer-social .el-icon:hover {
  color: #409eff;
}

.footer-subtitle {
  color: #ffffff;
  font-weight: 600;
  margin-bottom: 16px;
}

.footer-links li {
  margin-bottom: 8px;
}

.footer-links a {
  color: #a0a0a0;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: #409eff;
}

.footer-contact {
  color: #a0a0a0;
  font-size: 14px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.footer-divider {
  border-color: rgba(255, 255, 255, 0.1);
  margin: 24px 0 16px;
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.footer-copyright {
  color: #808080;
  font-size: 13px;
  margin: 0;
}

.footer-links-bottom {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.footer-links-bottom a {
  color: #808080;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-links-bottom a:hover {
  color: #409eff;
}

.footer-links-bottom .divider {
  color: #505050;
}

@media (max-width: 768px) {
  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }
}
</style>
