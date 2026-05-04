# Checklist

- [x] `handleAuthExpired()` 函数存在于 `api/index.js` 中
- [x] `handleAuthExpired()` 包含 1 秒防抖逻辑
- [x] axios 响应拦截器中 401 处理调用 `handleAuthExpired()`
- [x] `chatStream` 中 fetch 响应 status=401 时调用 `handleAuthExpired()`
- [x] `chatStream` 中 fetch 响应 status=401 时不继续读取流
- [x] 路由守卫从 `useUserStore()` 而非 localStorage 读取状态
- [x] 路由守卫逻辑行为与修改前完全等价
- [x] JWT 过期后任意 API（axios 或 fetch）返回 401 均能跳转登录页
