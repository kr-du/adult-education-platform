# Tasks

- [x] Task 1: 重写 main.css 全局色彩变量
  - 替换 `:root` 中所有 CSS 变量为新色彩体系
  - 更新 body 背景色
  - 移除不必要的鲜艳颜色变量
  - 保留响应式断点和工具类不变

- [x] Task 2: 重写 Navbar.vue 导航栏样式
  - 将导航栏默认背景改为白色实底 + 底部边框
  - 移除滚动前后的透明/渐变/毛玻璃相关样式
  - 调整品牌图标背景为纯色 accent
  - 调整导航链接、按钮、用户触发器的颜色
  - 移动端菜单面板改为白底
  - 移除 `.top-not-home` 相关多余条件样式

- [x] Task 3: 重写 Home.vue Hero 区域
  - 移除 `.hero-bg` SVG 图案背景
  - 移除 `.hero-circle` 浮动圆圈及 `@keyframes float`
  - 将 Hero 背景改为浅灰实色
  - 简化标题样式（纯色、缩小字号）
  - 移除 `.hero-badge` 药丸徽章
  - 调整按钮为实色风格
  - 保留右侧视觉区但简化设计

- [x] Task 4: 重写 Home.vue 平台特色区
  - 移除 `.section-badge` 药丸徽章
  - 调整卡片 hover 上移幅度（8px → 4px）
  - 降低卡片阴影强度
  - 缩小图标区域圆角

- [x] Task 5: 重写 Home.vue 热门课程区
  - 调整卡片 hover 上移幅度
  - 课程封面默认背景改用纯色而非渐变
  - 移除或简化 `.course-tag` 设计

- [x] Task 6: 重写 Home.vue 数据统计区
  - 移除全宽紫色渐变背景，改为白色/浅灰
  - 统计数字改为深色文字
  - 图标使用 accent 色

- [x] Task 7: 重写 Home.vue CTA 行动号召区
  - 将渐变背景替换为 `#111827` 实色
  - 简化按钮设计

# Task Dependencies
- Task 2, 3, 4, 5, 6, 7 均依赖 Task 1（共享色彩变量）
- Task 3, 4, 5, 6, 7 之间无依赖，可并行执行
