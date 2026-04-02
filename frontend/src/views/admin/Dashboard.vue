<template>
  <div class="admin-dashboard">
    <div class="page-header">
      <div>
        <h1 class="page-title">控制台</h1>
        <p class="page-subtitle">{{ currentDate }}</p>
      </div>
      <el-button type="primary" @click="fetchData">
        <el-icon class="me-1"><Refresh /></el-icon>刷新数据
      </el-button>
    </div>

    <el-skeleton :loading="loading" animated :count="4">
      <template #template>
        <div class="stat-grid">
          <div v-for="i in 4" :key="i" class="stat-card">
            <el-card><el-skeleton-item variant="h1" /></el-card>
          </div>
        </div>
      </template>

      <template #default>
        <div class="stat-grid">
          <div class="stat-card" v-for="stat in statCards" :key="stat.label" :class="stat.class">
            <div class="stat-card-inner">
              <div class="stat-info">
                <span class="stat-label">{{ stat.label }}</span>
                <span class="stat-value">{{ stat.value }}</span>
              </div>
              <div class="stat-icon-wrap" :class="stat.iconClass">
                <el-icon :size="24"><component :is="stat.icon" /></el-icon>
              </div>
            </div>
          </div>
        </div>

        <div class="content-grid">
          <div class="content-main">
            <div class="card">
              <div class="card-header">
                <span class="card-title">本月数据</span>
              </div>
              <div class="monthly-stats">
                <div class="monthly-item">
                  <div class="monthly-icon monthly-icon--blue">
                    <el-icon :size="20"><User /></el-icon>
                  </div>
                  <div class="monthly-info">
                    <span class="monthly-value">{{ statistics.monthly?.new_users || 0 }}</span>
                    <span class="monthly-label">新增用户</span>
                  </div>
                </div>
                <div class="monthly-item">
                  <div class="monthly-icon monthly-icon--green">
                    <el-icon :size="20"><Reading /></el-icon>
                  </div>
                  <div class="monthly-info">
                    <span class="monthly-value">{{ statistics.monthly?.new_courses || 0 }}</span>
                    <span class="monthly-label">新增课程</span>
                  </div>
                </div>
                <div class="monthly-item">
                  <div class="monthly-icon monthly-icon--orange">
                    <el-icon :size="20"><Notebook /></el-icon>
                  </div>
                  <div class="monthly-info">
                    <span class="monthly-value">{{ statistics.monthly?.new_enrollments || 0 }}</span>
                    <span class="monthly-label">新增报名</span>
                  </div>
                </div>
                <div class="monthly-item">
                  <div class="monthly-icon monthly-icon--purple">
                    <el-icon :size="20"><Document /></el-icon>
                  </div>
                  <div class="monthly-info">
                    <span class="monthly-value">{{ statistics.total_submissions || 0 }}</span>
                    <span class="monthly-label">作业提交</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="card">
              <div class="card-header">
                <span class="card-title">用户分布</span>
              </div>
              <div class="user-distribution">
                <div class="dist-item">
                  <div class="dist-bar">
                    <div class="dist-fill dist-fill--blue" :style="{ width: studentPercent + '%' }"></div>
                  </div>
                  <div class="dist-info">
                    <span class="dist-label">学生</span>
                    <span class="dist-value">{{ statistics.user_stats?.students || 0 }}人</span>
                  </div>
                </div>
                <div class="dist-item">
                  <div class="dist-bar">
                    <div class="dist-fill dist-fill--green" :style="{ width: teacherPercent + '%' }"></div>
                  </div>
                  <div class="dist-info">
                    <span class="dist-label">教师</span>
                    <span class="dist-value">{{ statistics.user_stats?.teachers || 0 }}人</span>
                  </div>
                </div>
                <div class="dist-item">
                  <div class="dist-bar">
                    <div class="dist-fill dist-fill--orange" :style="{ width: publishedPercent + '%' }"></div>
                  </div>
                  <div class="dist-info">
                    <span class="dist-label">已发布课程</span>
                    <span class="dist-value">{{ statistics.course_stats?.published || 0 }}门</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="content-side">
            <div class="card">
              <div class="card-header">
                <span class="card-title">待审核用户</span>
                <el-badge :value="pendingUsers.length" :max="99" type="warning" />
              </div>
              <div v-if="pendingUsers.length === 0" class="card-body-empty">
                <el-empty description="暂无待审核用户" :image-size="60" />
              </div>
              <div v-else class="pending-list">
                <div v-for="user in pendingUsers.slice(0, 5)" :key="user.id" class="pending-item">
                  <div class="pending-info">
                    <el-avatar :size="32" class="pending-avatar">{{ user.username?.charAt(0)?.toUpperCase() }}</el-avatar>
                    <div class="pending-text">
                      <p class="pending-name">{{ user.real_name || user.username }}</p>
                      <p class="pending-email">{{ user.role === 'teacher' ? '教师' : '学生' }} · {{ user.email }}</p>
                    </div>
                  </div>
                  <div class="pending-actions">
                    <el-button type="success" size="small" circle @click="handleApprove(user)">
                      <el-icon><Check /></el-icon>
                    </el-button>
                    <el-button type="danger" size="small" circle @click="handleReject(user)">
                      <el-icon><Close /></el-icon>
                    </el-button>
                  </div>
                </div>
                <div v-if="pendingUsers.length > 5" class="pending-more">
                  <el-button type="primary" link @click="$router.push('/admin/users?status=pending')">
                    查看全部 {{ pendingUsers.length }} 个待审核用户
                  </el-button>
                </div>
              </div>
            </div>

            <div class="card">
              <div class="card-header">
                <span class="card-title">快捷入口</span>
              </div>
              <div class="quick-actions">
                <div class="quick-item" @click="$router.push('/admin/users')">
                  <el-icon :size="24" class="quick-icon quick-icon--blue"><User /></el-icon>
                  <span>用户管理</span>
                </div>
                <div class="quick-item" @click="$router.push('/admin/courses')">
                  <el-icon :size="24" class="quick-icon quick-icon--green"><Reading /></el-icon>
                  <span>课程管理</span>
                </div>
                <div class="quick-item" @click="$router.push('/admin/categories')">
                  <el-icon :size="24" class="quick-icon quick-icon--orange"><Folder /></el-icon>
                  <span>分类管理</span>
                </div>
                <div class="quick-item" @click="$router.push('/admin/announcements')">
                  <el-icon :size="24" class="quick-icon quick-icon--purple"><Bell /></el-icon>
                  <span>公告管理</span>
                </div>
                <div class="quick-item" @click="$router.push('/admin/statistics')">
                  <el-icon :size="24" class="quick-icon quick-icon--red"><DataAnalysis /></el-icon>
                  <span>统计报表</span>
                </div>
                <div class="quick-item" @click="$router.push('/')">
                  <el-icon :size="24" class="quick-icon quick-icon--gray"><House /></el-icon>
                  <span>前台首页</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </el-skeleton>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Reading, Bell, DataAnalysis, Check, Close, Notebook, Clock, Refresh, Folder, House, Document } from '@element-plus/icons-vue'

