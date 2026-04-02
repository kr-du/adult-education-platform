import { defineStore } from "pinia";
import { ref, computed } from "vue";

/**
 * 用户状态管理store
 * 使用Pinia进行状态管理，包含用户token、用户信息、登录状态等功能
 */
export const useUserStore = defineStore("user", () => {
  // 从localStorage中获取token，如果没有则为空字符串
  const token = ref(localStorage.getItem("token") || "");
  // 从localStorage中获取用户信息，如果没有则为空对象
  const user = ref(JSON.parse(localStorage.getItem("user") || "{}"));

  // 计算属性：判断用户是否已登录
  const isLoggedIn = computed(() => !!token.value);
  // 计算属性：获取用户角色
  const userRole = computed(() => user.value.role || "");

  /**
   * 设置token
   * @param {string} newToken - 要设置的新token
   */
  function setToken(newToken) {
    token.value = newToken;
    localStorage.setItem("token", newToken);
  }

  /**
   * 设置用户信息
   * @param {Object} newUser - 要设置的用户信息对象
   */
  function setUser(newUser) {
    user.value = newUser;
    localStorage.setItem("user", JSON.stringify(newUser));
  }

  /**
   * 用户登出
   * 清除token和用户信息，并从localStorage中移除相关数据
   */
  function logout() {
    token.value = "";
    user.value = {};
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  }

  // 返回store中的状态和方法
  return {
    token,
    user,
    isLoggedIn,
    userRole,
    setToken,
    setUser,
    logout,
  };
});
