<template>
  <div class="teacher-courses py-4">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold mb-0">课程管理</h2>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon class="me-1"><Plus /></el-icon>创建课程
        </el-button>
      </div>

      <div class="row mb-4">
        <div class="col-lg-4 col-md-6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索课程..."
            :prefix-icon="Search"
            clearable
            size="large"
          />
        </div>
        <div class="col-lg-3 col-md-6 mt-2 mt-md-0">
          <el-select v-model="statusFilter" placeholder="课程状态" clearable size="large" class="w-100">
            <el-option label="已发布" value="published" />
            <el-option label="草稿" value="draft" />
          </el-select>
        </div>
        <div class="col-lg-3 col-md-6 mt-2 mt-md-0">
          <el-select v-model="categoryFilter" placeholder="课程分类" clearable size="large" class="w-100">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </div>
      </div>

      <el-skeleton :loading="loading" animated :count="6">
        <template #template>
          <div class="row g-4">
            <div v-for="i in 6" :key="i" class="col-lg-4 col-md-6">
              <el-card><el-skeleton-item variant="image" style="height:140px;" /><div class="mt-2"><el-skeleton-item variant="h3" /></div></el-card>
            </div>
          </div>
        </template>

        <template #default>
          <div v-if="filteredCourses.length === 0 && !loading" class="text-center py-5">
            <el-empty description="暂无课程">
              <el-button type="primary" @click="openCreateDialog">创建第一个课程</el-button>
            </el-empty>
          </div>

          <div class="row g-4">
            <div v-for="course in paginatedCourses" :key="course.id" class="col-lg-4 col-md-6">
              <el-card shadow="hover" class="h-100 course-card" :body-style="{ padding: '0' }">
                <div class="course-cover position-relative" style="height: 140px;">
                  <img v-if="course.cover_image" :src="course.cover_image" class="w-100 h-100" style="object-fit: cover;" />
                  <div v-else class="bg-gradient d-flex align-items-center justify-content-center w-100 h-100">
                    <el-icon :size="48" class="text-white-50"><Reading /></el-icon>
                  </div>
                  <el-tag
                    class="position-absolute top-0 end-0 m-2"
                    :type="course.status === 'published' ? 'success' : 'info'"
                    size="small"
                  >
                    {{ course.status === 'published' ? '已发布' : '草稿' }}
                  </el-tag>
                </div>

                <div class="p-3">
                  <h6 class="fw-bold mb-2 text-truncate" :title="course.title">{{ course.title }}</h6>
                  <p class="text-muted small mb-2" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                    {{ course.description || '暂无描述' }}
                  </p>

                  <div class="d-flex justify-content-between text-muted small mb-3">
                    <span><el-icon class="me-1"><User /></el-icon>{{ course.student_count || 0 }} 名学生</span>
                    <span><el-icon class="me-1"><Clock /></el-icon>{{ course.lesson_count || 0 }} 课时</span>
                  </div>

                  <div class="d-flex gap-2">
                    <router-link :to="`/teacher/course/${course.id}/edit`" class="btn btn-outline-primary btn-sm flex-grow-1">
                      编辑
                    </router-link>
                    <el-dropdown trigger="click" @command="handleCommand($event, course)">
                      <el-button size="small">
                        更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="students">
                            <el-icon class="me-1"><User /></el-icon>学生管理
                          </el-dropdown-item>
                          <el-dropdown-item command="questions">
                            <el-icon class="me-1"><ChatDotRound /></el-icon>答疑管理
                          </el-dropdown-item>
                          <el-dropdown-item command="notices">
                            <el-icon class="me-1"><Bell /></el-icon>公告管理
                          </el-dropdown-item>
                          <el-dropdown-item command="toggle-status" divided>
                            {{ course.status === 'published' ? '设为草稿' : '发布课程' }}
                          </el-dropdown-item>
                          <el-dropdown-item command="delete">
                            <span class="text-danger">删除课程</span>
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>
              </el-card>
            </div>
          </div>

          <div class="d-flex justify-content-center mt-4" v-if="filteredCourses.length > pageSize">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[9, 18, 36]"
              :total="filteredCourses.length"
              layout="total, sizes, prev, pager, next"
              background
            />
          </div>
        </template>
      </el-skeleton>
    </div>

    <el-dialog v-model="createDialogVisible" :title="editingCourse ? '编辑课程' : '创建课程'" width="600px" :close-on-click-modal="false">
      <el-form ref="courseFormRef" :model="courseForm" :rules="courseRules" label-position="top">
        <el-form-item label="课程名称" prop="title">
          <el-input v-model="courseForm.title" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="课程描述" prop="description">
          <el-input v-model="courseForm.description" type="textarea" :rows="4" placeholder="请输入课程描述" />
        </el-form-item>
        <div class="row">
          <div class="col-md-6">
            <el-form-item label="课程分类">
              <el-select v-model="courseForm.category_id" placeholder="选择分类" clearable class="w-100">
                <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
              </el-select>
            </el-form-item>
          </div>
          <div class="col-md-6">
            <el-form-item label="课程状态">
              <el-select v-model="courseForm.status" class="w-100">
                <el-option label="草稿" value="draft" />
                <el-option label="已发布" value="published" />
              </el-select>
            </el-form-item>
          </div>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmitCourse">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { courseApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Reading, User, Clock, ArrowDown, ChatDotRound, Bell } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const courses = ref([])
