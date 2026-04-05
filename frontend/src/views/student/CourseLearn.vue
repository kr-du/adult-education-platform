<template>
  <div class="course-learn d-flex" style="height: 100vh;">
    <!-- 全局 Loading -->
    <div v-if="pageLoading" class="global-loading">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <span class="ms-2">加载中...</span>
    </div>

    <!-- 视频区域 -->
    <div class="video-area flex-grow-1 bg-dark d-flex flex-column">
      <div class="video-header bg-dark text-white p-3 d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center">
          <el-button link class="text-white me-3" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            <span class="ms-1">返回</span>
          </el-button>
          <h5 class="mb-0">{{ course?.title || '课程加载中...' }}</h5>
        </div>
        <el-button link class="text-white" @click="toggleSidebar">
          <el-icon :size="20"><Fold v-if="sidebarVisible" /><Expand v-else /></el-icon>
        </el-button>
      </div>

      <div class="video-container flex-grow-1 d-flex align-items-center justify-content-center bg-black">
        <!-- 使用增强版视频播放器 -->
        <VideoPlayer
          v-if="currentLesson?.video_url"
          ref="videoPlayerRef"
          :src="currentLesson.video_url"
          @timeupdate="handleTimeUpdate"
          @ended="handleVideoEnd"
          class="w-100 h-100"
        />
        <div v-else class="text-white text-center">
          <el-icon :size="48"><VideoCamera /></el-icon>
          <p class="mt-2">暂无视频</p>
        </div>
      </div>

      <div class="video-info bg-white p-3">
        <h5 class="mb-1">{{ currentLesson?.title || '请选择课时' }}</h5>
        <p class="text-muted mb-0 small">{{ currentLesson?.content || '点击右侧目录开始学习' }}</p>
      </div>
    </div>

    <!-- 侧边栏 -->
    <div class="sidebar bg-white border-start" :class="{ 'd-none': !sidebarVisible }" style="width: 360px;">
      <!-- 进度卡片 -->
      <div class="progress-section p-3 border-bottom">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <span class="text-muted small">学习进度</span>
          <span class="fw-bold text-primary">{{ overallProgress }}%</span>
        </div>
        <el-progress :percentage="overallProgress" :stroke-width="6" :show-text="false" />
        <div class="text-muted small mt-2">{{ completedLessons }}/{{ lessons.length }} 课时已完成</div>
      </div>

      <!-- 标签页导航 -->
      <div class="nav-tabs-custom border-bottom">
        <button 
          v-for="tab in tabs" 
          :key="tab.name"
          class="nav-tab"
          :class="{ active: activeTab === tab.name }"
          @click="activeTab = tab.name"
        >
          <el-icon class="me-1"><component :is="tab.icon" /></el-icon>
          {{ tab.label }}
          <span v-if="tab.badge > 0" class="badge">{{ tab.badge }}</span>
        </button>
      </div>

      <!-- 标签内容区域 -->
      <div class="tab-content-area">
        <!-- 课程目录 -->
        <div v-show="activeTab === 'lessons'" class="lesson-list">
          <div v-if="lessons.length === 0" class="text-center py-5 text-muted">
            <el-icon :size="32"><VideoCamera /></el-icon>
            <p class="mt-2 small">暂无课时</p>
          </div>
          <div
            v-for="(lesson, index) in lessons"
            :key="lesson.id"
            class="lesson-item p-3 border-bottom d-flex align-items-center"
            :class="{ 'active': lesson.id === currentLesson?.id, 'completed': getLessonProgress(lesson.id)?.completed }"
            @click="selectLesson(lesson)"
          >
            <div class="lesson-index me-3">
              <el-icon v-if="getLessonProgress(lesson.id)?.completed" class="text-success">
                <CircleCheckFilled />
              </el-icon>
              <el-icon v-else-if="lesson.id === currentLesson?.id" class="text-primary">
                <VideoPlay />
              </el-icon>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <div class="flex-grow-1">
              <div class="lesson-title">{{ lesson.title }}</div>
              <small class="text-muted">{{ lesson.duration || 0 }}分钟</small>
            </div>
          </div>
        </div>

        <!-- 课程公告 -->
        <div v-show="activeTab === 'notices'" class="notice-list">
          <div v-if="noticesLoading" class="text-center py-5 text-muted">
            <el-icon class="is-loading"><Loading /></el-icon>
            <p class="mt-2 small">加载中...</p>
          </div>
          <div v-else-if="notices.length === 0" class="text-center py-5 text-muted">
            <el-icon :size="32"><Bell /></el-icon>
            <p class="mt-2 small">暂无公告</p>
          </div>
          <div v-else v-for="notice in notices" :key="notice.id" class="notice-item p-3 border-bottom">
            <div class="notice-title mb-2">
              <el-icon class="text-warning me-1"><Bell /></el-icon>
              {{ notice.title }}
            </div>
            <p class="notice-content text-muted small mb-2">{{ notice.content }}</p>
            <small class="text-muted">{{ formatDate(notice.created_at) }}</small>
          </div>
        </div>

        <!-- 课程讨论 -->
        <div v-show="activeTab === 'discussions'" class="discussion-list">
          <!-- 发表讨论 -->
          <div class="p-3 border-bottom">
            <el-input
              v-model="newDiscussion"
              type="textarea"
              :rows="2"
              placeholder="分享你的学习心得..."
              resize="none"
              class="mb-2"
            />
            <div class="text-end">
              <el-button type="primary" size="small" @click="submitDiscussion" :loading="submitting">
                发表
              </el-button>
            </div>
          </div>

          <!-- 讨论列表 -->
          <div v-if="discussionsLoading" class="text-center py-5 text-muted">
            <el-icon class="is-loading"><Loading /></el-icon>
            <p class="mt-2 small">加载中...</p>
          </div>
          <div v-else-if="discussions.length === 0" class="text-center py-5 text-muted">
            <el-icon :size="32"><ChatDotRound /></el-icon>
            <p class="mt-2 small">暂无讨论</p>
          </div>
          <div v-else v-for="item in discussions" :key="item.id" class="discussion-item p-3 border-bottom" :class="{ 'pending-item': item.status === 'pending' }">
            <div class="d-flex align-items-center mb-2">
              <el-avatar :size="24" class="me-2">{{ item.user_name?.charAt(0) || 'U' }}</el-avatar>
              <span class="fw-medium small">{{ item.user_name || '匿名' }}</span>
              <el-tag v-if="item.user_role === 'teacher'" size="small" type="warning" class="ms-2">讲师</el-tag>
              <el-tag v-if="item.status === 'pending'" size="small" type="info" class="ms-2">审核中</el-tag>
              <el-tag v-if="item.status === 'rejected'" size="small" type="danger" class="ms-2">已拒绝</el-tag>
              <span class="text-muted small ms-auto">{{ formatDate(item.created_at) }}</span>
            </div>
            <p class="small mb-2">{{ item.content }}</p>
            <div class="d-flex gap-2">
              <el-button size="small" type="primary" link @click="toggleReplies(item)">
                {{ item.showReplies ? '收起' : '回复' }} ({{ item.reply_count || 0 }})
                <el-icon v-if="item.loadingReplies" class="is-loading ms-1"><Loading /></el-icon>
              </el-button>
              <el-button v-if="canDelete(item)" size="small" type="danger" link @click="deleteDiscussion(item)">
                删除
              </el-button>
            </div>

            <!-- 回复区域 -->
            <div v-if="item.showReplies" class="mt-2 ms-4 pt-2 border-start">
              <div v-if="item.loadingReplies" class="text-center py-3 text-muted small">
                <el-icon class="is-loading"><Loading /></el-icon> 加载回复中...
              </div>
              <div v-else>
                <div v-for="reply in item.replies" :key="reply.id" class="reply-item py-2">
                  <div class="d-flex align-items-center mb-1">
                    <el-avatar :size="20" class="me-2">{{ reply.user_name?.charAt(0) || 'U' }}</el-avatar>
                    <span class="small">{{ reply.user_name }}</span>
                    <el-tag v-if="reply.user_role === 'teacher'" size="small" type="warning" class="ms-1">讲师</el-tag>
                    <el-tag v-if="reply.status === 'pending'" size="small" type="info" class="ms-1">审核中</el-tag>
                    <span class="text-muted small ms-auto me-2">{{ formatDate(reply.created_at) }}</span>
                    <el-button v-if="canDelete(reply)" size="small" type="danger" link @click="deleteReply(reply, item)">
                      删除
                    </el-button>
                  </div>
                  <p class="small mb-1 ms-5">{{ reply.content }}</p>
                </div>
                <el-input
                  v-model="item.replyContent"
                  size="small"
                  placeholder="回复..."
                  class="mt-2"
                  @keyup.enter="submitReply(item)"
                >
                  <template #append>
                    <el-button size="small" @click="submitReply(item)">回复</el-button>
                  </template>
                </el-input>
              </div>
            </div>
          </div>
        </div>

        <!-- 教师信息 -->
        <div v-show="activeTab === 'teacher'" class="teacher-info p-4">
          <div v-if="course?.teacher_name" class="text-center">
            <div class="teacher-avatar mx-auto mb-3">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <h6 class="fw-bold mb-2">{{ course.teacher_name }}</h6>
            <el-tag size="small" type="info">专业讲师</el-tag>
            <div class="d-flex justify-content-around mt-4 pt-3 border-top">
              <div class="text-center">
                <div class="fw-bold text-primary">{{ course.lesson_count || 0 }}</div>
                <small class="text-muted">课时</small>
              </div>
              <div class="text-center">
                <div class="fw-bold text-primary">{{ course.student_count || 0 }}</div>
                <small class="text-muted">学员</small>
              </div>
              <div class="text-center">
                <div class="fw-bold text-primary">{{ course.view_count || 0 }}</div>
                <small class="text-muted">浏览</small>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-5 text-muted">
            <el-icon :size="32"><User /></el-icon>
            <p class="mt-2 small">暂无讲师信息</p>
          </div>
        </div>

        <!-- 课程评价 -->
        <div v-show="activeTab === 'reviews'" class="review-list">
          <!-- 发表评价 -->
          <div class="p-3 border-bottom" v-if="!hasReviewed">
            <div class="mb-3">
              <span class="text-muted small">评分：</span>
              <el-rate v-model="newReview.rating" show-text />
            </div>
            <el-input
              v-model="newReview.content"
              type="textarea"
              :rows="3"
              placeholder="分享你对这门课程的学习体验..."
              resize="none"
              class="mb-2"
            />
            <div class="text-end">
              <el-button type="primary" size="small" @click="submitReview" :loading="submittingReview">
                提交评价
              </el-button>
            </div>
          </div>
          <div v-else class="p-3 bg-success bg-opacity-10 text-success text-center small">
            <el-icon class="me-1"><CircleCheckFilled /></el-icon>
            您已评价过此课程
          </div>

          <!-- 评价列表 -->
          <div v-if="reviews.length === 0" class="text-center py-5 text-muted">
            <el-icon :size="32"><Star /></el-icon>
            <p class="mt-2 small">暂无评价，来做第一个评价吧</p>
          </div>
          <div v-for="review in reviews" :key="review.id" class="review-item p-3 border-bottom" :class="{ 'pending-item': review.status === 'pending' }">
            <div class="d-flex align-items-center mb-2">
              <el-avatar :size="24" class="me-2">{{ review.user_name?.charAt(0) || 'U' }}</el-avatar>
              <span class="fw-medium small">{{ review.user_name || '匿名' }}</span>
              <el-tag v-if="review.status === 'pending'" size="small" type="info" class="ms-2">审核中</el-tag>
              <el-tag v-if="review.status === 'rejected'" size="small" type="danger" class="ms-2">已拒绝</el-tag>
              <div class="ms-2">
                <el-icon 
                  v-for="i in 5" 
                  :key="i" 
                  :class="i <= review.rating ? 'text-warning' : 'text-muted'"
                  class="small"
                >
                  <Star />
                </el-icon>
              </div>
              <span class="text-muted small ms-auto">{{ formatDate(review.created_at) }}</span>
            </div>
            <p class="small mb-0">{{ review.content }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { courseApi, discussionApi, interactionApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Fold, Expand, CircleCheckFilled, VideoPlay, VideoCamera, 
  Bell, User, ArrowLeft, ChatDotRound, List, Loading, CircleClose, Star 
} from '@element-plus/icons-vue'
import VideoPlayer from '@/components/common/VideoPlayer.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const videoPlayerRef = ref()
const course = ref(null)
const lessons = ref([])
const currentLesson = ref(null)
const lessonProgress = ref([])
const sidebarVisible = ref(true)
const activeTab = ref('lessons')

// Loading 状态
const pageLoading = ref(true)
const noticesLoading = ref(false)
const discussionsLoading = ref(false)
const submitting = ref(false)

// 公告相关
const notices = ref([])

// 讨论相关
const discussions = ref([])
const newDiscussion = ref('')

// 评价相关
const reviews = ref([])
const newReview = ref({ rating: 5, content: '' })
const submittingReview = ref(false)
const hasReviewed = ref(false)

// 记录当前课时是否已上报过完成状态，防止重复请求
const reportedCompletedLessons = ref(new Set())

// 标签页配置
const tabs = computed(() => [
  { name: 'lessons', label: '目录', icon: List, badge: 0 },
  { name: 'notices', label: '公告', icon: Bell, badge: notices.value.length },
  { name: 'discussions', label: '讨论', icon: ChatDotRound, badge: 0 },
  { name: 'reviews', label: '评价', icon: Star, badge: 0 },
  { name: 'teacher', label: '教师', icon: User, badge: 0 }
])

const overallProgress = computed(() => {
  if (lessons.value.length === 0) return 0
  const completed = lessonProgress.value.filter(p => p.completed).length
  return Math.round((completed / lessons.value.length) * 100)
})

const completedLessons = computed(() => {
  return lessonProgress.value.filter(p => p.completed).length
})

// 统一错误处理
function handleApiError(error, defaultMessage = '操作失败') {
  console.error(error)
  const message = error.response?.data?.error || error.message || defaultMessage
  ElMessage.error(message)
  // 如果是 401 未授权，跳转到登录页
  if (error.response?.status === 401) {
    userStore.logout()
    router.push('/login')
  }
}

function toggleSidebar() {
  sidebarVisible.value = !sidebarVisible.value
}

function goBack() {
  router.push(`/course/${route.params.id}`)
}

function getLessonProgress(lessonId) {
  return lessonProgress.value.find(p => p.lesson_id === lessonId)
}

function formatDate(dateStr) {
  if (!dateStr) return '未知'
  
  const date = new Date(dateStr.includes('T') ? dateStr : dateStr.replace(' ', 'T'))
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60 * 1000) return '刚刚'
  if (diff < 60 * 60 * 1000) return `${Math.floor(diff / (60 * 1000))}分钟前`
  
  const days = Math.floor(diff / (24 * 60 * 60 * 1000))
  if (days >= 1) return `${date.getMonth() + 1}月${date.getDate()}日`
  
  return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
}

