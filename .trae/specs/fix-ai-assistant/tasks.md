# Tasks

- [x] Task 1: 后端 SSE 数据帧 JSON 编码
  - 修改 `ai.py` `chat_stream` 的 `generate()` 函数
  - 每个 chunk 用 `json.dumps({"text": chunk})` 包装
  - 输出格式改为 `data: {json_string}\n\n`

- [x] Task 2: 前端 SSE 解析适配 JSON 编码
  - 修改 `api/index.js` `chatStream` 的 `read()` 解析逻辑
  - 解析 JSON 获取 `text` 字段
  - 保持 `[DONE]` 信号的兼容处理

- [x] Task 3: 修复双气泡问题 + 实现流式 raw text 显示
  - 修改 `AiAssistant.vue` `sendMessage` 函数：
    - 不再同时设置 `waitingResponse = true` 并 push 空消息
    - 改为 push 一个带 `streaming: true` 标记的 AI 消息，初始内容为空
    - 该消息在首个 chunk 到达前显示 typing 动画（三点），到达后显示 raw text
  - 模板中为 `streaming` 消息渲染 raw text（`<pre>` 或 `white-space: pre-wrap` 的 div）
  - 模板中为非 streaming 消息渲染 Markdown

- [x] Task 4: 流式完成后切换 Markdown 渲染
  - 在 `onDone` 回调中将消息的 `streaming` 标记设为 `false`
  - Markdown 渲染触发后执行 `highlightCodeBlocks()`

- [x] Task 5: 输入交互优化（Enter 发送 / Shift+Enter 换行）
  - 移除 `@keyup.enter.exact`，改用 `@keydown.enter.exact.prevent` 发送
  - 添加 `@keydown.enter.shift.exact` 允许换行

- [x] Task 6: 智能自动滚动
  - 检测用户是否手动上滚（通过 `scroll` 事件和"接近底部"阈值判断）
  - 用户上滚时暂缓自动滚动，显示"回到底部"浮动按钮
  - 用户滚回底部或点击按钮时恢复自动滚动

- [x] Task 7: 完善错误处理与边界状态
  - 流式失败时，将对应 AI 消息替换为错误提示气泡（红色文字+重试按钮）
  - 空对话列表时显示引导文案

# Task Dependencies
- Task 2 依赖 Task 1（前端需适配后端的 JSON 编码格式）
- Task 4 依赖 Task 3（流式标记由 Task 3 引入）
- Task 3, 6, 7 可部分并行（同文件但修改不同函数）
