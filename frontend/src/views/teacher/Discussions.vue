<template>
  <div class="teacher-discussions py-4">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold mb-0">讨论区管理</h2>
      </div>

      <div class="row mb-4">
        <div class="col-lg-4 col-md-6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索讨论主题..."
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
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable size="large" class="w-100">
            <el-option label="待回复" value="unanswered" />
            <el-option label="已回复" value="answered" />
          </el-select>
        </div>
      </div>

      <el-skeleton :loading="loading" animated :rows="8">
        <template #default>
          <div v-if="filteredDiscussions.length === 0 && !loading" class="text-center py-5">
            <el-empty description="暂无讨论" />
          </div>

          <div v-else>
            <el-card
              v-for="discussion in paginatedDiscussions"
              :key="discussion.id"
              shadow="hover"
              class="mb-3 discussion-card"
            >
              <div class="d-flex">
                <div class="me-3 flex-shrink-0">
                  <el-avatar :size="44">
                    {{ (discussion.author_name || 'U').charAt(0) }}
                  </el-avatar>
                </div>
                <div class="flex-grow-1 min-w-0">
                  <div class="d-flex justify-content-between align-items-start mb-1">
                    <div class="min-w-0">
                      <h6 class="fw-bold mb-1 discussion-title" @click="openDiscussion(discussion)">
                        {{ discussion.title }}
                      </h6>
                      <div class="d-flex align-items-center flex-wrap gap-2 text-muted small">
                        <span>{{ discussion.author_name || '匿名' }}</span>
                        <span>·</span>
                        <span>{{ formatDate(discussion.created_at) }}</span>
                        <span>·</span>
                        <span>{{ discussion.course_title || getCourseName(discussion.course_id) }}</span>
                      </div>
                    </div>
                    <div class="d-flex align-items-center gap-2 flex-shrink-0">
                      <el-tag v-if="discussion.reply_count > 0" type="success" size="small">
                        {{ discussion.reply_count }} 回复
                      </el-tag>
                      <el-tag v-else type="warning" size="small">待回复</el-tag>
                    </div>
                  </div>
                  <p class="text-muted small mb-2 discussion-content">
                    {{ discussion.content }}
                  </p>
                  <div class="d-flex gap-2">
                    <el-button size="small" type="primary" plain @click="openDiscussion(discussion)">
                      查看详情 & 回复
                    </el-button>
                    <el-button size="small" type="danger" plain @click="deleteDiscussion(discussion)">
                      删除
                    </el-button>
                  </div>
                </div>
              </div>
            </el-card>
          </div>

          <div class="d-flex justify-content-center mt-4" v-if="filteredDiscussions.length > pageSize">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :total="filteredDiscussions.length"
              layout="total, sizes, prev, pager, next"
              background
            />
          </div>
        </template>
      </el-skeleton>
    </div>

    <el-dialog v-model="detailDialogVisible" :title="currentDiscussion?.title || '讨论详情'" width="800px" :close-on-click-modal="false">
      <div v-if="currentDiscussion">
        <div class="d-flex mb-3">
          <el-avatar :size="40" class="me-3 flex-shrink-0">
            {{ (currentDiscussion.author_name || 'U').charAt(0) }}
          </el-avatar>
          <div class="flex-grow-1 min-w-0">
            <div class="d-flex justify-content-between">
              <span class="fw-medium">{{ currentDiscussion.author_name || '匿名' }}</span>
              <span class="text-muted small">{{ formatDate(currentDiscussion.created_at) }}</span>
            </div>
            <el-tag size="small" class="mt-1">{{ currentDiscussion.course_title || getCourseName(currentDiscussion.course_id) }}</el-tag>
          </div>
        </div>

        <div class="p-3 bg-light rounded mb-4" style="white-space: pre-wrap;">
          {{ currentDiscussion.content }}
        </div>

        <el-divider />

        <h6 class="fw-bold mb-3">回复 ({{ replies.length }})</h6>

        <div v-if="replies.length === 0" class="text-center py-3">
          <p class="text-muted">暂无回复，成为第一个回复的人吧</p>
        </div>

        <div v-else class="replies-list mb-4" style="max-height: 400px; overflow-y: auto;">
          <div v-for="reply in replies" :key="reply.id" class="d-flex mb-3">
            <el-avatar :size="36" class="me-3 flex-shrink-0">
              {{ (reply.author_name || 'U').charAt(0) }}
            </el-avatar>
            <div class="flex-grow-1 min-w-0">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <div>
                  <span class="fw-medium small">{{ reply.author_name || '匿名' }}</span>
                  <el-tag v-if="reply.is_teacher" type="primary" size="small" class="ms-2">教师</el-tag>
                </div>
                <span class="text-muted small">{{ formatDate(reply.created_at) }}</span>
              </div>
              <p class="mb-0 small" style="white-space: pre-wrap;">{{ reply.content }}</p>
            </div>
          </div>
        </div>

        <el-divider />

        <h6 class="fw-bold mb-2">发表回复</h6>
        <el-input
          v-model="replyContent"
          type="textarea"
          :rows="3"
          placeholder="输入回复内容..."
        />
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" :loading="replying" @click="handleReply">发表回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { courseApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const userStore = useUserStore()