async function selectLesson(lesson) {
  // 如果点击的是当前正在播放的课时，不做任何操作
  if (currentLesson.value?.id === lesson.id) return
  
  currentLesson.value = lesson
}

async function handleTimeUpdate({ currentTime, duration }) {
  if (!currentLesson.value || !duration || isNaN(duration)) return
  
  const percent = (currentTime / duration) * 100

  // 只有当进度超过 80% 且该课时未被标记为完成时才上报
  if (percent > 80 && !reportedCompletedLessons.value.has(currentLesson.value.id)) {
    try {
      // 乐观更新 UI
      updateLocalProgress(currentLesson.value.id, true)
      
      await courseApi.updateProgress(currentLesson.value.id, {
        watched_duration: Math.floor(currentTime),
        completed: true
      })
      
      // 标记为已上报
      reportedCompletedLessons.value.add(currentLesson.value.id)
    } catch (e) {
      // 如果失败，回滚 UI 状态
      updateLocalProgress(currentLesson.value.id, false)
      handleApiError(e, '进度同步失败')
    }
  }
}

async function handleVideoEnd() {
  if (!currentLesson.value || reportedCompletedLessons.value.has(currentLesson.value.id)) return

  try {
    updateLocalProgress(currentLesson.value.id, true)
    await courseApi.updateProgress(currentLesson.value.id, { completed: true })
    reportedCompletedLessons.value.add(currentLesson.value.id)
    ElMessage.success('课时学习完成')
  } catch (e) {
    updateLocalProgress(currentLesson.value.id, false)
    handleApiError(e, '进度同步失败')
  }
}

