<template>
  <div class="skeleton-wrapper" :style="{ width, height }">
    <!-- 文本骨架 -->
    <div v-if="type === 'text'" class="skeleton-text" :style="{ width: textWidth }"></div>
    
    <!-- 标题骨架 -->
    <div v-else-if="type === 'title'" class="skeleton-title" :style="{ width: textWidth }"></div>
    
    <!-- 图片骨架 -->
    <div v-else-if="type === 'image'" class="skeleton-image" :style="{ width, height }"></div>
    
    <!-- 头像骨架 -->
    <div v-else-if="type === 'avatar'" class="skeleton-avatar" :style="{ width: size, height: size }"></div>
    
    <!-- 按钮骨架 -->
    <div v-else-if="type === 'button'" class="skeleton-button" :style="{ width, height }"></div>
    
    <!-- 卡片骨架 -->
    <div v-else-if="type === 'card'" class="skeleton-card">
      <div class="skeleton-image" :style="{ height: imageHeight }"></div>
      <div class="skeleton-card-body">
        <div class="skeleton-title" style="width: 80%"></div>
        <div class="skeleton-text" style="width: 60%"></div>
        <div class="skeleton-text" style="width: 40%"></div>
      </div>
    </div>
    
    <!-- 列表项骨架 -->
    <div v-else-if="type === 'list-item'" class="skeleton-list-item">
      <div class="skeleton-avatar" :style="{ width: avatarSize, height: avatarSize }"></div>
      <div class="skeleton-list-content">
        <div class="skeleton-title" style="width: 70%"></div>
        <div class="skeleton-text" style="width: 90%"></div>
      </div>
    </div>
    
    <!-- 表格行骨架 -->
    <div v-else-if="type === 'table-row'" class="skeleton-table-row">
      <div v-for="i in columns" :key="i" class="skeleton-table-cell" :style="{ width: 100 / columns + '%' }">
        <div class="skeleton-text"></div>
      </div>
    </div>
    
    <!-- 自定义骨架 -->
    <div v-else class="skeleton-custom" :class="{ animated }"></div>
  </div>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'text',
    validator: (v) => ['text', 'title', 'image', 'avatar', 'button', 'card', 'list-item', 'table-row', 'custom'].includes(v)
  },
  width: { type: String, default: '100%' },
  height: { type: String, default: '16px' },
  textWidth: { type: String, default: '100%' },
  size: { type: String, default: '40px' },
  avatarSize: { type: String, default: '40px' },
  imageHeight: { type: String, default: '150px' },
  columns: { type: Number, default: 4 },
  animated: { type: Boolean, default: true }
})
</script>

<style scoped>
.skeleton-wrapper {
  display: inline-block;
}

.skeleton-text,
.skeleton-title,
.skeleton-image,
.skeleton-avatar,
.skeleton-button,
.skeleton-custom {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: 4px;
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

.skeleton-text {
  height: 16px;
  margin: 8px 0;
}

.skeleton-title {
  height: 20px;
  margin: 12px 0;
}

.skeleton-image {
  width: 100%;
  border-radius: 8px;
}

.skeleton-avatar {
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-button {
  height: 32px;
  width: 80px;
  border-radius: 4px;
}

.skeleton-card {
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.skeleton-card-body {
  padding: 16px;
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
}

.skeleton-list-content {
  flex: 1;
}

.skeleton-table-row {
  display: flex;
  gap: 16px;
  padding: 12px 0;
}

.skeleton-table-cell {
  flex-shrink: 0;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
