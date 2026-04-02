<template>
  <div class="home">
    <!-- 英雄区域 -->
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="container">
        <div class="row align-items-center min-vh-50">
          <div class="col-lg-6">
            <div class="hero-content">
              <span class="hero-badge">终身学习平台</span>
              <h1 class="hero-title">开启你的<br><span class="text-gradient">学习之旅</span></h1>
              <p class="hero-desc">专业的成人再教育平台，提供丰富的在线课程资源，随时随地学习，提升职业技能，成就更好的自己</p>
              <div class="hero-actions">
                <router-link to="/courses" class="btn btn-hero-primary">
                  <el-icon class="me-2"><Reading /></el-icon>浏览课程
                </router-link>
                <router-link to="/register" class="btn btn-hero-outline" v-if="!userStore.isLoggedIn">
                  免费注册
                </router-link>
              </div>
              <div class="hero-stats">
                <div class="hero-stat">
                  <span class="hero-stat-value">1000+</span>
                  <span class="hero-stat-label">精品课程</span>
                </div>
                <div class="hero-stat">
                  <span class="hero-stat-value">500+</span>
                  <span class="hero-stat-label">专业讲师</span>
                </div>
                <div class="hero-stat">
                  <span class="hero-stat-value">10万+</span>
                  <span class="hero-stat-label">注册学员</span>
                </div>
              </div>
            </div>
          </div>
          <div class="col-lg-6 d-none d-lg-block">
            <div class="hero-visual">
              <div class="hero-circle hero-circle-1"></div>
              <div class="hero-circle hero-circle-2"></div>
              <div class="hero-circle hero-circle-3"></div>
              <div class="hero-icon-wrap">
                <el-icon :size="120" class="hero-icon"><Reading /></el-icon>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 平台特色 -->
    <section class="features-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">为什么选择我们</span>
          <h2 class="section-title">平台特色</h2>
          <p class="section-desc">我们致力于为学员提供最优质的学习体验</p>
        </div>
        <div class="row g-4">
          <div class="col-lg-3 col-md-6" v-for="feature in features" :key="feature.title">
            <div class="feature-card">
              <div class="feature-icon" :style="{ background: feature.bgColor }">
                <el-icon :size="28" :style="{ color: feature.iconColor }">
                  <component :is="feature.icon" />
                </el-icon>
              </div>
              <h5 class="feature-title">{{ feature.title }}</h5>
              <p class="feature-desc">{{ feature.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 热门课程 -->
    <section class="courses-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">精选推荐</span>
          <h2 class="section-title">热门课程</h2>
          <p class="section-desc">精心挑选的优质课程，助你快速成长</p>
        </div>
        <div class="row g-4">
          <div class="col-lg-3 col-md-6" v-for="course in hotCourses" :key="course.id">
            <div class="course-card">
              <div class="course-cover">
                <img v-if="course.cover_image" :src="course.cover_image" class="w-100 h-100" style="object-fit: cover;" />
                <div v-else class="course-cover-bg">
                  <el-icon :size="40"><VideoPlay /></el-icon>
                </div>
                <span class="course-tag" v-if="course.category_name">{{ course.category_name }}</span>
              </div>
              <div class="course-body">
                <h6 class="course-title">{{ course.title }}</h6>
                <div class="course-meta">
                  <span><el-icon><User /></el-icon>{{ course.teacher_name || '讲师' }}</span>
                  <span><el-icon><User /></el-icon>{{ course.student_count || 0 }}人学习</span>
                </div>
                <div class="course-footer">
                  <span class="course-price">¥{{ course.price || 0 }}</span>
                  <router-link :to="`/course/${course.id}`" class="course-link">
                    查看详情 <el-icon><ArrowRight /></el-icon>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="text-center mt-5">
          <router-link to="/courses" class="btn btn-more">
            查看全部课程 <el-icon class="ms-1"><ArrowRight /></el-icon>
          </router-link>
        </div>
      </div>
    </section>

    <!-- 数据统计 -->
    <section class="stats-section">
      <div class="container">
        <div class="row g-4">
          <div class="col-6 col-md-3" v-for="stat in stats" :key="stat.label">
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon :size="24"><component :is="stat.icon" /></el-icon>
              </div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 行动号召 -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-card">
          <div class="cta-content">
            <h2 class="cta-title">准备好开始学习了吗？</h2>
            <p class="cta-desc">立即注册，开启你的学习之旅，获取海量优质课程资源</p>
            <div class="cta-actions">
              <router-link to="/register" class="btn btn-cta-primary" v-if="!userStore.isLoggedIn">
                立即注册
              </router-link>
              <router-link to="/courses" class="btn btn-cta-outline">
                浏览课程
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { courseApi } from '@/api'
import { Reading, VideoPlay, User, Trophy, Monitor, ChatDotRound, ArrowRight, Notebook, Star } from '@element-plus/icons-vue'

const userStore = useUserStore()
const hotCourses = ref([])

const features = [
  { icon: 'Monitor', title: '随时随地学习', desc: '支持电脑、手机、平板多端访问，碎片化时间高效利用', bgColor: 'rgba(59, 130, 246, 0.1)', iconColor: '#3b82f6' },
  { icon: 'VideoPlay', title: '优质视频课程', desc: '专业讲师录制，高清视频在线播放，学习体验更佳', bgColor: 'rgba(16, 185, 129, 0.1)', iconColor: '#10b981' },
  { icon: 'ChatDotRound', title: '互动答疑', desc: '在线讨论交流，讲师实时答疑，学习不再孤单', bgColor: 'rgba(245, 158, 11, 0.1)', iconColor: '#f59e0b' },
  { icon: 'Trophy', title: '证书认证', desc: '完成课程学习获得证书，为职业发展加分', bgColor: 'rgba(139, 92, 246, 0.1)', iconColor: '#8b5cf6' }
]

const stats = [
  { value: '1000+', label: '精品课程', icon: 'Reading' },
  { value: '500+', label: '专业讲师', icon: 'User' },
  { value: '10万+', label: '注册学员', icon: 'Notebook' },
  { value: '98%', label: '好评率', icon: 'Star' }
]

onMounted(async () => {
  try {
    const res = await courseApi.getCourses({ per_page: 8 })
    hotCourses.value = res.data.courses || []
  } catch (e) {
    console.error('获取课程失败')
  }
})
</script>

<style scoped>
/* 英雄区域 */
.hero {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 120px 0 80px;
  overflow: hidden;
  margin-top: -72px;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-block;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50px;
  color: #fff;
  font-size: 14px;
  margin-bottom: 24px;
  backdrop-filter: blur(10px);
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  color: #fff;
  line-height: 1.2;
  margin-bottom: 24px;
}

.text-gradient {
  background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.8;
  margin-bottom: 32px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 48px;
}

.btn-hero-primary {
  padding: 14px 32px;
  background: #fff;
  color: #667eea;
  border-radius: 12px;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
}

.btn-hero-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  color: #667eea;
}

.btn-hero-outline {
  padding: 14px 32px;
  background: transparent;
  color: #fff;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s;
}

.btn-hero-outline:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #fff;
  color: #fff;
}