function updateLocalProgress(lessonId, completed) {
  const existing = lessonProgress.value.find(p => p.lesson_id === lessonId)
  if (existing) {
    existing.completed = completed
  } else {
    lessonProgress.value.push({ lesson_id: lessonId, completed })
  }
}

async function fetchNotices() {
  if (noticesLoading.value) return
  noticesLoading.value = true
  try {
    const res = await interactionApi.getCourseNotices(route.params.id)
    notices.value = (res.data.notices || res.data || []).sort(
      (a, b) => new Date(b.created_at) - new Date(a.created_at)
    )
  } catch (e) {
    handleApiError(e, '获取公告失败')
  } finally {
    noticesLoading.value = false
  }
}

async function fetchDiscussions() {
  if (discussionsLoading.value) return
  discussionsLoading.value = true
  try {
    const res = await discussionApi.getCourseDiscussions(route.params.id)
    discussions.value = (res.data.discussions || []).map(d => ({
      ...d, 
      showReplies: false, 
      replies: [], 
      replyContent: '',
      loadingReplies: false
    }))
  } catch (e) {
    handleApiError(e, '获取讨论失败')
  } finally {
    discussionsLoading.value = false
  }
}

async function submitDiscussion() {
  if (!newDiscussion.value.trim()) return ElMessage.warning('请输入内容')
  if (!userStore.isLoggedIn) return ElMessage.warning('请先登录')
  
  submitting.value = true
  try {
    await discussionApi.createDiscussion({
      course_id: route.params.id,
      content: newDiscussion.value
    })
    newDiscussion.value = ''
    await fetchDiscussions()
    ElMessage.success('发表成功，内容审核通过后将显示')
  } catch (e) {
    handleApiError(e, '发表失败')
  } finally {
    submitting.value = false
  }
}

