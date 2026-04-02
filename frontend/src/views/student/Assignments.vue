<template>
  <div class="student-assignments py-4">
    <div class="container">
      <h2 class="fw-bold mb-4">
        <el-icon class="me-2"><Document /></el-icon>我的作业
      </h2>

      <div class="row mb-4">
        <div class="col-md-4">
          <el-select v-model="statusFilter" placeholder="筛选状态" size="large" class="w-100">
            <el-option label="全部" value="all" />
            <el-option label="待提交" value="pending" />
            <el-option label="已提交" value="submitted" />
            <el-option label="已批改" value="graded" />
          </el-select>
        </div>
      </div>

      <el-skeleton :loading="loading" animated :count="3">
        <template #template>
          <div class="row">
            <div class="col-md-6 col-lg-4 mb-3" v-for="i in 6" :key="i">
              <el-skeleton-item variant="rect" style="height: 200px; border-radius: 8px;" />
            </div>
          </div>
        </template>
        <template #default>
          <div v-if="filteredAssignments.length === 0" class="text-center py-5">
            <el-empty description="暂无作业" />
          </div>

          <div class="row">
            <div
              v-for="assignment in filteredAssignments"
              :key="assignment.id"
              class="col-md-6 col-lg-4 mb-4"
            >
              <el-card shadow="hover" class="assignment-card h-100">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <h5 class="fw-bold mb-0">{{ assignment.title }}</h5>
                  <el-tag :type="getStatusType(assignment)" size="small">
                    <el-icon class="me-1">
                      <Check v-if="assignment.score != null" />
                      <Clock v-else-if="assignment.submitted" />
                      <Edit v-else />
                    </el-icon>
                    {{ getStatusText(assignment) }}
                  </el-tag>
                </div>

                <p class="text-muted small mb-2">
                  <el-icon class="me-1"><Document /></el-icon>
                  {{ assignment.course_title || '未知课程' }}
                </p>

                <p
                  class="small mb-3"
                  :class="isOverdue(assignment.due_date) && !assignment.submitted ? 'text-danger' : 'text-muted'"
                >
                  <el-icon class="me-1"><Clock /></el-icon>
                  截止: {{ formatDate(assignment.due_date) }}
                  <el-tag v-if="isOverdue(assignment.due_date) && !assignment.submitted" type="danger" size="small" class="ms-2">已过期</el-tag>
                </p>

                <div v-if="assignment.score != null" class="mb-3 p-2 bg-light rounded">
                  <div class="d-flex justify-content-between">
                    <span>得分</span>
                    <span :class="getScoreClass(assignment.score)" class="fw-bold">
                      {{ assignment.score }} / {{ assignment.max_score || assignment.assignment_max_score || 100 }}
                    </span>
                  </div>
                </div>

                <div class="d-flex gap-2">
                  <template v-if="!assignment.submitted && !isOverdue(assignment.due_date)">
                    <el-button type="primary" @click="openSubmitDialog(assignment)">
                      <el-icon class="me-1"><Edit /></el-icon>提交作业
                    </el-button>
                  </template>
                  <template v-else-if="assignment.submitted">
                    <el-button type="info" plain @click="viewSubmission(assignment)">
                      <el-icon class="me-1"><Document /></el-icon>查看提交
                    </el-button>
                  </template>
                </div>
              </el-card>
            </div>
          </div>
        </template>
      </el-skeleton>
    </div>

    <el-dialog v-model="submitDialogVisible" title="提交作业" width="600px" :close-on-click-modal="false">
      <div v-if="currentAssignment">
        <h6 class="fw-bold mb-2">{{ currentAssignment.title }}</h6>
        <p class="text-muted mb-3">{{ currentAssignment.description || '暂无作业描述' }}</p>
        <el-divider />
        <el-form label-position="top">
          <el-form-item label="作业内容">
            <el-input
              v-model="submitForm.content"
              type="textarea"
              :rows="6"
              placeholder="请输入你的作业内容..."
            />
          </el-form-item>
          <el-form-item label="附件 (可选)">
            <el-upload
              v-model:file-list="submitForm.files"
              :auto-upload="false"
              :limit="5"
              accept=".pdf,.doc,.docx,.zip,.rar,.jpg,.png"
              drag
              multiple
            >
              <el-icon class="el-icon--upload"><Upload /></el-icon>
              <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
              <template #tip>
                <div class="el-upload__tip">支持 PDF、Word、压缩包、图片等格式，最多5个文件</div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="submitDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">提交作业</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="viewDialogVisible" title="查看提交" width="600px">
      <div v-if="currentAssignment">
        <h6 class="fw-bold mb-2">{{ currentAssignment.title }}</h6>
        <p class="text-muted small mb-2">课程: {{ currentAssignment.course_title || '未知课程' }}</p>
        <el-divider />

        <p class="fw-medium mb-2">提交内容:</p>
        <div class="bg-light p-3 rounded mb-3" style="white-space: pre-wrap; min-height: 100px;">
          {{ currentAssignment.submission_content || '无内容' }}
        </div>

        <template v-if="currentAssignment.attachment_url">
          <p class="fw-medium mb-2">附件:</p>
          <el-link :href="currentAssignment.attachment_url" target="_blank" type="primary">
            <el-icon class="me-1"><Document /></el-icon>查看附件
          </el-link>
          <el-divider />
        </template>

        <template v-if="currentAssignment.score != null">
          <div class="d-flex align-items-center mb-3">
            <span class="fw-medium me-3">得分:</span>
            <span class="fw-bold fs-4" :class="getScoreClass(currentAssignment.score)">
              {{ currentAssignment.score }}
            </span>
          </div>
          <p class="fw-medium mb-2">教师评语:</p>
          <div class="bg-light p-3 rounded">
            {{ currentAssignment.feedback || '无评语' }}
          </div>
        </template>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { assignmentApi, uploadApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Edit, Upload, Check, Clock, Document } from '@element-plus/icons-vue'

