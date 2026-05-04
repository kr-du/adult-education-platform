# Checklist

- [x] 后端 SSE 输出每个 chunk 使用 JSON 编码格式
- [x] 后端 SSE 输出 `[DONE]` 信号保持不编码
- [x] 前端 chatStream 解析 JSON 数据帧获取 text 字段
- [x] 前端 chatStream 正确处理 `[DONE]` 信号
- [x] 流式输出期间消息列表仅有一个 AI 气泡（无双气泡）
- [x] AI 气泡在首个 chunk 到达前显示打字动画（三点跳动）
- [x] AI 气泡在首个 chunk 到达后以 raw text 逐字显示
- [x] 流式完成后 AI 气泡切换为 Markdown 渲染
- [x] Markdown 代码块正确触发 highlight.js 高亮
- [x] Enter 键发送消息（不换行）
- [x] Shift+Enter 换行（不发送）
- [x] 用户未手动上滚时自动滚动到底部
- [x] 用户手动上滚后暂停自动滚动，显示"回到底部"按钮
- [x] 点击"回到底部"按钮恢复自动滚动
- [x] 流式失败时 AI 气泡显示错误提示 + 重试按钮
- [x] 空对话列表时显示引导文案
