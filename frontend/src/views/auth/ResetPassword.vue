<template>
  <div class="reset-page min-vh-100 d-flex align-items-center bg-light">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow-lg border-0">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <el-icon :size="48" class="text-primary"><Lock /></el-icon>
                <h3 class="mt-3">重置密码</h3>
                <p class="text-muted">输入您的邮箱和新密码</p>
              </div>

              <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleReset">
                <el-form-item prop="email">
                  <el-input v-model="form.email" placeholder="请输入注册邮箱" size="large" prefix-icon="Message" />
                </el-form-item>

                <el-form-item prop="new_password">
                  <el-input v-model="form.new_password" type="password" placeholder="请输入新密码" size="large" prefix-icon="Lock" show-password />
                </el-form-item>

                <el-form-item prop="confirm_password">
                  <el-input v-model="form.confirm_password" type="password" placeholder="请确认新密码" size="large" prefix-icon="Lock" show-password />
                </el-form-item>

                <el-button type="primary" size="large" class="w-100" :loading="loading" @click="handleReset">
                  重置密码
                </el-button>
              </el-form>

              <div class="text-center mt-4">
                <router-link to="/login" class="text-primary">返回登录</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Lock } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  email: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirm = (rule, value, callback) => {
  if (value !== form.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'change' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'change' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'change' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'change' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'change' },
    { validator: validateConfirm, trigger: 'change' }
  ]
}

async function handleReset() {
  await formRef.value.validate()
  loading.value = true

  try {
    await authApi.resetPassword({ email: form.email, new_password: form.new_password })
    ElMessage.success('密码重置成功，请登录')
    router.push('/login')
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '重置失败')
  } finally {
    loading.value = false
  }
}
</script>