const userStore = useUserStore()

const loading = ref(true)
const assignments = ref([])
const statusFilter = ref('all')
const submitDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const currentAssignment = ref(null)
const submitting = ref(false)
const submitForm = ref({
  content: '',
  files: []
})

const filteredAssignments = computed(() => {
  if (statusFilter.value === 'all') return assignments.value
  if (statusFilter.value === 'pending') return assignments.value.filter(a => !a.submitted && !isOverdue(a.due_date))
  if (statusFilter.value === 'submitted') return assignments.value.filter(a => a.submitted && a.score == null)
  if (statusFilter.value === 'graded') return assignments.value.filter(a => a.score != null)
  return assignments.value
})

function isOverdue(dueDate) {
  if (!dueDate) return false
  return new Date(dueDate) < new Date()
}

function formatDate(dateStr) {
  if (!dateStr) return '无截止日期'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getStatusText(assignment) {
  if (assignment.score != null) return '已批改'
  if (assignment.submitted) return '已提交'
  if (isOverdue(assignment.due_date)) return '已过期'
  return '待提交'
}

function getStatusType(assignment) {
  if (assignment.score != null) return 'success'
  if (assignment.submitted) return 'warning'
  if (isOverdue(assignment.due_date)) return 'danger'
  return 'info'
}

function getScoreClass(score) {
  if (score == null) return ''
  if (score >= 90) return 'text-success'
  if (score >= 60) return 'text-primary'
  return 'text-danger'
}

function openSubmitDialog(assignment) {
  currentAssignment.value = assignment
  submitForm.value = { content: '', files: [] }
  submitDialogVisible.value = true
}

function viewSubmission(assignment) {
  currentAssignment.value = assignment
  viewDialogVisible.value = true
}

async function handleSubmit() {
  if (!submitForm.value.content.trim()) {
    ElMessage.warning('请输入作业内容')
    return
  }

  submitting.value = true
  try {
    let attachmentUrl = ''
    if (submitForm.value.files.length > 0) {
      const file = submitForm.value.files[0]
      if (file.raw) {
        const formData = new FormData()
        formData.append('file', file.raw)
        const uploadRes = await uploadApi.uploadCourseImage(formData)
        attachmentUrl = uploadRes.data.url || uploadRes.data.file_url || ''
      }
    }

    const data = {
      content: submitForm.value.content,
      attachment_url: attachmentUrl
    }

    await assignmentApi.submitAssignment(currentAssignment.value.id, data)
    ElMessage.success('提交成功！')
    submitDialogVisible.value = false
    await fetchAssignments()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  } finally {
    submitting.value = false
  }
}

async function fetchAssignments() {
  loading.value = true
  try {
    const res = await assignmentApi.getStudentAssignments()
    assignments.value = res.data.assignments || res.data || []
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
.assignment-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.assignment-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}
    /* 响应式样式 */
    @media (max-width: 992px) {
      /* 平板适配 */
    }

    @media (max-width: 768px) {
      /* 手机适配 */
      .page-header { flex-direction: column; gap: 12px; }
      .el-card { margin-bottom: 12px; }
      .el-table { font-size: 12px; }
    .d-flex { flex-wrap: wrap; }
      .stats-card { margin-bottom: 12px; }
    }

    @media (max-width: 576px) {
      /* 小手机适配 */
    }
</style>
