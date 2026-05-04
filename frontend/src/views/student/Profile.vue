<template>
  <div class="profile-page">
    <div class="container">
      <h2 class="page-title mb-4">个人中心</h2>

      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar-section">
            <el-upload
              class="avatar-uploader"
              :action="uploadUrl"
              :headers="uploadHeaders"
              :show-file-list="false"
              :on-success="handleAvatarUpload"
              :before-upload="beforeAvatarUpload"
              :disabled="uploading"
            >
              <img v-if="user.avatar" :src="getAvatarUrl(user.avatar)" class="avatar-img" />
              <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            </el-upload>
            <div class="user-basic-info">
              <h3>{{ user.real_name || user.username }}</h3>
              <p>
                <el-tag :type="user.role === 'admin' ? 'danger' : user.role === 'teacher' ? 'warning' : 'primary'" size="small">
                  {{ roleMap[user.role] || user.role }}
                </el-tag>
                <el-tag :type="user.status === 'active' ? 'success' : 'danger'" size="small" class="ms-2">
                  {{ statusMap[user.status] || user.status }}
                </el-tag>
              </p>
              <p class="text-muted small">注册时间: {{ formatDate(user.created_at) }}</p>
            </div>
          </div>
        </div>

        <div class="profile-body mt-4">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="编辑资料" name="profile">
              <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" class="profile-form">
                <el-form-item label="姓名" prop="real_name">
                  <el-input v-model="form.real_name" placeholder="请输入姓名" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="form.email" placeholder="请输入邮箱" />
                </el-form-item>
                <el-form-item label="手机" prop="phone">
                  <el-input v-model="form.phone" placeholder="请输入手机号" />
                </el-form-item>
                <el-form-item label="简介" prop="bio">
                  <el-input v-model="form.bio" type="textarea" :rows="3" placeholder="请输入个人简介" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSave(formRef)">保存修改</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="修改密码" name="password">
              <el-form :model="pwdForm" :rules="pwdRules" ref="pwdFormRef" label-width="100px" class="profile-form">
                <el-form-item label="当前密码" prop="old_password">
                  <el-input v-model="pwdForm.old_password" type="password" placeholder="请输入当前密码" show-password />
                </el-form-item>
                <el-form-item label="新密码" prop="new_password">
                  <el-input v-model="pwdForm.new_password" type="password" placeholder="请输入新密码" show-password />
                </el-form-item>
                <el-form-item label="确认密码" prop="confirm_password">
                  <el-input v-model="pwdForm.confirm_password" type="password" placeholder="请确认新密码" show-password />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleChangePassword(pwdFormRef)">修改密码</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { useUserProfile } from '@/composables/useUserProfile'

const {
  user,
  form,
  pwdForm,
  rules,
  pwdRules,
  statusMap,
  getAvatarUrl,
  formatDate,
  handleAvatarUpload,
  handleSave,
  handleChangePassword
} = useUserProfile()

const activeTab = ref('profile')
const uploading = ref(false)

const formRef = ref(null)
const pwdFormRef = ref(null)

const uploadUrl = computed(() => import.meta.env.VITE_API_BASE_URL + '/api/upload/avatar')
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

const roleMap = {
  student: '学员',
  teacher: '教师',
  admin: '管理员'
}

function beforeAvatarUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过2MB')
    return false
  }

  uploading.value = true
  setTimeout(() => {
    uploading.value = false
  }, 3000)

  return true
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.profile-card {
  background: #fff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.profile-header {
  display: flex;
  align-items: center;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-uploader .avatar-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #e6e8eb;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #dcdfe6;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
}

.avatar-uploader-icon:hover {
  border-color: #409eff;
  color: #409eff;
}

.user-basic-info h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
}

.profile-form {
  max-width: 500px;
  margin-top: 20px;
}
</style>
