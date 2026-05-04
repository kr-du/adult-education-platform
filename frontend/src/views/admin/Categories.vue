<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">分类管理</h1>
        <p class="page-subtitle">管理课程分类，便于课程归类</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        <span>新增分类</span>
      </el-button>
    </div>

    <div class="table-card">
      <el-table :data="categories" stripe v-loading="loading" class="admin-table">
        <el-table-column label="ID" width="80" align="center">
          <template #default="{ $index }">
            <span class="id-badge">#{{ $index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="分类名称" min-width="180">
          <template #default="{ row }">
            <div class="category-name-cell">
              <el-icon class="category-icon" :size="18"><Folder /></el-icon>
              <span class="category-name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="desc-text">{{ row.description || '暂无描述' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="课程数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info" effect="plain" size="small" round>
              {{ row.course_count || 0 }} 门
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" plain @click="openEditDialog(row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button type="danger" size="small" plain @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="categories.length === 0 && !loading" class="empty-wrap">
        <el-empty description="暂无分类">
          <el-button type="primary" @click="openCreateDialog">创建第一个分类</el-button>
        </el-empty>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="editingCategory ? '编辑分类' : '新增分类'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="分类描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入分类描述" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { courseApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Folder } from '@element-plus/icons-vue'

const loading = ref(true)
const categories = ref([])
const dialogVisible = ref(false)
const editingCategory = ref(null)
const submitting = ref(false)
const formRef = ref(null)

const form = ref({ name: '', description: '' })

const rules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'change' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'change' }
  ]
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

function openCreateDialog() {
  editingCategory.value = null
  form.value = { name: '', description: '' }
  dialogVisible.value = true
}

function openEditDialog(category) {
  editingCategory.value = category
  form.value = { name: category.name, description: category.description || '' }
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editingCategory.value) {
      const res = await courseApi.updateCategory(editingCategory.value.id, form.value)
      const updated = res.data.category || form.value
      const idx = categories.value.findIndex(c => c.id === editingCategory.value.id)
      if (idx > -1) categories.value[idx] = { ...categories.value[idx], ...updated }
      ElMessage.success('更新成功')
    } else {
      const res = await courseApi.createCategory(form.value)
      const newCat = res.data.category || { id: Date.now(), ...form.value, course_count: 0, created_at: new Date().toISOString() }
      categories.value.push(newCat)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(category) {
  try {
    await ElMessageBox.confirm(`确定删除分类 "${category.name}" 吗？该分类下的课程将变为未分类。`, '警告', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'error'
    })
    await courseApi.deleteCategory(category.id)
    categories.value = categories.value.filter(c => c.id !== category.id)
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.error || '删除失败')
  }
}

async function fetchCategories() {
  loading.value = true
  try {
    const res = await courseApi.getCategories()
    categories.value = res.data.categories || res.data || []
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '获取分类列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => { fetchCategories() })
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

.table-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.admin-table :deep(.el-table__row:hover) {
  background-color: #f8fafc !important;
}

.id-badge {
  font-size: 13px;
  color: #9ca3af;
  font-weight: 500;
}

.category-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-icon {
  color: #f59e0b;
  flex-shrink: 0;
}

.category-name {
  font-weight: 500;
  color: #1f2937;
}

.desc-text {
  color: #6b7280;
  font-size: 13px;
}

.empty-wrap { padding: 40px 0; }

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
}
</style>
