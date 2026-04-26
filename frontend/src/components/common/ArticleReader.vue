<template>
  <div class="article-reader" ref="readerRef">
    <!-- 文章标题 -->
    <div class="article-header" v-if="title">
      <h1 class="article-title">{{ title }}</h1>
      <div class="article-meta" v-if="duration">
        <span class="meta-item">
          <el-icon><Clock /></el-icon>
          预计阅读 {{ duration }} 分钟
        </span>
        <span class="meta-item" v-if="readProgress > 0">
          <el-icon><Reading /></el-icon>
          已阅读 {{ Math.round(readProgress) }}%
        </span>
      </div>
    </div>

    <!-- 文章内容 -->
    <div
      class="article-content"
      ref="contentRef"
      v-html="renderedContent"
      @scroll="handleScroll"
    ></div>

    <!-- 阅读进度条 -->
    <div class="progress-bar-container">
      <div class="progress-bar" :style="{ width: readProgress + '%' }"></div>
    </div>

    <!-- 底部完成提示 -->
    <div class="article-footer" v-if="showCompleteHint">
      <div class="complete-badge" :class="{ completed: isCompleted }">
        <el-icon v-if="isCompleted"><CircleCheckFilled /></el-icon>
        <el-icon v-else><CircleCheck /></el-icon>
        <span>{{ isCompleted ? '已完成学习' : '继续阅读以完成学习' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'
import { Clock, Reading, CircleCheck, CircleCheckFilled } from '@element-plus/icons-vue'

const props = defineProps({
  content: { type: String, default: '' },
  title: { type: String, default: '' },
  duration: { type: Number, default: 0 }
})

const emit = defineEmits(['progress-update', 'complete'])

const readerRef = ref(null)
const contentRef = ref(null)

// 阅读状态
const readProgress = ref(0)
const isCompleted = ref(false)
const readStartTime = ref(null)
const totalReadTime = ref(0)

// 配置 marked
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true
})

// 渲染 Markdown 内容
const renderedContent = computed(() => {
  if (!props.content) return '<p class="text-muted">暂无内容</p>'
  const html = marked(props.content)
  return DOMPurify.sanitize(html)
})

// 是否显示完成提示
const showCompleteHint = computed(() => {
  return props.content && props.content.length > 0
})

// 处理滚动事件
function handleScroll() {
  if (!contentRef.value || isCompleted.value) return

  const element = contentRef.value
  const scrollTop = element.scrollTop
  const scrollHeight = element.scrollHeight
  const clientHeight = element.clientHeight

  // 计算阅读进度
  const progress = (scrollTop / (scrollHeight - clientHeight)) * 100
  readProgress.value = Math.min(100, Math.max(0, progress))

  // 发送进度更新
  emit('progress-update', {
    progress: readProgress.value,
    readTime: getReadTime()
  })

  // 滚动到底部时标记完成
  if (readProgress.value >= 95 && !isCompleted.value) {
    markAsCompleted()
  }
}

// 获取阅读时长（秒）
function getReadTime() {
  if (!readStartTime.value) return 0
  return Math.floor((Date.now() - readStartTime.value) / 1000) + totalReadTime.value
}

// 标记为已完成
function markAsCompleted() {
  if (isCompleted.value) return
  isCompleted.value = true
  emit('complete', {
    progress: 100,
    readTime: getReadTime()
  })
}

// 重置阅读状态
function resetReadingState() {
  readProgress.value = 0
  isCompleted.value = false
  readStartTime.value = null
  totalReadTime.value = 0
}

// 监听内容变化
watch(() => props.content, () => {
  resetReadingState()
  readStartTime.value = Date.now()
  
  // 滚动到顶部
  if (contentRef.value) {
    contentRef.value.scrollTop = 0
  }
})

// 监听滚动事件
let scrollListener = null

onMounted(() => {
  readStartTime.value = Date.now()
  
  // 添加滚动监听
  if (contentRef.value) {
    scrollListener = () => handleScroll()
    contentRef.value.addEventListener('scroll', scrollListener)
  }
})