const categories = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const categoryFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(9)

const createDialogVisible = ref(false)
const editingCourse = ref(null)
const submitting = ref(false)
const courseFormRef = ref(null)

const courseForm = ref({
  title: '',
  description: '',
  category_id: null,
  status: 'draft'
})

const courseRules = {
  title: [{ required: true, message: '请输入课程名称', trigger: 'change' }]
}

const filteredCourses = computed(() => {
  let result = [...courses.value]

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(c => c.title.toLowerCase().includes(q))
  }

  if (statusFilter.value) {
    result = result.filter(c => c.status === statusFilter.value)
  }

  if (categoryFilter.value) {
    result = result.filter(c => c.category_id === categoryFilter.value)
  }

  return result
})

const paginatedCourses = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredCourses.value.slice(start, start + pageSize.value)
})

function openCreateDialog() {
  editingCourse.value = null
  courseForm.value = { title: '', description: '', category_id: null, status: 'draft' }
  createDialogVisible.value = true
}

function handleCommand(command, course) {
  if (command === 'toggle-status') {
    toggleStatus(course)
  } else if (command === 'delete') {
    deleteCourse(course)
  } else if (command === 'students') {
    router.push(`/teacher/course/${course.id}/students`)
  } else if (command === 'questions') {
    router.push(`/teacher/course/${course.id}/questions`)
  } else if (command === 'notices') {
    router.push(`/teacher/course/${course.id}/notices`)
  }
}

async function toggleStatus(course) {
  const newStatus = course.status === 'published' ? 'draft' : 'published'
  const label = newStatus === 'published' ? '发布' : '设为草稿'
  try {
    await ElMessageBox.confirm(`确定要${label}该课程吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await courseApi.updateCourse(course.id, { status: newStatus })
    course.status = newStatus
    ElMessage.success(`${label}成功`)
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(`${label}失败`)
    }
  }
}

async function deleteCourse(course) {
  try {
    await ElMessageBox.confirm(`确定要删除课程"${course.title}"吗？此操作不可恢复。`, '警告', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'error'
    })
    await courseApi.updateCourse(course.id, { status: 'deleted' })
    courses.value = courses.value.filter(c => c.id !== course.id)
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function handleSubmitCourse() {
  const valid = await courseFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editingCourse.value) {
      await courseApi.updateCourse(editingCourse.value.id, courseForm.value)
      ElMessage.success('更新成功')
    } else {
      await courseApi.createCourse(courseForm.value)
      ElMessage.success('创建成功')
    }
    createDialogVisible.value = false
    await fetchCourses()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function fetchCourses() {
  loading.value = true
  try {
    const [courseRes, catRes] = await Promise.allSettled([
      courseApi.getCourses({ teacher_id: userStore.user.id }),
      courseApi.getCategories()
    ])

    if (courseRes.status === 'fulfilled') {
      courses.value = courseRes.value.data.courses || courseRes.value.data || []
    }
    if (catRes.status === 'fulfilled') {
      categories.value = catRes.value.data.categories || catRes.value.data || []
    }
  } catch (e) {
    ElMessage.error('获取课程列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCourses()
})
</script>

<style scoped>
.course-card {
  transition: transform 0.3s, box-shadow 0.3s;
}

.course-card:hover {
  transform: translateY(-4px);
}

.bg-gradient {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}
/* 响应式 */
@media (max-width: 992px) {
  /* 平板适配 */
  .el-table { font-size: 12px; }
  .el-card { margin-bottom: 12px; }
}

@media (max-width: 768px) {
  /* 手机适配 */
  .el-card { margin-bottom: 12px; }
  .el-table { font-size: 12px; }
  .d-flex { flex-wrap: wrap; }
  .el-dialog { width: 95% !important; }
}

@media (max-width: 576px) {
  /* 小手机适配 */
  .el-card__body { padding: 12px; }
}
</style>
