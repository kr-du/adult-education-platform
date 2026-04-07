<template>
  <div class="course-notices py-4">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold mb-0">课程公告</h2>
        <el-button type="primary" :disabled="!selectedCourse" @click="openCreateDialog">
          <el-icon class="me-1"><Plus /></el-icon>发布公告
        </el-button>
      </div>

      <div class="row mb-4">
        <div class="col-12">
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
        <div class="col-12 mt-2">
          <el-input
            v-model="searchQuery"
            placeholder="搜索公告标题..."
            :prefix-icon="Search"
            clearable
            size="large"
          />
        </div>
      </div>

      <el-skeleton :loading="loading" animated :rows="8">
        <template #default>
          <div v-if="!selectedCourse" class="text-center py-5">
            <el-empty description="请先选择课程" />
          </div>

          <div v-else-if="filteredNotices.length === 0 && !loading" class="text-center py-5">
            <el-empty description="暂无公告">
              <el-button type="primary" @click="openCreateDialog">发布第一条公告</el-button>
            </el-empty>
          </div>

          <div v-else>
            <!-- 桌面端表格 -->
            <el-table :data="paginatedNotices" stripe border class="d-none d-md-block">
              <el-table-column prop="title" label="公告标题" min-width="200" show-overflow-tooltip />
              <el-table-column label="内容预览" min-width="300">
                <template #default="{ row }">
                  <p class="mb-0 text-muted small text-truncate" style="max-width: 300px;">
                    {{ row.content }}
                  </p>
                </template>
              </el-table-column>
              <el-table-column label="发布时间" width="160" align="center">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" align="center">
                <template #default="{ row }">
                  <el-button size="small" @click="viewNotice(row)">查看</el-button>
                  <el-button size="small" type="danger" plain @click="deleteNotice(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <!-- 移动端卡片 -->
            <div class="d-md-none">
              <div v-for="item in paginatedNotices" :key="item.id" class="mb-3">
                <el-card shadow="hover">
                  <h6 class="mb-1">{{ item.title }}</h6>
                  <p class="small text-muted mb-2 text-truncate-2">{{ item.content }}</p>
                  <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">{{ formatDate(item.created_at) }}</small>
                    <div class="d-flex gap-2">
                      <el-button size="small" @click="viewNotice(item)">查看</el-button>
                      <el-button size="small" type="danger" plain @click="deleteNotice(item)">删除</el-button>
                    </div>
                  </div>
                </el-card>
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-center mt-4" v-if="filteredNotices.length > pageSize">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :total="filteredNotices.length"
              layout="total, sizes, prev, pager, next"
              background
            />
          </div>
        </template>
      </el-skeleton>
    </div>

    <el-dialog v-model="createDialogVisible" title="发布公告" width="600px" :close-on-click-modal="false">
      <el-form ref="noticeFormRef" :model="noticeForm" :rules="noticeRules" label-position="top">
        <el-form-item label="公告标题" prop="title">
          <el-input v-model="noticeForm.title" placeholder="请输入公告标题" />
        </el-form-item>
        <el-form-item label="公告内容" prop="content">
          <el-input
            v-model="noticeForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入公告内容..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreateNotice">发布</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="viewDialogVisible" :title="currentNotice?.title || '公告详情'" width="600px">
      <div v-if="currentNotice">
        <div class="text-muted small mb-3">
          <el-icon class="me-1"><Clock /></el-icon>
          发布于 {{ formatDate(currentNotice.created_at) }}
        </div>
        <div class="p-3 bg-light rounded" style="white-space: pre-wrap;">
          {{ currentNotice.content }}
        </div>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { courseApi, interactionApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Clock } from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const courses = ref([])
const notices = ref([])
const selectedCourse = ref(null)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const createDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const currentNotice = ref(null)
const submitting = ref(false)
const noticeFormRef = ref(null)

const noticeForm = ref({
  title: '',
  content: ''
})

const noticeRules = {
  title: [{ required: true, message: '请输入公告标题', trigger: 'change' }],
  content: [{ required: true, message: '请输入公告内容', trigger: 'change' }]
}

const filteredNotices = computed(() => {
  let result = [...notices.value]

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(n =>
      (n.title || '').toLowerCase().includes(q) ||
      (n.content || '').toLowerCase().includes(q)
    )
  }

  return result
})

const paginatedNotices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredNotices.value.slice(start, start + pageSize.value)
})

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function openCreateDialog() {
  noticeForm.value = { title: '', content: '' }
  createDialogVisible.value = true
}

function viewNotice(notice) {
  currentNotice.value = notice
  viewDialogVisible.value = true
}

async function handleCreateNotice() {
  const valid = await noticeFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const res = await interactionApi.createNotice({
      course_id: selectedCourse.value,
      title: noticeForm.value.title,
      content: noticeForm.value.content
    })
    const newNotice = res.data || {
      id: Date.now(),
      title: noticeForm.value.title,
      content: noticeForm.value.content,
      course_id: selectedCourse.value,
      created_at: new Date().toISOString()
    }
    notices.value.unshift(newNotice)
    createDialogVisible.value = false
    ElMessage.success('公告发布成功')
  } catch {
    ElMessage.error('发布失败')
  } finally {
    submitting.value = false
  }
}

async function deleteNotice(notice) {
  try {
    await ElMessageBox.confirm(`确定要删除公告"${notice.title}"吗？`, '警告', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await interactionApi.deleteNotice(notice.id)
    notices.value = notices.value.filter(n => n.id !== notice.id)
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handleCourseChange(courseId) {
  if (courseId) {
    fetchNotices(courseId)
  } else {
    notices.value = []
  }
}

async function fetchNotices(courseId) {
  loading.value = true
  try {
    const res = await interactionApi.getCourseNotices(courseId)
    notices.value = (res.data.notices || res.data || []).sort(
      (a, b) => new Date(b.created_at) - new Date(a.created_at)
    )
  } catch {
    ElMessage.error('获取公告列表失败')
    notices.value = []
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
      await fetchNotices(selectedCourse.value)
    }
  } catch {
    ElMessage.error('获取课程列表失败')
  }
}

onMounted(() => {
  fetchCourses()
})
</script>

<style scoped>
.min-w-0 {
  min-width: 0;
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
