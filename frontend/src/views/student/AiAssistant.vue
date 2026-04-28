<template>
  <div class="ai-assistant">
    <div class="chat-container">
      <!-- 左侧对话列表 -->
      <div class="conversation-sidebar">
        <div class="sidebar-header">
          <h5 class="mb-0"><el-icon class="me-2"><ChatDotRound /></el-icon>AI学习助手</h5>
          <el-button type="primary" size="small" @click="createNewChat">
            <el-icon><Plus /></el-icon>新对话
          </el-button>
        </div>

        <div class="conversation-list">
          <div
            v-for="conv in conversations"
            :key="conv.id"
            class="conversation-item"
            :class="{ active: currentConversation?.id === conv.id }"
            @click="selectConversation(conv)"
          >
            <div class="conv-info">
              <el-icon class="conv-icon"><ChatLineRound /></el-icon>
              <span class="conv-title">{{ conv.title }}</span>
            </div>
            <el-button
              type="danger"
              size="small"
              text
              @click.stop="deleteConversation(conv)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>

          <div v-if="conversations.length === 0" class="no-conversations">
            <el-empty description="暂无对话" :image-size="60" />
          </div>
        </div>
      </div>

      <!-- 右侧聊天区域 -->
      <div class="chat-main">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <h5 class="mb-0">{{ currentConversation?.title || 'AI学习助手' }}</h5>
          <span class="text-muted small">基于智谱AI | 随时为您解答学习问题</span>
        </div>

        <!-- 消息区域 -->
        <div class="chat-messages" ref="messagesContainer">
          <!-- 欢迎消息 -->
          <div v-if="messages.length === 0 && !loading" class="welcome-message">
            <div class="welcome-icon">
              <el-icon :size="48"><Service /></el-icon>
            </div>
            <h4>欢迎使用AI学习助手</h4>
            <p class="text-muted">我可以帮助您解答学习疑问、理解课程内容、提供学习建议</p>
            <div class="quick-questions">
              <el-button
                v-for="q in quickQuestions"
                :key="q"
                size="small"
                @click="sendQuickQuestion(q)"
              >
                {{ q }}
              </el-button>
            </div>
          </div>

          <!-- 消息列表 -->
          <div v-for="(msg, index) in messages" :key="msg.id" class="message-item" :class="msg.role">
            <div class="message-avatar">
              <el-avatar v-if="msg.role === 'user'" :size="32" class="user-avatar">
                {{ userStore.user.real_name?.charAt(0) || '我' }}
              </el-avatar>
              <el-avatar v-else :size="32" class="ai-avatar">
                <el-icon :size="16"><Service /></el-icon>
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="message-sender">{{ msg.role === 'user' ? (userStore.user.real_name || '我') : 'AI助手' }}</span>
              </div>
              <div class="message-bubble" :class="msg.role">
                <!-- AI回复使用Markdown渲染 -->
                <div v-if="msg.role === 'assistant'" class="message-text markdown-body" v-html="renderMarkdown(msg.content)"></div>
                <!-- 用户消息纯文本 -->
                <div v-else class="message-text">{{ msg.content }}</div>
              </div>
              <span class="message-time">{{ formatTime(msg.created_at) }}</span>
            </div>
          </div>

          <!-- 加载中 -->
          <div v-if="loading" class="message-item assistant">
            <div class="message-avatar">
              <el-avatar :size="32" class="ai-avatar">
                <el-icon :size="16"><Service /></el-icon>
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-bubble typing">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="2"
            placeholder="请输入您的问题..."
            @keyup.enter.exact="sendMessage"
            :disabled="loading"
          />
          <el-button
            type="primary"
            :loading="loading"
            :disabled="!inputMessage.trim()"
            @click="sendMessage"
          >
            <el-icon><Position /></el-icon>发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { useUserStore } from '@/store/user'
import { aiApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ChatDotRound, ChatLineRound, Plus, Delete, Service, Position, CopyDocument } from '@element-plus/icons-vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

const userStore = useUserStore()

const conversations = ref([])
const currentConversation = ref(null)
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

const quickQuestions = [
  '如何提高学习效率？',
  '如何做好笔记？',
  '课程内容太难怎么办？',
  '推荐一些学习方法'
]

// 配置marked with highlight.js
const renderer = new marked.Renderer()

renderer.code = function(code, language) {
  const validLanguage = hljs.getLanguage(language) ? language : 'plaintext'
  const highlighted = hljs.highlight(code, { language: validLanguage }).value
  return `<div class="code-block">
    <div class="code-header">
      <span class="code-language">${language || 'code'}</span>
      <button class="copy-btn" onclick="copyCode(this)" data-code="${encodeURIComponent(code)}">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
          <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
        </svg>
        复制
      </button>
    </div>
    <pre><code class="hljs language-${validLanguage}">${highlighted}</code></pre>
  </div>`
}

marked.setOptions({
  renderer: renderer,
  breaks: true,
  gfm: true,
  headerIds: false,
  mangle: false
})