const loading = ref(true)
const statistics = ref({})
const pendingUsers = ref([])

const currentDate = computed(() => {
  const now = new Date()
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return `${now.getFullYear()}年${String(now.getMonth() + 1).padStart(2, '0')}月${String(now.getDate()).padStart(2, '0')}日 ${weekdays[now.getDay()]}`
})

const statCards = computed(() => [
  { label: '用户总数', value: statistics.value.total_users || 0, class: 'stat-card--blue', iconClass: 'stat-icon--blue', icon: 'User' },
  { label: '课程总数', value: statistics.value.total_courses || 0, class: 'stat-card--green', iconClass: 'stat-icon--green', icon: 'Reading' },
  { label: '报名总数', value: statistics.value.total_enrollments || 0, class: 'stat-card--orange', iconClass: 'stat-icon--orange', icon: 'Notebook' },
  { label: '待审核', value: statistics.value.user_stats?.pending || pendingUsers.value.length, class: 'stat-card--red', iconClass: 'stat-icon--red', icon: 'Clock' }
])

const studentPercent = computed(() => {
  const total = statistics.value.total_users || 1
  return Math.round((statistics.value.user_stats?.students || 0) / total * 100)
})

const teacherPercent = computed(() => {
  const total = statistics.value.total_users || 1
  return Math.round((statistics.value.user_stats?.teachers || 0) / total * 100)
})

const publishedPercent = computed(() => {
  const total = statistics.value.total_courses || 1
  return Math.round((statistics.value.course_stats?.published || 0) / total * 100)
})

async function handleApprove(user) {
  try {
    await adminApi.approveUser(user.id)
    pendingUsers.value = pendingUsers.value.filter(u => u.id !== user.id)
    if (statistics.value.user_stats) {
      statistics.value.user_stats.pending = Math.max(0, (statistics.value.user_stats.pending || 0) - 1)
    }
    ElMessage.success(`已通过用户 ${user.real_name || user.username}`)
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '操作失败')
  }
}

async function handleReject(user) {
  try {
    await ElMessageBox.confirm(`确定拒绝用户 "${user.real_name || user.username}" 吗？`, '确认', { type: 'warning' })
    await adminApi.rejectUser(user.id)
    pendingUsers.value = pendingUsers.value.filter(u => u.id !== user.id)
    if (statistics.value.user_stats) {
      statistics.value.user_stats.pending = Math.max(0, (statistics.value.user_stats.pending || 0) - 1)
    }
    ElMessage.success(`已拒绝用户 ${user.real_name || user.username}`)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.error || '操作失败')
  }
}