onUnmounted(() => {
  // 记录总阅读时长
  if (readStartTime.value) {
    totalReadTime.value += Math.floor((Date.now() - readStartTime.value) / 1000)
  }
  
  // 移除滚动监听
  if (contentRef.value && scrollListener) {
    contentRef.value.removeEventListener('scroll', scrollListener)
  }
})

// 暴露方法
defineExpose({
  getReadTime,
  getProgress: () => readProgress.value,
  isCompleted: () => isCompleted.value,
  markAsCompleted
})
</script>

<style scoped>
.article-reader {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
}

/* 文章头部 */
.article-header {
  padding: 24px 32px;
  border-bottom: 1px solid #ebeef5;
  background: #fafafa;
}

.article-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.article-meta {
  display: flex;
  gap: 20px;
  color: #909399;
  font-size: 14px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 文章内容 */
.article-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  font-size: 16px;
  line-height: 1.8;
  color: #303133;
}

/* Markdown 样式 */
.article-content :deep(h1) {
  font-size: 28px;
  font-weight: 600;
  margin: 24px 0 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.article-content :deep(h2) {
  font-size: 24px;
  font-weight: 600;
  margin: 20px 0 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.article-content :deep(h3) {
  font-size: 20px;
  font-weight: 600;
  margin: 18px 0 12px;
}

.article-content :deep(h4) {
  font-size: 18px;
  font-weight: 600;
  margin: 16px 0 10px;
}

.article-content :deep(p) {
  margin: 0 0 16px;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin: 0 0 16px;
  padding-left: 24px;
}

.article-content :deep(li) {
  margin: 8px 0;
}

.article-content :deep(blockquote) {
  margin: 16px 0;
  padding: 16px 20px;
  background: #f5f7fa;
  border-left: 4px solid #409eff;
  color: #606266;
}

.article-content :deep(blockquote p) {
  margin: 0;
}

.article-content :deep(code) {
  padding: 2px 6px;
  background: #f5f7fa;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  color: #e6a23c;
}

.article-content :deep(pre) {
  margin: 16px 0;
  padding: 16px;
  background: #282c34;
  border-radius: 8px;
  overflow-x: auto;
}

.article-content :deep(pre code) {
  padding: 0;
  background: transparent;
  color: #abb2bf;
  font-size: 14px;
  line-height: 1.6;
}

.article-content :deep(table) {
  width: 100%;
  margin: 16px 0;
  border-collapse: collapse;
}

.article-content :deep(th),
.article-content :deep(td) {
  padding: 12px 16px;
  border: 1px solid #ebeef5;
  text-align: left;
}

.article-content :deep(th) {
  background: #f5f7fa;
  font-weight: 600;
}

.article-content :deep(tr:hover) {
  background: #fafafa;
}

.article-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 16px 0;
}

.article-content :deep(a) {
  color: #409eff;
  text-decoration: none;
}

.article-content :deep(a:hover) {
  text-decoration: underline;
}

.article-content :deep(hr) {
  margin: 24px 0;
  border: none;
  border-top: 1px solid #ebeef5;
}

/* 进度条 */
.progress-bar-container {
  height: 4px;
  background: #ebeef5;
  position: sticky;
  bottom: 0;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #67c23a);
  transition: width 0.3s ease;
}

/* 底部完成提示 */
.article-footer {
  padding: 16px 32px;
  background: #fafafa;
  border-top: 1px solid #ebeef5;
  text-align: center;
}

.complete-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #fdf6ec;
  color: #e6a23c;
  border-radius: 8px;
  font-size: 14px;
}

.complete-badge.completed {
  background: #f0f9eb;
  color: #67c23a;
}

/* 响应式 */
@media (max-width: 768px) {
  .article-header {
    padding: 16px 20px;
  }

  .article-title {
    font-size: 20px;
  }

  .article-content {
    padding: 20px;
    font-size: 15px;
  }

  .article-footer {
    padding: 12px 20px;
  }
}
</style>
