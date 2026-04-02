<template>
  <div class="register-page min-vh-100 d-flex align-items-center bg-light py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="card shadow-lg border-0">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <el-icon :size="48" class="text-primary"><Reading /></el-icon>
                <h3 class="mt-3">用户注册</h3>
                <p class="text-muted">创建账号，开始学习之旅</p>
              </div>

              <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleRegister">
                <el-form-item prop="username">
                  <el-input v-model="form.username" placeholder="请输入用户名" size="large" prefix-icon="User" />
                </el-form-item>

                <el-form-item prop="email">
                  <el-input v-model="form.email" placeholder="请输入邮箱" size="large" prefix-icon="Message" />
                </el-form-item>

                <el-form-item prop="real_name">
                  <el-input v-model="form.real_name" placeholder="请输入真实姓名" size="large" prefix-icon="UserFilled" />
                </el-form-item>

                <el-form-item prop="phone">
                  <el-input v-model="form.phone" placeholder="请输入手机号" size="large" prefix-icon="Phone" />
                </el-form-item>

                <el-form-item prop="role">
                  <el-select v-model="form.role" placeholder="请选择角色" size="large" class="w-100">
                    <el-option label="学生" value="student" />
                    <el-option label="教师" value="teacher" />
                  </el-select>
                </el-form-item>

                <el-form-item prop="password">
                  <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large" prefix-icon="Lock" show-password />
                </el-form-item>

                <el-form-item prop="confirmPassword">
                  <el-input v-model="form.confirmPassword" type="password" placeholder="请确认密码" size="large" prefix-icon="Lock" show-password />
                </el-form-item>

                <el-button type="primary" size="large" class="w-100" :loading="loading" @click="handleRegister">
                  注册
                </el-button>
              </el-form>

              <div class="text-center mt-4">
                <span class="text-muted">已有账号？</span>
                <router-link to="/login" class="text-primary ms-1">立即登录</router-link>
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
import { Reading } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  real_name: '',
  phone: '',
  role: 'student',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
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
  phone: [
    { required: true, message: '请输入手机号', trigger: 'change' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'change' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'change' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'change' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'change' },
    { validator: validateConfirmPassword, trigger: 'change' }
  ]
}

async function handleRegister() {
  await formRef.value.validate()
  loading.value = true

  try {
    const { confirmPassword, ...data } = form
    await authApi.register(data)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>