async function toggleReplies(item) {
  // 如果已经展开且有数据，则收起
  if (item.showReplies) {
    item.showReplies = false
    return
  }
  
  // 如果正在加载，直接返回
  if (item.loadingReplies) return
  
  // 如果已经有数据，直接展开
  if (item.replies.length > 0) {
    item.showReplies = true
    return
  }
  
  // 否则加载数据
  item.loadingReplies = true
  try {
    const res = await discussionApi.getReplies(item.id)
    item.replies = res.data.replies || []
    item.showReplies = true
  } catch (e) {
    handleApiError(e, '获取回复失败')
  } finally {
    item.loadingReplies = false
  }
}

async function submitReply(item) {
  if (!item.replyContent?.trim()) return ElMessage.warning('请输入内容')
  if (!userStore.isLoggedIn) return ElMessage.warning('请先登录')
  
  submitting.value = true
  try {
    await discussionApi.createDiscussion({
      course_id: route.params.id,
      parent_id: item.id,
      content: item.replyContent
    })
    item.replyContent = ''
    const res = await discussionApi.getReplies(item.id)
    item.replies = res.data.replies || []
    item.reply_count = (item.reply_count || 0) + 1
    ElMessage.success('回复成功，内容审核通过后将显示')
  } catch (e) {
    handleApiError(e, '回复失败')
  } finally {
    submitting.value = false
  }
}

