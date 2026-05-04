<template>
  <nav class="navbar" :class="{ scrolled: isScrolled, 'top-not-home': !isHomePage && !isScrolled }">
    <div class="container">
      <router-link class="navbar-brand" to="/">
        <div class="brand-icon">
          <el-icon :size="22"><Reading /></el-icon>
        </div>
        <span class="brand-text">成人再教育平台</span>
      </router-link>

      <button class="navbar-toggler" type="button" @click="menuOpen = !menuOpen">
        <span class="toggler-icon" :class="{ active: menuOpen }"></span>
      </button>

      <!-- 移动端遮罩层 -->
      <div class="mobile-backdrop" :class="{ show: menuOpen }" @click="menuOpen = false"></div>
      
      <div class="navbar-menu" :class="{ show: menuOpen }">
        <!-- 移动端关闭按钮 -->
        <button class="mobile-close" @click="menuOpen = false">
          <el-icon :size="24"><Close /></el-icon>
        </button>
        
        <ul class="nav-links">
          <li>
            <router-link class="nav-link" to="/" exact-active-class="active" @click="menuOpen = false">
              <el-icon><HomeFilled /></el-icon>首页
            </router-link>
          </li>
          <li>
            <router-link class="nav-link" to="/courses" active-class="active" @click="menuOpen = false">
              <el-icon><Reading /></el-icon>课程中心
            </router-link>
          </li>
          <li v-if="userStore.userRole === 'student'">
            <router-link class="nav-link" to="/student/my-courses" active-class="active" @click="menuOpen = false">
              <el-icon><Notebook /></el-icon>我的课程
            </router-link>
          </li>
          <li v-if="userStore.userRole === 'student'">
            <router-link class="nav-link" to="/student/reviews" active-class="active" @click="menuOpen = false">
              <el-icon><Star /></el-icon>我的评价
            </router-link>
          </li>
          <li v-if="userStore.userRole === 'student'">
            <router-link class="nav-link" to="/student/messages" active-class="active" @click="menuOpen = false">
              <el-icon><Bell /></el-icon>消息中心
            </router-link>
          </li>
          <li v-if="userStore.userRole === 'student'">
            <router-link class="nav-link" to="/student/ai-assistant" active-class="active" @click="menuOpen = false">
              <el-icon><Service /></el-icon>AI助手
            </router-link>
          </li>
          <li v-if="userStore.userRole === 'teacher'">
            <router-link class="nav-link" to="/teacher/dashboard" active-class="active" @click="menuOpen = false">
              <el-icon><DataLine /></el-icon>控制台
            </router-link>
          </li>
          <li v-if="userStore.userRole === 'teacher'">
            <router-link class="nav-link" to="/teacher/courses" active-class="active" @click="menuOpen = false">
              <el-icon><Management /></el-icon>课程管理
            </router-link>
          </li>
          <li v-if="userStore.userRole === 'teacher'">
            <router-link class="nav-link" to="/teacher/assignments" active-class="active" @click="menuOpen = false">
              <el-icon><Edit /></el-icon>作业管理
            </router-link>
          </li>
          <li v-if="userStore.userRole === 'teacher'">
            <router-link class="nav-link" to="/teacher/students" active-class="active" @click="menuOpen = false">
              <el-icon><User /></el-icon>学生管理
            </router-link>
          </li>
          <li v-if="userStore.userRole === 'teacher'">
            <router-link class="nav-link" to="/teacher/review-moderation" active-class="active" @click="menuOpen = false">
              <el-icon><Check /></el-icon>内容审核
            </router-link>
          </li>
          <li v-if="userStore.userRole === 'admin'">
            <router-link class="nav-link" to="/admin/dashboard" active-class="active" @click="menuOpen = false">
              <el-icon><Setting /></el-icon>管理后台
            </router-link>
          </li>
        </ul>

        <div class="nav-actions">
          <template v-if="userStore.isLoggedIn">
            <el-dropdown trigger="click" @command="handleCommand">
              <div class="user-trigger">
                <el-avatar :size="34" class="user-avatar">
                  {{ userStore.user.real_name?.charAt(0) || userStore.user.username?.charAt(0) }}
                </el-avatar>
                <span class="user-name">{{ userStore.user.real_name || userStore.user.username }}</span>
                <el-icon class="arrow-icon"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="dashboard">
                    <el-icon><DataLine /></el-icon>我的控制台
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <router-link to="/login" class="btn-login" @click="menuOpen = false">登录</router-link>
            <router-link to="/register" class="btn-register" @click="menuOpen = false">免费注册</router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { Reading, ArrowDown, User, DataLine, SwitchButton, HomeFilled, Notebook, Bell, Management, Setting, Service, Edit, Star, Close, Check } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const isScrolled = ref(false)
const menuOpen = ref(false)
const isComponentMounted = ref(true)

const isHomePage = computed(() => {
  return route.path === '/'
})

function handleScroll() {
  isScrolled.value = window.scrollY > 20
}

