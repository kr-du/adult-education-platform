<template>
  <div class="video-player-wrapper" ref="wrapperRef">
    <video
      ref="videoRef"
      class="video-element"
      :src="src"
      :poster="poster"
      @timeupdate="handleTimeUpdate"
      @loadedmetadata="handleLoadedMetadata"
      @play="isPlaying = true"
      @pause="isPlaying = false"
      @ended="handleEnded"
      @waiting="isLoading = true"
      @canplay="isLoading = false"
      @click="togglePlay"
    ></video>

    <!-- 加载动画 -->
    <div v-if="isLoading" class="video-loading">
      <div class="loading-spinner"></div>
    </div>

    <!-- 大播放按钮 -->
    <div v-if="!isPlaying && !isLoading" class="play-overlay" @click="togglePlay">
      <div class="play-button-large">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M8 5v14l11-7z"/>
        </svg>
      </div>
    </div>

    <!-- 控制栏 -->
    <div class="video-controls" :class="{ show: showControls }">
      <!-- 进度条 -->
      <div class="progress-bar-container" @click="seekTo" @mousemove="updateHoverTime" @mouseleave="hoverTime = null">
        <div class="progress-bar">
          <div class="progress-buffered" :style="{ width: bufferedPercent + '%' }"></div>
          <div class="progress-played" :style="{ width: progressPercent + '%' }">
            <div class="progress-thumb"></div>
          </div>
        </div>
        <div v-if="hoverTime !== null" class="progress-tooltip" :style="{ left: hoverPosition + '%' }">
          {{ formatTime(hoverTime) }}
        </div>
      </div>

      <div class="controls-bottom">
        <div class="controls-left">
          <!-- 播放/暂停 -->
          <button class="control-btn" @click="togglePlay" :title="isPlaying ? '暂停' : '播放'">
            <svg v-if="!isPlaying" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
            </svg>
          </button>

          <!-- 快退10秒 -->
          <button class="control-btn" @click="skip(-10)" title="快退10秒">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
              <text x="12" y="14" text-anchor="middle" font-size="6" fill="currentColor">10</text>
            </svg>
          </button>

          <!-- 快进10秒 -->
          <button class="control-btn" @click="skip(10)" title="快进10秒">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 5V1l5 5-5 5V7c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6h2c0 4.42-3.58 8-8 8s-8-3.58-8-8 3.58-8 8-8z"/>
              <text x="12" y="14" text-anchor="middle" font-size="6" fill="currentColor">10</text>
            </svg>
          </button>

          <!-- 音量 -->
          <div class="volume-control">
            <button class="control-btn" @click="toggleMute" :title="isMuted ? '取消静音' : '静音'">
              <svg v-if="isMuted || volume === 0" viewBox="0 0 24 24" fill="currentColor">
                <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
              </svg>
              <svg v-else-if="volume < 0.5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
              </svg>
            </button>
            <input
              type="range"
              class="volume-slider"
              min="0"
              max="1"
              step="0.1"
              :value="volume"
              @input="setVolume"
            />
          </div>

          <!-- 时间显示 -->
          <span class="time-display">
            {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
          </span>
        </div>

        <div class="controls-right">
          <!-- 倍速播放 -->
          <div class="speed-control">
            <button class="control-btn speed-btn" @click="showSpeedMenu = !showSpeedMenu">
              {{ playbackRate }}x
            </button>
            <div v-if="showSpeedMenu" class="speed-menu">
              <button
                v-for="speed in speedOptions"
                :key="speed"
                class="speed-option"
                :class="{ active: playbackRate === speed }"
                @click="setPlaybackRate(speed)"
              >
                {{ speed }}x
              </button>
            </div>
          </div>

          <!-- 画中画 -->
          <button class="control-btn" @click="togglePictureInPicture" title="画中画">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 7h-8v6h8V7zm2-4H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14z"/>
            </svg>
          </button>

          <!-- 全屏 -->
          <button class="control-btn" @click="toggleFullscreen" title="全屏">
            <svg v-if="!isFullscreen" viewBox="0 0 24 24" fill="currentColor">
              <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="currentColor">
              <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  src: { type: String, default: '' },
  poster: { type: String, default: '' },
  autoplay: { type: Boolean, default: false }
})

const emit = defineEmits(['timeupdate', 'ended', 'play', 'pause'])

// Refs
const wrapperRef = ref(null)
const videoRef = ref(null)

// 状态
const isPlaying = ref(false)
const isLoading = ref(false)
const isFullscreen = ref(false)
const isMuted = ref(false)
const showControls = ref(true)
const showSpeedMenu = ref(false)

