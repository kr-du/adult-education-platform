<template>
  <div class="course-questions py-4">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold mb-0">答疑管理</h2>
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
        <div class="col-6 mt-2">
          <el-input
            v-model="searchQuery"
            placeholder="搜索问题标题..."
            :prefix-icon="Search"
            clearable
            size="large"
          />
        </div>
        <div class="col-6 mt-2">
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
            <el-empty description="暂无提问" />
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
                      <div class="d-flex align-items-center flex-wrap gap-2 text-muted small">
                        <span>{{ question.user_name || '匿名学生' }}</span>
                        <span>·</span>
                        <span>{{ formatDate(question.created_at) }}</span>
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
                        v-if="!question.is_resolved"
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { courseApi, interactionApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Loading } from '@element-plus/icons-vue'

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
      result = result.filter(question => question.resolved)
    } else if (statusFilter.value === 'unresolved') {
      result = result.filter(question => !question.resolved)
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
      user_name: userStore.user.real_name || userStore.user.username || '教师',
      is_teacher: true,
      created_at: new Date().toISOString()
    }
    answers.value.push(newAnswer)
    replyContent.value = ''
    question.answer_count = (question.answer_count || 0) + 1
    ElMessage.success('回答成功')
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
    const res = await courseApi.getCourses({ teacher_id: userStore.user.id })
    courses.value = res.data.courses || res.data || []

    if (route.params.id) {
      selectedCourse.value = Number(route.params.id)
      await fetchQuestions(selectedCourse.value)
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