function canDelete(item) {
  if (!userStore.isLoggedIn) return false
  return userStore.user.role === 'admin' || item.user_id === userStore.user.id
}

async function deleteDiscussion(item, parent = null) {
  try {
    await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
    await discussionApi.deleteDiscussion(item.id)
    if (parent) {
      parent.replies = parent.replies.filter(r => r.id !== item.id)
      parent.reply_count = Math.max(0, (parent.reply_count || 0) - 1)
    } else {
      discussions.value = discussions.value.filter(d => d.id !== item.id)
    }
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') handleApiError(e, '删除失败')
  }
}

async function deleteReply(reply, parentItem) {
  try {
    await ElMessageBox.confirm('确定删除这条回复？', '提示', { type: 'warning' })
    await discussionApi.deleteDiscussion(reply.id)
    parentItem.replies = parentItem.replies.filter(r => r.id !== reply.id)
    parentItem.reply_count = Math.max(0, (parentItem.reply_count || 0) - 1)
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') handleApiError(e, '删除失败')
  }
}

// 获取评价列表
async function fetchReviews() {
  try {
    const res = await interactionApi.getCourseReviews(route.params.id)
    reviews.value = res.data.reviews || []
    // 检查当前用户是否已评价
    if (userStore.isLoggedIn) {
      hasReviewed.value = reviews.value.some(r => r.user_id === userStore.user.id)
    }
  } catch (e) {
    console.error('获取评价失败')
  }
}