async function fetchData() {
  loading.value = true
  try {
    const [statRes, userRes] = await Promise.allSettled([
      adminApi.getStatistics(),
      adminApi.getUsers({ status: 'pending' })
    ])
    if (statRes.status === 'fulfilled') {
      statistics.value = statRes.value.data || {}
    }
    if (userRes.status === 'fulfilled') {
      pendingUsers.value = userRes.value.data.users || userRes.value.data || []
    }
  } catch {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchData())
</script>

<style scoped>
.admin-dashboard { min-height: 100%; }

.page-header {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title { font-size: 20px; font-weight: 600; color: #1f2937; margin: 0; }
.page-subtitle { font-size: 14px; color: #6b7280; margin: 4px 0 0 0; }

.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 24px; }

.stat-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 24px;
  border-left: 4px solid transparent;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); }
.stat-card--blue { border-left-color: #3b82f6; }
.stat-card--green { border-left-color: #10b981; }
.stat-card--orange { border-left-color: #f59e0b; }
.stat-card--red { border-left-color: #ef4444; }

.stat-card-inner { display: flex; justify-content: space-between; align-items: center; }
.stat-info { display: flex; flex-direction: column; }
.stat-label { font-size: 14px; color: #6b7280; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; color: #1f2937; }

.stat-icon-wrap { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #fff; }
.stat-icon--blue { background: linear-gradient(135deg, #3b82f6, #60a5fa); }
.stat-icon--green { background: linear-gradient(135deg, #10b981, #34d399); }
.stat-icon--orange { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.stat-icon--red { background: linear-gradient(135deg, #ef4444, #f87171); }

.content-grid { display: grid; grid-template-columns: 1fr 360px; gap: 24px; }
.content-main, .content-side { display: flex; flex-direction: column; gap: 24px; }

.card { background: #fff; border-radius: 8px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06); padding: 24px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.card-title { font-size: 16px; font-weight: 600; color: #1f2937; }

.monthly-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.monthly-item { display: flex; align-items: center; gap: 12px; padding: 16px; background: #f9fafb; border-radius: 8px; }
.monthly-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #fff; }
.monthly-icon--blue { background: #3b82f6; }
.monthly-icon--green { background: #10b981; }
.monthly-icon--orange { background: #f59e0b; }
.monthly-icon--purple { background: #8b5cf6; }
.monthly-info { display: flex; flex-direction: column; }
.monthly-value { font-size: 20px; font-weight: 700; color: #1f2937; }
.monthly-label { font-size: 12px; color: #6b7280; }

.user-distribution { display: flex; flex-direction: column; gap: 16px; }
.dist-item { display: flex; flex-direction: column; gap: 8px; }
.dist-bar { height: 8px; background: #f3f4f6; border-radius: 4px; overflow: hidden; }
.dist-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
.dist-fill--blue { background: #3b82f6; }
.dist-fill--green { background: #10b981; }
.dist-fill--orange { background: #f59e0b; }
.dist-info { display: flex; justify-content: space-between; font-size: 13px; }
.dist-label { color: #6b7280; }
.dist-value { color: #1f2937; font-weight: 500; }

.card-body-empty { padding: 20px 0; }
.pending-list { display: flex; flex-direction: column; }
.pending-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f3f4f6; }
.pending-item:last-child { border-bottom: none; }
.pending-info { display: flex; align-items: center; gap: 12px; min-width: 0; }
.pending-avatar { background: linear-gradient(135deg, #3b82f6, #60a5fa); color: #fff; font-weight: 600; flex-shrink: 0; }
.pending-text { min-width: 0; }
.pending-name { font-size: 14px; font-weight: 500; color: #1f2937; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.pending-email { font-size: 12px; color: #9ca3af; margin: 2px 0 0 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.pending-actions { display: flex; gap: 8px; flex-shrink: 0; }
.pending-more { padding-top: 12px; text-align: center; }

.quick-actions { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: #f9fafb;
}
.quick-item:hover { background: #f3f4f6; transform: translateY(-2px); }
.quick-item span { font-size: 13px; color: #374151; }
.quick-icon { padding: 8px; border-radius: 8px; }
.quick-icon--blue { color: #3b82f6; }
.quick-icon--green { color: #10b981; }
.quick-icon--orange { color: #f59e0b; }
.quick-icon--purple { color: #8b5cf6; }
.quick-icon--red { color: #ef4444; }
.quick-icon--gray { color: #6b7280; }

@media (max-width: 1200px) {
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
  .content-grid { grid-template-columns: 1fr; }
  .monthly-stats { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .stat-grid { grid-template-columns: 1fr; }
  .monthly-stats { grid-template-columns: 1fr; }
  .quick-actions { grid-template-columns: repeat(2, 1fr); }
}
</style>