// 渲染Markdown
function renderMarkdown(content) {
  if (!content) return ''
  const html = marked.parse(content)
  return DOMPurify.sanitize(html, {
    ADD_ATTR: ['onclick', 'data-code']
  })
}

// 复制代码功能
window.copyCode = function(btn) {
  const code = decodeURIComponent(btn.dataset.code)
  navigator.clipboard.writeText(code).then(() => {
    btn.innerHTML = `<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
    </svg> 已复制`
    setTimeout(() => {
      btn.innerHTML = `<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
        <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
      </svg> 复制`
    }, 2000)
  })
}

// 高亮已有代码块
function highlightCodeBlocks() {
  nextTick(() => {
    document.querySelectorAll('.markdown-body pre code').forEach((block) => {
      hljs.highlightElement(block)
    })
  })
}

// 获取对话列表
async function fetchConversations() {
  try {
    const res = await aiApi.getConversations()
    conversations.value = res.data.conversations || []
  } catch (e) {
    console.error('获取对话列表失败')
  }
}

// 选择对话
async function selectConversation(conv) {
  currentConversation.value = conv
  await fetchMessages(conv.id)
}

// 获取消息
async function fetchMessages(conversationId) {
  try {
    const res = await aiApi.getConversationMessages(conversationId)
    messages.value = res.data.messages || []
    scrollToBottom()
  } catch (e) {
    ElMessage.error('获取消息失败')
  }
}

// 创建新对话
async function createNewChat() {
  currentConversation.value = null
  messages.value = []
}

// 删除对话
async function deleteConversation(conv) {
  try {
    await ElMessageBox.confirm('确定删除这个对话吗？', '确认', { type: 'warning' })
    await aiApi.deleteConversation(conv.id)
    conversations.value = conversations.value.filter(c => c.id !== conv.id)
    if (currentConversation.value?.id === conv.id) {
      currentConversation.value = null
      messages.value = []
    }
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// 发送消息
async function sendMessage() {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''

  // 添加用户消息到界面（使用本地时间）
  const now = new Date()
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: userMessage,
    created_at: now.toISOString()
  })

  scrollToBottom()
  loading.value = true

  // 添加一个空的AI消息，用于流式填充
  const aiMsgId = Date.now() + 1
  messages.value.push({
    id: aiMsgId,
    role: 'assistant',
    content: '',
    created_at: new Date().toISOString()
  })

  try {
    await aiApi.chatStream(
      {
        conversation_id: currentConversation.value?.id,
        message: userMessage
      },
      // onMessage - 每收到一个chunk就追加显示
      (chunk) => {
        const aiMsg = messages.value.find(m => m.id === aiMsgId)
        if (aiMsg) {
          aiMsg.content += chunk
          scrollToBottom()
        }
      },
      // onDone - 流式完成
      async (conversationId) => {
        // 更新当前对话ID（新对话时）
        if (!currentConversation.value && conversationId) {
          currentConversation.value = { id: parseInt(conversationId) }
          await fetchConversations()
        }
        loading.value = false
        scrollToBottom()
      },
      // onError - 出错处理
      (err) => {
        console.error('流式请求失败:', err)
        ElMessage.error('发送失败，请重试')
        // 移除失败的AI消息
        const idx = messages.value.findIndex(m => m.id === aiMsgId)
        if (idx !== -1) messages.value.splice(idx, 1)
        loading.value = false
      }
    )
  } catch (e) {
    ElMessage.error('发送失败，请重试')
    const idx = messages.value.findIndex(m => m.id === aiMsgId)
    if (idx !== -1) messages.value.splice(idx, 1)
    loading.value = false
  }
}

// 快捷问题
function sendQuickQuestion(question) {
  inputMessage.value = question
  sendMessage()
}

