<template>
  <div class="teacher-assignments py-4">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold mb-0">作业管理</h2>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon class="me-1"><Plus /></el-icon>创建作业
        </el-button>
      </div>

      <div class="row mb-4">
        <div class="col-lg-4 col-md-6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索作业..."
            :prefix-icon="Search"
            clearable
            size="large"
          />
        </div>
        <div class="col-lg-3 col-md-6 mt-2 mt-md-0">
          <el-select v-model="courseFilter" placeholder="所属课程" clearable size="large" class="w-100">
            <el-option v-for="c in courses" :key="c.id" :label="c.title" :value="c.id" />
          </el-select>
        </div>
        <div class="col-lg-3 col-md-6 mt-2 mt-md-0">
          <el-select v-model="statusFilter" placeholder="状态" clearable size="large" class="w-100">
            <el-option label="已过期" value="expired" />
            <el-option label="进行中" value="active" />
          </el-select>
        </div>
      </div>

      <el-skeleton :loading="loading" animated :rows="6">
        <template #default>
          <div v-if="filteredAssignments.length === 0 && !loading" class="text-center py-5">
            <el-empty description="暂无作业">
              <el-button type="primary" @click="openCreateDialog">创建第一个作业</el-button>
            </el-empty>
          </div>

          <el-table v-else :data="paginatedAssignments" stripe border>
            <el-table-column label="作业名称" min-width="220" show-overflow-tooltip>
              <template #default="{ row }">
                <div>
                  <span class="fw-medium">{{ row.title }}</span>
                </div>
                <small class="text-muted">{{ row.course_title || getCourseName(row.course_id) }}</small>
              </template>
            </el-table-column>
            <el-table-column label="所属课程" width="160" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.course_title || getCourseName(row.course_id) }}
              </template>
            </el-table-column>
            <el-table-column label="截止时间" width="170" align="center">
              <template #default="{ row }">
                <span :class="{ 'text-danger': isExpired(row.due_date) }">
                  {{ formatDate(row.due_date) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="满分" width="80" align="center">
              <template #default="{ row }">
                {{ row.max_score || 100 }}
              </template>
            </el-table-column>
            <el-table-column label="提交数" width="90" align="center">
              <template #default="{ row }">
                <el-badge :value="row.submission_count || 0" :max="99" type="primary" />
              </template>
            </el-table-column>
            <el-table-column label="待批改" width="90" align="center">
              <template #default="{ row }">
                <el-badge :value="row.pending_count || 0" :max="99" :type="row.pending_count > 0 ? 'warning' : 'info'" />
              </template>
            </el-table-column>
            <el-table-column label="状态" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="isExpired(row.due_date) ? 'info' : 'success'" size="small">
                  {{ isExpired(row.due_date) ? '已过期' : '进行中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" align="center">
              <template #default="{ row }">
                <el-button size="small" @click="viewSubmissions(row)">查看提交</el-button>
                <el-button size="small" type="primary" plain @click="openEditDialog(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" type="danger" plain @click="deleteAssignment(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="d-flex justify-content-center mt-4" v-if="filteredAssignments.length > pageSize">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :total="filteredAssignments.length"
              layout="total, sizes, prev, pager, next"
              background
            />
          </div>
        </template>
      </el-skeleton>
    </div>

    <!-- Create / Edit Assignment Dialog -->
    <el-dialog v-model="createDialogVisible" :title="editingAssignment ? '编辑作业' : '创建作业'" width="650px" :close-on-click-modal="false">
      <el-form ref="assignmentFormRef" :model="assignmentForm" :rules="assignmentRules" label-position="top">
        <el-form-item label="作业名称" prop="title">
          <el-input v-model="assignmentForm.title" placeholder="请输入作业名称" />
        </el-form-item>
        <el-form-item label="所属课程" prop="course_id">
          <el-select v-model="assignmentForm.course_id" placeholder="选择课程" class="w-100">
            <el-option v-for="c in courses" :key="c.id" :label="c.title" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="作业描述">
          <el-input v-model="assignmentForm.description" type="textarea" :rows="4" placeholder="作业要求说明" />
        </el-form-item>
        <div class="row">
          <div class="col-md-6">
            <el-form-item label="截止时间">
              <el-date-picker v-model="assignmentForm.due_date" type="datetime" placeholder="选择截止时间" class="w-100" value-format="YYYY-MM-DD HH:mm:ss" />
            </el-form-item>
          </div>
          <div class="col-md-6">
            <el-form-item label="满分">
              <el-input-number v-model="assignmentForm.max_score" :min="1" :max="1000" class="w-100" />
            </el-form-item>
          </div>
        </div>
        <el-form-item label="附件上传">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="3"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :file-list="fileList"
            accept=".pdf,.doc,.docx,.zip,.rar,.png,.jpg,.jpeg"
          >
            <el-button type="primary" plain>
              <el-icon class="me-1"><Upload /></el-icon>选择文件
            </el-button>
            <template #tip>
              <div class="text-muted small mt-1">支持 PDF、Word、ZIP、图片，最多 3 个文件</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmitAssignment">确认</el-button>
      </template>
    </el-dialog>

    <!-- Submissions Dialog -->
    <el-dialog v-model="submissionsDialogVisible" title="提交记录" width="900px" :close-on-click-modal="false">
      <div v-if="currentAssignment">
        <h6 class="fw-bold mb-3">{{ currentAssignment.title }} - 提交列表</h6>
        <div class="mb-3">
          <el-select v-model="submissionFilter" placeholder="筛选状态" clearable size="small">
            <el-option label="待批改" value="pending" />
            <el-option label="已批改" value="graded" />
          </el-select>
        </div>

        <el-skeleton :loading="submissionsLoading" animated :rows="5">
          <template #default>
            <div v-if="filteredSubmissions.length === 0" class="text-center py-4">
              <el-empty description="暂无提交记录" :image-size="60" />
            </div>
            <el-table v-else :data="filteredSubmissions" stripe>
              <el-table-column prop="student_name" label="学生" width="120" show-overflow-tooltip />
              <el-table-column label="提交时间" width="170" align="center">
                <template #default="{ row }">
                  {{ formatDate(row.submitted_at) }}
                </template>
              </el-table-column>
              <el-table-column label="内容" min-width="200" show-overflow-tooltip>
                <template #default="{ row }">
                  {{ row.content || '无文本内容' }}
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.score != null ? 'success' : 'warning'" size="small">
                    {{ row.score != null ? '已批改' : '待批改' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="分数" width="100" align="center">
                <template #default="{ row }">
                  <span v-if="row.score != null" class="fw-bold">{{ row.score }}</span>
                  <span v-else class="text-muted">-</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" align="center">
                <template #default="{ row }">
                  <el-button
                    :type="row.score != null ? 'info' : 'primary'"
                    size="small"
                    @click="openGradeDialog(row)"
                  >
                    {{ row.score != null ? '重新批改' : '批改' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </template>
        </el-skeleton>
      </div>
      <template #footer>
        <el-button @click="submissionsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- Grade Submission Dialog -->
    <el-dialog v-model="gradeDialogVisible" title="批改作业" width="600px" :close-on-click-modal="false">
      <div v-if="currentSubmission">
        <div class="mb-3 p-3 bg-light rounded">
          <p class="fw-medium mb-1">学生: {{ currentSubmission.student_name }}</p>
          <p class="text-muted small mb-2">提交时间: {{ formatDate(currentSubmission.submitted_at) }}</p>
          <el-divider />
          <p class="fw-medium mb-1">提交内容:</p>
          <p class="text-muted" style="white-space: pre-wrap;">{{ currentSubmission.content || '无内容' }}</p>
        </div>

        <el-form ref="gradeFormRef" :model="gradeForm" :rules="gradeRules" label-position="top">
          <el-form-item label="分数" prop="score">
            <el-input-number
              v-model="gradeForm.score"
              :min="0"
              :max="currentAssignment?.max_score || 100"
              class="w-100"
            />
            <small class="text-muted">满分: {{ currentAssignment?.max_score || 100 }}</small>
          </el-form-item>
          <el-form-item label="评语">
            <el-input v-model="gradeForm.feedback" type="textarea" :rows="4" placeholder="请输入评语" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="gradeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="grading" @click="handleGrade">提交批改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { assignmentApi, courseApi, uploadApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search, Upload } from '@element-plus/icons-vue'

const userStore = useUserStore()

const loading = ref(true)
const courses = ref([])
const assignments = ref([])
const searchQuery = ref('')
const courseFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const createDialogVisible = ref(false)
const editingAssignment = ref(null)
const submitting = ref(false)
const assignmentFormRef = ref(null)
const uploadRef = ref(null)
const fileList = ref([])
const pendingFiles = ref([])

const assignmentForm = ref({
  title: '',
  description: '',
  course_id: null,
  due_date: null,
  max_score: 100,
  attachment_url: ''
})

const assignmentRules = {
  title: [{ required: true, message: '请输入作业名称', trigger: 'change' }],
  course_id: [{ required: true, message: '请选择所属课程', trigger: 'change' }]
}

const submissionsDialogVisible = ref(false)
const submissionsLoading = ref(false)
const currentAssignment = ref(null)
const submissions = ref([])
const submissionFilter = ref('')

const gradeDialogVisible = ref(false)
const currentSubmission = ref(null)
const grading = ref(false)
const gradeFormRef = ref(null)
const gradeForm = ref({
  score: 0,
  feedback: ''
})

const gradeRules = {
  score: [{ required: true, message: '请输入分数', trigger: 'change' }]
}

const filteredAssignments = computed(() => {
  let result = [...assignments.value]

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(a =>
      a.title.toLowerCase().includes(q) ||
      (a.course_title || '').toLowerCase().includes(q)
    )
  }

  if (courseFilter.value) {
    result = result.filter(a => a.course_id === courseFilter.value)
  }

  if (statusFilter.value) {
    if (statusFilter.value === 'expired') {
      result = result.filter(a => isExpired(a.due_date))
    } else if (statusFilter.value === 'active') {
      result = result.filter(a => !isExpired(a.due_date))
    }
  }

  return result
})

const paginatedAssignments = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredAssignments.value.slice(start, start + pageSize.value)
})

const filteredSubmissions = computed(() => {
  let result = [...submissions.value]
  if (submissionFilter.value === 'pending') {
    result = result.filter(s => s.score == null)
  } else if (submissionFilter.value === 'graded') {
    result = result.filter(s => s.score != null)
  }
  return result
})

function getCourseName(courseId) {
  const course = courses.value.find(c => c.id === courseId)
  return course?.title || '未知课程'
}

function formatDate(dateStr) {
  if (!dateStr) return '未设置'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function isExpired(dateStr) {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}

function openCreateDialog() {
  editingAssignment.value = null
  assignmentForm.value = { title: '', description: '', course_id: null, due_date: null, max_score: 100, attachment_url: '' }
  fileList.value = []
  pendingFiles.value = []
  createDialogVisible.value = true
}

function openEditDialog(assignment) {
  editingAssignment.value = assignment
  assignmentForm.value = {
    title: assignment.title,
    description: assignment.description || '',
    course_id: assignment.course_id,
    due_date: assignment.due_date || null,
    max_score: assignment.max_score || 100,
    attachment_url: assignment.attachment_url || ''
  }
  fileList.value = []
  pendingFiles.value = []
  createDialogVisible.value = true
}

function handleFileChange(file, fileLst) {
  fileList.value = fileLst
  pendingFiles.value = fileLst
}

function handleFileRemove(file, fileLst) {
  fileList.value = fileLst
  pendingFiles.value = fileLst
}

async function uploadAttachments() {
  if (pendingFiles.value.length === 0) return ''
  const urls = []
  for (const file of pendingFiles.value) {
    const formData = new FormData()
    formData.append('file', file.raw)
    try {
      const res = await uploadApi.uploadCourseImage(formData)
      const url = res.data?.url || res.data?.path || ''
      if (url) urls.push(url)
    } catch (e) {
      ElMessage.warning(`文件 "${file.name}" 上传失败`)
    }
  }
  return urls.join(',')
}

async function handleSubmitAssignment() {
  const valid = await assignmentFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const attachmentUrls = await uploadAttachments()
    const payload = { ...assignmentForm.value }
    if (attachmentUrls) payload.attachment_url = attachmentUrls

    // 处理日期格式
    if (payload.due_date) {
      if (payload.due_date instanceof Date) {
        payload.due_date = payload.due_date.toISOString()
      } else if (typeof payload.due_date === 'string' && !payload.due_date.includes('T')) {
        // 如果是 YYYY-MM-DD HH:mm:ss 格式，转换为 ISO 格式
        payload.due_date = payload.due_date.replace(' ', 'T')
      }
    }

    if (editingAssignment.value) {
      await assignmentApi.updateAssignment(editingAssignment.value.id, payload)
      ElMessage.success('更新成功')
    } else {
      await assignmentApi.createAssignment(payload)
      ElMessage.success('创建成功')
    }
    createDialogVisible.value = false
    await fetchAssignments()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function deleteAssignment(assignment) {
  try {
    await ElMessageBox.confirm(`确定要删除作业"${assignment.title}"吗？删除后相关提交记录也会丢失。`, '警告', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'error'
    })
    await assignmentApi.deleteAssignment(assignment.id)
    assignments.value = assignments.value.filter(a => a.id !== assignment.id)
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.error || '删除失败')
    }
  }
}

async function viewSubmissions(assignment) {
  currentAssignment.value = assignment
  submissionsDialogVisible.value = true
  submissionsLoading.value = true
  submissionFilter.value = ''

  try {
    const res = await assignmentApi.getSubmissions(assignment.id)
    submissions.value = res.data.submissions || res.data || []
  } catch (e) {
    ElMessage.error('获取提交记录失败')
    submissions.value = []
  } finally {
    submissionsLoading.value = false
  }
}

function openGradeDialog(submission) {
  currentSubmission.value = submission
  gradeForm.value = {
    score: submission.score ?? 0,
    feedback: submission.feedback || ''
  }
  gradeDialogVisible.value = true
}

async function handleGrade() {
  const valid = await gradeFormRef.value.validate().catch(() => false)
  if (!valid) return

  grading.value = true
  try {
    await assignmentApi.gradeSubmission(currentSubmission.value.id, gradeForm.value)
    currentSubmission.value.score = gradeForm.value.score
    currentSubmission.value.feedback = gradeForm.value.feedback
    ElMessage.success('批改成功')
    gradeDialogVisible.value = false

    const idx = submissions.value.findIndex(s => s.id === currentSubmission.value.id)
    if (idx !== -1) {
      submissions.value[idx] = { ...submissions.value[idx], ...gradeForm.value }
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '批改失败')
  } finally {
    grading.value = false
  }
}

async function fetchAssignments() {
  loading.value = true
  try {
    const courseRes = await courseApi.getCourses({ teacher_id: userStore.user.id })
    courses.value = courseRes.data.courses || courseRes.data || []

    let assignmentList = []
    try {
      const assignRes = await assignmentApi.getTeacherAssignments()
      assignmentList = assignRes.data.assignments || assignRes.data || []
    } catch {
      const results = await Promise.allSettled(
        courses.value.map(c => assignmentApi.getCourseAssignments(c.id))
      )
      results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          const courseAssignments = result.value.data.assignments || result.value.data || []
          courseAssignments.forEach(a => {
            assignmentList.push({
              ...a,
              course_title: a.course_title || courses.value[index]?.title || ''
            })
          })
        }
      })
    }

    assignments.value = assignmentList.map(a => ({
      ...a,
      course_title: a.course_title || getCourseName(a.course_id)
    }))
  } catch (e) {
    ElMessage.error('获取作业列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAssignments()
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
