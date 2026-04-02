/**
 * 图片懒加载指令
 * 使用方式: v-lazy="图片URL"
 */

const LazyImageDirective = {
  mounted(el, binding) {
    // 设置占位背景
    el.style.backgroundColor = '#f0f0f0'
    el.style.transition = 'opacity 0.3s'
    el.style.opacity = '0'
    
    // 创建IntersectionObserver
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = new Image()
          img.src = binding.value
          
          img.onload = () => {
            el.src = binding.value
            el.style.opacity = '1'
            el.style.backgroundColor = 'transparent'
          }
          
          img.onerror = () => {
            // 加载失败时显示默认图片或保持占位
            el.style.opacity = '1'
            el.style.backgroundColor = '#e0e0e0'
          }
          
          observer.unobserve(el)
        }
      })
    }, {
      rootMargin: '100px', // 提前100px开始加载
      threshold: 0.1
    })
    
    observer.observe(el)
    el._lazyObserver = observer
  },
  
  updated(el, binding) {
    if (binding.value !== binding.oldValue) {
      el.style.opacity = '0'
      const observer = el._lazyObserver
      if (observer) {
        observer.observe(el)
      }
    }
  },
  
  unmounted(el) {
    if (el._lazyObserver) {
      el._lazyObserver.disconnect()
      delete el._lazyObserver
    }
  }
}

export default LazyImageDirective
