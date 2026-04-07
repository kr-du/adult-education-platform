<template>
  <div id="app">
    <Navbar v-if="showNavbar" />
    <div class="page-content" :class="{ 'has-navbar': showNavbar }">
      <router-view />
    </div>
    <Footer v-if="showFooter" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '@/components/common/Navbar.vue'
import Footer from '@/components/common/Footer.vue'

const route = useRoute()

const isAdminRoute = computed(() => {
  return route.path.startsWith('/admin')
})

const showNavbar = computed(() => {
  if (isAdminRoute.value) return false
  return !['Login', 'Register', 'ResetPassword', 'CourseLearn'].includes(route.name)
})

const showFooter = computed(() => {
  if (isAdminRoute.value) return false
  return !['Login', 'Register', 'ResetPassword', 'CourseLearn'].includes(route.name)
})
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.page-content.has-navbar {
  padding-top: 72px;
}

@media (max-width: 992px) {
  .page-content.has-navbar {
    padding-top: 76px;
  }
}

@media (max-width: 768px) {
  .page-content.has-navbar {
    padding-top: 76px;
  }
}

@media (max-width: 576px) {
  .page-content.has-navbar {
    padding-top: 72px;
  }
}
</style>
