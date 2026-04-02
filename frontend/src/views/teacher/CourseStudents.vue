<template>
  <div class="course-students py-4">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold mb-0">课程学生</h2>
      </div>

      <div class="row mb-4">
        <div class="col-lg-4 col-md-6">
          <el-select
            v-model="selectedCourse"
            placeholder="选择课程"
            size="large"
            class="w-100"
            filterable
            @change="handleCourseChange"
          >
            <el-option
              v-for="course in courses"
              :key="course.id"
              :label="course.title"
              :value="course.id"
            />
          </el-select>
        </div>
        <div class="col-lg-3 col-md-6 mt-2 mt-md-0">
          <el-input
            v-model="searchQuery"
            placeholder="搜索学生姓名..."
            :prefix-icon="Search"
            clearable
            size="large"
          />
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
          <div v-if="!selectedCourse" class="text-center py-5">
            <el-empty description="请先选择课程" />
          </div>

          <div v-else-if="filteredStudents.length === 0 && !loading" class="text-center py-5">
            <el-empty description="暂无学生报名此课程" />
          </div>

          <div v-else>
            <el-table :data="paginatedStudents" stripe border>
              <el-table-column label="学生信息" min-width="200">
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
              <el-table-column label="学习进度" width="220" align="center">
                <template #default="{ row }">
                  <div class="d-flex align-items-center justify-content-center">
                    <el-progress
                      :percentage="row.progress || 0"
                      :stroke-width="10"
                      :color="getProgressColor(row.progress)"
                      class="flex-grow-1 me-2"
                    />
                    <span class="small fw-medium" style="width: 40px;">{{ row.progress || 0 }}%</span>
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
              <el-table-column label="报名时间" width="150" align="center">
                <template #default="{ row }">
                  {{ formatDate(row.enrolled_at) }}
                </template>
              </el-table-column>
              <el-table-column label="完成课时" width="110" align="center">
                <template #default="{ row }">
                  {{ row.completed_lessons || 0 }} / {{ row.total_lessons || 0 }}
                </template>
              </el-table-column>
            </el-table>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { courseApi, interactionApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const courses = ref([])
const students = ref([])
const selectedCourse = ref(null)
const searchQuery = ref('')
const progressFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const totalStudents = computed(() => students.value.length)

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

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function handleCourseChange(courseId) {
  if (courseId) {
    fetchStudents(courseId)
  } else {
    students.value = []
  }
}

async function fetchStudents(courseId) {
  loading.value = true
  try {
    const res = await interactionApi.getCourseStudents(courseId)
    students.value = res.data.students || res.data || []
  } catch (e) {
    ElMessage.error('获取学生列表失败')
    students.value = []
  } finally {
    loading.value = false
  }
}

async function fetchCourses() {
  try {
    const res = await courseApi.getCourses({ teacher_id: userStore.user.id })
    courses.value = res.data.courses || res.data || []

    if (route.params.id) {
      selectedCourse.value = Number(route.params.id)
      await fetchStudents(selectedCourse.value)
    }
  } catch (e) {
    ElMessage.error('获取课程列表失败')
  }
}

onMounted(() => {
  fetchCourses()
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
</style>