.hero-stats {
  display: flex;
  gap: 40px;
}

.hero-stat {
  display: flex;
  flex-direction: column;
}

.hero-stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
}

.hero-stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.hero-visual {
  position: relative;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-circle {
  position: absolute;
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.hero-circle-1 {
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.1);
  animation-delay: 0s;
}

.hero-circle-2 {
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.15);
  animation-delay: 1s;
}

.hero-circle-3 {
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.2);
  animation-delay: 2s;
}

.hero-icon-wrap {
  position: relative;
  z-index: 1;
  width: 180px;
  height: 180px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.hero-icon {
  color: #fff;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

/* 通用区块样式 */
.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.section-badge {
  display: inline-block;
  padding: 6px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50px;
  color: #fff;
  font-size: 13px;
  margin-bottom: 16px;
}

.section-title {
  font-size: 36px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 12px;
}

.section-desc {
  font-size: 16px;
  color: #6b7280;
}

/* 平台特色 */
.features-section {
  padding: 80px 0;
  background: #f8fafc;
}

.feature-card {
  background: #fff;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  transition: all 0.3s;
  height: 100%;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.feature-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
}

.feature-desc {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

/* 热门课程 */
.courses-section {
  padding: 80px 0;
  background: #fff;
}

.course-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
  border: 1px solid #f3f4f6;
}

.course-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.course-cover {
  position: relative;
  height: 160px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.course-cover-bg {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.5);
}

.course-tag {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50px;
  font-size: 12px;
  color: #667eea;
  font-weight: 500;
}

.course-body {
  padding: 20px;
}

.course-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  height: 44px;
}

.course-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.course-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #9ca3af;
}