function handleCommand(command) {
  menuOpen.value = false
  switch (command) {
    case 'profile':
      if (userStore.userRole === 'student') router.push('/student/profile')
      else if (userStore.userRole === 'teacher') router.push('/teacher/profile')
      else router.push('/admin/dashboard')
      break
    case 'dashboard':
      if (userStore.userRole === 'student') router.push('/student/dashboard')
      else if (userStore.userRole === 'teacher') router.push('/teacher/dashboard')
      else router.push('/admin/dashboard')
      break
    case 'logout':
      userStore.logout()
      router.push('/')
      break
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  isComponentMounted.value = false
  window.removeEventListener('scroll', handleScroll)
  document.body.style.overflow = ''
})

// 监听菜单状态变化，禁止/恢复背景滚动
watch(menuOpen, (newVal) => {
  if (!isComponentMounted.value) return
  if (newVal) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 16px 0;
  transition: box-shadow 0.3s ease, padding 0.3s ease;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

.navbar.scrolled {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  padding: 12px 0;
}

.navbar .container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.brand-icon {
  width: 40px;
  height: 40px;
  background: #2563eb;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.brand-text {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.navbar-toggler {
  display: none;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  cursor: pointer;
  position: relative;
}

.toggler-icon,
.toggler-icon::before,
.toggler-icon::after {
  display: block;
  width: 24px;
  height: 2px;
  background: #111827;
  border-radius: 2px;
  transition: all 0.3s;
  position: absolute;
  left: 4px;
}

.toggler-icon {
  top: 50%;
  transform: translateY(-50%);
}

.toggler-icon::before {
  content: '';
  top: -8px;
}

.toggler-icon::after {
  content: '';
  top: 8px;
}

.toggler-icon.active {
  background: transparent;
}

.toggler-icon.active::before {
  top: 0;
  transform: rotate(45deg);
}

.toggler-icon.active::after {
  top: 0;
  transform: rotate(-45deg);
}

.navbar-menu {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  color: #4b5563;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  border-radius: 6px;
  transition: all 0.2s;
  position: relative;
}

.nav-link:hover {
  background: #f3f4f6;
  color: #111827;
}

.nav-link.active {
  color: #111827;
  background: transparent;
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 16px;
  right: 16px;
  height: 2px;
  background: #2563eb;
  border-radius: 1px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  background: #f3f4f6;
}

.user-trigger:hover {
  background: #e5e7eb;
}

.user-avatar {
  background: #2563eb;
  color: #fff;
  font-weight: 600;
  font-size: 14px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
}

.arrow-icon {
  color: #9ca3af;
  font-size: 12px;
}

.btn-login {
  padding: 10px 20px;
  color: #2563eb;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s;
  border: 1px solid #2563eb;
  background: transparent;
}

.btn-login:hover {
  background: #f0f5ff;
}

.btn-register {
  padding: 10px 20px;
  background: #2563eb;
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  transition: all 0.2s;
  border: 1px solid #2563eb;
}

.btn-register:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
}

.mobile-close {
  display: none !important;
}

@media (max-width: 992px) {
  .navbar-toggler {
    display: block;
  }

  .navbar-menu {
    position: fixed;
    top: 0;
    right: 0;
    width: 100vw;
    height: 100vh;
    height: 100dvh;
    background: #ffffff;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    gap: 20px;
    padding: 80px 24px 40px;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    z-index: 1000;
    box-sizing: border-box;
  }

  .navbar-menu.show {
    transform: translateX(0);
  }

  .mobile-close {
    display: flex !important;
    position: absolute;
    top: 20px;
    right: 20px;
    width: 40px;
    height: 40px;
    align-items: center;
    justify-content: center;
    background: #f3f4f6;
    border: none;
    border-radius: 50%;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.3s;
    z-index: 10;
  }

  .mobile-close:hover {
    background: #e5e7eb;
    color: #111827;
  }

  .mobile-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    height: 100dvh;
    background: rgba(0, 0, 0, 0.5);
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    z-index: 999;
  }

  .mobile-backdrop.show {
    opacity: 1;
    visibility: visible;
  }

  .navbar-menu.show {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }

  .nav-links {
    flex-direction: column;
    gap: 12px;
    width: 100%;
    text-align: center;
    padding: 0 20px;
  }

  .nav-link {
    font-size: 18px;
    padding: 16px 24px;
    color: #111827;
    justify-content: center;
    border-radius: 6px;
    width: 100%;
    max-width: 300px;
  }

  .nav-link:hover {
    background: #f3f4f6;
    color: #111827;
  }

  .nav-link.active {
    background: #f3f4f6;
    color: #111827;
  }

  .nav-link.active::after {
    display: none;
  }

  .nav-actions {
    flex-direction: column;
    width: 100%;
    padding: 20px;
    margin-top: 30px;
    gap: 12px;
    align-items: center;
  }

  .user-trigger {
    background: #f3f4f6;
    justify-content: center;
    padding: 14px 24px;
    border-radius: 6px;
    width: 100%;
    max-width: 300px;
  }

  .user-trigger:hover {
    background: #e5e7eb;
  }

  .user-name {
    color: #111827;
  }

  .arrow-icon {
    color: #9ca3af;
  }

  .btn-login,
  .btn-register {
    width: 100%;
    max-width: 300px;
    text-align: center;
    padding: 14px;
    border-radius: 8px;
  }

  .btn-login {
    color: #2563eb;
    border-color: #2563eb;
    background: transparent;
  }

  .btn-register {
    background: #2563eb;
    color: #fff;
    border-color: #2563eb;
  }

  .hide-on-mobile {
    display: none;
  }
}
</style>
