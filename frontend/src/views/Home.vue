<template>
  <div class="home">
    <!-- 英雄区域 -->
    <section class="hero">
      <div class="hero-pattern"></div>
      <div class="container">
        <div class="row align-items-center min-vh-50">
          <div class="col-lg-6">
            <div class="hero-content">
              <h1 class="hero-title">开启你的<br><span class="hero-title-accent">学习之旅</span></h1>
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
                <div class="hero-stat-divider"></div>
                <div class="hero-stat">
                  <span class="hero-stat-value">500+</span>
                  <span class="hero-stat-label">专业讲师</span>
                </div>
                <div class="hero-stat-divider"></div>
                <div class="hero-stat">
                  <span class="hero-stat-value">10万+</span>
                  <span class="hero-stat-label">注册学员</span>
                </div>
              </div>
            </div>
          </div>
          <div class="col-lg-6 d-none d-lg-block">
            <div class="hero-visual">
              <div class="hero-shape hero-shape-1"></div>
              <div class="hero-shape hero-shape-2"></div>
              <div class="hero-illustration">
                <div class="hero-book-stack">
                  <div class="hero-book hero-book-1"></div>
                  <div class="hero-book hero-book-2"></div>
                  <div class="hero-book hero-book-3"></div>
                </div>
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
          <div class="section-accent"></div>
          <h2 class="section-title">平台特色</h2>
          <p class="section-desc">我们致力于为学员提供最优质的学习体验</p>
        </div>
        <div class="row g-4">
          <div class="col-lg-3 col-md-6" v-for="feature in features" :key="feature.title">
            <div class="feature-card">
              <div class="feature-icon" :class="`feature-icon--${feature.colorKey}`">
                <el-icon :size="28">
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
          <div class="section-accent"></div>
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
        <div class="stats-wrapper">
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
  { icon: 'Monitor', title: '随时随地学习', desc: '支持电脑、手机、平板多端访问，碎片化时间高效利用', colorKey: 'blue' },
  { icon: 'VideoPlay', title: '优质视频课程', desc: '专业讲师录制，高清视频在线播放，学习体验更佳', colorKey: 'green' },
  { icon: 'ChatDotRound', title: '互动答疑', desc: '在线讨论交流，讲师实时答疑，学习不再孤单', colorKey: 'amber' },
  { icon: 'Trophy', title: '证书认证', desc: '完成课程学习获得证书，为职业发展加分', colorKey: 'purple' }
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
  background: linear-gradient(160deg, #eef2ff 0%, #f8f9fb 50%, #fff 100%);
  padding: 100px 0 60px;
  overflow: hidden;
}

.hero-pattern {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, #c7d2fe 1px, transparent 1px);
  background-size: 28px 28px;
  opacity: 0.4;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 44px;
  font-weight: 700;
  color: #111827;
  line-height: 1.2;
  margin-bottom: 24px;
}

.hero-title-accent {
  color: #2563eb;
}

.hero-desc {
  font-size: 18px;
  color: #6b7280;
  line-height: 1.8;
  margin-bottom: 32px;
  max-width: 480px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 48px;
}

.btn-hero-primary {
  padding: 14px 32px;
  background: #2563eb;
  color: #fff;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
}

.btn-hero-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.25);
  color: #fff;
}

.btn-hero-outline {
  padding: 14px 32px;
  background: #fff;
  color: #2563eb;
  border: 1px solid #2563eb;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s;
}

.btn-hero-outline:hover {
  background: #2563eb;
  color: #fff;
}

.hero-stats {
  display: flex;
  align-items: center;
  gap: 36px;
}

.hero-stat-divider {
  width: 1px;
  height: 40px;
  background: #d1d5db;
}

.hero-stat {
  display: flex;
  flex-direction: column;
}

.hero-stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
}

.hero-stat-label {
  font-size: 14px;
  color: #6b7280;
}

