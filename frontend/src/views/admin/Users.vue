<template>
  <div class="admin-users">
    <div class="page-header">
      <div>
        <h1 class="page-title">用户管理</h1>
        <p class="page-subtitle">管理系统中的所有用户账号</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon class="me-1"><Plus /></el-icon>添加用户
      </el-button>
    </div>

    <div class="filter-card">
      <div class="filter-row">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户名/邮箱..."
          :prefix-icon="Search"
          clearable
          class="filter-input"
          @clear="fetchUsers"
          @keyup.enter="fetchUsers"
        />
        <el-select v-model="roleFilter" placeholder="用户角色" clearable class="filter-select" @change="fetchUsers">
          <el-option label="管理员" value="admin" />
          <el-option label="教师" value="teacher" />
          <el-option label="学生" value="student" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="用户状态" clearable class="filter-select" @change="fetchUsers">
          <el-option label="已通过" value="approved" />
          <el-option label="待审核" value="pending" />
          <el-option label="已拒绝" value="rejected" />
        </el-select>
        <el-button type="primary" @click="fetchUsers" :loading="loading">
          <el-icon><Search /></el-icon>
          <span>搜索</span>
        </el-button>
      </div>
    </div>

    <div class="table-card">
      <!-- 桌面端表格视图 -->
      <el-table :data="users" stripe v-loading="loading" class="admin-table d-none d-md-block">
        <el-table-column label="用户名" min-width="150">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="32" class="user-avatar">{{ row.username?.charAt(0)?.toUpperCase() }}</el-avatar>
              <span class="user-name">{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="200" show-overflow-tooltip />
        <el-table-column prop="real_name" label="真实姓名" width="120" show-overflow-tooltip />
        <el-table-column label="角色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)" size="small" effect="light" round>
              {{ getRoleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small" effect="light" round>
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="170" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" plain @click.stop="openEditDialog(row)">编辑</el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              size="small"
              plain
              @click.stop="handleApprove(row)"
            >通过</el-button>
            <el-button type="danger" size="small" plain @click.stop="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 移动端卡片列表视图 -->
      <div class="d-md-none" v-loading="loading">
        <div v-if="users.length === 0" class="text-center py-5">
          <el-empty description="暂无用户数据" />
        </div>
        <div v-else v-for="user in users" :key="user.id" class="mb-3">
          <el-card shadow="hover">
            <div class="d-flex align-items-center mb-2">
              <el-avatar :size="40" class="me-2 user-avatar">
                {{ user.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <div class="min-w-0 flex-grow-1">
                <h6 class="mb-0 text-truncate">{{ user.username }}</h6>
                <small class="text-muted text-truncate d-block">{{ user.email }}</small>
              </div>
            </div>
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div class="d-flex gap-2">
                <el-tag :type="getRoleTagType(user.role)" size="small" effect="light" round>
                  {{ getRoleLabel(user.role) }}
                </el-tag>
                <el-tag :type="getStatusTagType(user.status)" size="small" effect="light" round>
                  {{ getStatusLabel(user.status) }}
                </el-tag>
              </div>
              <small class="text-muted">{{ formatDate(user.created_at) }}</small>
            </div>
            <div class="d-flex gap-2 mt-2">
              <el-button type="primary" size="small" class="flex-grow-1" @click="openEditDialog(user)">编辑</el-button>
              <el-button
                v-if="user.status === 'pending'"
                type="success"
                size="small"
                class="flex-grow-1"
                @click="handleApprove(user)"
              >通过</el-button>
              <el-button type="danger" size="small" class="flex-grow-1" @click="handleDelete(user)">删除</el-button>
            </div>
          </el-card>
        </div>
      </div>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="totalUsers"
          layout="total, sizes, prev, pager, next"
          background
          @current-change="fetchUsers"
          @size-change="fetchUsers"
        />
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="editingUser ? '编辑用户' : '添加用户'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" class="w-100">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status" v-if="editingUser">
          <el-select v-model="form.status" placeholder="请选择状态" class="w-100">
            <el-option label="已通过" value="approved" />
            <el-option label="待审核" value="pending" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item :label="editingUser ? '新密码' : '密码'" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            :placeholder="editingUser ? '留空则不修改' : '请输入密码'"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ editingUser ? '保存修改' : '确认添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'

const loading = ref(true)
const users = ref([])
const totalUsers = ref(0)
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const dialogVisible = ref(false)
const editingUser = ref(null)
const submitting = ref(false)
const formRef = ref(null)

const form = ref({
  username: '',
  email: '',
  real_name: '',
  phone: '',
  role: 'student',
  status: 'approved',
  password: ''
})

const validatePassword = (rule, value, callback) => {
  if (!editingUser.value && !value) {
    callback(new Error('请输入密码'))
  } else if (value && value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'change' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'change' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'change' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'change' }
  ],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'change' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  password: [{ validator: validatePassword, trigger: 'change' }]
}

function getRoleTagType(role) {
  return { admin: 'danger', teacher: 'warning', student: '' }[role] || 'info'
}

function getRoleLabel(role) {
  return { admin: '管理员', teacher: '教师', student: '学生' }[role] || role
}

function getStatusTagType(status) {
  return { approved: 'success', pending: 'warning', rejected: 'danger' }[status] || 'info'
}

function getStatusLabel(status) {
  return { approved: '已通过', pending: '待审核', rejected: '已拒绝' }[status] || status
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

function openCreateDialog() {
  editingUser.value = null
  form.value = { username: '', email: '', real_name: '', phone: '', role: 'student', status: 'approved', password: '' }
  dialogVisible.value = true
}

function openEditDialog(user) {
  editingUser.value = user
  form.value = {
    username: user.username, email: user.email,
    real_name: user.real_name || '', phone: user.phone || '',
    role: user.role, status: user.status, password: ''
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editingUser.value) {
      const data = { ...form.value }
      if (!data.password) delete data.password
      await adminApi.updateUser(editingUser.value.id, data)
      const idx = users.value.findIndex(u => u.id === editingUser.value.id)
      if (idx > -1) {
        users.value[idx] = { ...users.value[idx], ...data }
        if (!data.password) delete users.value[idx].password
      }
      ElMessage.success('更新成功')
    } else {
      const res = await adminApi.createUser(form.value)
      const newUser = res.data.user || { id: Date.now(), ...form.value, created_at: new Date().toISOString() }
      users.value.unshift(newUser)
      totalUsers.value++
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function handleApprove(user) {
  try {
    await ElMessageBox.confirm(`确定通过用户 "${user.username}" 的注册申请吗？`, '确认', {
      confirmButtonText: '确定', cancelButtonText: '取消', type: 'success'
    })
    await adminApi.approveUser(user.id)
    const target = users.value.find(u => u.id === user.id)
    if (target) target.status = 'approved'
    ElMessage.success(`已通过用户 ${user.username}`)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.error || '操作失败')
  }
}

async function handleDelete(user) {
  try {
    await ElMessageBox.confirm(`确定删除用户 "${user.username}" 吗？此操作不可恢复。`, '警告', {
      confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'error'
    })
    await adminApi.deleteUser(user.id)
    users.value = users.value.filter(u => u.id !== user.id)
    totalUsers.value--
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.error || '删除失败')
  }
}

async function fetchUsers() {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchQuery.value) params.keyword = searchQuery.value
    if (roleFilter.value) params.role = roleFilter.value
    if (statusFilter.value) params.status = statusFilter.value
    const res = await adminApi.getUsers(params)
    users.value = res.data.users || res.data || []
    totalUsers.value = res.data.total || users.value.length
  } catch {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.admin-users { min-height: 100%; }

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

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: #fff;
  font-weight: 600;
  flex-shrink: 0;
}

.user-name {
  font-weight: 500;
  color: #1f2937;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f3f4f6;
}

.w-100 { width: 100%; }

@media (max-width: 768px) {
  .admin-users { padding: 12px; }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start !important;
    padding: 16px;
  }
  
  .page-title { font-size: 18px; }
  .page-subtitle { font-size: 13px; }
  
  .filter-card { padding: 12px; }
  .filter-input, .filter-select { width: 100% !important; }
  .filter-row { flex-direction: column; gap: 8px; }
  
  .table-card { padding: 12px; }
  
  .pagination-wrap {
    justify-content: center;
    padding-top: 12px;
    margin-top: 12px;
  }
  
  .el-pagination__total, .el-pagination__jump { display: none; }
  
  .el-dialog { width: 95% !important; margin: 10vh auto !important; }
}
</style>
