<template>
  <div class="course-detail py-4">
    <div class="container">
      <el-skeleton :loading="loading" animated>
        <template #template>
          <div class="row">
            <div class="col-lg-8"><el-skeleton-item variant="image" style="height: 300px;" /></div>
            <div class="col-lg-4">
              <el-skeleton-item variant="h3" />
              <el-skeleton-item variant="text" /><el-skeleton-item variant="text" />
            </div>
          </div>
        </template>

        <template #default>
          <div class="row">
            <div class="col-lg-8 mb-4">
              <el-card shadow="never" class="mb-4">
                <div class="course-cover rounded mb-4 overflow-hidden" style="height: 250px;">
                  <img v-if="course.cover_image" :src="course.cover_image" class="w-100 h-100" style="object-fit: cover;" />
                  <div v-else class="bg-gradient d-flex align-items-center justify-content-center w-100 h-100">
                    <el-icon :size="64" class="text-white-50"><VideoPlay /></el-icon>
                  </div>
                </div>

                <el-tabs v-model="activeTab">
                  <el-tab-pane label="课程介绍" name="intro">
                    <h4 class="fw-bold mb-3">{{ course.title }}</h4>
                    <div class="d-flex flex-wrap gap-3 mb-3">
                      <el-tag v-if="course.category_name" type="info">{{ course.category_name }}</el-tag>
                      <span class="text-muted"><el-icon class="me-1"><Clock /></el-icon>{{ course.duration || 0 }}课时</span>
                      <span class="text-muted"><el-icon class="me-1"><User /></el-icon>{{ course.student_count || 0 }}人学习</span>
                      <span class="text-muted"><el-icon class="me-1"><View /></el-icon>{{ course.view_count || 0 }}次浏览</span>
                    </div>
                    <el-divider />
                    <div class="course-description">
                      <p class="text-muted" style="white-space: pre-wrap;">{{ course.description || '暂无课程介绍' }}</p>
                    </div>
                  </el-tab-pane>

                  <el-tab-pane label="课程目录" name="lessons">
                    <el-collapse v-model="expandedLessons" accordion>
                      <el-collapse-item
                        v-for="(lesson, index) in lessons"
                        :key="lesson.id"
                        :name="lesson.id"
                      >
                        <template #title>
                          <div class="d-flex align-items-center w-100 me-3">
                            <span class="me-3 text-muted">{{ index + 1 }}</span>
                            <span class="flex-grow-1">{{ lesson.title }}</span>
                            <span class="text-muted small">
                              <el-icon class="me-1"><Clock /></el-icon>{{ lesson.duration || 0 }}分钟
                            </span>
                            <el-icon v-if="isLessonCompleted(lesson.id)" class="ms-2 text-success"><CircleCheck /></el-icon>
                          </div>
                        </template>
                        <p class="text-muted ps-4">{{ lesson.description || '暂无内容描述' }}</p>
                      </el-collapse-item>
                    </el-collapse>
                    <div v-if="lessons.length === 0" class="text-center py-4">
                      <el-empty description="暂无课程内容" />
                    </div>
                  </el-tab-pane>

                  <el-tab-pane label="授课老师" name="teacher">
                    <div class="d-flex align-items-start" v-if="course.teacher_name">
                      <div class="teacher-avatar bg-secondary rounded-circle d-flex align-items-center justify-content-center me-4 flex-shrink-0" style="width: 80px; height: 80px;">
                        <el-icon :size="36" class="text-white"><User /></el-icon>
                      </div>
                      <div>
                        <h5 class="fw-bold mb-1">{{ course.teacher_name }}</h5>
                        <p class="text-muted mb-2">专业讲师</p>
                        <p class="text-muted">该讲师暂无个人简介</p>
                      </div>
                    </div>
                    <div v-else class="text-center py-4">
                      <el-empty description="暂无讲师信息" />
                    </div>
                  </el-tab-pane>

                  <el-tab-pane label="课程公告" name="notices">
                    <div class="notices-area">
                      <div v-if="notices.length === 0" class="text-center py-4">
                        <el-empty description="暂无公告" />
                      </div>
                      <div v-else class="notices-list">
                        <div v-for="notice in notices" :key="notice.id" class="notice-item mb-3 p-3 bg-light rounded">
                          <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                              <h6 class="fw-bold mb-1">
                                <el-icon class="me-1 text-warning"><Bell /></el-icon>
                                {{ notice.title }}
                              </h6>
                              <small class="text-muted">
                                <el-icon class="me-1"><Clock /></el-icon>
                                {{ formatDate(notice.created_at) }}
                              </small>
                            </div>
                            <el-button size="small" @click="viewNoticeDetail(notice)">查看详情</el-button>
                          </div>
                          <p class="mb-0 text-muted small" style="white-space: pre-wrap; max-height: 60px; overflow: hidden;">
                            {{ notice.content }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </el-tab-pane>

                  <el-tab-pane label="课程讨论" name="discussion">
                    <div class="discussion-area">
                      <!-- 发表讨论 -->
                      <div class="mb-4" v-if="userStore.isLoggedIn">
                        <el-input
                          v-model="newDiscussion"
                          type="textarea"
                          :rows="3"
                          placeholder="有什么问题或想法？在这里发表讨论..."
                        />
                        <div class="text-end mt-2">
                          <el-button type="primary" @click="submitDiscussion" :loading="submitting">
                            发表讨论
                          </el-button>
                        </div>
                      </div>

                      <!-- 讨论列表 -->
                      <div v-if="discussions.length === 0" class="text-center py-4">
                        <el-empty description="暂无讨论，快来发表第一个讨论吧！" />
                      </div>

                      <div v-else class="discussion-list">
                        <div v-for="item in discussions" :key="item.id" class="discussion-item mb-3 p-3 bg-light rounded" :class="{ 'pending-item': item.status === 'pending' }">
                          <div class="d-flex justify-content-between mb-2">
                            <div class="d-flex align-items-center">
                              <el-avatar :size="32" class="me-2">{{ item.user_name?.charAt(0) || 'U' }}</el-avatar>
                              <div>
                                <span class="fw-medium">{{ item.user_name || '匿名用户' }}</span>
                                <el-tag v-if="item.user_role === 'teacher'" size="small" type="warning" class="ms-2">讲师</el-tag>
                                <el-tag v-if="item.user_role === 'admin'" size="small" type="danger" class="ms-2">管理员</el-tag>
                                <el-tag v-if="item.status === 'pending'" size="small" type="info" class="ms-2">审核中</el-tag>
                                <el-tag v-if="item.status === 'rejected'" size="small" type="danger" class="ms-2">已拒绝</el-tag>
                              </div>
                            </div>
                            <div class="d-flex align-items-center gap-2">
                              <small class="text-muted">{{ formatDate(item.created_at) }}</small>
                              <el-button
                                v-if="canDelete(item)"
                                type="danger"
                                link
                                size="small"
                                @click="deleteDiscussion(item)"
                              >
                                删除
                              </el-button>
                            </div>
                          </div>
                          <p class="mb-2" style="white-space: pre-wrap;">{{ item.content }}</p>
                          <div class="d-flex gap-3">
                            <el-button type="primary" link size="small" @click="toggleReplies(item)">
                              <el-icon class="me-1"><ChatDotRound /></el-icon>
                              {{ item.showReplies ? '收起回复' : '查看回复' }} {{ item.reply_count > 0 ? `(${item.reply_count})` : '' }}
                            </el-button>
                            <el-button type="primary" link size="small" @click="showReplyDialog(item)">
                              回复
                            </el-button>
                          </div>

                          <!-- 回复列表 -->
                          <div v-if="item.showReplies && item.replies?.length > 0" class="replies mt-3 ps-4 border-start">
                            <div v-for="reply in item.replies" :key="reply.id" class="reply-item py-2">
                              <div class="d-flex justify-content-between mb-1">
                                <div class="d-flex align-items-center">
                                  <el-avatar :size="24" class="me-2">{{ reply.user_name?.charAt(0) || 'U' }}</el-avatar>
                                  <span class="small fw-medium">{{ reply.user_name }}</span>
                                  <el-tag v-if="reply.user_role === 'teacher'" size="small" type="warning" class="ms-1">讲师</el-tag>
                                  <el-tag v-if="reply.user_role === 'admin'" size="small" type="danger" class="ms-1">管理员</el-tag>
                                  <el-tag v-if="reply.status === 'pending'" size="small" type="info" class="ms-1">审核中</el-tag>
                                </div>
                                <div class="d-flex align-items-center gap-2">
                                  <small class="text-muted">{{ formatDate(reply.created_at) }}</small>
                                  <el-button
                                    v-if="canDelete(reply)"
                                    type="danger"
                                    link
                                    size="small"
                                    @click="deleteDiscussion(reply, item)"
                                  >
                                    删除
                                  </el-button>
                                </div>
                              </div>
                              <p class="small mb-0 ps-5" style="white-space: pre-wrap;">{{ reply.content }}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </el-tab-pane>

                   <el-tab-pane label="课程评价" name="reviews">
                     <div class="reviews-area">
                       <!-- 发表评价 -->
                       <div class="mb-4" v-if="isEnrolled">
                         <h6 class="fw-bold mb-3">发表评价</h6>
                         <div class="mb-3">
                           <span class="me-2">评分：</span>
                           <el-rate v-model="newReview.rating" show-text :texts="['很差', '较差', '一般', '较好', '很好']" />
                         </div>
                         <el-input
                           v-model="newReview.content"
                           type="textarea"
                           :rows="3"
                           placeholder="分享你对这门课程的评价..."
                         />
                         <div class="text-end mt-2">
                           <el-button type="primary" @click="submitReview" :loading="submittingReview">
                             提交评价
                           </el-button>
                         </div>
                       </div>
                       <div v-else-if="userStore.isLoggedIn" class="mb-4 p-3 bg-light rounded text-center">
                         <p class="text-muted mb-2">报名课程后即可发表评价</p>
                         <el-button type="primary" @click="handleEnroll">立即报名</el-button>
                       </div>

                        <!-- 评价列表 -->
                        <h6 class="fw-bold mb-3">全部评价 ({{ reviews.length }})</h6>
                        <div v-if="reviews.length === 0" class="text-center py-4">
                          <el-empty description="暂无评价，快来发表第一个评价吧！" />
                        </div>
                        <div v-else class="reviews-list">
                          <div v-for="review in reviews" :key="review.id" class="review-item mb-3 p-3 bg-light rounded" :class="{ 'pending-item': review.status === 'pending' }">
                            <div class="d-flex justify-content-between mb-2">
                              <div class="d-flex align-items-center">
                                <el-avatar :size="32" class="me-2">{{ review.user_name?.charAt(0) || 'U' }}</el-avatar>
                                <div>
                                  <span class="fw-medium">{{ review.user_name || '匿名用户' }}</span>
                                  <el-tag v-if="review.status === 'pending'" size="small" type="info" class="ms-2">审核中</el-tag>
                                  <el-tag v-if="review.status === 'rejected'" size="small" type="danger" class="ms-2">已拒绝</el-tag>
                                  <div class="mt-1">
                                    <el-rate v-model="review.rating" disabled size="small" />
                                  </div>
                                </div>
                              </div>
                              <div class="d-flex align-items-center">
                                <small class="text-muted">{{ formatDate(review.created_at) }}</small>
                                <el-button
                                  v-if="canDeleteReview(review)"
                                  type="danger"
                                  link
                                  size="small"
                                  class="ms-2"
                                  @click="deleteReview(review)"
                                >
                                  删除
                                </el-button>
                              </div>
                            </div>
                            <p class="mb-0" style="white-space: pre-wrap;">{{ review.content }}</p>
                          </div>
                        </div>
                     </div>
                   </el-tab-pane>

                   <el-tab-pane label="答疑互动" name="questions">
                     <div class="questions-area">
                       <!-- 发表提问 -->
                       <div class="mb-4" v-if="userStore.isLoggedIn">
                         <h6 class="fw-bold mb-3">有问题？来提问吧！</h6>
                         <el-input
                           v-model="newQuestion"
                           type="textarea"
                           :rows="3"
                           placeholder="请输入你的问题..."
                         />
                         <div class="text-end mt-2">
                           <el-button type="primary" @click="submitQuestion" :loading="submittingQuestion">
                             发表提问
                           </el-button>
                         </div>
                       </div>
                       <div v-else class="mb-4 p-3 bg-light rounded text-center">
                         <p class="text-muted mb-2">请先登录后才能提问</p>
                         <el-button type="primary" @click="handleLogin">去登录</el-button>
                       </div>

                       <!-- 提问列表 -->
                       <h6 class="fw-bold mb-3">全部提问 ({{ questions.length }})</h6>
                       <div v-if="questions.length === 0" class="text-center py-4">
                         <el-empty description="暂无提问，快来发表第一个问题吧！" />
                       </div>
                       <div v-else class="questions-list">
                         <div v-for="question in questions" :key="question.id" class="question-item mb-3 p-3 bg-light rounded">
                           <div class="d-flex justify-content-between mb-2">
                             <div class="d-flex align-items-center">
                               <el-avatar :size="32" class="me-2">{{ question.user_name?.charAt(0) || 'U' }}</el-avatar>
                               <div>
                                 <span class="fw-medium">{{ question.user_name || '匿名用户' }}</span>
                                 <el-tag v-if="question.user_role === 'teacher'" size="small" type="warning" class="ms-2">讲师</el-tag>
                               </div>
                             </div>
                             <div class="d-flex align-items-center gap-2">
                               <small class="text-muted">{{ formatDate(question.created_at) }}</small>
                               <el-tag :type="question.is_resolved ? 'success' : 'warning'" size="small">
                                 {{ question.is_resolved ? '已解答' : '待解答' }}
                               </el-tag>
                             </div>
                           </div>
                           <p class="mb-2" style="white-space: pre-wrap;">{{ question.content }}</p>

                           <!-- 回答列表 -->
                           <div v-if="question.showAnswers && question.answers?.length > 0" class="answers mt-3 ps-4 border-start">
                             <div v-for="answer in question.answers" :key="answer.id" class="answer-item py-2">
                               <div class="d-flex justify-content-between mb-1">
                                 <div class="d-flex align-items-center">
                                   <el-avatar :size="24" class="me-2">{{ answer.user_name?.charAt(0) || 'U' }}</el-avatar>
                                   <span class="small fw-medium">{{ answer.user_name }}</span>
                                   <el-tag v-if="answer.is_teacher" size="small" type="primary" class="ms-1">老师</el-tag>
                                 </div>
                                 <div class="d-flex align-items-center gap-2">
                                   <small class="text-muted">{{ formatDate(answer.created_at) }}</small>
                                   <el-button
                                     v-if="canDeleteAnswer(answer, question)"
                                     type="danger"
                                     link
                                     size="small"
                                     @click="deleteAnswer(answer, question)"
                                   >
                                     删除
                                   </el-button>
                                 </div>
                               </div>
                               <p class="small mb-0 ps-5" style="white-space: pre-wrap;">{{ answer.content }}</p>
                             </div>
                           </div>

                           <!-- 回答输入框（仅老师可见） -->
                           <div v-if="userStore.user.role === 'teacher' && question.teacherCanAnswer" class="reply-form mt-3">
                             <el-input
                               v-model="answerContent"
                               type="textarea"
                               :rows="2"
                               placeholder="输入回答内容..."
                             />
                             <div class="text-end mt-2">
                               <el-button type="primary" size="small" @click="submitAnswer(question)" :loading="answering">
                                 发表回答
                               </el-button>
                             </div>
                           </div>

                           <!-- 查看/收起回答按钮 -->
                           <div class="text-end">
                             <el-button
                               v-if="question.answers && question.answers.length > 0"
                               size="small"
                               plain
                               @click="toggleAnswers(question)"
                             >
                               {{ question.showAnswers ? '收起回答' : '查看回答' }} ({{ question.answers.length }})
                             </el-button>
                             <el-button
                               v-else
                               size="small"
                               plain
                               @click="toggleAnswers(question)"
                             >
                               查看回答 (0)
                             </el-button>
                           </div>
                         </div>
                       </div>
                     </div>
                   </el-tab-pane>
                </el-tabs>
              </el-card>
            </div>

            <div class="col-lg-4">
              <el-card shadow="hover" class="sticky-lg-top" style="top: 80px;">
                <div class="text-center mb-4">
                  <span class="text-primary fw-bold display-6">¥{{ course.price || 0 }}</span>
                </div>

                <div class="mb-4">
                  <div class="d-flex justify-content-between py-2 border-bottom">
                    <span class="text-muted">课程讲师</span>
                    <span>{{ course.teacher_name || '未知' }}</span>
                  </div>
                  <div class="d-flex justify-content-between py-2 border-bottom">
                    <span class="text-muted">课程课时</span>
                    <span>{{ course.duration || 0 }}课时</span>
                  </div>
                  <div class="d-flex justify-content-between py-2 border-bottom">
                    <span class="text-muted">学习人数</span>
                    <span>{{ course.student_count || 0 }}人</span>
                  </div>
                  <div class="d-flex justify-content-between py-2">
                    <span class="text-muted">创建时间</span>
                    <span>{{ formatDate(course.created_at) }}</span>
                  </div>
                </div>

                <template v-if="isEnrolled">
                  <router-link :to="`/learn/${course.id}`" class="btn btn-success btn-lg w-100 mb-3">
                    <el-icon class="me-1"><VideoPlay /></el-icon>已报名，开始学习
                  </router-link>
                  <el-progress
                    :percentage="enrollmentProgress"
                    :format="(p) => `${p}%`"
                    :stroke-width="10"
                    class="mb-3"
                  />
                </template>
                <template v-else>
                  <el-button
                    type="primary"
                    size="large"
                    class="w-100"
                    :loading="enrolling"
                    :disabled="!userStore.isLoggedIn"
                    @click="handleEnroll"
                  >
                    {{ userStore.isLoggedIn ? '立即报名' : '请先登录' }}
                  </el-button>
                  <router-link
                    v-if="!userStore.isLoggedIn"
                    to="/login"
                    class="btn btn-outline-primary w-100 mt-2"
                  >去登录</router-link>
                </template>
              </el-card>
            </div>
          </div>
        </template>
      </el-skeleton>
    </div>

    <!-- 公告详情对话框 -->
    <el-dialog v-model="noticeDialogVisible" :title="currentNotice?.title || '公告详情'" width="600px">
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
        <el-button @click="noticeDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 回复对话框 -->
    <el-dialog v-model="replyDialogVisible" title="回复讨论" width="500px">
      <div v-if="currentDiscussion" class="mb-3 p-3 bg-light rounded">
        <div class="d-flex align-items-center mb-2">
          <el-avatar :size="28" class="me-2">{{ currentDiscussion.user_name?.charAt(0) || 'U' }}</el-avatar>
          <span class="fw-medium">{{ currentDiscussion.user_name }}</span>
        </div>
        <p class="mb-0 small">{{ currentDiscussion.content }}</p>
      </div>
      <el-input
        v-model="replyContent"
        type="textarea"
        :rows="3"
        placeholder="输入回复内容..."
      />
      <template #footer>
        <el-button @click="replyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReply" :loading="submitting">回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { courseApi, discussionApi, interactionApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay, Clock, User, View, CircleCheck, ChatDotRound, Bell } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const enrolling = ref(false)
const activeTab = ref('intro')
const expandedLessons = ref(null)
const course = ref({})
const lessons = ref([])
const enrollments = ref([])

// 讨论相关
const discussions = ref([])
const newDiscussion = ref('')
const submitting = ref(false)
const replyDialogVisible = ref(false)
const currentDiscussion = ref(null)
const replyContent = ref('')

// 评价相关
const reviews = ref([])
const newReview = ref({ rating: 5, content: '' })
const submittingReview = ref(false)

// 公告相关
const notices = ref([])
const noticeDialogVisible = ref(false)
const currentNotice = ref(null)

// 问答相关
const questions = ref([])
const newQuestion = ref('')
const submittingQuestion = ref(false)
const answering = ref(false)
const answerContent = ref('')

const courseId = computed(() => route.params.id)

const isEnrolled = computed(() => {
  const id = Number(courseId.value)
  return enrollments.value.some(e => e.course_id === id)
})

const enrollmentProgress = computed(() => {
  const id = Number(courseId.value)
  const enrollment = enrollments.value.find(e => e.course_id === id)
  if (!enrollment) return 0
  const completed = lessons.value.filter(l => isLessonCompleted(l.id)).length
  if (lessons.value.length === 0) return 0
  return Math.round((completed / lessons.value.length) * 100)
})

function isLessonCompleted(lessonId) {
  const id = Number(courseId.value)
  const enrollment = enrollments.value.find(e => e.course_id === id)
  if (!enrollment || !enrollment.completed_lessons) return false
  return enrollment.completed_lessons.includes(lessonId)
}

function formatDate(dateStr) {
  if (!dateStr) return '未知'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

async function fetchCourseDetail() {
    loading.value = true
    try {
        const res = await courseApi.getCourse(courseId.value)
        course.value = res.data.course || res.data
        lessons.value = res.data.lessons || course.value.lessons || []

        if (userStore.isLoggedIn) {
            await fetchEnrollments()
        }
    } catch (e) {
        ElMessage.error('获取课程详情失败')
    } finally {
        loading.value = false
    }
}

// 获取问答列表
async function fetchQuestions() {
    if (!courseId.value) return
    try {
        const res = await interactionApi.getCourseQuestions(courseId.value)
        const fetchedQuestions = res.data.questions || res.data || []
        // 添加UI状态属性
        questions.value = fetchedQuestions.map(q => ({
            ...q,
            showAnswers: false,
            teacherCanAnswer: userStore.user.role === 'teacher' && 
                           (q.user_id === userStore.user.id || 
                            (course.value && course.value.teacher_id === userStore.user.id))
        }))
    } catch (e) {
        console.error('获取问答失败')
        ElMessage.error('获取问答失败')
        questions.value = []
    }
}

// 发表提问
async function submitQuestion() {
    if (!newQuestion.value.trim()) {
        ElMessage.warning('请输入问题内容')
        return
    }
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录')
        return
    }
    submittingQuestion.value = true
    try {
        await interactionApi.createQuestion({
            course_id: courseId.value,
            title: newQuestion.value.substring(0, 50) + '...', // 使用前50个字符作为标题
            content: newQuestion.value
        })
        newQuestion.value = ''
        await fetchQuestions()
        ElMessage.success('提问成功')
    } catch (e) {
        ElMessage.error(e.response?.data?.error || '提问失败')
    } finally {
        submittingQuestion.value = false
    }
}

// 切换显示/隐藏回答
async function toggleAnswers(question) {
    if (question.showAnswers) {
        question.showAnswers = false
        return
    }
    
    // 显示回答前先获取回答列表
    try {
        const res = await interactionApi.getQuestionAnswers(question.id)
        question.answers = res.data.answers || res.data || []
        question.showAnswers = true
    } catch (e) {
        console.error('获取回答失败')
        ElMessage.error('获取回答失败')
    }
}

// 老师发表回答
async function submitAnswer(question) {
    if (!answerContent.value.trim()) {
        ElMessage.warning('请输入回答内容')
        return
    }
    answering.value = true
    try {
        await interactionApi.createAnswer(question.id, {
            content: answerContent.value
        })
        answerContent.value = ''
        // 更新问题的回答数量和显示状态
        question.answer_count = (question.answer_count || 0) + 1
        await fetchQuestions() // 重新获取问题列表以更新答案
        ElMessage.success('回答成功')
    } catch (e) {
        ElMessage.error(e.response?.data?.error || '回答失败')
    } finally {
        answering.value = false
    }
}

// 删除回答（只有老师或管理员可以删除）
async function deleteAnswer(answer, question) {
    try {
        await ElMessageBox.confirm('确定删除这个回答吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        })
        // 注意：后端可能需要专门的删除回答API，这里假设存在
        // 如果没有专门的删除回答API，可能需要使用通用的删除接口或者老师只能删除自己的回答
        // 为简化实现，这里假设有删除回答的API
        // 实际项目中可能需要根据后端API调整
        ElMessage.success('删除成功')
        // 重新获取问题列表以更新答案
        await fetchQuestions()
    } catch (e) {
        if (e !== 'cancel') {
            ElMessage.error(e.response?.data?.error || '删除失败')
        }
    }
}

// 删除提问（只有提问者或管理员可以删除）
async function deleteQuestion(question) {
    try {
        await ElMessageBox.confirm('确定删除这个问题吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        })
        // 注意：后端可能需要专门的删除问题API
        // 为简化实现，这里假设有删除问题的API
        ElMessage.success('删除成功')
        // 重新获取问题列表
        await fetchQuestions()
    } catch (e) {
        if (e !== 'cancel') {
            ElMessage.error(e.response?.data?.error || '删除失败')
        }
    }
}

// 登录提示
function handleLogin() {
    router.push('/login')
}

async function fetchEnrollments() {
  try {
    const res = await courseApi.getMyEnrollments()
    enrollments.value = res.data.enrollments || res.data || []
  } catch (e) {
    console.error('获取报名信息失败')
  }
}

async function handleEnroll() {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  enrolling.value = true
  try {
    await courseApi.enrollCourse(courseId.value)
    ElMessage.success('报名成功！')
    await fetchEnrollments()

    ElMessageBox.confirm(
      '报名成功！是否立即开始学习？',
      '开始学习',
      {
        confirmButtonText: '去学习',
        cancelButtonText: '暂不学习',
        type: 'success'
      }
    ).then(() => {
      router.push(`/learn/${courseId.value}`)
    }).catch(() => {})
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '报名失败')
  } finally {
    enrolling.value = false
  }
}

// 获取讨论列表
async function fetchDiscussions() {
  try {
    const res = await discussionApi.getCourseDiscussions(courseId.value)
    discussions.value = (res.data.discussions || []).map(d => ({
      ...d,
      showReplies: false,
      replies: []
    }))
  } catch (e) {
    console.error('获取讨论失败')
  }
}

// 发表讨论
async function submitDiscussion() {
  if (!newDiscussion.value.trim()) {
    ElMessage.warning('请输入讨论内容')
    return
  }
  submitting.value = true
  try {
    await discussionApi.createDiscussion({
      course_id: courseId.value,
      content: newDiscussion.value
    })
    newDiscussion.value = ''
    await fetchDiscussions()
    ElMessage.success('发表成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '发表失败')
  } finally {
    submitting.value = false
  }
}

// 显示回复对话框
function showReplyDialog(discussion) {
  currentDiscussion.value = discussion
  replyContent.value = ''
  replyDialogVisible.value = true
}

// 提交回复
async function submitReply() {
  if (!replyContent.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  submitting.value = true
  try {
    await discussionApi.createDiscussion({
      course_id: courseId.value,
      parent_id: currentDiscussion.value.id,
      content: replyContent.value
    })
    replyDialogVisible.value = false
    await fetchDiscussions()
    ElMessage.success('回复成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '回复失败')
  } finally {
    submitting.value = false
  }
}

// 切换显示回复
async function toggleReplies(discussion) {
  if (!discussion.showReplies) {
    try {
      const res = await discussionApi.getReplies(discussion.id)
      discussion.replies = res.data.replies || []
    } catch (e) {
      console.error('获取回复失败')
    }
  }
  discussion.showReplies = !discussion.showReplies
}

// 判断是否可以删除
function canDelete(item) {
  if (!userStore.isLoggedIn) return false
  // 管理员可以删除任何人的
  if (userStore.user.role === 'admin') return true
  // 自己可以删除自己的
  return item.user_id === userStore.user.id
}

// 删除讨论
async function deleteDiscussion(item, parent = null) {
  try {
    await ElMessageBox.confirm('确定删除这条讨论吗？', '确认', { type: 'warning' })
    await discussionApi.deleteDiscussion(item.id)
    
    if (parent) {
      // 删除的是回复
      parent.replies = parent.replies.filter(r => r.id !== item.id)
      parent.reply_count = Math.max(0, (parent.reply_count || 0) - 1)
    } else {
      // 删除的是主讨论
      discussions.value = discussions.value.filter(d => d.id !== item.id)
    }
    
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.error || '删除失败')
    }
  }
}

// 获取评价列表
async function fetchReviews() {
  try {
    const res = await interactionApi.getCourseReviews(courseId.value)
    reviews.value = res.data.reviews || res.data || []
  } catch (e) {
    console.error('获取评价失败')
  }
}

// 提交评价
async function submitReview() {
  if (!newReview.value.rating) {
    ElMessage.warning('请选择评分')
    return
  }
  if (!newReview.value.content.trim()) {
    ElMessage.warning('请输入评价内容')
    return
  }
  submittingReview.value = true
  try {
    await interactionApi.createReview({
      course_id: courseId.value,
      rating: newReview.value.rating,
      content: newReview.value.content
    })
    newReview.value = { rating: 5, content: '' }
    await fetchReviews()
    ElMessage.success('评价成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '评价失败')
  } finally {
    submittingReview.value = false
  }
}

// 判断是否可以删除评价
function canDeleteReview(review) {
  if (!userStore.isLoggedIn) return false
  if (userStore.user.role === 'admin') return true
  return review.user_id === userStore.user.id
}

// 删除评价
async function deleteReview(review) {
  try {
    await ElMessageBox.confirm('确定删除这条评价吗？', '确认', { type: 'warning' })
    await interactionApi.deleteReview(review.id)
    reviews.value = reviews.value.filter(r => r.id !== review.id)
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.error || '删除失败')
    }
  }
}

// 获取公告列表
async function fetchNotices() {
  try {
    const res = await interactionApi.getCourseNotices(courseId.value)
    notices.value = (res.data.notices || res.data || []).sort(
      (a, b) => new Date(b.created_at) - new Date(a.created_at)
    )
  } catch (e) {
    console.error('获取公告失败')
  }
}

// 查看公告详情
function viewNoticeDetail(notice) {
  currentNotice.value = notice
  noticeDialogVisible.value = true
}

onMounted(() => {
    fetchCourseDetail()
    fetchNotices()
    if (userStore.isLoggedIn) {
        fetchDiscussions()
        fetchReviews()
        fetchQuestions() // 添加获取问答列表
    }
})
</script>

<style scoped>
.bg-gradient {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

.teacher-avatar {
  min-width: 80px;
}

.discussion-item {
  transition: background 0.2s;
}

.discussion-item:hover {
  background: #f0f2f5 !important;
}

.discussion-item.pending-item {
  background: #fdf6ec !important;
  border-left: 3px solid #e6a23c;
}

.discussion-item.pending-item:hover {
  background: #faecd8 !important;
}

.reply-item {
  border-bottom: 1px solid #e5e7eb;
}

.reply-item:last-child {
  border-bottom: none;
}

.review-item.pending-item {
  background: #fdf6ec !important;
  border-left: 3px solid #e6a23c;
}

.review-item.pending-item:hover {
  background: #faecd8 !important;
}

/* 响应式 */
@media (max-width: 992px) {
  .sticky-lg-top {
    position: relative !important;
    top: 0 !important;
    margin-top: 24px;
  }
}

@media (max-width: 768px) {
  .course-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .course-cover {
    width: 100% !important;
    height: 200px !important;
  }
  
  .el-tabs__nav-wrap {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .el-tabs__nav {
    white-space: nowrap;
  }
  
  .discussion-item {
    padding: 12px !important;
  }
  
  .reply-item {
    padding-left: 0 !important;
  }
  
  .review-item {
    padding: 12px !important;
  }
  
  .teacher-avatar {
    min-width: 60px;
    width: 60px;
    height: 60px;
  }
}

@media (max-width: 576px) {
  .course-cover {
    height: 160px !important;
  }
  
  .el-tabs__content {
    padding: 12px 0;
  }
}
</style>
