<template>
  <div class="backup-management py-4">
    <div class="container">
      <h2 class="fw-bold mb-4">数据备份与恢复</h2>

      <!-- 统计卡片 -->
      <div class="row g-4 mb-4">
        <div class="col-lg-3 col-md-6" v-for="(value, key) in statistics" :key="key">
          <el-card shadow="hover" class="text-center">
            <h4 class="fw-bold mb-1">{{ value }}</h4>
            <p class="text-muted mb-0 small">{{ getTableLabel(key) }}</p>
          </el-card>
        </div>
      </div>

      <!-- 操作区域 -->
      <el-card class="mb-4">
        <template #header>
          <div class="d-flex justify-content-between align-items-center">
            <span class="fw-bold">备份操作</span>
          </div>
        </template>

        <div class="row g-3">
          <div class="col-md-6">
            <el-card shadow="never" class="h-100">
              <h5 class="fw-bold mb-3">创建备份</h5>
              <el-checkbox-group v-model="selectedTables" class="mb-3">
                <el-checkbox label="all">全部数据</el-checkbox>
                <el-checkbox label="users">用户</el-checkbox>
                <el-checkbox label="courses">课程</el-checkbox>
                <el-checkbox label="enrollments">报名</el-checkbox>
                <el-checkbox label="assignments">作业</el-checkbox>
                <el-checkbox label="submissions">提交</el-checkbox>
                <el-checkbox label="reviews">评价</el-checkbox>
                <el-checkbox label="questions">提问</el-checkbox>
                <el-checkbox label="discussions">讨论</el-checkbox>
              </el-checkbox-group>
              <el-button type="primary" :loading="exporting" @click="handleExport">
                <el-icon class="me-1"><Download /></el-icon>创建备份
              </el-button>
            </el-card>
          </div>
          <div class="col-md-6">
            <el-card shadow="never" class="h-100">
              <h5 class="fw-bold mb-3">恢复数据</h5>
              <el-upload
                ref="uploadRef"
                :auto-upload="false"
                :limit="1"
                accept=".json"
                :on-change="handleFileChange"
                drag
              >
                <el-icon class="el-icon--upload"><Upload /></el-icon>
                <div class="el-upload__text">将备份文件拖到此处，或<em>点击上传</em></div>
              </el-upload>
              <div class="mt-3">
                <el-radio-group v-model="restoreMode">
                  <el-radio value="merge">合并模式</el-radio>
                  <el-radio value="replace">替换模式</el-radio>
                </el-radio-group>
              </div>
              <el-button type="warning" :loading="restoring" :disabled="!restoreFile" @click="handleRestore" class="mt-3">
                <el-icon class="me-1"><RefreshRight /></el-icon>恢复数据
              </el-button>
            </el-card>
          </div>
        </div>
      </el-card>

      <!-- 备份列表 -->
      <el-card>
        <template #header>
          <div class="d-flex justify-content-between align-items-center">
            <span class="fw-bold">备份列表</span>
            <el-button type="primary" link @click="fetchBackups">
              <el-icon class="me-1"><Refresh /></el-icon>刷新
            </el-button>
          </div>
        </template>

        <el-table :data="backups" stripe border v-loading="loading" class="d-none d-md-block">
          <el-table-column prop="filename" label="文件名" min-width="200" />
          <el-table-column label="大小" width="120">
            <template #default="{ row }">
              {{ formatSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="handleDownload(row.filename)">下载</el-button>
              <el-button type="danger" size="small" @click="handleDelete(row.filename)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 移动端备份卡片 -->
        <div class="d-md-none" v-loading="loading">
          <div v-for="item in backups" :key="item.filename" class="mb-3">
            <el-card shadow="hover">
              <h6 class="mb-1 text-truncate">{{ item.filename }}</h6>
              <div class="d-flex justify-content-between text-muted small mb-2">
                <span>{{ formatSize(item.size) }}</span>
                <span>{{ formatDate(item.created_at) }}</span>
              </div>
              <div class="d-flex gap-2">
                <el-button type="primary" size="small" class="flex-grow-1" @click="handleDownload(item.filename)">下载</el-button>
                <el-button type="danger" size="small" class="flex-grow-1" @click="handleDelete(item.filename)">删除</el-button>
              </div>
            </el-card>
          </div>
        </div>

        <div v-if="backups.length === 0" class="text-center py-4">
          <el-empty description="暂无备份记录" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Upload, RefreshRight, Refresh } from '@element-plus/icons-vue'

const loading = ref(false)
const exporting = ref(false)
const restoring = ref(false)
const backups = ref([])
const statistics = ref({})
const selectedTables = ref(['all'])
const restoreMode = ref('merge')
const restoreFile = ref(null)
const uploadRef = ref(null)

const tableLabels = {
  users: '用户',
  categories: '分类',
  courses: '课程',
  lessons: '课时',
  enrollments: '报名',
  assignments: '作业',
  submissions: '提交',
  reviews: '评价',
  questions: '提问',
  answers: '回答',
  messages: '消息',
  course_notices: '公告',
  announcements: '通知',
  discussions: '讨论'
}

function getTableLabel(key) {
  return tableLabels[key] || key
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function fetchStatistics() {
  try {
    const res = await api.get('/backup/statistics')
    statistics.value = res.data.statistics
  } catch (e) {
    console.error('获取统计失败:', e)
  }
}

async function fetchBackups() {
  loading.value = true
  try {
    const res = await api.get('/backup/list')
    backups.value = res.data.backups || []
  } catch (e) {
    console.error('获取备份列表失败:', e)
  } finally {
    loading.value = false
  }
}

async function handleExport() {
  exporting.value = true
  try {
    const tables = selectedTables.value.includes('all') ? 'all' : selectedTables.value
    const res = await api.post('/backup/export', { tables })
    ElMessage.success('备份创建成功')
    await fetchBackups()
  } catch (e) {
    ElMessage.error('备份创建失败')
  } finally {
    exporting.value = false
  }
}

async function handleDownload(filename) {
  try {
    const res = await api.get(`/backup/download/${filename}`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

async function handleDelete(filename) {
  try {
    await ElMessageBox.confirm('确定删除这个备份文件吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/backup/delete/${filename}`)
    ElMessage.success('删除成功')
    await fetchBackups()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handleFileChange(file) {
  restoreFile.value = file.raw
}

async function handleRestore() {
  if (!restoreFile.value) {
    ElMessage.warning('请先选择备份文件')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要恢复数据吗？${restoreMode.value === 'replace' ? '替换模式将删除现有数据！' : ''}`,
      '确认恢复',
      {
        confirmButtonText: '确定恢复',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    restoring.value = true
    const formData = new FormData()
    formData.append('file', restoreFile.value)
    formData.append('mode', restoreMode.value)

    await api.post('/backup/restore', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    ElMessage.success('数据恢复成功')
    await fetchStatistics()
    
    // 清空上传
    restoreFile.value = null
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('恢复失败')
    }
  } finally {
    restoring.value = false
  }
}

onMounted(() => {
  fetchStatistics()
  fetchBackups()
})
</script>

<style scoped>
.backup-management .el-card {
  margin-bottom: 0;
}
</style>
