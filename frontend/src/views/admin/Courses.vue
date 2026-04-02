<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">课程管理</h1>
        <p class="page-subtitle">管理平台上的所有课程</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>添加课程
        </el-button>
        <el-button type="success" @click="$router.push('/admin/categories')">
          <el-icon><FolderOpened /></el-icon>管理分类
        </el-button>
      </div>
    </div>

    <div class="filter-card">
      <div class="filter-row">
        <el-input
          v-model="searchQuery"
          placeholder="搜索课程名称..."
          :prefix-icon="Search"
          clearable
          class="filter-input"
          @clear="fetchCourses"
          @keyup.enter="fetchCourses"
        />
        <el-select v-model="statusFilter" placeholder="课程状态" clearable class="filter-select" @change="fetchCourses">
          <el-option label="已发布" value="published" />
          <el-option label="草稿" value="draft" />
          <el-option label="已归档" value="archived" />
        </el-select>
        <el-select v-model="categoryFilter" placeholder="课程分类" clearable class="filter-select" @change="fetchCourses">
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
        <el-button type="primary" @click="fetchCourses" :loading="loading">
          <el-icon><Search /></el-icon>
          <span>搜索</span>
        </el-button>
      </div>
    </div>

    <div class="table-card">
      <el-table :data="courses" stripe v-loading="loading" class="admin-table">
        <el-table-column prop="title" label="课程名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="course-title">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="教师" width="130" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="teacher-cell">
              <el-avatar :size="24" class="teacher-avatar">{{ (row.teacher_name || '-').charAt(0) }}</el-avatar>
              <span>{{ row.teacher_name || '-' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="120" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag size="small" effect="plain" type="info">
              {{ row.category_name || getCategoryName(row.category_id) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="价格" width="90" align="center">
          <template #default="{ row }">
            <span class="price-text">¥{{ row.price || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="学生数" width="90" align="center">
          <template #default="{ row }">
            <span class="count-badge">{{ row.student_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small" effect="light" round>
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" plain @click="openEditDialog(row)">编辑</el-button>
            <el-button v-if="row.status === 'draft'" type="success" size="small" plain @click="toggleStatus(row, 'published')">发布</el-button>
            <el-button v-if="row.status === 'published'" type="warning" size="small" plain @click="toggleStatus(row, 'draft')">下架</el-button>
            <el-button type="danger" size="small" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="totalCourses"
          layout="total, sizes, prev, pager, next"
          background
          @current-change="fetchCourses"
          @size-change="fetchCourses"
        />
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="editingCourse ? '编辑课程' : '添加课程'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="课程名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="授课教师" prop="teacher_id">
          <el-select v-model="form.teacher_id" placeholder="请选择授课教师" style="width: 100%" filterable>
            <el-option v-for="t in teachers" :key="t.id" :label="t.real_name || t.username" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择课程分类" style="width: 100%">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <div style="display: flex; gap: 16px;">
          <el-form-item label="课程价格" prop="price" style="flex: 1">
            <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" />
          </el-form-item>
          <el-form-item label="课程状态" prop="status" style="flex: 1">
            <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
              <el-option label="草稿" value="draft" />
              <el-option label="已发布" value="published" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="课程封面" prop="cover_image">
          <div style="width: 100%;">
            <div style="display: flex; gap: 12px; margin-bottom: 8px;">
              <el-radio-group v-model="coverImageType">
                <el-radio value="url">网络图片</el-radio>
                <el-radio value="upload">本地上传</el-radio>
              </el-radio-group>
            </div>
            <div v-if="coverImageType === 'url'">
              <el-input v-model="form.cover_image" placeholder="请输入封面图片URL" />
            </div>
            <div v-else>
              <el-upload
                class="cover-uploader"
                :show-file-list="false"
                :before-upload="beforeCoverUpload"
                :http-request="handleCoverUpload"
                accept="image/*"
              >
                <img v-if="form.cover_image" :src="form.cover_image" class="cover-preview" />
                <div v-else class="cover-placeholder">
                  <el-icon :size="24"><Plus /></el-icon>
                  <p>点击上传封面</p>
                </div>
              </el-upload>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="课程描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入课程描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ editingCourse ? '保存修改' : '确认添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi, courseApi, uploadApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, FolderOpened, Upload } from '@element-plus/icons-vue'

const loading = ref(true)
const courses = ref([])
const categories = ref([])
const teachers = ref([])
const totalCourses = ref(0)
const searchQuery = ref('')
const statusFilter = ref('')
const categoryFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const dialogVisible = ref(false)
const editingCourse = ref(null)
const submitting = ref(false)
const coverImageType = ref('url')
const formRef = ref(null)

const form = ref({
  title: '',
  teacher_id: null,
  category_id: null,
  price: 0,
  status: 'draft',
  cover_image: '',
  description: ''
})

const rules = {
  title: [{ required: true, message: '请输入课程名称', trigger: 'change' }],
  teacher_id: [{ required: true, message: '请选择授课教师', trigger: 'change' }],
  category_id: [{ required: true, message: '请选择课程分类', trigger: 'change' }]
}

function getStatusTagType(status) {
  return { published: 'success', draft: 'info', archived: 'warning' }[status] || 'info'
}

function getStatusLabel(status) {
  return { published: '已发布', draft: '草稿', archived: '已归档' }[status] || status
}

function getCategoryName(id) {
  if (!id) return '未分类'
  return categories.value.find(c => c.id === id)?.name || '未分类'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

// 打开创建课程的对话框
function openCreateDialog() {
  editingCourse.value = null
  coverImageType.value = 'url'
  form.value = { title: '', teacher_id: null, category_id: null, price: 0, status: 'draft', cover_image: '', description: '' }
  dialogVisible.value = true
}

// 打开编辑课程的对话框
function openEditDialog(course) {
  editingCourse.value = course
  coverImageType.value = course.cover_image?.startsWith('http') ? 'url' : 'upload'
  form.value = {
    title: course.title,
    teacher_id: course.teacher_id,
    category_id: course.category_id,
    price: course.price || 0,
    status: course.status,
    cover_image: course.cover_image || '',
    description: course.description || ''
  }
  dialogVisible.value = true
}

// 上传封面图片前的校验函数
function beforeCoverUpload(file) {
  const isImage = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

// 处理封面图片上传
async function handleCoverUpload(options) {
  const formData = new FormData()
  formData.append('file', options.file)

  try {
    const res = await uploadApi.uploadCourseImage(formData)
    form.value.cover_image = res.data.url
    ElMessage.success('封面上传成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '上传失败')
  }
}

 // 提交表单
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editingCourse.value) {
      await courseApi.updateCourse(editingCourse.value.id, form.value)
      const idx = courses.value.findIndex(c => c.id === editingCourse.value.id)
      if (idx > -1) {
        const teacher = teachers.value.find(t => t.id === form.value.teacher_id)
        const category = categories.value.find(c => c.id === form.value.category_id)
        courses.value[idx] = {
          ...courses.value[idx],
          ...form.value,
          teacher_name: teacher?.real_name || teacher?.username,
          category_name: category?.name
        }
      }
      ElMessage.success('更新成功')
    } else {
      const res = await courseApi.createCourse(form.value)
      const newCourse = res.data.course || { id: Date.now(), ...form.value, created_at: new Date().toISOString() }
      const teacher = teachers.value.find(t => t.id === form.value.teacher_id)
      const category = categories.value.find(c => c.id === form.value.category_id)
      newCourse.teacher_name = teacher?.real_name || teacher?.username
      newCourse.category_name = category?.name
      newCourse.student_count = 0
      courses.value.unshift(newCourse)
      totalCourses.value++
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '操作失败')
  } finally {
    submitting.value = false
  }
}

 // 切换课程状态
async function toggleStatus(course, newStatus) {
  const label = { published: '发布', draft: '下架' }[newStatus] || '修改状态'
  try {
    await ElMessageBox.confirm(`确定要${label}课程 "${course.title}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await courseApi.updateCourse(course.id, { status: newStatus })
    const target = courses.value.find(c => c.id === course.id)
    if (target) target.status = newStatus
    ElMessage.success(`${label}成功`)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.error || `${label}失败`)
  }
}

 // 删除课程
async function handleDelete(course) {
  try {
    await ElMessageBox.confirm(`确定删除课程 "${course.title}" 吗？此操作不可恢复。`, '警告', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'error'
    })
    await courseApi.deleteCourse(course.id)
    courses.value = courses.value.filter(c => c.id !== course.id)
    totalCourses.value--
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.error || '删除失败')
  }
}

 // 获取课程列表
async function fetchCourses() {
  loading.value = true
  try {
    const params = { page: currentPage.value, per_page: pageSize.value }
    if (statusFilter.value) params.status = statusFilter.value
    if (categoryFilter.value) params.category_id = categoryFilter.value
    if (searchQuery.value) params.keyword = searchQuery.value
    const res = await adminApi.getAllCourses(params)
    courses.value = res.data.courses || res.data || []
    totalCourses.value = res.data.total || courses.value.length
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '获取课程列表失败')
  } finally {
    loading.value = false
  }
}

 // 获取课程分类列表
async function fetchCategories() {
  try {
    const res = await courseApi.getCategories()
    categories.value = res.data.categories || res.data || []
  } catch { categories.value = [] }
}

// 获取教师列表
async function fetchTeachers() {
  try {
    const res = await adminApi.getTeachers()
    teachers.value = res.data.teachers || res.data || []
  } catch { teachers.value = [] }
}

// 组件挂载后获取数据
onMounted(() => {
  fetchCourses()
  fetchCategories()
  fetchTeachers()
})
</script>

<style scoped>
.page { min-height: 100%; }

.page-header {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.header-actions { display: flex; gap: 12px; }

.filter-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-input { width: 240px; }
.filter-select { width: 160px; }

.table-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.admin-table :deep(.el-table__row:hover) {
  background-color: #f8fafc !important;
}

.course-title {
  font-weight: 500;
  color: #1f2937;
}

.teacher-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.teacher-avatar {
  background: linear-gradient(135deg, #10b981, #34d399);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.price-text {
  font-weight: 600;
  color: #f59e0b;
}

.count-badge {
  font-weight: 600;
  color: #374151;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f3f4f6;
}

.cover-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 200px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.3s;
}

.cover-uploader:hover {
  border-color: #409eff;
}

.cover-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8c939d;
}

.cover-placeholder p {
  margin: 8px 0 0;
  font-size: 12px;
}

@media (max-width: 768px) {
  .filter-input, .filter-select { width: 100%; }
  .filter-row { flex-direction: column; }
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  .header-actions { width: 100%; }
}
</style>
