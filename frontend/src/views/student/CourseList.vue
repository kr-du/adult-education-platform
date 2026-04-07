<template>
  <div class="course-list py-4">
    <div class="container">
      <div class="row mb-4">
        <div class="col-12">
          <h2 class="fw-bold mb-3">课程浏览</h2>
          <div class="row g-3">
            <div class="col-12">
              <el-input
                v-model="searchQuery"
                placeholder="搜索课程名称或讲师..."
                :prefix-icon="Search"
                clearable
                size="large"
                @clear="handleSearch"
                @keyup.enter="handleSearch"
              />
            </div>
            <div class="col-6">
              <el-select
                v-model="selectedCategory"
                placeholder="选择分类"
                clearable
                size="large"
                class="w-100"
                @change="handleCategoryChange"
              >
                <el-option
                  v-for="cat in categories"
                  :key="cat.id"
                  :label="cat.name"
                  :value="cat.id"
                />
              </el-select>
            </div>
            <div class="col-6">
              <el-select
                v-model="sortBy"
                placeholder="排序方式"
                size="large"
                class="w-100"
                @change="handleSortChange"
              >
                <el-option label="最新发布" value="created_at" />
                <el-option label="最多学习" value="student_count" />
                <el-option label="价格最低" value="price_asc" />
                <el-option label="价格最高" value="price_desc" />
              </el-select>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-3">
        <div class="col-12 d-flex justify-content-between align-items-center">
          <span class="text-muted">共找到 {{ totalCourses }} 门课程</span>
          <el-radio-group v-model="viewMode" size="small">
            <el-radio-button value="grid">
              <el-icon><Grid /></el-icon>
            </el-radio-button>
            <el-radio-button value="list">
              <el-icon><List /></el-icon>
            </el-radio-button>
          </el-radio-group>
        </div>
      </div>

      <el-skeleton :loading="loading" animated :count="8">
        <template #template>
          <div class="row g-4">
            <div v-for="i in 8" :key="i" class="col-lg-3 col-md-4 col-sm-6">
              <el-skeleton-item variant="image" style="height: 150px; border-radius: 8px;" />
              <div class="mt-2">
                <el-skeleton-item variant="h3" style="width: 80%;" />
                <el-skeleton-item variant="text" style="width: 60%;" />
              </div>
            </div>
          </div>
        </template>

        <template #default>
          <div v-if="viewMode === 'grid'" class="row g-4">
            <div v-for="course in courses" :key="course.id" class="col-lg-3 col-md-4 col-sm-6">
              <el-card shadow="hover" class="h-100 course-card" :body-style="{ padding: '0' }">
                <div class="course-cover position-relative" style="height: 150px;">
                  <img v-if="course.cover_image" :src="course.cover_image" class="w-100 h-100" style="object-fit: cover;" />
                  <div v-else class="bg-gradient d-flex align-items-center justify-content-center w-100 h-100">
                    <el-icon :size="48" class="text-white-50"><VideoPlay /></el-icon>
                  </div>
                </div>
                <div class="p-3">
                  <div class="d-flex mb-2">
                    <el-tag v-if="course.category_name" size="small" type="info">{{ course.category_name }}</el-tag>
                  </div>
                  <h6 class="fw-bold mb-2 text-truncate" :title="course.title">{{ course.title }}</h6>
                  <p class="text-muted small mb-2 d-flex align-items-center">
                    <el-icon class="me-1"><User /></el-icon>
                    {{ course.teacher_name || '未知讲师' }}
                  </p>
                  <div class="d-flex justify-content-between align-items-center">
                    <span class="text-primary fw-bold fs-5">¥{{ course.price || 0 }}</span>
                    <span class="text-muted small">
                      <el-icon class="me-1"><User /></el-icon>
                      {{ course.student_count || 0 }}人学习
                    </span>
                  </div>
                </div>
                <div class="px-3 pb-3">
                  <router-link :to="`/course/${course.id}`" class="btn btn-outline-primary btn-sm w-100">
                    查看详情
                  </router-link>
                </div>
              </el-card>
            </div>
          </div>

          <div v-else class="row g-3">
            <div v-for="course in courses" :key="course.id" class="col-12">
              <el-card shadow="hover" class="course-card-list">
                <div class="row align-items-center">
                  <div class="col-md-2 col-4">
                    <div class="rounded overflow-hidden position-relative" style="height: 100px;">
                      <img v-if="course.cover_image" :src="course.cover_image" class="w-100 h-100" style="object-fit: cover;" />
                      <div v-else class="bg-gradient d-flex align-items-center justify-content-center w-100 h-100">
                        <el-icon :size="36" class="text-white-50"><VideoPlay /></el-icon>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-7 col-8">
                    <div class="d-flex mb-1">
                      <el-tag v-if="course.category_name" size="small" type="info" class="me-2">{{ course.category_name }}</el-tag>
                    </div>
                    <h6 class="fw-bold mb-1">{{ course.title }}</h6>
                    <p class="text-muted small mb-1">{{ course.description?.substring(0, 80) }}{{ course.description?.length > 80 ? '...' : '' }}</p>
                    <span class="text-muted small">
                      <el-icon class="me-1"><User /></el-icon>{{ course.teacher_name }}
                      <span class="mx-2">|</span>
                      <el-icon class="me-1"><Clock /></el-icon>{{ course.lesson_count || 0 }}课时
                    </span>
                  </div>
                  <div class="col-md-3 text-md-end mt-2 mt-md-0">
                    <span class="text-primary fw-bold fs-5 d-block">¥{{ course.price || 0 }}</span>
                    <span class="text-muted small d-block mb-2">{{ course.student_count || 0 }}人学习</span>
                    <router-link :to="`/course/${course.id}`" class="btn btn-outline-primary btn-sm">查看详情</router-link>
                  </div>
                </div>
              </el-card>
            </div>
          </div>

          <div v-if="!loading && courses.length === 0" class="text-center py-5">
            <el-empty description="暂无课程数据" />
          </div>

          <div class="d-flex justify-content-center mt-4" v-if="totalCourses > 0">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[12, 24, 48]"
              :total="totalCourses"
              layout="total, sizes, prev, pager, next, jumper"
              background
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
            />
          </div>
        </template>
      </el-skeleton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { courseApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Search, VideoPlay, User, Clock, Grid, List } from '@element-plus/icons-vue'

