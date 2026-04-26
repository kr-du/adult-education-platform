<template>
  <div class="course-edit py-4">
    <div class="container">
      <div class="mb-4">
        <router-link to="/teacher/courses" class="text-muted text-decoration-none mb-2 d-inline-block">
          <el-icon class="me-1"><ArrowLeft /></el-icon>返回课程列表
        </router-link>
        <h2 class="fw-bold mb-0">{{ isEditing ? '编辑课程' : '创建课程' }}</h2>
      </div>

      <el-skeleton :loading="loading" animated :rows="10">
        <template #default>
          <el-tabs v-model="activeTab" type="border-card">
            <el-tab-pane label="基本信息" name="info">
              <el-form ref="courseFormRef" :model="courseForm" :rules="courseRules" label-position="top" class="mt-3">
                <div class="row">
                  <div class="col-lg-8">
                    <el-form-item label="课程名称" prop="title">
                      <el-input v-model="courseForm.title" placeholder="请输入课程名称" size="large" />
                    </el-form-item>
                    <el-form-item label="课程描述" prop="description">
                      <el-input v-model="courseForm.description" type="textarea" :rows="6" placeholder="请输入课程描述，支持详细的教学目标、适用人群等" />
                    </el-form-item>
                  </div>
                  <div class="col-lg-4">
                    <el-form-item label="课程分类">
                      <el-select v-model="courseForm.category_id" placeholder="选择分类" clearable class="w-100">
                        <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="课程状态">
                      <el-select v-model="courseForm.status" class="w-100">
                        <el-option label="草稿" value="draft" />
                        <el-option label="已发布" value="published" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="课程封面">
                      <div class="cover-upload-area">
                        <div class="d-flex gap-3 mb-3">
                          <el-radio-group v-model="coverImageType">
                            <el-radio value="url">网络图片</el-radio>
                            <el-radio value="upload">本地上传</el-radio>
                          </el-radio-group>
                        </div>
                        <div v-if="coverImageType === 'url'">
                          <el-input v-model="courseForm.cover_image" placeholder="请输入图片URL地址" />
                        </div>
                        <div v-else>
                          <el-upload
                            class="cover-uploader w-100"
                            :show-file-list="false"
                            :http-request="handleCoverUpload"
                            accept="image/*"
                          >
                            <div v-if="courseForm.cover_image" class="cover-preview">
                              <img :src="courseForm.cover_image" class="img-fluid rounded" />
                            </div>
                            <div v-else class="cover-placeholder d-flex align-items-center justify-content-center rounded border border-dashed" style="height: 150px;">
                              <div class="text-center text-muted">
                                <el-icon :size="32"><Plus /></el-icon>
                                <p class="small mb-0 mt-1">点击上传封面</p>
                                <p class="small text-muted mb-0">支持 jpg/png/gif/webp，不超过5MB</p>
                              </div>
                            </div>
                          </el-upload>
                        </div>
                        <div v-if="courseForm.cover_image" class="mt-2">
                          <el-button size="small" type="danger" plain @click="courseForm.cover_image = ''">
                            <el-icon class="me-1"><Delete /></el-icon>清除封面
                          </el-button>
                        </div>
                      </div>
                    </el-form-item>
                  </div>
                </div>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="课时管理" name="lessons">
              <div class="d-flex justify-content-between align-items-center mt-3 mb-3">
                <span class="text-muted">共 {{ lessons.length }} 个课时</span>
                <el-button type="primary" size="small" @click="openLessonDialog()">
                  <el-icon class="me-1"><Plus /></el-icon>添加课时
                </el-button>
              </div>

              <div v-if="lessons.length === 0" class="text-center py-5">
                <el-empty description="暂无课时">
                  <el-button type="primary" @click="openLessonDialog()">添加第一个课时</el-button>
                </el-empty>
              </div>

              <VueDraggable v-else v-model="lessons" item-key="id" tag="div">
                <template #item="{ element, index }">
                  <div :key="element.id || index" class="lesson-item d-flex align-items-center p-3 mb-2 border rounded bg-white">
                    <div class="lesson-order me-3 text-muted fw-bold" style="width: 30px;">
                      {{ index + 1 }}
                    </div>
                    <div class="flex-grow-1 min-w-0">
                      <h6 class="mb-1 text-truncate">{{ element.title }}</h6>
                      <small class="text-muted">{{ element.duration || 0 }} 分钟 · 图文教程</small>
                    </div>
                    <div class="d-flex gap-2">
                      <el-button size="small" @click="openLessonDialog(element, index)">
                        <el-icon><Edit /></el-icon>
                      </el-button>
                      <el-button size="small" type="danger" plain @click="deleteLesson(index)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </template>
              </VueDraggable>
            </el-tab-pane>

            <el-tab-pane label="作业管理" name="assignments">
              <div class="d-flex justify-content-between align-items-center mt-3 mb-3">
                <span class="text-muted">共 {{ assignments.length }} 个作业</span>
                <el-button type="primary" size="small" @click="openAssignmentDialog()">
                  <el-icon class="me-1"><Plus /></el-icon>添加作业
                </el-button>
              </div>

              <div v-if="assignments.length === 0" class="text-center py-5">
                <el-empty description="暂无作业">
                  <el-button type="primary" @click="openAssignmentDialog()">添加第一个作业</el-button>
                </el-empty>
              </div>

              <el-table v-else :data="assignments" stripe>
                <el-table-column prop="title" label="作业名称" min-width="200" show-overflow-tooltip />
                <el-table-column label="截止时间" width="180" align="center">
                  <template #default="{ row }">
                    {{ formatDate(row.deadline) }}
                  </template>
                </el-table-column>
                <el-table-column label="满分" width="100" align="center">
                  <template #default="{ row }">
                    {{ row.max_score || 100 }} 分
                  </template>
                </el-table-column>
                <el-table-column label="提交数" width="100" align="center">
                  <template #default="{ row }">
                    {{ row.submission_count || 0 }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="160" align="center">
                  <template #default="{ row, $index }">
                    <el-button size="small" @click="openAssignmentDialog(row, $index)">编辑</el-button>
                    <el-button size="small" type="danger" plain @click="deleteAssignment($index)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>

          <div class="d-flex justify-content-end mt-4">
            <el-button type="primary" size="large" :loading="saving" @click="saveCourse">
              <el-icon class="me-1"><Check /></el-icon>保存课程
            </el-button>
          </div>
        </template>
      </el-skeleton>
    </div>

    <!-- 课时编辑对话框 -->
    <el-dialog v-model="lessonDialogVisible" :title="editingLessonIndex != null ? '编辑课时' : '添加课时'" width="900px" :close-on-click-modal="false">
      <el-form ref="lessonFormRef" :model="lessonForm" :rules="lessonRules" label-position="top">
        <el-form-item label="课时标题" prop="title">
          <el-input v-model="lessonForm.title" placeholder="请输入课时标题" />
        </el-form-item>
        <el-form-item label="预估阅读时长 (分钟)">
          <el-input-number v-model="lessonForm.duration" :min="1" :max="999" class="w-100" />
        </el-form-item>
        
        <!-- Markdown 编辑器 -->
        <el-form-item label="课时内容 (支持 Markdown 格式)">
          <div class="markdown-editor">
            <div class="editor-toolbar">
              <el-button-group size="small">
                <el-button @click="insertMarkdown('**', '**')" title="加粗">B</el-button>
                <el-button @click="insertMarkdown('*', '*')" title="斜体"><em>I</em></el-button>
                <el-button @click="insertMarkdown('`', '`')" title="代码">&lt;/&gt;</el-button>
                <el-button @click="insertMarkdown('# ', '')" title="标题">H</el-button>
                <el-button @click="insertMarkdown('- ', '')" title="列表">•</el-button>
                <el-button @click="insertMarkdown('> ', '')" title="引用">"</el-button>
              </el-button-group>
              <el-button size="small" @click="showPreview = !showPreview">
                {{ showPreview ? '编辑' : '预览' }}
              </el-button>
            </div>
            <div class="editor-body" :class="{ 'split-view': showPreview }">
              <div class="editor-pane">
                <el-input
                  ref="contentEditorRef"
                  v-model="lessonForm.content"
                  type="textarea"
                  :rows="15"
                  placeholder="请输入 Markdown 格式的课时内容...

示例：
# 第一章节标题

这是一段正文内容，可以包含**加粗**和*斜体*文字。

## 小标题

- 列表项 1
- 列表项 2
- 列表项 3

```javascript
// 代码示例
console.log('Hello World');
```

> 这是一段引用文字"
                />
              </div>
              <div v-if="showPreview" class="preview-pane">
                <div class="preview-label">预览</div>
                <div class="preview-content">
                  <ArticleReader :content="lessonForm.content" :title="lessonForm.title" />
                </div>
              </div>
            </div>
            <div class="editor-footer text-muted small mt-2">
              支持 Markdown 语法：标题(#)、加粗(**)、斜体(*)、代码(`)、列表(-)、引用(>)、链接([]())等
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="lessonDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveLesson">确认</el-button>
      </template>
    </el-dialog>

    <!-- 作业编辑对话框 -->
    <el-dialog v-model="assignmentDialogVisible" :title="editingAssignmentIndex != null ? '编辑作业' : '添加作业'" width="600px" :close-on-click-modal="false">
      <el-form ref="assignmentFormRef" :model="assignmentForm" :rules="assignmentRules" label-position="top">
        <el-form-item label="作业名称" prop="title">
          <el-input v-model="assignmentForm.title" placeholder="请输入作业名称" />
        </el-form-item>
        <el-form-item label="作业描述">
          <el-input v-model="assignmentForm.description" type="textarea" :rows="4" placeholder="作业要求说明" />
        </el-form-item>
        <div class="row">
          <div class="col-md-6">
            <el-form-item label="截止时间">
              <el-date-picker v-model="assignmentForm.deadline" type="datetime" placeholder="选择截止时间" class="w-100" />
            </el-form-item>
          </div>
          <div class="col-md-6">
            <el-form-item label="满分">
              <el-input-number v-model="assignmentForm.max_score" :min="1" :max="1000" class="w-100" />
            </el-form-item>
          </div>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="assignmentDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submittingAssignment" @click="handleSaveAssignment">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { courseApi, assignmentApi, uploadApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Check, Plus, Edit, Delete } from '@element-plus/icons-vue'
import VueDraggable from 'vuedraggable'
import ArticleReader from '@/components/common/ArticleReader.vue'

const route = useRoute()
const router = useRouter()

const courseId = computed(() => route.params.id)
const isEditing = computed(() => !!courseId.value && courseId.value !== 'new')
const activeTab = ref('info')
const loading = ref(true)
const saving = ref(false)
const courseFormRef = ref(null)
const coverImageType = ref('url')

const courseForm = ref({
  title: '',
  description: '',
  category_id: null,
  status: 'draft',
  cover_image: ''
})

const courseRules = {
  title: [{ required: true, message: '请输入课程名称', trigger: 'change' }]
}

const categories = ref([])
const lessons = ref([])
const assignments = ref([])

// Lesson dialog
const lessonDialogVisible = ref(false)
const editingLessonIndex = ref(null)
const lessonFormRef = ref(null)
const contentEditorRef = ref(null)
const showPreview = ref(false)
const lessonForm = ref({
  title: '',
  content_type: 'article',
  duration: 10,
  content: '',
  description: ''
})
const lessonRules = {
  title: [{ required: true, message: '请输入课时标题', trigger: 'change' }]
}

// Assignment dialog
const assignmentDialogVisible = ref(false)
const editingAssignmentIndex = ref(null)
const assignmentFormRef = ref(null)
const submittingAssignment = ref(false)
const assignmentForm = ref({
  title: '',
  description: '',
  deadline: null,
  max_score: 100
})
const assignmentRules = {
  title: [{ required: true, message: '请输入作业名称', trigger: 'change' }]
}

function formatDate(dateStr) {
  if (!dateStr) return '未设置'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function handleCoverUpload(options) {
  const formData = new FormData()
  formData.append('file', options.file)

  try {
    const res = await uploadApi.uploadCourseImage(formData)
    courseForm.value.cover_image = res.data.url
    ElMessage.success('封面上传成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '上传失败')
  }
}

function openLessonDialog(lesson = null, index = null) {
  editingLessonIndex.value = index
  showPreview.value = false
  if (lesson) {
    lessonForm.value = {
      title: lesson.title || '',
      content_type: 'article',
      duration: lesson.duration || 10,
      content: lesson.content || '',
      description: lesson.description || ''
    }
  } else {
    lessonForm.value = {
      title: '',
      content_type: 'article',
      duration: 10,
      content: '',
      description: ''
    }
  }
  lessonDialogVisible.value = true
}

function insertMarkdown(before, after) {
  const textarea = contentEditorRef.value?.textarea
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = lessonForm.value.content || ''
  const selectedText = text.substring(start, end)

  const newText = text.substring(0, start) + before + selectedText + after + text.substring(end)
  lessonForm.value.content = newText

  // 恢复光标位置
  setTimeout(() => {
    textarea.focus()
    textarea.setSelectionRange(start + before.length, end + before.length)
  }, 0)
}

function handleSaveLesson() {
  if (!lessonForm.value.title.trim()) {
    ElMessage.warning('请输入课时标题')
    return
  }
  if (editingLessonIndex.value != null) {
    lessons.value[editingLessonIndex.value] = { ...lessonForm.value }
  } else {
    lessons.value.push({ ...lessonForm.value })
  }
  lessonDialogVisible.value = false
  ElMessage.success('保存成功')
}

async function deleteLesson(index) {
  try {
    await ElMessageBox.confirm('确定要删除该课时吗？', '提示', { type: 'warning' })
    lessons.value.splice(index, 1)
    ElMessage.success('删除成功')
  } catch {
    // cancelled
  }
}

function openAssignmentDialog(assignment = null, index = null) {
  editingAssignmentIndex.value = index
  if (assignment) {
    assignmentForm.value = { ...assignment }
  } else {
    assignmentForm.value = { title: '', description: '', deadline: null, max_score: 100 }
  }
  assignmentDialogVisible.value = true
}

async function handleSaveAssignment() {
  const valid = await assignmentFormRef.value.validate().catch(() => false)
  if (!valid) return

  if (!isEditing.value) {
    ElMessage.warning('请先保存课程后再添加作业')
    return
  }

  submittingAssignment.value = true
  try {
    const data = {
      ...assignmentForm.value,
      course_id: parseInt(courseId.value)
    }

    if (editingAssignmentIndex.value != null) {
      const existing = assignments.value[editingAssignmentIndex.value]
      assignments.value[editingAssignmentIndex.value] = { ...existing, ...assignmentForm.value }
      ElMessage.success('更新成功')
    } else {
      const res = await assignmentApi.createAssignment(data)
      const newAssignment = res.data || { ...data, id: Date.now() }
      assignments.value.push(newAssignment)
      ElMessage.success('创建成功')
    }
    assignmentDialogVisible.value = false
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    submittingAssignment.value = false
  }
}

async function deleteAssignment(index) {
  try {
    await ElMessageBox.confirm('确定要删除该作业吗？', '提示', { type: 'warning' })
    assignments.value.splice(index, 1)
    ElMessage.success('删除成功')
  } catch {
    // cancelled
  }
}

async function saveCourse() {
  const valid = await courseFormRef.value.validate().catch(() => false)
  if (!valid) {
    activeTab.value = 'info'
    return
  }

  saving.value = true
  try {
    if (isEditing.value) {
      await courseApi.updateCourse(courseId.value, courseForm.value)
      for (const lesson of lessons.value) {
        if (!lesson.id) {
          await courseApi.addLesson(courseId.value, lesson)
        }
      }
      ElMessage.success('保存成功')
    } else {
      const res = await courseApi.createCourse(courseForm.value)
      const newId = res.data?.id || res.data?.course?.id
      if (newId) {
        for (const lesson of lessons.value) {
          await courseApi.addLesson(newId, lesson)
        }
        router.replace(`/teacher/course/${newId}/edit`)
      }
      ElMessage.success('创建成功')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function fetchData() {
  loading.value = true
  try {
    const catRes = await courseApi.getCategories()
    categories.value = catRes.data.categories || catRes.data || []

    if (isEditing.value) {
      const [courseRes, assignRes] = await Promise.allSettled([
        courseApi.getCourse(courseId.value),
        assignmentApi.getCourseAssignments(courseId.value)
      ])

      if (courseRes.status === 'fulfilled') {
        const data = courseRes.value.data.course || courseRes.value.data || {}
        courseForm.value = {
          title: data.title || '',
          description: data.description || '',
          category_id: data.category_id || null,
          status: data.status || 'draft',
          cover_image: data.cover_image || ''
        }
        lessons.value = (data.lessons || []).map(l => ({
          ...l,
          content_type: 'article'
        }))

        if (data.cover_image && !data.cover_image.startsWith('http')) {
          coverImageType.value = 'upload'
        }
      }

      if (assignRes.status === 'fulfilled') {
        assignments.value = assignRes.value.data.assignments || assignRes.value.data || []
      }
    }
  } catch (e) {
    ElMessage.error('获取课程信息失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.min-w-0 {
  min-width: 0;
}

.lesson-item {
  transition: box-shadow 0.2s;
}

.lesson-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.border-dashed {
  border-style: dashed !important;
}

.cover-preview img {
  max-height: 150px;
  object-fit: cover;
}

/* Markdown 编辑器样式 */
.markdown-editor {
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

.editor-body {
  display: flex;
}

.editor-body.split-view .editor-pane {
  width: 50%;
  border-right: 1px solid #dcdfe6;
}

.editor-pane {
  flex: 1;
}

.editor-pane :deep(.el-textarea__inner) {
  border: none;
  border-radius: 0;
  resize: none;
}

.preview-pane {
  width: 50%;
  max-height: 400px;
  overflow-y: auto;
  background: #fafafa;
}

.preview-label {
  padding: 8px 12px;
  background: #f0f0f0;
  font-size: 12px;
  color: #666;
  border-bottom: 1px solid #ebeef5;
}

.preview-content {
  padding: 16px;
  font-size: 14px;
}

.preview-content :deep(.article-reader) {
  height: auto;
}

.preview-content :deep(.article-header) {
  display: none;
}

.preview-content :deep(.article-content) {
  padding: 0;
  max-height: 350px;
}

.preview-content :deep(.progress-bar-container),
.preview-content :deep(.article-footer) {
  display: none;
}

.editor-footer {
  padding: 8px 12px;
  background: #fafafa;
  border-top: 1px solid #ebeef5;
}

/* 响应式 */
@media (max-width: 992px) {
  .el-table { font-size: 12px; }
  .el-card { margin-bottom: 12px; }
}

@media (max-width: 768px) {
  .el-card { margin-bottom: 12px; }
  .el-table { font-size: 12px; }
  .d-flex { flex-wrap: wrap; }
  .el-dialog { width: 95% !important; }
  .el-tabs__content { padding: 12px; }
  
  .editor-body.split-view {
    flex-direction: column;
  }
  
  .editor-body.split-view .editor-pane,
  .editor-body.split-view .preview-pane {
    width: 100%;
  }
  
  .preview-pane {
    max-height: 300px;
    border-top: 1px solid #dcdfe6;
  }
}

@media (max-width: 576px) {
  .el-card__body { padding: 12px; }
  .el-form-item__label { width: 100%; }
}
</style>