.course-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-price {
  font-size: 20px;
  font-weight: 700;
  color: #f59e0b;
}

.course-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #667eea;
  text-decoration: none;
  transition: all 0.2s;
}

.course-link:hover {
  color: #764ba2;
}

.btn-more {
  padding: 12px 32px;
  background: transparent;
  color: #667eea;
  border: 2px solid #667eea;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
}

.btn-more:hover {
  background: #667eea;
  color: #fff;
}

/* 数据统计 */
.stats-section {
  padding: 60px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-item {
  text-align: center;
  padding: 24px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: #fff;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

/* 行动号召 */
.cta-section {
  padding: 80px 0;
  background: #f8fafc;
}

.cta-card {
  background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
  border-radius: 24px;
  padding: 60px;
  text-align: center;
}

.cta-title {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 16px;
}

.cta-desc {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 32px;
}

.cta-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn-cta-primary {
  padding: 14px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-cta-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
  color: #fff;
}

.btn-cta-outline {
  padding: 14px 32px;
  background: transparent;
  color: #fff;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-cta-outline:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #fff;
  color: #fff;
}

/* 响应式 */
@media (max-width: 992px) {
  .hero { padding: 60px 0; margin-top: -56px; }
  .hero-title { font-size: 40px; }
  .hero-stats { gap: 24px; }
  .hero-stat-value { font-size: 22px; }
  .min-vh-50 { min-height: auto; }
  .hero-visual { height: 300px; }
  .hero-circle-1 { width: 200px; height: 200px; }
  .hero-circle-2 { width: 150px; height: 150px; }
  .hero-circle-3 { width: 80px; height: 80px; }
  .hero-icon-wrap { width: 140px; height: 140px; }
  .section-header { margin-bottom: 32px; }
  .features-section, .courses-section, .cta-section { padding: 60px 0; }
}

@media (max-width: 768px) {
  .hero { padding: 40px 0; margin-top: -48px; }
  .hero-title { font-size: 28px; margin-bottom: 16px; }
  .hero-desc { font-size: 14px; margin-bottom: 24px; }
  .hero-actions { flex-direction: column; margin-bottom: 32px; gap: 12px; }
  .btn-hero-primary, .btn-hero-outline { width: 100%; justify-content: center; padding: 12px 24px; font-size: 14px; }
  .hero-stats { flex-wrap: wrap; gap: 16px; justify-content: center; }
  .hero-stat { width: calc(50% - 8px); text-align: center; }
  .hero-stat-value { font-size: 20px; }
  .hero-stat-label { font-size: 12px; }
  .hero-visual { display: none; }
  .section-title { font-size: 24px; margin-bottom: 8px; }
  .section-desc { font-size: 14px; margin-bottom: 0; }
  .section-badge { font-size: 12px; padding: 4px 12px; margin-bottom: 12px; }
  .feature-card { padding: 24px 16px; }
  .feature-icon { width: 48px; height: 48px; margin-bottom: 12px; }
  .feature-title { font-size: 16px; margin-bottom: 8px; }
  .feature-desc { font-size: 13px; }
  .course-cover { height: 140px; }
  .course-body { padding: 16px; }
  .course-title { font-size: 14px; height: 40px; }
  .course-meta { flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
  .course-meta span { font-size: 12px; }
  .course-price { font-size: 18px; }
  .course-link { font-size: 12px; }
  .stat-item { padding: 16px; }
  .stat-icon { width: 44px; height: 44px; margin-bottom: 12px; }
  .stat-value { font-size: 28px; margin-bottom: 4px; }
  .stat-label { font-size: 12px; }
  .cta-card { padding: 32px 20px; border-radius: 16px; }
  .cta-title { font-size: 20px; margin-bottom: 12px; }
  .cta-desc { font-size: 14px; margin-bottom: 24px; }
  .cta-actions { flex-direction: column; gap: 12px; }
  .btn-cta-primary, .btn-cta-outline { width: 100%; justify-content: center; padding: 12px 24px; font-size: 14px; }
  .btn-more { width: 100%; justify-content: center; }
}

@media (max-width: 576px) {
  .hero { padding: 30px 0; }
  .hero-title { font-size: 24px; }
  .section-title { font-size: 20px; }
  .features-section, .courses-section, .cta-section { padding: 40px 0; }
  .course-cover { height: 120px; }
}
</style>