// 提交评价
async function submitReview() {
  if (!newReview.value.content.trim()) {
    ElMessage.warning('请输入评价内容')
    return
  }
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  
  submittingReview.value = true
  try {
    await interactionApi.createReview({
      course_id: route.params.id,
      rating: newReview.value.rating,
      content: newReview.value.content
    })
    newReview.value = { rating: 5, content: '' }
    await fetchReviews()
    ElMessage.success('评价提交成功，内容审核通过后将显示')
  } catch (e) {
    handleApiError(e, '评价提交失败')
  } finally {
    submittingReview.value = false
  }
}

async function fetchLessonProgress() {
  try {
    const enrollRes = await courseApi.getMyEnrollments()
    const enrollments = enrollRes.data.enrollments || enrollRes.data || []
    const enrollment = enrollments.find(e => e.course_id === course.value?.id)
    
    if (enrollment && enrollment.progress > 0) {
      const completedCount = Math.round((enrollment.progress / 100) * lessons.value.length)
      lessonProgress.value = lessons.value.slice(0, completedCount).map(l => ({
        lesson_id: l.id, completed: true
      }))
      // 初始化已上报集合
      reportedCompletedLessons.value = new Set(lessonProgress.value.map(p => p.lesson_id))
    }
  } catch (e) {
    // 进度获取失败不阻塞页面渲染，仅打印日志
    console.error('获取进度失败', e)
  }
}

onMounted(async () => {
  try {
    const res = await courseApi.getCourse(route.params.id)
    course.value = res.data.course
    lessons.value = res.data.lessons || []

    // 并行请求不依赖的数据
    const tasks = [fetchNotices(), fetchReviews()]
    if (userStore.isLoggedIn) tasks.push(fetchDiscussions())
    
    await Promise.allSettled([
      fetchLessonProgress(),
      ...tasks
    ])
    
    // 默认选中第一个课时
    if (lessons.value.length > 0) {
      currentLesson.value = lessons.value[0]
    }
  } catch (e) {
    handleApiError(e, '获取课程信息失败')
  } finally {
    pageLoading.value = false
  }
})

// 组件卸载时清理资源
onUnmounted(() => {
  if (videoPlayerRef.value) {
    videoPlayerRef.value.pause()
  }
})
</script>

<style scoped>
/* ... 保持原有样式不变 ... */
.lesson-item {
  cursor: pointer;
  transition: all 0.2s;
}

