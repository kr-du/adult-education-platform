<template>
  <div class="teacher-dashboard py-4">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold mb-1">教师工作台</h2>
          <p class="text-muted mb-0">欢迎回来，{{ userStore.user.real_name || userStore.user.username }}</p>
        </div>
        <div class="d-flex gap-2">
          <router-link to="/teacher/courses" class="btn btn-outline-primary">
            <el-icon class="me-1"><Plus /></el-icon>创建课程
          </router-link>
          <router-link to="/teacher/assignments" class="btn btn-primary">
            <el-icon class="me-1"><Edit /></el-icon>批改作业
          </router-link>
        </div>
      </div>

      <el-skeleton :loading="loading" animated :count="4">
        <template #template>
          <div class="row g-4 mb-4">
            <div v-for="i in 4" :key="i" class="col-lg-3 col-md-6">
              <el-card><el-skeleton-item variant="h1" /></el-card>
            </div>
          </div>
        </template>

        <template #default>
          <div class="row g-4 mb-4">
            <div class="col-lg-3 col-md-6" v-for="stat in stats" :key="stat.label">
              <el-card shadow="hover" class="stat-card text-center">
                <el-icon :size="40" :class="`mb-3 ${stat.iconColor}`">
                  <component :is="stat.icon" />
                </el-icon>
                <h3 class="fw-bold mb-1">{{ stat.value }}</h3>
                <p class="text-muted mb-0">{{ stat.label }}</p>
              </el-card>
            </div>
          </div>

          <div class="row g-4">
            <div class="col-lg-8">
              <el-card shadow="never">
                <template #header>
                  <div class="d-flex justify-content-between align-items-center">
                    <span class="fw-bold">最近提交的作业</span>
                    <router-link to="/teacher/assignments" class="btn btn-sm btn-outline-primary">查看全部</router-link>
                  </div>
                </template>
                <div v-if="recentSubmissions.length === 0">
                  <el-empty description="暂无提交记录" :image-size="80" />
                </div>
                <el-table v-else :data="recentSubmissions" stripe>
                  <el-table-column prop="student_name" label="学生" min-width="120" show-overflow-tooltip />
                  <el-table-column prop="assignment_title" label="作业" min-width="150" show-overflow-tooltip />
                  <el-table-column prop="course_title" label="课程" min-width="130" show-overflow-tooltip />
                  <el-table-column label="提交时间" width="160" align="center">
                    <template #default="{ row }">
                      {{ formatDate(row.submitted_at) }}
                    </template>
                  </el-table-column>
                  <el-table-column label="状态" width="100" align="center">
                    <template #default="{ row }">
                      <el-tag :type="row.score != null ? 'success' : 'warning'" size="small">
                        {{ row.score != null ? '已批改' : '待批改' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="100" align="center">
                    <template #default="{ row }">
                      <el-button v-if="row.score == null" type="primary" size="small" @click="goGrade(row)">
                        批改
                      </el-button>
                      <span v-else class="text-muted">{{ row.score }}分</span>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </div>

            <div class="col-lg-4">
              <el-card shadow="never" class="mb-4">
                <template #header>
                  <div class="d-flex justify-content-between align-items-center">
                    <span class="fw-bold">我的课程</span>
                    <router-link to="/teacher/courses" class="btn btn-sm btn-outline-primary">管理</router-link>
                  </div>
                </template>
                <div v-if="courses.length === 0">
                  <el-empty description="暂无课程" :image-size="60">
                    <router-link to="/teacher/courses" class="btn btn-primary btn-sm">创建课程</router-link>
                  </el-empty>
                </div>
                <div v-else>
                  <div
                    v-for="course in courses.slice(0, 5)"
                    :key="course.id"
                    class="d-flex justify-content-between align-items-center py-2 border-bottom"
                  >
                    <div class="min-w-0">
                      <p class="mb-0 text-truncate fw-medium">{{ course.title }}</p>
                      <small class="text-muted">{{ course.student_count || 0 }} 名学生</small>
                    </div>
                    <el-tag :type="course.status === 'published' ? 'success' : 'info'" size="small">
                      {{ course.status === 'published' ? '已发布' : '草稿' }}
                    </el-tag>
                  </div>
                </div>
              </el-card>

              <el-card shadow="never" class="mb-4">
                <template #header>
                  <span class="fw-bold">待处理事项</span>
                </template>
                <router-link to="/teacher/assignments" class="d-flex justify-content-between align-items-center py-2 border-bottom text-decoration-none text-dark">
                  <span>待批改作业</span>
                  <el-badge :value="pendingSubmissionsCount" :max="99" type="warning" />
                </router-link>
                <div class="d-flex justify-content-between align-items-center py-2">
                  <span>课程总数</span>
                  <el-badge :value="courses.length" :max="99" type="primary" />
                </div>
              </el-card>

              <el-card shadow="never">
                <template #header>
                  <span class="fw-bold">快捷操作</span>
                </template>
                <div class="d-grid gap-2">
                  <router-link to="/teacher/courses" class="btn btn-outline-primary btn-sm">
                    <el-icon class="me-1"><Reading /></el-icon>课程管理
                  </router-link>
                  <router-link to="/teacher/assignments" class="btn btn-outline-success btn-sm">
                    <el-icon class="me-1"><Edit /></el-icon>作业管理
                  </router-link>
                  <router-link to="/teacher/profile" class="btn btn-outline-info btn-sm">
                    <el-icon class="me-1"><User /></el-icon>个人中心
                  </router-link>
                </div>
              </el-card>
            </div>
          </div>
        </template>
      </el-skeleton>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { courseApi, userApi, assignmentApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Reading, User, Edit, Document, Plus } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const courses = ref([])
const recentSubmissions = ref([])
const statistics = ref({})
const allSubmissions = ref([])

const pendingSubmissionsCount = computed(() => {
  return allSubmissions.value.filter(s => s.score == null).length
})

const stats = computed(() => [
  { label: '我的课程', value: statistics.value.course_count || courses.value.length, icon: Reading, iconColor: 'text-primary' },
  { label: '学生总数', value: statistics.value.total_students || 0, icon: User, iconColor: 'text-success' },
  { label: '待批改', value: statistics.value.pending_submissions || pendingSubmissionsCount.value, icon: Edit, iconColor: 'text-warning' },
  { label: '总提交数', value: statistics.value.total_submissions || allSubmissions.value.length, icon: Document, iconColor: 'text-info' }
])

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function goGrade(submission) {
  router.push('/teacher/assignments')
}

async function fetchData() {
  loading.value = true
  courses.value = []
  statistics.value = {}
  
  // 检查用户是否登录
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    loading.value = false
    return
  }
  
  try {
    const [courseRes, statRes] = await Promise.allSettled([
      courseApi.getCourses({ teacher_id: userStore.user.id }),
      userApi.getTeacherStatistics()
    ])

    if (courseRes.status === 'fulfilled') {
      courses.value = courseRes.value.data.courses || courseRes.value.data || []
    } else {
      console.warn('获取课程失败:', courseRes.reason)
    }

    if (statRes.status === 'fulfilled') {
      statistics.value = statRes.value.data.statistics || statRes.value.data || {}
    } else {
      console.warn('获取统计信息失败:', statRes.reason)
    }

    const submissionsTemp = []
    const results = await Promise.allSettled(
      courses.value.map(c => assignmentApi.getCourseAssignments(c.id))
    )

    for (const result of results) {
      if (result.status === 'fulfilled') {
        const assignments = result.value.data.assignments || result.value.data || []
        for (const assignment of assignments) {
          try {
            const subRes = await assignmentApi.getSubmissions(assignment.id)
            const subs = subRes.data.submissions || subRes.data || []
            subs.forEach(s => {
              submissionsTemp.push({
                ...s,
                assignment_title: assignment.title,
                course_title: assignment.course_title || ''
              })
            })
          } catch {
            // skip
          }
        }
      }
    }

    allSubmissions.value = submissionsTemp
    recentSubmissions.value = submissionsTemp
      .sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at))
      .slice(0, 10)
  } catch (e) {
    console.error('获取数据失败:', e)
    ElMessage.error('获取数据失败，请刷新页面重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.stat-card {
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.min-w-0 {
  min-width: 0;
}
/* 响应式 */
@media (max-width: 992px) {
  /* 平板适配 */
  .el-table { font-size: 12px; }
}

@media (max-width: 768px) {
  /* 手机适配 */
  .page-header { flex-direction: column; gap: 12px; }
  .el-card { margin-bottom: 12px; }
  .el-table { font-size: 12px; }
  .stats-card { margin-bottom: 12px; }
  .d-flex { flex-wrap: wrap; }
  .el-dialog { width: 95% !important; }
}

@media (max-width: 576px) {
  /* 小手机适配 */
  .el-card__body { padding: 12px; }
}
</style>
