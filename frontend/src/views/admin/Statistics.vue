<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">统计报表</h1>
        <p class="page-subtitle">查看平台运营数据概览</p>
      </div>
    </div>

    <div class="stat-grid">
      <div class="stat-card stat-card--blue">
        <div class="stat-card-inner">
          <div class="stat-info">
            <span class="stat-label">用户总数</span>
            <span class="stat-value">{{ statistics.total_users || 0 }}</span>
          </div>
          <div class="stat-icon-wrap stat-icon--blue">
            <el-icon :size="24"><User /></el-icon>
          </div>
        </div>
      </div>
      <div class="stat-card stat-card--green">
        <div class="stat-card-inner">
          <div class="stat-info">
            <span class="stat-label">课程总数</span>
            <span class="stat-value">{{ statistics.total_courses || 0 }}</span>
          </div>
          <div class="stat-icon-wrap stat-icon--green">
            <el-icon :size="24"><Reading /></el-icon>
          </div>
        </div>
      </div>
      <div class="stat-card stat-card--orange">
        <div class="stat-card-inner">
          <div class="stat-info">
            <span class="stat-label">报名总数</span>
            <span class="stat-value">{{ statistics.total_enrollments || 0 }}</span>
          </div>
          <div class="stat-icon-wrap stat-icon--orange">
            <el-icon :size="24"><Notebook /></el-icon>
          </div>
        </div>
      </div>
      <div class="stat-card stat-card--purple">
        <div class="stat-card-inner">
          <div class="stat-info">
            <span class="stat-label">提交总数</span>
            <span class="stat-value">{{ submissionStats.total || 0 }}</span>
          </div>
          <div class="stat-icon-wrap stat-icon--purple">
            <el-icon :size="24"><Document /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <div class="content-grid">
      <div class="card">
        <div class="card-header">
          <span class="card-title">用户统计</span>
        </div>
        <div class="stat-blocks-row">
          <div class="stat-block">
            <span class="stat-block-label">学生</span>
            <span class="stat-block-value">{{ userStats.students || 0 }}</span>
          </div>
          <div class="stat-block">
            <span class="stat-block-label">教师</span>
            <span class="stat-block-value">{{ userStats.teachers || 0 }}</span>
          </div>
          <div class="stat-block">
            <span class="stat-block-label">管理员</span>
            <span class="stat-block-value">{{ userStats.admins || 0 }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <span class="card-title">课程统计</span>
        </div>
        <div class="stat-blocks-row">
          <div class="stat-block">
            <span class="stat-block-label">已发布</span>
            <span class="stat-block-value text-success">{{ courseStats.published || 0 }}</span>
          </div>
          <div class="stat-block">
            <span class="stat-block-label">草稿</span>
            <span class="stat-block-value text-info">{{ courseStats.draft || 0 }}</span>
          </div>
          <div class="stat-block">
            <span class="stat-block-label">已归档</span>
            <span class="stat-block-value text-warning">{{ courseStats.archived || 0 }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <span class="card-title">提交统计</span>
        </div>
        <div class="stat-blocks-row stat-blocks-four">
          <div class="stat-block">
            <span class="stat-block-label">总提交</span>
            <span class="stat-block-value">{{ submissionStats.total || 0 }}</span>
          </div>
          <div class="stat-block">
            <span class="stat-block-label">已批改</span>
            <span class="stat-block-value text-success">{{ submissionStats.graded || 0 }}</span>
          </div>
          <div class="stat-block">
            <span class="stat-block-label">待批改</span>
            <span class="stat-block-value text-warning">{{ submissionStats.pending || 0 }}</span>
          </div>
          <div class="stat-block">
            <span class="stat-block-label">平均分</span>
            <span class="stat-block-value text-primary">{{ submissionStats.avg_score || 0 }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <span class="card-title">热门课程 Top 5</span>
        </div>
        <div v-if="topCourses.length === 0" class="card-empty">
          <el-empty description="暂无数据" :image-size="60" />
        </div>
        <div v-else class="top-list">
          <div v-for="(course, index) in topCourses" :key="course.id" class="top-item">
            <div class="top-rank" :class="index < 3 ? 'top-rank--hot' : ''">{{ index + 1 }}</div>
            <span class="top-name">{{ course.title }}</span>
            <span class="top-count">{{ course.student_count || 0 }}人</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'
import { ElMessage } from 'element-plus'
import { User, Reading, Notebook, Document } from '@element-plus/icons-vue'

const loading = ref(true)
const statistics = ref({})

const userStats = computed(() => statistics.value.user_stats || {})
const courseStats = computed(() => statistics.value.course_stats || {})
const submissionStats = computed(() => statistics.value.submission_stats || {})
const topCourses = computed(() => statistics.value.top_courses || [])

async function fetchStatistics() {
  loading.value = true
  try {
    const res = await adminApi.getStatistics()
    statistics.value = res.data || {}
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '获取统计数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => { fetchStatistics() })
</script>

<style scoped>
.page { min-height: 100%; }

.page-header {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.page-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 4px 0 0 0;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 24px;
  border-left: 4px solid transparent;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-card--blue { border-left-color: #3b82f6; }
.stat-card--green { border-left-color: #10b981; }
.stat-card--orange { border-left-color: #f59e0b; }
.stat-card--purple { border-left-color: #8b5cf6; }

.stat-card-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-info { display: flex; flex-direction: column; }

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
}

.stat-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-icon--blue { background: linear-gradient(135deg, #3b82f6, #60a5fa); }
.stat-icon--green { background: linear-gradient(135deg, #10b981, #34d399); }
.stat-icon--orange { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.stat-icon--purple { background: linear-gradient(135deg, #8b5cf6, #a78bfa); }

.content-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.card-empty { padding: 10px 0; }

.stat-blocks-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-blocks-four {
  grid-template-columns: repeat(4, 1fr);
}

.stat-block {
  background: #f9fafb;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.stat-block-label {
  display: block;
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 4px;
}

.stat-block-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
}

.text-success { color: #10b981; }
.text-info { color: #6b7280; }
.text-warning { color: #f59e0b; }
.text-primary { color: #3b82f6; }

.top-list { display: flex; flex-direction: column; }

.top-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
}

.top-item:last-child { border-bottom: none; }

.top-rank {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #9ca3af;
  background: #f3f4f6;
  flex-shrink: 0;
}

.top-rank--hot {
  color: #fff;
  background: linear-gradient(135deg, #ef4444, #f87171);
}

.top-name {
  flex: 1;
  font-size: 14px;
  color: #374151;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.top-count {
  font-size: 13px;
  color: #9ca3af;
  flex-shrink: 0;
}

@media (max-width: 1200px) {
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
  .content-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .stat-grid { grid-template-columns: 1fr; }
  .stat-blocks-four { grid-template-columns: repeat(2, 1fr); }
}
</style>
