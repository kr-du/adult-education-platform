# AI 助手模块修复与优化 Spec

## Why
当前 AI 助手存在两个主要 Bug：流式输出时同时出现打字动画气泡和空 AI 消息气泡（双气泡问题）；流式内容以 Markdown 整体块形式呈现而非流畅的逐字流式效果。此外 SSE 协议解析未正确转义换行符，存在数据截断风险。整体交互和边界处理也有优化空间。

## What Changes
- 修复流式输出期间同时出现打字动画 + 空消息气泡的双气泡 Bug
- 流式输出过程中使用 raw text 逐字追加显示，完成后切换为 Markdown 渲染
- 后端 SSE 输出对 chunk 进行 JSON 编码，防止换行符破坏协议解析
- 前端 SSE 解析适配 JSON 编码的数据帧
- 优化输入交互：Enter 发送、Shift+Enter 换行
- 优化消息列表自动滚动策略
- 完善错误处理与空状态提示

## Impact
- Affected specs: redesign-ui
- Affected code:
  - `backend/app/routes/ai.py` — SSE chunk 编码
  - `frontend/src/api/index.js` — SSE 解析适配
  - `frontend/src/views/student/AiAssistant.vue` — 模板 + 逻辑 + 样式

## MODIFIED Requirements

### Requirement: 流式输出期间单一 AI 气泡
AI 回复流式输出过程中，系统 SHALL 只在消息列表中显示一个 AI 气泡，不再同时显示打字动画气泡和空内容气泡。

#### Scenario: 正常流式回复
- **WHEN** 用户发送消息后等待 AI 回复
- **THEN** 消息列表中仅追加一个 AI 消息气泡
- **AND** 该气泡在首个 chunk 到达前显示打字动画（三点跳动）
- **AND** 首个 chunk 到达后打字动画消失，开始逐字追加文本
- **AND** 不再出现第二个空内容 AI 气泡

### Requirement: 流式文本逐字显示
流式输出期间，AI 回复 SHALL 以 raw text（`white-space: pre-wrap`）逐字追加显示；流式完成后切换为 Markdown 渲染。

#### Scenario: 流式过程中
- **WHEN** SSE 持续推送 chunk
- **THEN** AI 消息气泡内容以纯文本模式逐字增长
- **AND** 不使用 `marked.parse()` 重复渲染

#### Scenario: 流式完成
- **WHEN** 收到 `[DONE]` 或流结束信号
- **THEN** 消息标记 `streaming = false`
- **AND** 内容切换为 Markdown 渲染（`v-html` 模式）
- **AND** 代码块触发 highlight.js 高亮

### Requirement: SSE 数据帧 JSON 编码
后端 SSE 输出 SHALL 将每个 chunk 包装为 JSON 字符串，防止内容中的换行符破坏 SSE 行解析协议。

#### Scenario: chunk 含换行符
- **WHEN** AI 返回的 chunk 包含 `\n` 字符
- **THEN** 后端以 `data: {"text":"chunk content with \n"}\n\n` 格式输出
- **AND** 前端解析 JSON 后取出 `text` 字段追加显示

### Requirement: 输入交互优化
输入框 SHALL 支持 Enter 发送、Shift+Enter 换行。

#### Scenario: Enter 发送
- **WHEN** 用户在输入框按 Enter（未按 Shift）
- **THEN** 发送消息
- **AND** 不插入换行符

#### Scenario: Shift+Enter 换行
- **WHEN** 用户在输入框按 Shift+Enter
- **THEN** 插入换行符
- **AND** 不发送消息

### Requirement: 智能自动滚动
消息区 SHALL 在以下情况下自动滚动到底部：用户发送新消息、AI 流式输出过程中（用户未手动上滚时）。用户主动上滚后暂停自动滚动，用户滚回底部后恢复。

#### Scenario: 用户未手动滚动
- **WHEN** AI 流式推送新内容且用户未手动向上滚动
- **THEN** 消息区自动滚动到底部

#### Scenario: 用户手动上滚查看历史
- **WHEN** 用户向上滚动查看历史消息
- **THEN** 暂停自动滚动
- **AND** 显示"滚动到底部"浮动按钮

### Requirement: 完善错误与边界处理
系统 SHALL 在网络错误时在消息列表中显示红色错误提示气泡，而非仅弹 toast。

#### Scenario: 网络错误
- **WHEN** SSE 连接失败或中断
- **THEN** 对应的 AI 消息气泡显示"抱歉，回复失败，请重试"红色文字
- **AND** 消息旁显示重试按钮
- **AND** 同时弹出 ElMessage 提示

#### Scenario: 空对话列表
- **WHEN** 用户没有任何历史对话
- **THEN** 显示引导性插图和"开启你的第一次对话"文案
- **AND** 自动聚焦输入框
