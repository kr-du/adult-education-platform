<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">公告管理</h1>
        <p class="page-subtitle">发布和管理平台公告</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        <span>发布公告</span>
      </el-button>
    </div>

    <div class="filter-card">
      <div class="filter-row">
        <el-input
          v-model="searchQuery"
          placeholder="搜索公告标题..."
          :prefix-icon="Search"
          clearable
          class="filter-input"
        />
      </div>
    </div>

    <div class="table-card">
      <el-table :data="filteredAnnouncements" stripe v-loading="loading" class="admin-table">
        <el-table-column label="" width="50" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.is_pinned" class="pinned-icon" :size="18"><Star /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="250">
          <template #default="{ row }">
            <div class="title-cell">
              <el-tag v-if="row.is_pinned" type="warning" size="small" effect="dark" round class="pin-tag">置顶</el-tag>
              <span class="announcement-title">{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="author_name" label="发布者" width="120" align="center">
          <template #default="{ row }">
            <div class="author-cell">
              <el-avatar :size="24" class="author-avatar">{{ (row.author_name || '-').charAt(0) }}</el-avatar>
              <span>{{ row.author_name || '-' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="置顶" width="80" align="center">
          <template #default="{ row }">
            <el-switch :model-value="row.is_pinned" @change="togglePin(row)" :disabled="loading" />
          </template>
        </el-table-column>
        <el-table-column label="发布时间" width="170" align="center">
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

      <div v-if="filteredAnnouncements.length === 0 && !loading" class="empty-wrap">
        <el-empty description="暂无公告">
          <el-button type="primary" @click="openCreateDialog">发布公告</el-button>
        </el-empty>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="editingAnnouncement ? '编辑公告' : '发布公告'"
      width="650px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="公告标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公告标题" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="置顶">
          <div class="pin-row">
            <el-switch v-model="form.is_pinned" />
            <span class="pin-hint">置顶公告将显示在列表最前面</span>
          </div>
        </el-form-item>
        <el-form-item label="公告内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="8" placeholder="请输入公告内容" maxlength="2000" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ editingAnnouncement ? '保存修改' : '发布公告' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Star, Edit, Delete } from '@element-plus/icons-vue'

const loading = ref(true)
const announcements = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const editingAnnouncement = ref(null)
const submitting = ref(false)
const formRef = ref(null)

const form = ref({ title: '', content: '', is_pinned: false })

const rules = {
  title: [{ required: true, message: '请输入公告标题', trigger: 'change' }],
  content: [{ required: true, message: '请输入公告内容', trigger: 'change' }]
}

const filteredAnnouncements = computed(() => {
  let result = [...announcements.value].sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1
    if (!a.is_pinned && b.is_pinned) return 1
    return new Date(b.created_at) - new Date(a.created_at)
  })
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(a => a.title?.toLowerCase().includes(q))
  }
  return result
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

function openCreateDialog() {
  editingAnnouncement.value = null
  form.value = { title: '', content: '', is_pinned: false }
  dialogVisible.value = true
}

function openEditDialog(announcement) {
  editingAnnouncement.value = announcement
  form.value = {
    title: announcement.title,
    content: announcement.content,
    is_pinned: announcement.is_pinned ?? false
  }
  dialogVisible.value = true
}

async function togglePin(announcement) {
  try {
    const newPinned = !announcement.is_pinned
    await adminApi.updateAnnouncement(announcement.id, { is_pinned: newPinned })
    const target = announcements.value.find(a => a.id === announcement.id)
    if (target) target.is_pinned = newPinned
    ElMessage.success(newPinned ? '已置顶' : '已取消置顶')
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '操作失败')
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editingAnnouncement.value) {
      const res = await adminApi.updateAnnouncement(editingAnnouncement.value.id, form.value)
      const updated = res.data.announcement || form.value
      const idx = announcements.value.findIndex(a => a.id === editingAnnouncement.value.id)
      if (idx > -1) announcements.value[idx] = { ...announcements.value[idx], ...updated }
      ElMessage.success('更新成功')
    } else {
      const res = await adminApi.createAnnouncement(form.value)
      const newAnn = res.data.announcement || { id: Date.now(), ...form.value, created_at: new Date().toISOString() }
      announcements.value.unshift(newAnn)
      ElMessage.success('发布成功')
    }
    dialogVisible.value = false
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(announcement) {
  try {
    await ElMessageBox.confirm(`确定删除公告 "${announcement.title}" 吗？此操作不可恢复。`, '警告', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'error'
    })
    await adminApi.deleteAnnouncement(announcement.id)
    announcements.value = announcements.value.filter(a => a.id !== announcement.id)
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.error || '删除失败')
  }
}

async function fetchAnnouncements() {
  loading.value = true
  try {
    const res = await adminApi.getAnnouncements()
    announcements.value = res.data.announcements || res.data || []
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '获取公告列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => { fetchAnnouncements() })
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
}

.filter-input { width: 300px; }

.table-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.admin-table :deep(.el-table__row:hover) {
  background-color: #f8fafc !important;
}

.pinned-icon { color: #f59e0b; }

.title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pin-tag { flex-shrink: 0; }

.announcement-title {
  font-weight: 500;
  color: #1f2937;
}

.author-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.author-avatar {
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.pin-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pin-hint {
  color: #9ca3af;
  font-size: 13px;
}

.empty-wrap { padding: 40px 0; }

@media (max-width: 768px) {
  .filter-input { width: 100%; }
  .filter-row { flex-direction: column; }
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
}
</style>
