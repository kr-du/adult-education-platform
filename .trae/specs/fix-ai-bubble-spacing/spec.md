# AI 助手消息气泡段落间距优化 Spec

## Why
当前 AI 助手消息气泡中 Markdown 渲染后的文字段落之间上下间距过大（`line-height: 1.6` + `p` 底边距 `6px`），视觉上不够紧凑，影响阅读体验。

## What Changes
- 缩小 `.markdown-body` 的行高（line-height）
- 缩小段落 `<p>` 元素之间的底边距
- 同步调整 `.streaming-text` 流式文本的间距

## Impact
- Affected specs: fix-ai-assistant
- Affected code: `frontend/src/views/student/AiAssistant.vue` (CSS 部分)

## MODIFIED Requirements

### Requirement: 消息气泡段落间距紧凑化
消息气泡内 Markdown 渲染的文字段落 SHALL 使用更紧凑的间距，段落之间的视觉间隔显著缩小。

#### Scenario: 多段 AI 回复
- **WHEN** AI 回复包含多个段落（多个 `<p>` 标签）
- **THEN** 段落之间的上下间距明显小于修改前
- **AND** 段落内文字行间距也适当缩小
