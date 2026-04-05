<template>
  <div class="student-questions py-4">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold mb-0">课程答疑</h2>
        <el-button type="primary" @click="openAskDialog" :disabled="!selectedCourse">
          <el-icon class="me-1"><Edit /></el-icon>我要提问
        </el-button>
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
            placeholder="搜索问题标题..."
            :prefix-icon="Search"
            clearable
            size="large"
          />
        </div>
        <div class="col-lg-3 col-md-6 mt-2 mt-md-0">
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable size="large" class="w-100">
            <el-option label="待解答" value="unresolved" />
            <el-option label="已解答" value="resolved" />
          </el-select>
        </div>
      </div>

      <el-skeleton :loading="loading" animated :rows="8">
        <template #default>
          <div v-if="!selectedCourse" class="text-center py-5">
            <el-empty description="请先选择课程" />
          </div>

          <div v-else-if="filteredQuestions.length === 0 && !loading" class="text-center py-5">
            <el-empty description="暂无提问">
              <el-button type="primary" @click="openAskDialog">我要提问</el-button>
            </el-empty>
          </div>

          <div v-else>
            <el-card
              v-for="question in paginatedQuestions"
              :key="question.id"
              shadow="hover"
              class="mb-3 question-card"
            >
              <div class="d-flex">
                <div class="me-3 flex-shrink-0">
                  <el-avatar :size="44">
                    {{ (question.user_name || 'U').charAt(0) }}
                  </el-avatar>
                </div>
                <div class="flex-grow-1 min-w-0">
                  <div class="d-flex justify-content-between align-items-start mb-1">
                    <div class="min-w-0">
                      <h6 class="fw-bold mb-1 question-title" @click="toggleExpand(question)">
                        {{ question.title }}
                      </h6>
                      <el-tag v-if="question.status === 'pending'" size="small" type="info" class="ms-2">审核中</el-tag>
                      <el-tag v-if="question.status === 'rejected'" size="small" type="danger" class="ms-2">已拒绝</el-tag>
                      <div class="d-flex align-items-center flex-wrap gap-2 text-muted small">
                        <span>{{ question.user_name || '匿名学生' }}</span>
                        <span>·</span>
                        <span>{{ formatDate(question.created_at) }}</span>
                        <el-tag v-if="question.user_id === userStore.user.id" type="info" size="small">我的提问</el-tag>
                      </div>
                    </div>
                    <div class="d-flex align-items-center gap-2 flex-shrink-0">
                      <el-tag :type="question.is_resolved ? 'success' : 'warning'" size="small">
                        {{ question.is_resolved ? '已解答' : '待解答' }}
                      </el-tag>
                    </div>
                  </div>

                  <p class="text-muted small mb-2" style="white-space: pre-wrap;">{{ question.content }}</p>

                  <div class="d-flex gap-2">
                    <el-button size="small" type="primary" plain @click="toggleExpand(question)">
                      {{ expandedId === question.id ? '收起' : '查看回答' }} ({{ question.answer_count || 0 }})
                    </el-button>
                    <el-button
                      v-if="!question.is_resolved && question.user_id === userStore.user.id"
                      size="small"
                      type="success"
                      plain
                      @click="markResolved(question)"
                    >
                      标记已解答
                    </el-button>
                  </div>

                  <div v-if="expandedId === question.id" class="mt-3 pt-3 border-top">
                    <h6 class="fw-bold mb-3">回答 ({{ answers.length }})</h6>

                    <div v-if="answersLoading" class="text-center py-3">
                      <el-icon class="is-loading" :size="24"><Loading /></el-icon>
                    </div>

                    <div v-else-if="answers.length === 0" class="text-center py-2">
                      <p class="text-muted small">暂无回答</p>
                    </div>

                    <div v-else class="answers-list mb-3" style="max-height: 300px; overflow-y: auto;">
                      <div v-for="answer in answers" :key="answer.id" class="d-flex mb-3">
                        <el-avatar :size="32" class="me-2 flex-shrink-0">
                          {{ (answer.user_name || 'U').charAt(0) }}
                        </el-avatar>
                        <div class="flex-grow-1 min-w-0">
                          <div class="d-flex justify-content-between align-items-center mb-1">
                            <div>
                              <span class="fw-medium small">{{ answer.user_name || '匿名' }}</span>
                              <el-tag v-if="answer.is_teacher" type="primary" size="small" class="ms-2">教师</el-tag>
                            </div>
                            <span class="text-muted small">{{ formatDate(answer.created_at) }}</span>
                          </div>
                          <p class="mb-0 small" style="white-space: pre-wrap;">{{ answer.content }}</p>
                        </div>
                      </div>
                    </div>

                    <div class="reply-form">
                      <el-input
                        v-model="replyContent"
                        type="textarea"
                        :rows="3"
                        placeholder="输入回答内容..."
                      />
                      <div class="d-flex justify-content-end mt-2">
                        <el-button type="primary" size="small" :loading="replying" @click="handleReply(question)">
                          发表回答
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </div>

          <div class="d-flex justify-content-center mt-4" v-if="filteredQuestions.length > pageSize">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :total="filteredQuestions.length"
              layout="total, sizes, prev, pager, next"
              background
            />
          </div>
        </template>
      </el-skeleton>
    </div>

    <!-- 提问对话框 -->
    <el-dialog v-model="askDialogVisible" title="我要提问" width="600px" :close-on-click-modal="false">
      <el-form ref="questionFormRef" :model="questionForm" :rules="questionRules" label-position="top">
        <el-form-item label="问题标题" prop="title">
          <el-input v-model="questionForm.title" placeholder="请输入问题标题" />
        </el-form-item>
        <el-form-item label="问题内容" prop="content">
          <el-input
            v-model="questionForm.content"
            type="textarea"
            :rows="6"
            placeholder="请详细描述您的问题..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="askDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmitQuestion">提交问题</el-button>
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
import { Search, Loading, Edit } from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const courses = ref([])
const questions = ref([])
const selectedCourse = ref(null)
const searchQuery = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const expandedId = ref(null)
const answers = ref([])
const answersLoading = ref(false)
const replyContent = ref('')
const replying = ref(false)

