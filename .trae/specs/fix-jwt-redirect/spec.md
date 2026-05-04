# JWT 过期自动退出但未跳转登录页修复 Spec

## Why
当前系统在 JWT token 过期后，可以触发账号退出（token 被清除），但页面不会跳转到登录页。经过分析，根因有三个方面：

1. **SSE/fetch 请求绕过 axios 拦截器**：AI 助手聊天流使用 `fetch()` 直接发起 SSE 请求，当此请求返回 401 时，不经过 axios 响应拦截器，不会触发 `logout()` + `router.push("/login")`。
2. **无统一认证失败处理中心**：系统缺乏一个集中的机制，确保任何来源（axios 或 fetch）的 401 都能可靠地触发跳转。
3. **路由守卫与 store 状态脱节**：路由守卫从 `localStorage` 直接读取 token，而非引用 Pinia store 的统一状态，状态不一致时可能产生边缘问题。

## What Changes
- 创建统一的认证失效处理函数，供 axios 拦截器和 fetch 调用方共同使用
- 在 `aiApi.chatStream` 的 fetch 错误处理中增加 401 状态码检测，触发退出+跳转
- 添加防抖机制，避免多个并发 401 响应产生重复跳转
- 路由守卫改为从 Pinia store 读取认证状态，保持状态一致性

## Impact
- Affected specs: fix-ai-assistant
- Affected code:
  - `frontend/src/api/index.js` — 新增统一 auth 失效处理 + fetch 401 检测
  - `frontend/src/router/index.js` — 路由守卫改为引用 Pinia store
  - `frontend/src/views/student/AiAssistant.vue` — onError 回调适配

## ADDED Requirements

### Requirement: 统一认证失效处理
系统 SHALL 提供一个集中的 `handleAuthExpired()` 函数，完成退出登录并跳转登录页，且对短时间内多次调用进行防抖处理。

#### Scenario: 单次 401 触发
- **WHEN** 任意 API 请求返回 401
- **THEN** `handleAuthExpired()` 被调用
- **AND** 清除用户 token 和用户信息
- **AND** 页面跳转到 `/login`
- **AND** 显示"登录已过期，请重新登录"提示

#### Scenario: 并发多个 401
- **WHEN** 多个 API 请求在 1 秒内同时返回 401
- **THEN** 仅执行一次退出+跳转操作
- **AND** 不产生重复的页面跳转

### Requirement: fetch 请求 401 检测
使用 `fetch()` 发起的 AI 聊天流请求 SHALL 在收到 401 状态码时触发统一的认证失效处理。

#### Scenario: SSE 流返回 401
- **WHEN** AI 聊天流 `fetch()` 请求收到 HTTP 401 响应
- **THEN** 调用 `handleAuthExpired()` 执行退出+跳转
- **AND** AI 消息气泡不显示错误重试按钮（因为已跳转）

## MODIFIED Requirements

### Requirement: 路由守卫认证检查
路由守卫 SHALL 从 Pinia userStore 读取 token 和角色信息，而非直接从 localStorage 读取。

#### Scenario: 认证状态检查
- **WHEN** 路由导航发生时
- **THEN** 从 `useUserStore()` 获取 `token` 和 `user.role`
- **AND** 行为与之前保持一致（无 token 跳登录、角色不匹配跳首页）
