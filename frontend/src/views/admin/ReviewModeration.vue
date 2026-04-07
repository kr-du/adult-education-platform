<template>
  <div class="review-moderation py-4">
    <div class="container">
      <h2 class="fw-bold mb-4">内容审核管理</h2>

      <!-- 统计卡片 -->
      <div class="row g-4 mb-4">
        <div class="col-lg-3 col-md-6">
          <el-card shadow="hover" class="text-center stat-card" @click="activeTab = 'reviews'">
            <h3 class="fw-bold text-warning mb-1">{{ statistics.pending_reviews }}</h3>
            <p class="text-muted mb-0">待审评价</p>
          </el-card>
        </div>
        <div class="col-lg-3 col-md-6">
          <el-card shadow="hover" class="text-center stat-card" @click="activeTab = 'questions'">
            <h3 class="fw-bold text-info mb-1">{{ statistics.pending_questions }}</h3>
            <p class="text-muted mb-0">待审提问</p>
          </el-card>
        </div>
        <div class="col-lg-3 col-md-6">
          <el-card shadow="hover" class="text-center stat-card" @click="activeTab = 'answers'">
            <h3 class="fw-bold text-primary mb-1">{{ statistics.pending_answers }}</h3>
            <p class="text-muted mb-0">待审回答</p>
          </el-card>
        </div>
        <div class="col-lg-3 col-md-6">
          <el-card shadow="hover" class="text-center stat-card" @click="activeTab = 'discussions'">
            <h3 class="fw-bold text-success mb-1">{{ statistics.pending_discussions }}</h3>
            <p class="text-muted mb-0">待审讨论</p>
          </el-card>
        </div>
      </div>

      <!-- 标签页 -->
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 课程评价审核 -->
        <el-tab-pane label="课程评价" name="reviews">
          <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2 review-mod-header">
            <el-select v-model="reviewStatus" placeholder="状态筛选" clearable size="small" class="review-mod-select">
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
            <el-button type="danger" size="small" class="review-mod-btn" @click="handleDeleteAllApproved('review')">删除全部已通过</el-button>
          </div>
          
          <el-table :data="reviews" stripe border v-loading="reviewsLoading" class="d-none d-md-block">
            <el-table-column prop="user_name" label="用户" width="100" />
            <el-table-column prop="course_title" label="课程" min-width="150" show-overflow-tooltip />
            <el-table-column label="评分" width="80" align="center">
              <template #default="{ row }">
                <span>{{ '⭐'.repeat(row.rating) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" align="center">
              <template #default="{ row }">
                <el-button v-if="row.status === 'pending'" type="success" size="small" @click="handleApprove('review', row.id)">通过</el-button>
                <el-button v-if="row.status === 'pending'" type="warning" size="small" @click="handleReject('review', row.id)">拒绝</el-button>
                <el-button type="danger" size="small" @click="handleDelete('review', row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 移动端评价卡片 -->
          <div class="d-md-none">
            <div v-if="reviews.length === 0 && !reviewsLoading" class="text-center py-4">
              <el-empty description="暂无数据" :image-size="80" />
            </div>
            <div v-else v-loading="reviewsLoading">
              <div v-for="item in reviews" :key="item.id" class="mb-3">
                <el-card shadow="hover">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                      <h6 class="mb-0">{{ item.user_name }}</h6>
                      <small class="text-muted">{{ item.course_title }}</small>
                    </div>
                    <el-tag :type="getStatusType(item.status)" size="small">{{ getStatusText(item.status) }}</el-tag>
                  </div>
                  <div class="mb-2">{{ '⭐'.repeat(item.rating) }}</div>
                  <p class="small text-muted mb-2 text-truncate-2">{{ item.content }}</p>
                  <div class="d-flex gap-2 flex-wrap">
                    <el-button v-if="item.status === 'pending'" type="success" size="small" class="flex-grow-1" @click="handleApprove('review', item.id)">通过</el-button>
                    <el-button v-if="item.status === 'pending'" type="warning" size="small" class="flex-grow-1" @click="handleReject('review', item.id)">拒绝</el-button>
                    <el-button type="danger" size="small" class="flex-grow-1" @click="handleDelete('review', item.id)">删除</el-button>
                  </div>
                </el-card>
              </div>
            </div>
          </div>
          
          <div class="d-flex justify-content-center mt-3">
            <el-pagination v-model:current-page="reviewPage" :page-size="20" :total="reviewTotal" layout="prev, pager, next" background />
          </div>
        </el-tab-pane>

        <!-- 提问审核 -->
        <el-tab-pane label="提问" name="questions">
          <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2 review-mod-header">
            <el-select v-model="questionStatus" placeholder="状态筛选" clearable size="small" class="review-mod-select">
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
            <el-button type="danger" size="small" class="review-mod-btn" @click="handleDeleteAllApproved('question')">删除全部已通过</el-button>
          </div>
          
          <el-table :data="questions" stripe border v-loading="questionsLoading" class="d-none d-md-block">
            <el-table-column prop="user_name" label="用户" width="100" />
            <el-table-column prop="course_title" label="课程" min-width="150" show-overflow-tooltip />
            <el-table-column prop="title" label="标题" min-width="150" show-overflow-tooltip />
            <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" align="center">
              <template #default="{ row }">
                <el-button v-if="row.status === 'pending'" type="success" size="small" @click="handleApprove('question', row.id)">通过</el-button>
                <el-button v-if="row.status === 'pending'" type="warning" size="small" @click="handleReject('question', row.id)">拒绝</el-button>
                <el-button type="danger" size="small" @click="handleDelete('question', row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 移动端提问卡片 -->
          <div class="d-md-none">
            <div v-if="questions.length === 0 && !questionsLoading" class="text-center py-4">
              <el-empty description="暂无数据" :image-size="80" />
            </div>
            <div v-else v-loading="questionsLoading">
              <div v-for="item in questions" :key="item.id" class="mb-3">
                <el-card shadow="hover">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="flex-grow-1 me-2">
                      <h6 class="mb-0 text-truncate">{{ item.title }}</h6>
                      <small class="text-muted">{{ item.user_name }} · {{ item.course_title }}</small>
                    </div>
                    <el-tag :type="getStatusType(item.status)" size="small">{{ getStatusText(item.status) }}</el-tag>
                  </div>
                  <p class="small text-muted mb-2 text-truncate-2">{{ item.content }}</p>
                  <div class="d-flex gap-2 flex-wrap">
                    <el-button v-if="item.status === 'pending'" type="success" size="small" class="flex-grow-1" @click="handleApprove('question', item.id)">通过</el-button>
                    <el-button v-if="item.status === 'pending'" type="warning" size="small" class="flex-grow-1" @click="handleReject('question', item.id)">拒绝</el-button>
                    <el-button type="danger" size="small" class="flex-grow-1" @click="handleDelete('question', item.id)">删除</el-button>
                  </div>
                </el-card>
              </div>
            </div>
          </div>
          
          <div class="d-flex justify-content-center mt-3">
            <el-pagination v-model:current-page="questionPage" :page-size="20" :total="questionTotal" layout="prev, pager, next" background />
          </div>
        </el-tab-pane>

        <!-- 回答审核 -->
        <el-tab-pane label="回答" name="answers">
          <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2 review-mod-header">
            <el-select v-model="answerStatus" placeholder="状态筛选" clearable size="small" class="review-mod-select">
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
            <el-button type="danger" size="small" class="review-mod-btn" @click="handleDeleteAllApproved('answer')">删除全部已通过</el-button>
          </div>
          
          <el-table :data="answers" stripe border v-loading="answersLoading" class="d-none d-md-block">
            <el-table-column prop="user_name" label="用户" width="100" />
            <el-table-column prop="course_title" label="课程" min-width="120" show-overflow-tooltip />
            <el-table-column prop="question_title" label="问题" min-width="150" show-overflow-tooltip />
            <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" align="center">
              <template #default="{ row }">
                <el-button v-if="row.status === 'pending'" type="success" size="small" @click="handleApprove('answer', row.id)">通过</el-button>
                <el-button v-if="row.status === 'pending'" type="warning" size="small" @click="handleReject('answer', row.id)">拒绝</el-button>
                <el-button type="danger" size="small" @click="handleDelete('answer', row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 移动端回答卡片 -->
          <div class="d-md-none">
            <div v-if="answers.length === 0 && !answersLoading" class="text-center py-4">
              <el-empty description="暂无数据" :image-size="80" />
            </div>
            <div v-else v-loading="answersLoading">
              <div v-for="item in answers" :key="item.id" class="mb-3">
                <el-card shadow="hover">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="flex-grow-1 me-2">
                      <h6 class="mb-0 text-truncate">{{ item.user_name }}</h6>
                      <small class="text-muted">{{ item.course_title }}</small>
                    </div>
                    <el-tag :type="getStatusType(item.status)" size="small">{{ getStatusText(item.status) }}</el-tag>
                  </div>
                  <p class="small text-primary mb-1 text-truncate">Q: {{ item.question_title }}</p>
                  <p class="small text-muted mb-2 text-truncate-2">{{ item.content }}</p>
                  <div class="d-flex gap-2 flex-wrap">
                    <el-button v-if="item.status === 'pending'" type="success" size="small" class="flex-grow-1" @click="handleApprove('answer', item.id)">通过</el-button>
                    <el-button v-if="item.status === 'pending'" type="warning" size="small" class="flex-grow-1" @click="handleReject('answer', item.id)">拒绝</el-button>
                    <el-button type="danger" size="small" class="flex-grow-1" @click="handleDelete('answer', item.id)">删除</el-button>
                  </div>
                </el-card>
              </div>
            </div>
          </div>
          
          <div class="d-flex justify-content-center mt-3">
            <el-pagination v-model:current-page="answerPage" :page-size="20" :total="answerTotal" layout="prev, pager, next" background />
          </div>
        </el-tab-pane>

        <!-- 讨论审核 -->
        <el-tab-pane label="讨论" name="discussions">
          <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2 review-mod-header">
            <el-select v-model="discussionStatus" placeholder="状态筛选" clearable size="small" class="review-mod-select">
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
            <el-button type="danger" size="small" class="review-mod-btn" @click="handleDeleteAllApproved('discussion')">删除全部已通过</el-button>
          </div>
          
          <el-table :data="discussions" stripe border v-loading="discussionsLoading" class="d-none d-md-block">
            <el-table-column prop="user_name" label="用户" width="100" />
            <el-table-column prop="course_title" label="课程" min-width="150" show-overflow-tooltip />
            <el-table-column prop="content" label="内容" min-width="250" show-overflow-tooltip />
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" align="center">
              <template #default="{ row }">
                <el-button v-if="row.status === 'pending'" type="success" size="small" @click="handleApprove('discussion', row.id)">通过</el-button>
                <el-button v-if="row.status === 'pending'" type="warning" size="small" @click="handleReject('discussion', row.id)">拒绝</el-button>
                <el-button type="danger" size="small" @click="handleDelete('discussion', row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 移动端讨论卡片 -->
          <div class="d-md-none">
            <div v-if="discussions.length === 0 && !discussionsLoading" class="text-center py-4">
              <el-empty description="暂无数据" :image-size="80" />
            </div>
            <div v-else v-loading="discussionsLoading">
              <div v-for="item in discussions" :key="item.id" class="mb-3">
                <el-card shadow="hover">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="flex-grow-1 me-2">
                      <h6 class="mb-0">{{ item.user_name }}</h6>
                      <small class="text-muted">{{ item.course_title }}</small>
                    </div>
                    <el-tag :type="getStatusType(item.status)" size="small">{{ getStatusText(item.status) }}</el-tag>
                  </div>
                  <p class="small text-muted mb-2 text-truncate-3">{{ item.content }}</p>
                  <div class="d-flex gap-2 flex-wrap">
                    <el-button v-if="item.status === 'pending'" type="success" size="small" class="flex-grow-1" @click="handleApprove('discussion', item.id)">通过</el-button>
                    <el-button v-if="item.status === 'pending'" type="warning" size="small" class="flex-grow-1" @click="handleReject('discussion', item.id)">拒绝</el-button>
                    <el-button type="danger" size="small" class="flex-grow-1" @click="handleDelete('discussion', item.id)">删除</el-button>
                  </div>
                </el-card>
              </div>
            </div>
          </div>
          
          <div class="d-flex justify-content-center mt-3">
            <el-pagination v-model:current-page="discussionPage" :page-size="20" :total="discussionTotal" layout="prev, pager, next" background />
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { adminApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('reviews')
const statistics = ref({ pending_reviews: 0, pending_questions: 0, pending_answers: 0, pending_discussions: 0 })

const reviews = ref([]), reviewsLoading = ref(false), reviewPage = ref(1), reviewTotal = ref(0), reviewStatus = ref('pending')
const questions = ref([]), questionsLoading = ref(false), questionPage = ref(1), questionTotal = ref(0), questionStatus = ref('pending')
const answers = ref([]), answersLoading = ref(false), answerPage = ref(1), answerTotal = ref(0), answerStatus = ref('pending')
const discussions = ref([]), discussionsLoading = ref(false), discussionPage = ref(1), discussionTotal = ref(0), discussionStatus = ref('pending')

async function fetchStatistics() {
  try { const res = await adminApi.getReviewStatistics(); statistics.value = res.data } catch (e) { console.error(e) }
}

async function fetchReviews() {
  reviewsLoading.value = true
  try { const res = await adminApi.getAdminReviews({ page: reviewPage.value, status: reviewStatus.value }); reviews.value = res.data.reviews || []; reviewTotal.value = res.data.total || 0 }
  catch (e) { console.error(e) } finally { reviewsLoading.value = false }
}

async function fetchQuestions() {
  questionsLoading.value = true
  try { const res = await adminApi.getAdminQuestions({ page: questionPage.value, status: questionStatus.value }); questions.value = res.data.questions || []; questionTotal.value = res.data.total || 0 }
  catch (e) { console.error(e) } finally { questionsLoading.value = false }
}

async function fetchAnswers() {
  answersLoading.value = true
  try { const res = await adminApi.getAdminAnswers({ page: answerPage.value, status: answerStatus.value }); answers.value = res.data.answers || []; answerTotal.value = res.data.total || 0 }
  catch (e) { console.error(e) } finally { answersLoading.value = false }
}

async function fetchDiscussions() {
  discussionsLoading.value = true
  try { const res = await adminApi.getAdminDiscussions({ page: discussionPage.value, status: discussionStatus.value }); discussions.value = res.data.discussions || []; discussionTotal.value = res.data.total || 0 }
  catch (e) { console.error(e) } finally { discussionsLoading.value = false }
}

async function handleApprove(type, id) {
  try {
    if (type === 'review') { await adminApi.approveReview(id); fetchReviews() }
    else if (type === 'question') { await adminApi.approveQuestion(id); fetchQuestions() }
    else if (type === 'answer') { await adminApi.approveAnswer(id); fetchAnswers() }
    else if (type === 'discussion') { await adminApi.approveDiscussion(id); fetchDiscussions() }
    ElMessage.success('审核通过'); fetchStatistics()
  } catch (e) { ElMessage.error('操作失败') }
}

async function handleReject(type, id) {
  try {
    if (type === 'review') { await adminApi.rejectReview(id); fetchReviews() }
    else if (type === 'question') { await adminApi.rejectQuestion(id); fetchQuestions() }
    else if (type === 'answer') { await adminApi.rejectAnswer(id); fetchAnswers() }
    else if (type === 'discussion') { await adminApi.rejectDiscussion(id); fetchDiscussions() }
    ElMessage.success('已拒绝'); fetchStatistics()
  } catch (e) { ElMessage.error('操作失败') }
}

async function handleDelete(type, id) {
  try {
    await ElMessageBox.confirm('确定删除这条记录吗？此操作不可恢复。', '确认删除', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    if (type === 'review') { await adminApi.deleteReview(id); fetchReviews() }
    else if (type === 'question') { await adminApi.deleteQuestion(id); fetchQuestions() }
    else if (type === 'answer') { await adminApi.deleteAnswer(id); fetchAnswers() }
    else if (type === 'discussion') { await adminApi.deleteDiscussion(id); fetchDiscussions() }
    ElMessage.success('删除成功')
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

async function handleDeleteAllApproved(type) {
  try {
    await ElMessageBox.confirm('确定删除全部已通过的记录吗？此操作不可恢复！', '确认删除', { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' })
    if (type === 'review') { await adminApi.deleteAllApprovedReviews(); fetchReviews() }
    else if (type === 'question') { await adminApi.deleteAllApprovedQuestions(); fetchQuestions() }
    else if (type === 'answer') { await adminApi.deleteAllApprovedAnswers(); fetchAnswers() }
    else if (type === 'discussion') { await adminApi.deleteAllApprovedDiscussions(); fetchDiscussions() }
    ElMessage.success('删除成功')
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

function getStatusType(status) { return status === 'approved' ? 'success' : status === 'rejected' ? 'danger' : 'warning' }
function getStatusText(status) { return status === 'approved' ? '已通过' : status === 'rejected' ? '已拒绝' : '待审核' }

watch([reviewPage, reviewStatus], fetchReviews)
watch([questionPage, questionStatus], fetchQuestions)
watch([answerPage, answerStatus], fetchAnswers)
watch([discussionPage, discussionStatus], fetchDiscussions)

onMounted(() => { fetchStatistics(); fetchReviews(); fetchQuestions(); fetchAnswers(); fetchDiscussions() })
</script>

<style scoped>
.stat-card { cursor: pointer; transition: transform 0.3s; }
.stat-card:hover { transform: translateY(-4px); }

/* 审核管理头部按钮适配 */
.review-mod-header {
  flex-wrap: wrap;
  gap: 8px;
}

.review-mod-select {
  width: 100%;
  max-width: 200px;
}

@media (max-width: 768px) {
  .review-mod-select {
    max-width: 100%;
  }
  
  .review-mod-btn {
    width: 100%;
  }
  
  /* 移动端按钮组换行 */
  .d-flex.gap-2.flex-wrap {
    flex-wrap: wrap;
  }
  
  .d-flex.gap-2.flex-wrap .el-button {
    flex: 1 1 calc(50% - 4px);
    min-width: 0;
  }
}
</style>