const courses = ref([])
const categories = ref([])
const loading = ref(true)
const searchQuery = ref('')
const selectedCategory = ref('')
const sortBy = ref('created_at')
const currentPage = ref(1)
const pageSize = ref(12)
const totalCourses = ref(0)
const viewMode = ref('grid')

async function fetchCourses() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      keyword: searchQuery.value || undefined,
      category_id: selectedCategory.value || undefined,
      sort: sortBy.value,
      status: 'published'
    }
    const res = await courseApi.getCourses(params)
    courses.value = res.data.courses || []
    totalCourses.value = res.data.total || res.data.courses?.length || 0
  } catch (e) {
    ElMessage.error('获取课程列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    const res = await courseApi.getCategories()
    categories.value = res.data.categories || res.data || []
  } catch (e) {
    console.error('获取分类失败')
  }
}

function handleSearch() {
  currentPage.value = 1
  fetchCourses()
}

function handleCategoryChange() {
  currentPage.value = 1
  fetchCourses()
}

function handleSortChange() {
  currentPage.value = 1
  fetchCourses()
}

function handlePageChange(page) {
  currentPage.value = page
  fetchCourses()
}

function handleSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1
  fetchCourses()
}

onMounted(() => {
  fetchCategories()
  fetchCourses()
})
</script>

<style scoped>
.course-cover {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

.course-card {
  transition: transform 0.3s, box-shadow 0.3s;
}

.course-card:hover {
  transform: translateY(-4px);
}

.bg-gradient {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

/* 响应式 */
@media (max-width: 992px) {
  .course-card:hover {
    transform: none;
  }
}

@media (max-width: 768px) {
  .course-list {
    padding: 10px 0;
  }
  
  .course-card {
    margin-bottom: 12px;
  }
  
  .course-cover {
    height: 120px !important;
  }
  
  .card-body {
    padding: 12px !important;
  }
  
  .card-title {
    font-size: 14px;
  }
}

@media (max-width: 576px) {
  .course-cover {
    height: 100px !important;
  }
  
  .el-pagination {
    font-size: 12px;
  }
}
</style>