// 格式化时间
function formatTime(dateStr) {
  if (!dateStr) {
    return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  try {
    // 处理ISO格式时间
    let date
    if (typeof dateStr === 'string') {
      // 处理可能没有时区信息的时间
      if (dateStr.includes('T') && !dateStr.includes('Z') && !dateStr.includes('+')) {
        date = new Date(dateStr + 'Z')  // 假设是UTC时间
      } else {
        date = new Date(dateStr)
      }
    } else {
      date = new Date(dateStr)
    }

    if (isNaN(date.getTime())) {
      return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }

    // 转换为本地时间显示
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
  } catch (e) {
    return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
}

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

onMounted(() => {
  fetchConversations()
})
</script>

<style scoped>
.ai-assistant {
  height: calc(100vh - 72px);
  background: #f5f7fa;
}

.chat-container {
  display: flex;
  height: 100%;
}

/* 左侧对话列表 */
.conversation-sidebar {
  width: 280px;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conversation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: background 0.2s;
}

.conversation-item:hover {
  background: #f3f4f6;
}

.conversation-item.active {
  background: #e6f0ff;
}

.conv-info {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex: 1;
}

.conv-icon {
  color: #6b7280;
  flex-shrink: 0;
}

.conv-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
}

.no-conversations {
  padding: 40px 0;
}

/* 右侧聊天区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

/* 欢迎消息 */
.welcome-message {
  text-align: center;
  padding: 60px 20px;
}

.welcome-icon {
  width: 100px;
  height: 100px;
  border-radius: 24px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  color: #fff;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}

.welcome-message h4 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.welcome-message p {
  color: #6b7280;
  font-size: 15px;
  max-width: 400px;
  margin: 0 auto;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 28px;
}

.quick-questions .el-button {
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 13px;
  border-color: #e5e7eb;
  color: #4b5563;
  transition: all 0.2s;
}

.quick-questions .el-button:hover {
  border-color: #667eea;
  color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

/* 消息项 */
.message-item {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  padding: 0 4px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 75%;
  min-width: 60px;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 2px;
}

.message-sender {
  font-size: 11px;
  color: #9ca3af;
}

.message-item.user .message-header {
  justify-content: flex-end;
}

.message-bubble {
  padding: 8px 12px;
  border-radius: 10px;
  line-height: 1.5;
  word-break: break-word;
}

.message-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  padding: 0;
}

.message-item.assistant .message-bubble {
  background: #f1f5f9;
  color: #1f2937;
  border-bottom-left-radius: 4px;
}

.message-item.user .message-bubble {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message-time {
  display: block;
  font-size: 10px;
  color: #b0b0b0;
  margin-top: 2px;
  padding: 0;
}

.message-item.user .message-time {
  text-align: right;
}

.user-avatar {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: #fff;
  font-weight: 600;
}

.ai-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
}

/* 打字动画 */
.typing {
  display: flex;
  gap: 4px;
  padding: 10px 14px;
  align-items: center;
}

.typing .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing .dot:nth-child(1) { animation-delay: -0.32s; }
.typing .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

/* Markdown样式 */
.markdown-body {
  font-size: 14px;
  line-height: 1.5;
}

.markdown-body :deep(p) {
  margin: 0;
  padding: 0;
}

.markdown-body :deep(p) + :deep(p) {
  margin-top: 4px;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin: 6px 0 4px 0;
  font-weight: 600;
  color: #1f2937;
}

.markdown-body :deep(h1) { font-size: 16px; }
.markdown-body :deep(h2) { font-size: 15px; }
.markdown-body :deep(h3) { font-size: 14px; }

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 4px 0;
  padding-left: 18px;
}

.markdown-body :deep(li) {
  margin: 2px 0;
}

.markdown-body :deep(code) {
  background: #e8e8e8;
  padding: 1px 4px;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  color: #e11d48;
}

.markdown-body :deep(pre) {
  margin: 4px 0;
  border-radius: 6px;
  overflow: hidden;
}

.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}

.markdown-body :deep(blockquote) {
  border-left: 3px solid #667eea;
  margin: 4px 0;
  padding: 4px 8px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 0 4px 4px 0;
  color: #4b5563;
}

.markdown-body :deep(table) {
  border-collapse: collapse;
  margin: 4px 0;
  width: 100%;
  border-radius: 4px;
  overflow: hidden;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 4px 8px;
  text-align: left;
  font-size: 13px;
}

.markdown-body :deep(th) {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
}

.markdown-body :deep(tr:hover) {
  background: #f8fafc;
}

.markdown-body :deep(a) {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

.markdown-body :deep(strong) {
  font-weight: 600;
  color: #1f2937;
}

.markdown-body :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 16px 0;
}

.markdown-body :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 8px 0;
}

/* 代码块样式 */
.markdown-body :deep(.code-block) {
  margin: 4px 0;
  border-radius: 6px;
  overflow: hidden;
  background: #1e293b;
}

.markdown-body :deep(.code-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 8px;
  background: #0f172a;
  border-bottom: 1px solid #334155;
}

.markdown-body :deep(.code-language) {
  font-size: 10px;
  color: #94a3b8;
  text-transform: uppercase;
  font-weight: 500;
}

.markdown-body :deep(.copy-btn) {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 2px 6px;
  background: #334155;
  border: none;
  border-radius: 3px;
  color: #e2e8f0;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.markdown-body :deep(.copy-btn:hover) {
  background: #475569;
}

.markdown-body :deep(pre) {
  margin: 0 !important;
  padding: 8px !important;
  background: #1e293b !important;
  border-radius: 0 !important;
}

.markdown-body :deep(pre code) {
  font-size: 12px;
  line-height: 1.4;
}

/* 输入区域 */
.chat-input {
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-input .el-textarea {
  flex: 1;
}

/* 响应式 */
    @media (max-width: 992px) {
      /* 平板适配 */
    }

    @media (max-width: 576px) {
      /* 小手机适配 */
    }
@media (max-width: 768px) {
  .conversation-sidebar {
    width: 60px;
  }

  .sidebar-header h5,
  .conv-title {
    display: none;
  }

  .sidebar-header .el-button span {
    display: none;
  }

  .conversation-item {
    justify-content: center;
    padding: 8px;
  }
    .d-flex { flex-wrap: wrap; }
}
</style>
