# 前端 UI 风格重设计 Spec

## Why
当前首页和导航栏大量使用 `#667eea → #764ba2` 紫色渐变、浮动动画、装饰性圆圈、毛玻璃效果、过多药丸徽章等典型 AI 生成 UI 模式，缺乏真人设计感。需要重构色彩体系与视觉风格，使其简洁大方、现代专业。

## What Changes
- **BREAKING** 全局 CSS 变量色彩体系重定义（main.css :root）
- 导航栏 Navbar 从透明渐变玻璃风格改为实底简明风格
- 首页 Hero 区域移除浮动圆圈动画、SVG 图案背景、渐变文字，改为排版驱动的简洁设计
- 平台特色区去除药丸徽章，卡片设计更克制
- 热门课程区卡片悬挂动画幅度减小
- 数据统计区从全宽紫色渐变条带改为融入区块的轻量设计
- CTA 行动号召区简化设计

## Impact
- Affected specs: 无
- Affected code:
  - `frontend/src/assets/css/main.css` — CSS 变量 + 全局样式
  - `frontend/src/components/common/Navbar.vue` — 导航栏样式
  - `frontend/src/views/Home.vue` — 首页全部区块样式

## MODIFIED Requirements

### Requirement: 全局色彩体系
系统 SHALL 使用克制、专业的色彩变量替代现有紫色渐变体系。

#### Scenario: 色彩变量定义
- **WHEN** 加载全局样式
- **THEN** `:root` 中包含以下新变量：
  - `--color-primary: #1e40af`（深蓝，替代 #409eff）
  - `--color-accent: #2563eb`（亮蓝）
  - `--color-bg: #f8f9fb`（页面底色）
  - `--color-surface: #ffffff`（卡片底色）
  - `--color-text: #111827`（主文字）
  - `--color-text-secondary: #6b7280`（次级文字）
  - `--color-border: #e5e7eb`（边框）
- **AND** 移除 `--primary-color`, `--success-color`, `--warning-color`, `--danger-color`, `--info-color` 变量中不必要的鲜艳值

### Requirement: 导航栏风格
导航栏 SHALL 使用白色实底 + 底部细线边框，不再使用透明渐变玻璃风格。

#### Scenario: 导航栏默认状态
- **WHEN** 页面在顶部未滚动
- **THEN** 导航栏背景为 `#ffffff`
- **AND** 有 `1px solid #e5e7eb` 底部边框
- **AND** 品牌文字颜色为 `#111827`
- **AND** 导航链接颜色为 `#4b5563`
- **AND** 激活链接有左侧细色条或底部色条指示

#### Scenario: 导航栏滚动后
- **WHEN** 页面已向下滚动
- **THEN** 导航栏添加 `box-shadow: 0 1px 3px rgba(0,0,0,0.08)`
- **AND** 其余样式不变

#### Scenario: 移动端菜单
- **WHEN** 屏幕宽度 ≤ 992px 且菜单打开
- **THEN** 侧滑面板背景为 `#ffffff`
- **AND** 菜单项颜色为 `#111827`
- **AND** 不再使用紫色渐变背景

### Requirement: 首页 Hero 区域
Hero 区域 SHALL 使用简洁的排版驱动设计，移除所有装饰性动画元素。

#### Scenario: Hero 区域展示
- **WHEN** 访问首页
- **THEN** Hero 背景为浅灰 `#f8f9fb` 或白色
- **AND** 不包含浮动圆圈动画
- **AND** 不包含 SVG 装饰图案
- **AND** 标题使用纯色 `#111827`，字号约 44-48px，不再使用渐变文字效果
- **AND** 移除"终身学习平台"药丸徽章
- **AND** 统计数字以简洁行内方式展示

### Requirement: 平台特色区
特色卡片 SHALL 使用干净的白底细边框设计，hover 效果克制。

#### Scenario: 特色卡片
- **WHEN** 鼠标悬停在特色卡片上
- **THEN** 卡片上移不超过 4px
- **AND** 阴影为 `0 4px 12px rgba(0,0,0,0.06)`
- **AND** 图标区域使用纯色背景小方块，不再用大圆角

### Requirement: 数据统计区
数据统计 SHALL 融入页面流，不再使用全宽渐变背景条带。

#### Scenario: 统计展示
- **WHEN** 滚动到统计区
- **THEN** 背景为白色或浅灰，不再使用紫色渐变
- **AND** 统计数字颜色为 `#111827`
- **AND** 标签颜色为 `#6b7280`
- **AND** 图标使用 accent 色小图标

### Requirement: CTA 行动号召区
CTA 区 SHALL 使用深色实底 + 亮色按钮的简洁布局。

#### Scenario: CTA 展示
- **WHEN** 滚动到 CTA 区
- **THEN** 背景为 `#111827` 实色（不使用渐变）
- **AND** 主按钮使用 `#2563eb` 或 `#ffffff` 实色

## REMOVED Requirements
### Requirement: 紫色渐变体系
**Reason**: 典型 AI 生成 UI 特征，缺乏设计个性
**Migration**: 全部替换为 `--color-primary` 等新变量

### Requirement: 浮动装饰动画
**Reason**: 纯装饰性元素，增加视觉噪音
**Migration**: 直接删除 hero-circle 和 @keyframes float

### Requirement: 毛玻璃效果 (backdrop-filter: blur)
**Reason**: 当前 AI UI 高频特征
**Migration**: 替换为实色背景 + 细边框

### Requirement: 药丸徽章 (pill badges)
**Reason**: 被 AI 工具过度使用的设计模式
**Migration**: 移除或替换为下划线/色块指示
