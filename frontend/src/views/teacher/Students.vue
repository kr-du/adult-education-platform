<template>
  <div class="teacher-students py-4">
    <div class="container">
      <h2 class="fw-bold mb-4">学生管理</h2>

      <div class="row mb-4">
        <div class="col-lg-4 col-md-6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索学生姓名..."
            :prefix-icon="Search"
            clearable
            size="large"
          />
        </div>
        <div class="col-lg-3 col-md-6 mt-2 mt-md-0">
          <el-select v-model="courseFilter" placeholder="按课程筛选" clearable size="large" class="w-100">
            <el-option v-for="c in courses" :key="c.id" :label="c.title" :value="c.id" />
          </el-select>
        </div>
        <div class="col-lg-3 col-md-6 mt-2 mt-md-0">
          <el-select v-model="progressFilter" placeholder="学习进度" clearable size="large" class="w-100">
            <el-option label="未开始" value="not_started" />
            <el-option label="学习中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-lg-3 col-md-6">
          <el-card shadow="hover" class="text-center stat-card">
            <h3 class="fw-bold text-primary mb-1">{{ totalStudents }}</h3>
            <p class="text-muted mb-0">学生总数</p>
          </el-card>
        </div>
        <div class="col-lg-3 col-md-6">
          <el-card shadow="hover" class="text-center stat-card">
            <h3 class="fw-bold text-success mb-1">{{ completedCount }}</h3>
            <p class="text-muted mb-0">已完成</p>
          </el-card>
        </div>
        <div class="col-lg-3 col-md-6">
          <el-card shadow="hover" class="text-center stat-card">
            <h3 class="fw-bold text-warning mb-1">{{ inProgressCount }}</h3>
            <p class="text-muted mb-0">学习中</p>
          </el-card>
        </div>
        <div class="col-lg-3 col-md-6">
          <el-card shadow="hover" class="text-center stat-card">
            <h3 class="fw-bold text-info mb-1">{{ avgProgress }}%</h3>
            <p class="text-muted mb-0">平均进度</p>
          </el-card>
        </div>
      </div>

      <el-skeleton :loading="loading" animated :rows="8">
        <template #default>
          <div v-if="filteredStudents.length === 0 && !loading" class="text-center py-5">
            <el-empty description="暂无学生数据" />
          </div>

          <div v-else class="d-none d-md-block">
            <el-table :data="paginatedStudents" stripe border>
              <el-table-column label="学生信息" min-width="180">
                <template #default="{ row }">
                  <div class="d-flex align-items-center">
                    <el-avatar :size="36" class="me-2">
                      {{ (row.student_name || 'U').charAt(0) }}
                    </el-avatar>
                    <div class="min-w-0">
                      <p class="mb-0 fw-medium text-truncate">{{ row.student_name || '未知' }}</p>
                      <small class="text-muted">{{ row.student_email || '' }}</small>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="course_title" label="课程" min-width="160" show-overflow-tooltip />
              <el-table-column label="学习进度" width="180" align="center">
                <template #default="{ row }">
                  <div class="d-flex align-items-center justify-content-center">
                    <el-progress
                      :percentage="row.progress || 0"
                      :stroke-width="8"
                      :color="getProgressColor(row.progress)"
                      class="flex-grow-1 me-2"
                    />
                    <span class="small fw-medium" style="width: 35px;">{{ row.progress || 0 }}%</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.progress)" size="small">
                    {{ getStatusText(row.progress) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="平均分" width="100" align="center">
                <template #default="{ row }">
                  <span v-if="row.avg_score != null" :class="getScoreClass(row.avg_score)" class="fw-bold">
                    {{ row.avg_score }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </template>
              </el-table-column>
              <el-table-column label="完成课时" width="100" align="center">
                <template #default="{ row }">
                  {{ row.completed_lessons || 0 }} / {{ row.total_lessons || 0 }}
                </template>
              </el-table-column>
              <el-table-column label="报名时间" width="150" align="center">
                <template #default="{ row }">
                  {{ formatDate(row.enrolled_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" align="center">
                <template #default="{ row }">
                  <el-button size="small" @click="viewStudentDetail(row)">详情</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="d-md-none">
            <div v-for="student in paginatedStudents" :key="`${student.student_id}-${student.course_id}`" class="mb-3">
              <el-card shadow="hover">
                <div class="d-flex align-items-center mb-2">
                  <el-avatar :size="40" class="me-2">
                    {{ (student.student_name || 'U').charAt(0) }}
                  </el-avatar>
                  <div class="min-w-0 flex-grow-1">
                    <h6 class="mb-0 text-truncate">{{ student.student_name || '未知' }}</h6>
                    <small class="text-muted">{{ student.course_title }}</small>
                  </div>
                  <el-tag :type="getStatusType(student.progress)" size="small">
                    {{ getStatusText(student.progress) }}
                  </el-tag>
                </div>
                <div class="mb-2">
                  <div class="d-flex justify-content-between mb-1">
                    <small class="text-muted">学习进度</small>
                    <small class="fw-medium">{{ student.progress || 0 }}%</small>
                  </div>
                  <el-progress :percentage="student.progress || 0" :stroke-width="6" :color="getProgressColor(student.progress)" />
                </div>
                <div class="d-flex justify-content-between text-muted small mb-2">
                  <span>完成 {{ student.completed_lessons || 0 }}/{{ student.total_lessons || 0 }} 课时</span>
                  <span v-if="student.avg_score != null" :class="getScoreClass(student.avg_score)" class="fw-bold">
                    平均 {{ student.avg_score }} 分
                  </span>
                </div>
                <div class="text-end">
                  <el-button size="small" type="primary" @click="viewStudentDetail(student)">查看详情</el-button>
                </div>
              </el-card>
            </div>
          </div>

          <div class="d-flex justify-content-center mt-4" v-if="filteredStudents.length > pageSize">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :total="filteredStudents.length"
              layout="total, sizes, prev, pager, next"
              background
            />
          </div>
        </template>
      </el-skeleton>
    </div>

    <el-dialog v-model="detailDialogVisible" title="学生详情" width="700px">
      <div v-if="currentStudent">
        <div class="d-flex align-items-center mb-4">
          <el-avatar :size="64" class="me-3">
            {{ (currentStudent.student_name || 'U').charAt(0) }}
          </el-avatar>
          <div>
            <h5 class="fw-bold mb-1">{{ currentStudent.student_name }}</h5>
            <p class="text-muted mb-0">{{ currentStudent.student_email || '' }}</p>
          </div>
        </div>

        <el-divider />

        <div class="row g-3 mb-4">
          <div class="col-4 text-center">
            <h4 class="fw-bold text-primary mb-0">{{ currentStudent.progress || 0 }}%</h4>
            <small class="text-muted">学习进度</small>
          </div>
          <div class="col-4 text-center">
            <h4 class="fw-bold text-success mb-0">{{ currentStudent.completed_lessons || 0 }}</h4>
            <small class="text-muted">完成课时</small>
          </div>
          <div class="col-4 text-center">
            <h4 class="fw-bold mb-0" :class="getScoreClass(currentStudent.avg_score)">
              {{ currentStudent.avg_score ?? '-' }}
            </h4>
            <small class="text-muted">平均分</small>
          </div>
        </div>

        <h6 class="fw-bold mb-3">成绩详情</h6>
        <div v-if="studentGrades.length === 0">
          <p class="text-muted text-center">暂无成绩记录</p>
        </div>
        <el-table v-else :data="studentGrades" stripe size="small">
          <el-table-column prop="assignment_title" label="作业" min-width="150" show-overflow-tooltip />
          <el-table-column label="分数" width="100" align="center">
            <template #default="{ row }">
              <span :class="getScoreClass(row.score)">{{ row.score ?? '-' }} / {{ row.max_score || 100 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="feedback" label="评语" min-width="150" show-overflow-tooltip />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { courseApi, userApi, assignmentApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const userStore = useUserStore()

const loading = ref(true)
const students = ref([])
const courses = ref([])
const searchQuery = ref('')
const courseFilter = ref('')
const progressFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const detailDialogVisible = ref(false)
const currentStudent = ref(null)
const studentGrades = ref([])

const totalStudents = computed(() => {
  const unique = new Set(students.value.map(s => s.student_id))
  return unique.size
})

const completedCount = computed(() => {
  return students.value.filter(s => (s.progress || 0) >= 100).length
})

const inProgressCount = computed(() => {
  return students.value.filter(s => (s.progress || 0) > 0 && (s.progress || 0) < 100).length
})

const avgProgress = computed(() => {
  if (students.value.length === 0) return 0
  const total = students.value.reduce((sum, s) => sum + (s.progress || 0), 0)
  return Math.round(total / students.value.length)
})

const filteredStudents = computed(() => {
  let result = [...students.value]

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(s =>
      (s.student_name || '').toLowerCase().includes(q) ||
      (s.student_email || '').toLowerCase().includes(q)
    )
  }

  if (courseFilter.value) {
    result = result.filter(s => s.course_id === courseFilter.value)
  }

  if (progressFilter.value) {
    result = result.filter(s => {
      const p = s.progress || 0
      if (progressFilter.value === 'not_started') return p === 0
      if (progressFilter.value === 'in_progress') return p > 0 && p < 100
      if (progressFilter.value === 'completed') return p >= 100
      return true
    })
  }

  return result
})

const paginatedStudents = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredStudents.value.slice(start, start + pageSize.value)
})

function getProgressColor(progress) {
  if (progress >= 100) return '#67c23a'
  if (progress >= 50) return '#409eff'
  if (progress > 0) return '#e6a23c'
  return '#909399'
}

function getStatusText(progress) {
  if (!progress || progress === 0) return '未开始'
  if (progress >= 100) return '已完成'
  return '学习中'
}

function getStatusType(progress) {
  if (!progress || progress === 0) return 'info'
  if (progress >= 100) return 'success'
  return 'warning'
}

function getScoreClass(score) {
  if (score == null) return ''
  if (score >= 90) return 'text-success'
  if (score >= 60) return 'text-primary'
  return 'text-danger'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

async function viewStudentDetail(student) {
  currentStudent.value = student
  detailDialogVisible.value = true
  studentGrades.value = []

  try {
    const res = await userApi.getGrades()
    const allGrades = res.data.grades || res.data || []
    studentGrades.value = allGrades.filter(g =>
      g.student_id === student.student_id && g.course_id === student.course_id
    )
  } catch {
    // ignore
  }
}

async function fetchData() {
  loading.value = true
  students.value = []
  courses.value = []
  
  // 检查用户是否登录
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    loading.value = false
    return
  }
  
  try {
    const [courseRes, studentRes] = await Promise.allSettled([
      courseApi.getCourses({ teacher_id: userStore.user.id }),
      userApi.getTeacherStudents()
    ])

    if (courseRes.status === 'fulfilled') {
      courses.value = courseRes.value.data.courses || courseRes.value.data || []
    } else {
      console.warn('获取课程失败:', courseRes.reason)
    }

    if (studentRes.status === 'fulfilled') {
      const responseData = studentRes.value.data
      students.value = responseData.students || responseData || []
    } else {
      console.warn('获取学生列表失败:', studentRes.reason)
      // 使用fallback逻辑
      const allStudents = []
      const results = await Promise.allSettled(
        courses.value.map(c => {
          return courseApi.getCourse(c.id).then(res => {
            const course = res.data.course || res.data || {}
            return { course, courseId: c.id }
          })
        })
      )
      for (const result of results) {
        if (result.status === 'fulfilled') {
          const { course } = result.value
          if (course.enrollments) {
            course.enrollments.forEach(e => {
              // 适配不同的字段名
              const studentName = e.student_name || e.user_name || e.real_name || e.name || e.user?.real_name || e.user?.username || '未知'
              const studentEmail = e.student_email || e.user_email || e.email || e.user?.email || ''
              allStudents.push({
                student_id: e.student_id || e.user_id || e.id,
                student_name: studentName,
                student_email: studentEmail,
                course_id: course.id,
                course_title: course.title,
                progress: e.progress || 0,
                enrolled_at: e.enrolled_at || e.created_at,
                completed_lessons: e.completed_lessons || 0,
                total_lessons: course.lessons?.length || 0,
                avg_score: e.avg_score
              })
            })
          }
        }
      }
      students.value = allStudents
    }
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
  .el-card { margin-bottom: 12px; }
  .stat-card { margin-bottom: 12px; }
}

@media (max-width: 768px) {
  /* 手机适配 */
  .teacher-students { padding: 12px 0 !important; }
  .teacher-students h2 { font-size: 20px; margin-bottom: 16px !important; }
  
  .el-card { margin-bottom: 12px; }
  .el-table { display: none; }
  .d-flex { flex-wrap: wrap; }
  .el-dialog { width: 95% !important; margin: 10vh auto !important; }
  .stat-card { margin-bottom: 12px; }
  
  /* 筛选条件全宽 */
  .row.mb-4 .col-lg-4,
  .row.mb-4 .col-lg-3 { width: 100%; margin-bottom: 8px; }
  
  /* 统计卡片两列布局 */
  .row.g-4.mb-4 .col-lg-3 { width: 50%; }
  .stat-card h3 { font-size: 18px; }
  .stat-card p { font-size: 12px; }
  
  /* 分页适配 */
  .el-pagination { justify-content: center; flex-wrap: wrap; gap: 8px; }
  .el-pagination__total, .el-pagination__jump { display: none; }
}

@media (max-width: 576px) {
  /* 小手机适配 */
  .el-card__body { padding: 12px; }
  .stat-card h3 { font-size: 16px; }
  .stat-card p { font-size: 11px; }
}
</style>