.hero-visual {
  position: relative;
  height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-shape {
  position: absolute;
  border-radius: 50%;
}

.hero-shape-1 {
  width: 280px;
  height: 280px;
  background: rgba(37, 99, 235, 0.04);
  top: 40px;
  right: 40px;
}

.hero-shape-2 {
  width: 200px;
  height: 200px;
  background: rgba(37, 99, 235, 0.06);
  bottom: 30px;
  left: 60px;
}

.hero-illustration {
  position: relative;
  z-index: 1;
}

.hero-book-stack {
  position: relative;
  width: 180px;
  height: 200px;
}

.hero-book {
  position: absolute;
  border-radius: 4px 12px 12px 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: transform 0.4s ease;
}

.hero-book-1 {
  bottom: 0;
  left: 10px;
  width: 140px;
  height: 24px;
  background: #93c5fd;
}

.hero-book-2 {
  bottom: 22px;
  left: 20px;
  width: 150px;
  height: 28px;
  background: #60a5fa;
}

.hero-book-3 {
  bottom: 48px;
  left: 0;
  width: 160px;
  height: 32px;
  background: #2563eb;
}

.hero-book-stack:hover .hero-book-1 { transform: translateX(4px) rotate(-2deg); }
.hero-book-stack:hover .hero-book-2 { transform: translateX(-3px) rotate(1deg); }
.hero-book-stack:hover .hero-book-3 { transform: translateX(2px) rotate(-1deg); }

/* 通用区块样式 */
.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.section-accent {
  width: 40px;
  height: 4px;
  background: #2563eb;
  border-radius: 2px;
  margin: 0 auto 16px;
}

.section-title {
  font-size: 36px;
  font-weight: 600;
  color: #111827;
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
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 32px 24px;
  text-align: center;
  transition: all 0.3s;
  height: 100%;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.feature-icon {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.feature-icon--blue   { background: #eff6ff; color: #2563eb; }
.feature-icon--green  { background: #ecfdf5; color: #059669; }
.feature-icon--amber  { background: #fffbeb; color: #d97706; }
.feature-icon--purple { background: #f5f3ff; color: #7c3aed; }

.feature-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
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
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  border: 1px solid #e5e7eb;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.course-cover {
  position: relative;
  height: 160px;
  background: #e5e7eb;
  overflow: hidden;
}

.course-cover img {
  transition: transform 0.4s ease;
}

.course-card:hover .course-cover img {
  transform: scale(1.05);
}

.course-cover-bg {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.course-tag {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 12px;
  background: #fff;
  border-radius: 4px;
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  border: 1px solid #e5e7eb;
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
  color: #111827;
}

.course-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #2563eb;
  text-decoration: none;
  transition: all 0.2s;
}

.course-link:hover {
  color: #1d4ed8;
}

.btn-more {
  padding: 12px 32px;
  background: transparent;
  color: #2563eb;
  border: 1px solid #2563eb;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
}

.btn-more:hover {
  background: #2563eb;
  color: #fff;
}

/* 数据统计 */
.stats-section {
  padding: 80px 0;
  background: #f8fafc;
}

.stats-wrapper {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 40px 20px;
}

.stat-item {
  text-align: center;
  padding: 24px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  background: #eff6ff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: #2563eb;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
}

/* 行动号召 */
.cta-section {
  padding: 80px 0;
  background: #f8fafc;
}

.cta-card {
  background: #111827;
  border-radius: 8px;
  padding: 60px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.cta-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(ellipse at 30% 20%, rgba(37,99,235,0.15) 0%, transparent 60%),
                    radial-gradient(ellipse at 70% 80%, rgba(37,99,235,0.08) 0%, transparent 60%);
}

.cta-content {
  position: relative;
  z-index: 1;
}

.cta-title {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 16px;
}

.cta-desc {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.75);
  margin-bottom: 32px;
}

.cta-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn-cta-primary {
  padding: 14px 32px;
  background: #2563eb;
  color: #fff;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-cta-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.5);
  color: #fff;
}

.btn-cta-outline {
  padding: 14px 32px;
  background: transparent;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
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
  .hero { padding: 60px 0; }
  .hero-title { font-size: 40px; }
  .hero-stats { gap: 24px; }
  .hero-stat-value { font-size: 22px; }
  .hero-stat-divider { display: none; }
  .min-vh-50 { min-height: auto; }
  .hero-visual { display: none; }
  .section-header { margin-bottom: 32px; }
  .features-section, .courses-section, .cta-section { padding: 60px 0; }
}

@media (max-width: 768px) {
  .hero { padding: 40px 0; }
  .hero-title { font-size: 28px; margin-bottom: 16px; }
  .hero-desc { font-size: 14px; margin-bottom: 24px; }
  .hero-actions { flex-direction: column; margin-bottom: 32px; gap: 12px; }
  .btn-hero-primary, .btn-hero-outline { width: 100%; justify-content: center; padding: 12px 24px; font-size: 14px; }
  .hero-stats { flex-wrap: wrap; gap: 16px; justify-content: center; }
  .hero-stat { width: auto; }
  .hero-stat-value { font-size: 20px; }
  .hero-stat-label { font-size: 12px; }
  .section-title { font-size: 24px; margin-bottom: 8px; }
  .section-desc { font-size: 14px; margin-bottom: 0; }
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
  .cta-card { padding: 32px 20px; border-radius: 8px; }
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