.lesson-item:hover {
  background-color: #f5f7fa;
}

.lesson-item.active {
  background-color: #e6f0ff;
  border-left: 3px solid #409eff;
}

.lesson-item.completed {
  background-color: #f0f9eb;
}

.lesson-index {
  width: 24px;
  text-align: center;
  font-weight: 500;
}

.lesson-title {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 自定义标签页样式 */
.nav-tabs-custom {
  display: flex;
  background: #fafafa;
}

.nav-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  border: none;
  background: none;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  position: relative;
}

.nav-tab:hover {
  color: #409eff;
  background: #f0f0f0;
}

.nav-tab.active {
  color: #409eff;
  border-bottom-color: #409eff;
  background: #fff;
}

.nav-tab .badge {
  position: absolute;
  top: 6px;
  right: 15%;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: #f56c6c;
  border-radius: 8px;
  font-size: 10px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 进度区域 */
.progress-section {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
}

/* 教师头像 */
.teacher-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 讨论项 */
.discussion-item:hover {
  background: #fafafa;
}

.discussion-item.pending-item {
  background: #fdf6ec;
  border-left: 3px solid #e6a23c;
}

.discussion-item.pending-item:hover {
  background: #faecd8;
}

.reply-item {
  font-size: 13px;
}

/* 公告项 */
.notice-item:hover {
  background: #fafafa;
}

.notice-title {
  font-size: 14px;
  font-weight: 500;
}

.notice-content {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 标签内容区域 */
.tab-content-area {
  height: calc(100vh - 180px);
  overflow-y: auto;
}

/* 全局 Loading */
.global-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  color: #409eff;
  font-size: 16px;
}

/* 评价项 */
.review-item:hover {
  background: #fafafa;
}

.review-item.pending-item {
  background: #fdf6ec;
  border-left: 3px solid #e6a23c;
}

.review-item.pending-item:hover {
  background: #faecd8;
}

.reply-item {
  font-size: 13px;
}

/* 响应式 */
@media (max-width: 992px) {
  .sidebar {
    width: 320px !important;
  }
  
  .tab-content-area {
    height: calc(100vh - 160px);
  }
}

@media (max-width: 768px) {
  .course-learn {
    flex-direction: column;
    height: auto;
    min-height: 100vh;
  }
  
  .video-area {
    height: 50vh;
    min-height: 300px;
  }
  
  .video-header {
    padding: 10px 12px;
  }
  
  .video-header .title-text {
    font-size: 14px;
    max-width: 180px;
  }
  
  .back-btn {
    padding: 6px 10px;
    font-size: 12px;
  }
  
  .video-info {
    padding: 12px;
  }
  
  .video-info h5 {
    font-size: 14px;
  }
  
  .sidebar {
    position: fixed;
    right: 0;
    top: 0;
    height: 100vh;
    width: 100% !important;
    max-width: 100%;
    z-index: 1000;
    transform: translateX(100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar:not(.d-none) {
    transform: translateX(0);
  }
  
  .progress-section {
    padding: 12px !important;
  }
  
  .nav-tab {
    padding: 10px 6px;
    font-size: 12px;
  }
  
  .nav-tab .el-icon {
    font-size: 16px;
  }
  
  .tab-content-area {
    height: calc(100vh - 200px);
  }
  
  .lesson-item {
    padding: 10px 12px;
  }
  
  .discussion-item,
  .review-item,
  .notice-item {
    padding: 10px !important;
  }
  
  .teacher-avatar {
    width: 60px;
    height: 60px;
  }
  
  /* 移动端遮罩层 */
  .sidebar-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 999;
  }
}

@media (max-width: 576px) {
  .video-area {
    height: 45vh;
    min-height: 250px;
  }
  
  .lesson-card {
    padding: 8px 10px;
  }
  
  .lesson-number {
    width: 24px;
    height: 24px;
    font-size: 12px;
  }
  
  .lesson-name {
    font-size: 13px;
  }
  
  .tab-content-area {
    height: calc(100vh - 180px);
  }
}
</style>