// 播放数据
const currentTime = ref(0)
const duration = ref(0)
const buffered = ref(0)
const volume = ref(1)
const playbackRate = ref(1)

// 进度条悬停
const hoverTime = ref(null)
const hoverPosition = ref(0)

// 倍速选项
const speedOptions = [0.5, 0.75, 1, 1.25, 1.5, 2]

// 计算属性
const progressPercent = computed(() => {
  if (!duration.value) return 0
  return (currentTime.value / duration.value) * 100
})

const bufferedPercent = computed(() => {
  if (!duration.value) return 0
  return (buffered.value / duration.value) * 100
})

// 方法
function togglePlay() {
  if (!videoRef.value) return
  if (isPlaying.value) {
    videoRef.value.pause()
  } else {
    videoRef.value.play()
  }
}

function skip(seconds) {
  if (!videoRef.value) return
  videoRef.value.currentTime = Math.max(0, Math.min(videoRef.value.currentTime + seconds, duration.value))
}

function toggleMute() {
  if (!videoRef.value) return
  videoRef.value.muted = !videoRef.value.muted
  isMuted.value = videoRef.value.muted
}

function setVolume(e) {
  const val = parseFloat(e.target.value)
  volume.value = val
  if (videoRef.value) {
    videoRef.value.volume = val
    isMuted.value = val === 0
  }
}

function setPlaybackRate(rate) {
  playbackRate.value = rate
  if (videoRef.value) {
    videoRef.value.playbackRate = rate
  }
  showSpeedMenu.value = false
}

function seekTo(e) {
  if (!videoRef.value || !duration.value) return
  const rect = e.currentTarget.getBoundingClientRect()
  const percent = (e.clientX - rect.left) / rect.width
  videoRef.value.currentTime = percent * duration.value
}

function updateHoverTime(e) {
  if (!duration.value) return
  const rect = e.currentTarget.getBoundingClientRect()
  hoverPosition.value = ((e.clientX - rect.left) / rect.width) * 100
  hoverTime.value = ((e.clientX - rect.left) / rect.width) * duration.value
}

async function togglePictureInPicture() {
  if (!videoRef.value) return
  try {
    if (document.pictureInPictureElement) {
      await document.exitPictureInPicture()
    } else {
      await videoRef.value.requestPictureInPicture()
    }
  } catch (err) {
    console.error('画中画错误:', err)
  }
}

async function toggleFullscreen() {
  if (!wrapperRef.value) return
  try {
    if (!document.fullscreenElement) {
      await wrapperRef.value.requestFullscreen()
      isFullscreen.value = true
    } else {
      await document.exitFullscreen()
      isFullscreen.value = false
    }
  } catch (err) {
    console.error('全屏错误:', err)
  }
}

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 事件处理
function handleTimeUpdate() {
  if (!videoRef.value) return
  currentTime.value = videoRef.value.currentTime
  buffered.value = videoRef.value.buffered.length > 0 ? videoRef.value.buffered.end(videoRef.value.buffered.length - 1) : 0
  emit('timeupdate', { currentTime: currentTime.value, duration: duration.value })
}

function handleLoadedMetadata() {
  if (!videoRef.value) return
  duration.value = videoRef.value.duration
  if (props.autoplay) {
    videoRef.value.play()
  }
}

function handleEnded() {
  isPlaying.value = false
  emit('ended')
}

// 快捷键处理
function handleKeydown(e) {
  if (!videoRef.value) return
  
  switch (e.key) {
    case ' ':
    case 'k':
      e.preventDefault()
      togglePlay()
      break
    case 'ArrowLeft':
      e.preventDefault()
      skip(-5)
      break
    case 'ArrowRight':
      e.preventDefault()
      skip(5)
      break
    case 'ArrowUp':
      e.preventDefault()
      volume.value = Math.min(1, volume.value + 0.1)
      videoRef.value.volume = volume.value
      break
    case 'ArrowDown':
      e.preventDefault()
      volume.value = Math.max(0, volume.value - 0.1)
      videoRef.value.volume = volume.value
      break
    case 'm':
      toggleMute()
      break
    case 'f':
      toggleFullscreen()
      break
    case 'j':
      skip(-10)
      break
    case 'l':
      skip(10)
      break
  }
}

// 全屏变化监听
function handleFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement
}

