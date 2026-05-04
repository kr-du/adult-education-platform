# Tasks

- [x] Task 1: 创建统一的认证失效处理函数 + 优化 axios 拦截器
  - 在 `api/index.js` 顶部新增 `handleAuthExpired()` 函数
  - 函数内包含防抖逻辑（1秒内只执行一次）
  - 函数执行 `userStore.logout()` + `router.push("/login")` + `ElMessage.error`
  - 修改 axios 响应拦截器，将 401 处理逻辑替换为调用 `handleAuthExpired()`

- [x] Task 2: fetch 请求增加 401 检测
  - 修改 `api/index.js` 中 `chatStream` 函数
  - 在 `.then(response => ...)` 中，当 `response.status === 401` 时，调用 `handleAuthExpired()` 并 return（不继续读取流）

- [x] Task 3: 路由守卫改为引用 Pinia store
  - 修改 `router/index.js` 的 `beforeEach` 守卫
  - 从 `useUserStore()` 获取 token 和 role，而非直接读 localStorage
  - 保持原有判断逻辑不变

# Task Dependencies
- Task 2 依赖 Task 1（需要 `handleAuthExpired` 函数已存在）
- Task 3 可与其他任务并行（独立文件修改）
