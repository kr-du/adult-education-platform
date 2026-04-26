import { ElMessage } from 'element-plus'

// 验证用户名格式
export const validateUsername = (username) => {
  if (!username) {
    return '请输入用户名'
  }
  
  if (username.length < 3 || username.length > 50) {
    return '用户名长度应在3-50个字符之间'
  }
  
  const usernameRegex = /^[a-zA-Z0-9_]+$/
  if (!usernameRegex.test(username)) {
    return '用户名只能包含字母、数字和下划线'
  }
  
  return null
}

// 验证密码强度
export const validatePassword = (password) => {
  if (!password) {
    return '请输入密码'
  }
  
  if (password.length < 6) {
    return '密码长度至少为6个字符'
  }
  
  return null
}

// 验证邮箱格式
export const validateEmail = (email) => {
  if (!email) {
    return '请输入邮箱'
  }
  
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (!emailRegex.test(email)) {
    return '请输入有效的邮箱地址'
  }
  
  return null
}

// 统一处理API错误
export const handleApiError = (error) => {
  console.error('API Error:', error)
  
  if (error.response) {
    const status = error.response.status
    const data = error.response.data
    
    if (status === 400) {
      ElMessage.error(data.error || '请求参数错误')
    } else if (status === 401) {
      ElMessage.error('登录已过期，请重新登录')
    } else if (status === 403) {
      ElMessage.error('无权限访问')
    } else if (status === 404) {
      ElMessage.error('资源未找到')
    } else if (status >= 500) {
      ElMessage.error('服务器错误，请稍后重试')
    } else {
      ElMessage.error(data.error || '操作失败')
    }
  } else if (error.request) {
    ElMessage.error('网络连接失败，请检查网络')
  } else {
    ElMessage.error('未知错误')
  }
  
  return null
}

// 清理输入内容
export const sanitizeInput = (input) => {
  if (!input) return ''
  
  // 移除前后空白
  let sanitized = input.trim()
  
  // 移除危险字符
  sanitized = sanitized.replace(/[<>"'%;()&]/g, '')
  
  return sanitized
}

// 验证文件上传
export const validateFileUpload = (file, maxSize = 50 * 1024 * 1024, allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4']) => {
  if (!file) {
    throw new Error('请选择文件')
  }
  
  if (file.size > maxSize) {
    throw new Error(`文件大小不能超过 ${(maxSize / (1024 * 1024)).toFixed(1)}MB`)
  }
  
  if (!allowedTypes.includes(file.type)) {
    throw new Error('不支持的文件类型')
  }
  
  return true
}