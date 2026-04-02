<template>
  <div class="admin-layout">
    <!-- 移动端遮罩 -->
    <div class="sidebar-overlay" :class="{ show: mobileMenuOpen }" @click="mobileMenuOpen = false"></div>
    
    <aside class="sidebar" :class="{ collapsed: isCollapsed, 'mobile-open': mobileMenuOpen }">
      <div class="sidebar-header">
        <div class="logo">
          <el-icon :size="28"><Reading /></el-icon>
          <span v-show="!isCollapsed">管理后台</span>
        </div>
        <!-- 移动端关闭按钮 -->
        <el-button class="mobile-close-btn" text @click="mobileMenuOpen = false">
          <el-icon :size="20"><Close /></el-icon>
        </el-button>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        router
        class="sidebar-menu"
        @select="mobileMenuOpen = false"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>控制台</template>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/courses">
          <el-icon><Reading /></el-icon>
          <template #title>课程管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/categories">
          <el-icon><Folder /></el-icon>
          <template #title>分类管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/announcements">
          <el-icon><Bell /></el-icon>
          <template #title>公告管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/review-moderation">
          <el-icon><Check /></el-icon>
          <template #title>内容审核</template>
        </el-menu-item>
        <el-menu-item index="/admin/statistics">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>统计报表</template>
        </el-menu-item>
        <el-menu-item index="/admin/backup">
          <el-icon><Download /></el-icon>
          <template #title>数据备份</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-bottom">
        <div class="collapse-btn" @click="toggleSidebar">
          <el-icon :size="18"><Fold v-if="!isCollapsed" /><Expand v-else /></el-icon>
          <span v-show="!isCollapsed">收起</span>
        </div>
      </div>
    </aside>

    <div class="main-wrapper" :style="{ marginLeft: isCollapsed ? '64px' : '240px' }">
      <header class="top-header">
        <!-- 移动端菜单按钮 -->
        <el-button class="mobile-menu-btn" text @click="mobileMenuOpen = true">
          <el-icon :size="22"><Fold /></el-icon>
        </el-button>
        
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item v-if="route.meta?.title">{{ route.meta.title }}</el-breadcrumb-item>
        </el-breadcrumb>

        <div class="header-right">
          <el-tooltip content="全屏" placement="bottom">
            <el-button text @click="toggleFullscreen">
              <el-icon :size="18"><FullScreen /></el-icon>
            </el-button>
          </el-tooltip>
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32">{{ userStore.user.real_name?.charAt(0) || 'A' }}</el-avatar>
              <span class="username">{{ userStore.user.real_name || '管理员' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="home"><el-icon><House /></el-icon>前台首页</el-dropdown-item>
                <el-dropdown-item divided command="logout"><el-icon><SwitchButton /></el-icon>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { Reading, Fold, Expand, DataBoard, User, Folder, Bell, DataAnalysis, FullScreen, ArrowDown, House, SwitchButton, Check, Close, Download } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isCollapsed = ref(false)
const mobileMenuOpen = ref(false)

const activeMenu = computed(() => route.path)

function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value
}

function toggleFullscreen() {
  document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen()
}

function handleCommand(cmd) {
  cmd === 'home' ? router.push('/') : (userStore.logout(), router.push('/login'))
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #f0f2f5;
}

.sidebar {
  width: 240px;
  background: linear-gradient(180deg, #001529 0%, #002140 100%);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  transition: width 0.3s;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar:not(.collapsed) .sidebar-header {
  justify-content: flex-start;
  padding-left: 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  background: transparent;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}

.sidebar-menu.el-menu--collapse {
  width: 64px;
}

:deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.65);
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
  border-radius: 8px;
}

:deep(.el-menu-item:hover) {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

:deep(.el-menu-item.is-active) {
  color: #fff;
  background: #1890ff;
}

.sidebar-bottom {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  color: rgba(255, 255, 255, 0.65);
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  font-size: 14px;
}

.collapse-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.main-wrapper {
  flex: 1;
  transition: margin-left 0.3s;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.top-header {
  height: 64px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 99;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
}

.user-info:hover {
  background: #f5f5f5;
}

:deep(.user-info .el-avatar) {
  background: linear-gradient(135deg, #1890ff, #36cfc9);
  color: #fff;
  font-weight: 600;
}

.username {
  font-size: 14px;
  color: #333;
}

.main-content {
  flex: 1;
  padding: 24px;
  background: #f0f2f5;
}

/* 移动端菜单按钮 - 默认隐藏 */
.mobile-menu-btn {
  display: none;
}

/* 移动端关闭按钮 - 默认隐藏 */
.mobile-close-btn {
  display: none;
}

/* 移动端遮罩 - 默认隐藏 */
.sidebar-overlay {
  display: none;
}

@media (max-width: 768px) {
  .admin-layout {
    min-height: 100vh;
  }
  
  .sidebar {
    position: fixed;
    left: -240px;
    width: 240px;
    transition: left 0.3s ease;
    z-index: 1001;
  }
  
  .sidebar.mobile-open {
    left: 0;
  }
  
  .sidebar-overlay {
    display: block;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    z-index: 1000;
  }
  
  .sidebar-overlay.show {
    opacity: 1;
    visibility: visible;
  }
  
  .mobile-menu-btn {
    display: flex;
  }
  
  .mobile-close-btn {
    display: flex;
    color: rgba(255, 255, 255, 0.7);
  }
  
  .mobile-close-btn:hover {
    color: #fff;
  }
  
  .sidebar-header {
    justify-content: space-between;
  }
  
  .main-wrapper {
    margin-left: 0 !important;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .username {
    display: none;
  }
  
  .top-header {
    padding: 0 16px;
  }
  
  .el-breadcrumb {
    display: none;
  }
}

@media (max-width: 576px) {
  .main-content {
    padding: 12px;
  }
}
</style>