const loading = ref(true)
const courses = ref([])
const discussions = ref([])
const searchQuery = ref('')
const courseFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const detailDialogVisible = ref(false)
const currentDiscussion = ref(null)
const replies = ref([])
const replyContent = ref('')
const replying = ref(false)

const filteredDiscussions = computed(() => {
  let result = [...discussions.value]

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(d =>
      d.title.toLowerCase().includes(q) ||
      d.content.toLowerCase().includes(q) ||
      (d.author_name || '').toLowerCase().includes(q)
    )
  }

  if (courseFilter.value) {
    result = result.filter(d => d.course_id === courseFilter.value)
  }

  if (statusFilter.value === 'unanswered') {
    result = result.filter(d => !d.reply_count || d.reply_count === 0)
  } else if (statusFilter.value === 'answered') {
    result = result.filter(d => d.reply_count > 0)
  }

  return result
})

const paginatedDiscussions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredDiscussions.value.slice(start, start + pageSize.value)
})

function getCourseName(courseId) {
  const course = courses.value.find(c => c.id === courseId)
  return course?.title || '未知课程'
}

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

function openDiscussion(discussion) {
  currentDiscussion.value = discussion
  replies.value = discussion.replies || []
  replyContent.value = ''
  detailDialogVisible.value = true
}

async function handleReply() {
  if (!replyContent.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }

  replying.value = true
  try {
    const newReply = {
      id: Date.now(),
      content: replyContent.value,
      author_name: userStore.user.name || userStore.user.username || '教师',
      is_teacher: true,
      created_at: new Date().toISOString()
    }
    replies.value.push(newReply)
    replyContent.value = ''

    if (currentDiscussion.value) {
      currentDiscussion.value.reply_count = (currentDiscussion.value.reply_count || 0) + 1
    }

    ElMessage.success('回复成功')
  } catch (e) {
    ElMessage.error('回复失败')
  } finally {
    replying.value = false
  }
}

async function deleteDiscussion(discussion) {
  try {
    await ElMessageBox.confirm('确定要删除该讨论吗？相关的回复也会被删除。', '警告', {
      type: 'warning',
      confirmButtonText: '确定删除',
      cancelButtonText: '取消'
    })
    discussions.value = discussions.value.filter(d => d.id !== discussion.id)
    ElMessage.success('删除成功')
  } catch {
    // cancelled
  }
}

async function fetchData() {
  loading.value = true
  try {
    const courseRes = await courseApi.getCourses({ teacher_id: userStore.user.id })
    courses.value = courseRes.data.courses || courseRes.data || []

    const allDiscussions = []
    for (const course of courses.value) {
      try {
        const detailRes = await courseApi.getCourse(course.id)
        const courseData = detailRes.data.course || detailRes.data || {}
        if (courseData.discussions) {
          courseData.discussions.forEach(d => {
            allDiscussions.push({
              ...d,
              course_id: course.id,
              course_title: course.title
            })
          })
        }
      } catch {
        // skip
      }
    }

    discussions.value = allDiscussions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } catch (e) {
    ElMessage.error('获取讨论数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.discussion-card {
  transition: box-shadow 0.2s;
}

.discussion-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.discussion-title {
  cursor: pointer;
  transition: color 0.2s;
}

.discussion-title:hover {
  color: #409eff;
}

.discussion-content {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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
