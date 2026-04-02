/**
 * 页面缓存工具
 * 用于缓存API响应数据，减少重复请求
 */

class PageCache {
  constructor() {
    this.cache = new Map()
    this.defaultTTL = 5 * 60 * 1000 // 默认5分钟
  }

  /**
   * 生成缓存键
   */
  generateKey(url, params = {}) {
    const sortedParams = Object.keys(params).sort().map(key => `${key}=${params[key]}`).join('&')
    return `${url}?${sortedParams}`
  }

  /**
   * 设置缓存
   */
  set(key, data, ttl = this.defaultTTL) {
    this.cache.set(key, {
      data,
      expire: Date.now() + ttl
    })
  }

  /**
   * 获取缓存
   */
  get(key) {
    const item = this.cache.get(key)
    if (!item) return null
    
    if (Date.now() > item.expire) {
      this.cache.delete(key)
      return null
    }
    
    return item.data
  }

  /**
   * 删除缓存
   */
  delete(key) {
    this.cache.delete(key)
  }

  /**
   * 清除指定URL模式的所有缓存
   */
  clearPattern(pattern) {
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key)
      }
    }
  }

  /**
   * 清除所有缓存
   */
  clear() {
    this.cache.clear()
  }

  /**
   * 清除过期缓存
   */
  clearExpired() {
    const now = Date.now()
    for (const [key, item] of this.cache.entries()) {
      if (now > item.expire) {
        this.cache.delete(key)
      }
    }
  }

  /**
   * 获取缓存大小
   */
  get size() {
    return this.cache.size
  }
}

// 创建单例实例
const pageCache = new PageCache()

// 定期清理过期缓存
setInterval(() => {
  pageCache.clearExpired()
}, 60000) // 每分钟清理一次

export default pageCache

/**
 * API缓存装饰器
 * @param {number} ttl 缓存时间（毫秒）
 */
export function withCache(ttl = 5 * 60 * 1000) {
  return function(target, propertyKey, descriptor) {
    const originalMethod = descriptor.value
    
    descriptor.value = async function(...args) {
      const url = args[0]
      const params = args[1] || {}
      const cacheKey = pageCache.generateKey(url, params)
      
      // 尝试从缓存获取
      const cachedData = pageCache.get(cacheKey)
      if (cachedData) {
        return cachedData
      }
      
      // 调用原始方法
      const result = await originalMethod.apply(this, args)
      
      // 缓存结果
      pageCache.set(cacheKey, result, ttl)
      
      return result
    }
    
    return descriptor
  }
}