const askDialogVisible = ref(false)
const questionFormRef = ref(null)
const submitting = ref(false)
const questionForm = ref({
  title: '',
  content: ''
})

const questionRules = {
  title: [{ required: true, message: '请输入问题标题', trigger: 'change' }],
  content: [{ required: true, message: '请输入问题内容', trigger: 'change' }]
}

const filteredQuestions = computed(() => {
  let result = [...questions.value]

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(question =>
      (question.title || '').toLowerCase().includes(q) ||
      (question.content || '').toLowerCase().includes(q)
    )
  }

  if (statusFilter.value) {
    if (statusFilter.value === 'resolved') {
      result = result.filter(question => question.is_resolved)
    } else if (statusFilter.value === 'unresolved') {
      result = result.filter(question => !question.is_resolved)
    }
  }

  return result
})

const paginatedQuestions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredQuestions.value.slice(start, start + pageSize.value)
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  if (hours < 24) return `${hours} 小时前`
  if (days < 7) return `${days} 天前`
  return date.toLocaleDateString('zh-CN')
}

async function toggleExpand(question) {
  if (expandedId.value === question.id) {
    expandedId.value = null
    answers.value = []
    replyContent.value = ''
    return
  }

  expandedId.value = question.id
  replyContent.value = ''
  await fetchAnswers(question.id)
}

async function fetchAnswers(questionId) {
  answersLoading.value = true
  try {
    const res = await interactionApi.getQuestionAnswers(questionId)
    answers.value = res.data.answers || res.data || []
  } catch {
    answers.value = []
  } finally {
    answersLoading.value = false
  }
}

async function handleReply(question) {
  if (!replyContent.value.trim()) {
    ElMessage.warning('请输入回答内容')
    return
  }

  replying.value = true
  try {
    const res = await interactionApi.createAnswer(question.id, {
      content: replyContent.value
    })
    const newAnswer = res.data || {
      id: Date.now(),
      content: replyContent.value,
      user_name: userStore.user.real_name || userStore.user.username || '学生',
      is_teacher: false,
      created_at: new Date().toISOString()
    }
    answers.value.push(newAnswer)
    replyContent.value = ''
    question.answer_count = (question.answer_count || 0) + 1
    ElMessage.success('回答成功，内容审核通过后将显示')
  } catch {
    ElMessage.error('回答失败')
  } finally {
    replying.value = false
  }
}

async function markResolved(question) {
  try {
    await ElMessageBox.confirm('确定标记该问题为已解答吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    await interactionApi.resolveQuestion(question.id)
    question.is_resolved = true
    ElMessage.success('已标记为解答')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

function handleCourseChange(courseId) {
  expandedId.value = null
  answers.value = []
  replyContent.value = ''
  if (courseId) {
    fetchQuestions(courseId)
  } else {
    questions.value = []
  }
}

async function fetchQuestions(courseId) {
  loading.value = true
  try {
    const res = await interactionApi.getCourseQuestions(courseId)
    questions.value = (res.data.questions || res.data || []).sort(
      (a, b) => new Date(b.created_at) - new Date(a.created_at)
    )
  } catch {
    ElMessage.error('获取问题列表失败')
    questions.value = []
  } finally {
    loading.value = false
  }
}

async function fetchCourses() {
  try {
    const res = await courseApi.getMyEnrollments()
    const enrollments = res.data.enrollments || res.data || []
    courses.value = enrollments.map(e => ({
      id: e.course_id || e.id,
      title: e.course_title || e.title
    }))

    if (route.params.id) {
      selectedCourse.value = Number(route.params.id)
      await fetchQuestions(selectedCourse.value)
    }
  } catch {
    ElMessage.error('获取课程列表失败')
  }
}

function openAskDialog() {
  questionForm.value = { title: '', content: '' }
  askDialogVisible.value = true
}

async function handleSubmitQuestion() {
  const valid = await questionFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const res = await interactionApi.createQuestion({
      course_id: selectedCourse.value,
      title: questionForm.value.title,
      content: questionForm.value.content
    })
    const newQuestion = res.data.question || {
      id: Date.now(),
      course_id: selectedCourse.value,
      user_id: userStore.user.id,
      user_name: userStore.user.real_name || userStore.user.username || '学生',
      title: questionForm.value.title,
      content: questionForm.value.content,
      is_resolved: false,
      answer_count: 0,
      created_at: new Date().toISOString()
    }
    questions.value.unshift(newQuestion)
    askDialogVisible.value = false
    ElMessage.success('提问成功，内容审核通过后将显示')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提问失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchCourses()
})
</script>

<style scoped>
.question-card {
  transition: box-shadow 0.2s;
}

.question-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.question-title {
  cursor: pointer;
  transition: color 0.2s;
}

.question-title:hover {
  color: #409eff;
}

.min-w-0 {
  min-width: 0;
}

/* 响应式 */
@media (max-width: 992px) {
  .el-table { font-size: 12px; }
  .el-card { margin-bottom: 12px; }
}

@media (max-width: 768px) {
  .el-card { margin-bottom: 12px; }
  .el-table { font-size: 12px; }
  .d-flex { flex-wrap: wrap; }
  .el-dialog { width: 95% !important; }
}

@media (max-width: 576px) {
  .el-card__body { padding: 12px; }
}
</style>
