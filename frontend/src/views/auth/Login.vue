<template>
  <div class="login-page min-vh-100 d-flex align-items-center bg-light">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow-lg border-0">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <el-icon :size="48" class="text-primary"><Reading /></el-icon>
                <h3 class="mt-3">用户登录</h3>
                <p class="text-muted">欢迎回来，请登录您的账号</p>
              </div>

              <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
                <el-form-item prop="username">
                  <el-input v-model="form.username" placeholder="请输入用户名" size="large" prefix-icon="User" />
                </el-form-item>

                <el-form-item prop="password">
                  <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large" prefix-icon="Lock" show-password />
                </el-form-item>

                <el-form-item>
                  <div class="d-flex justify-content-between w-100">
                    <el-checkbox v-model="rememberMe">记住我</el-checkbox>
                    <router-link to="/reset-password" class="text-primary">忘记密码？</router-link>
                  </div>
                </el-form-item>

                <el-button type="primary" size="large" class="w-100" :loading="loading" @click="handleLogin">
                  登录
                </el-button>
              </el-form>

              <div class="text-center mt-4">
                <span class="text-muted">还没有账号？</span>
                <router-link to="/register" class="text-primary ms-1">立即注册</router-link>
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
import { useUserStore } from '@/store/user'
import { authApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Reading } from '@element-plus/icons-vue'
import { validateUsername, validatePassword, handleApiError } from '@/utils/security'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const rememberMe = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'change' },
    { validator: (rule, value, callback) => {
      const error = validateUsername(value)
      callback(error)
    }, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'change' },
    { validator: (rule, value, callback) => {
      const error = validatePassword(value)
      callback(error)
    }, trigger: 'blur' }
  ]
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true

  try {
    const res = await authApi.login(form)
    userStore.setToken(res.data.access_token)
    userStore.setUser(res.data.user)
    ElMessage.success('登录成功')

    const role = res.data.user.role
    if (role === 'admin') router.push('/admin/dashboard')
    else if (role === 'teacher') router.push('/teacher/dashboard')
    else router.push('/student/dashboard')
  } catch (e) {
    handleApiError(e)
  } finally {
    loading.value = false
  }
}
</script>