// 鼠标移动显示控制栏
let hideControlsTimer = null
function handleMouseMove() {
  showControls.value = true
  clearTimeout(hideControlsTimer)
  hideControlsTimer = setTimeout(() => {
    if (isPlaying.value) {
      showControls.value = false
    }
  }, 3000)
}

// 点击外部关闭倍速菜单
function handleClickOutside(e) {
  if (!e.target.closest('.speed-control')) {
    showSpeedMenu.value = false
  }
}

// 生命周期
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('click', handleClickOutside)
  
  if (wrapperRef.value) {
    wrapperRef.value.addEventListener('mousemove', handleMouseMove)
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('click', handleClickOutside)
  clearTimeout(hideControlsTimer)
})

// 监听src变化
watch(() => props.src, () => {
  currentTime.value = 0
  duration.value = 0
  isPlaying.value = false
})

// 暴露方法
defineExpose({
  play: () => videoRef.value?.play(),
  pause: () => videoRef.value?.pause(),
  seek: (time) => { if (videoRef.value) videoRef.value.currentTime = time },
  getCurrentTime: () => currentTime.value,
  getDuration: () => duration.value
})
</script>

<style scoped>
.video-player-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  background: #000;
  overflow: hidden;
  user-select: none;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: contain;
  cursor: pointer;
}

/* 加载动画 */
.video-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 大播放按钮 */
.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  cursor: pointer;
  z-index: 5;
}

.play-button-large {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, background 0.2s;
}

.play-button-large svg {
  width: 40px;
  height: 40px;
  margin-left: 4px;
}

.play-button-large:hover {
  transform: scale(1.1);
  background: #fff;
}

/* 控制栏 */
.video-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  padding: 20px 16px 12px;
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 20;
}

.video-controls.show {
  opacity: 1;
}

/* 进度条 */
.progress-bar-container {
  position: relative;
  height: 20px;
  cursor: pointer;
  margin-bottom: 8px;
}

.progress-bar {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  transform: translateY(-50%);
}

.progress-bar-container:hover .progress-bar {
  height: 6px;
}

.progress-buffered {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 2px;
}

.progress-played {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: #409eff;
  border-radius: 2px;
}

.progress-thumb {
  position: absolute;
  right: -6px;
  top: 50%;
  transform: translateY(-50%);
  width: 12px;
  height: 12px;
  background: #409eff;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.2s;
}

.progress-bar-container:hover .progress-thumb {
  opacity: 1;
}

.progress-tooltip {
  position: absolute;
  bottom: 100%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-bottom: 8px;
  white-space: nowrap;
}

/* 底部控制区 */
.controls-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.controls-left,
.controls-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 控制按钮 */
.control-btn {
  background: none;
  border: none;
  color: #fff;
  width: 36px;
  height: 36px;
  padding: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.control-btn svg {
  width: 24px;
  height: 24px;
}

/* 音量控制 */
.volume-control {
  display: flex;
  align-items: center;
  gap: 4px;
}

.volume-slider {
  width: 0;
  opacity: 0;
  transition: width 0.2s, opacity 0.2s;
  cursor: pointer;
}

.volume-control:hover .volume-slider {
  width: 80px;
  opacity: 1;
}

/* 时间显示 */
.time-display {
  color: #fff;
  font-size: 13px;
  margin-left: 8px;
  white-space: nowrap;
}

/* 倍速控制 */
.speed-control {
  position: relative;
}

.speed-btn {
  font-size: 14px;
  font-weight: 500;
  width: auto;
  padding: 6px 12px;
}

.speed-menu {
  position: absolute;
  bottom: 100%;
  right: 0;
  background: rgba(0, 0, 0, 0.9);
  border-radius: 8px;
  padding: 8px 0;
  margin-bottom: 8px;
  min-width: 80px;
}

.speed-option {
  display: block;
  width: 100%;
  padding: 8px 16px;
  background: none;
  border: none;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  text-align: center;
}

.speed-option:hover {
  background: rgba(255, 255, 255, 0.1);
}

.speed-option.active {
  color: #409eff;
}

/* 响应式 */
@media (max-width: 768px) {
  .video-controls {
    padding: 16px 12px 8px;
  }
  
  .control-btn {
    width: 32px;
    height: 32px;
    padding: 4px;
  }
  
  .control-btn svg {
    width: 20px;
    height: 20px;
  }
  
  .time-display {
    font-size: 11px;
  }
  
  .volume-control:hover .volume-slider {
    width: 60px;
  }
  
  .play-button-large {
    width: 60px;
    height: 60px;
  }
  
  .play-button-large svg {
    width: 30px;
    height: 30px;
  }
}
</style>
