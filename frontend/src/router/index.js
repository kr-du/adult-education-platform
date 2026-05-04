import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/store/user";

const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("@/views/Home.vue"),
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/auth/Login.vue"),
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("@/views/auth/Register.vue"),
  },
  {
    path: "/reset-password",
    name: "ResetPassword",
    component: () => import("@/views/auth/ResetPassword.vue"),
  },
  {
    path: "/courses",
    name: "CourseList",
    component: () => import("@/views/student/CourseList.vue"),
  },
  {
    path: "/course/:id",
    name: "CourseDetail",
    component: () => import("@/views/student/CourseDetail.vue"),
  },
  {
    path: "/learn/:id",
    name: "CourseLearn",
    component: () => import("@/views/student/CourseLearn.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/student",
    meta: { requiresAuth: true, role: "student" },
    children: [
      {
        path: "dashboard",
        name: "StudentDashboard",
        component: () => import("@/views/student/Dashboard.vue"),
      },
      {
        path: "my-courses",
        name: "MyCourses",
        component: () => import("@/views/student/MyCourses.vue"),
      },
      {
        path: "assignments",
        name: "StudentAssignments",
        component: () => import("@/views/student/Assignments.vue"),
      },
      {
        path: "grades",
        name: "StudentGrades",
        component: () => import("@/views/student/Grades.vue"),
      },
      {
        path: "profile",
        name: "StudentProfile",
        component: () => import("@/views/student/Profile.vue"),
      },
      {
        path: "messages",
        name: "StudentMessages",
        component: () => import("@/views/student/Messages.vue"),
      },
      {
        path: "reviews",
        name: "StudentReviews",
        component: () => import("@/views/student/Reviews.vue"),
      },
      {
        path: "ai-assistant",
        name: "AiAssistant",
        component: () => import("@/views/student/AiAssistant.vue"),
      },
      {
        path: "questions",
        name: "StudentQuestions",
        component: () => import("@/views/student/Questions.vue"),
      },
      {
        path: "course/:id/questions",
        name: "StudentCourseQuestions",
        component: () => import("@/views/student/Questions.vue"),
      },
    ],
  },
  {
    path: "/teacher",
    meta: { requiresAuth: true, role: "teacher" },
    children: [
      {
        path: "dashboard",
        name: "TeacherDashboard",
        component: () => import("@/views/teacher/Dashboard.vue"),
      },
      {
        path: "courses",
        name: "TeacherCourses",
        component: () => import("@/views/teacher/Courses.vue"),
      },
      {
        path: "course/:id/edit",
        name: "CourseEdit",
        component: () => import("@/views/teacher/CourseEdit.vue"),
      },
      {
        path: "assignments",
        name: "TeacherAssignments",
        component: () => import("@/views/teacher/Assignments.vue"),
      },
      {
        path: "students",
        name: "TeacherStudents",
        component: () => import("@/views/teacher/Students.vue"),
      },
      {
        path: "discussions",
        name: "TeacherDiscussions",
        component: () => import("@/views/teacher/Discussions.vue"),
      },
      {
        path: "course/:id/students",
        name: "CourseStudents",
        component: () => import("@/views/teacher/CourseStudents.vue"),
      },
      {
        path: "course/:id/questions",
        name: "CourseQuestions",
        component: () => import("@/views/teacher/CourseQuestions.vue"),
      },
      {
        path: "course/:id/notices",
        name: "CourseNotices",
        component: () => import("@/views/teacher/CourseNotices.vue"),
      },
      {
        path: "review-moderation",
        name: "TeacherReviewModeration",
        component: () => import("@/views/teacher/ReviewModeration.vue"),
      },
      {
        path: "profile",
        name: "TeacherProfile",
        component: () => import("@/views/teacher/Profile.vue"),
      },
    ],
  },
  {
    path: "/admin",
    component: () => import("@/components/admin/AdminLayout.vue"),
    meta: { requiresAuth: true, role: "admin" },
    redirect: "/admin/dashboard",
    children: [
      {
        path: "dashboard",
        name: "AdminDashboard",
        component: () => import("@/views/admin/Dashboard.vue"),
        meta: { title: "控制台" },
      },
      {
        path: "users",
        name: "AdminUsers",
        component: () => import("@/views/admin/Users.vue"),
        meta: { title: "用户管理" },
      },
      {
        path: "courses",
        name: "AdminCourses",
        component: () => import("@/views/admin/Courses.vue"),
        meta: { title: "课程管理" },
      },
      {
        path: "categories",
        name: "AdminCategories",
        component: () => import("@/views/admin/Categories.vue"),
        meta: { title: "分类管理" },
      },
      {
        path: "announcements",
        name: "AdminAnnouncements",
        component: () => import("@/views/admin/Announcements.vue"),
        meta: { title: "公告管理" },
      },
      {
        path: "review-moderation",
        name: "AdminReviewModeration",
        component: () => import("@/views/admin/ReviewModeration.vue"),
        meta: { title: "内容审核" },
      },
      {
        path: "statistics",
        name: "AdminStatistics",
        component: () => import("@/views/admin/Statistics.vue"),
        meta: { title: "统计报表" },
      },
      {
        path: "backup",
        name: "AdminBackup",
        component: () => import("@/views/admin/BackupManagement.vue"),
        meta: { title: "数据备份" },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  const token = userStore.token;
  const userRole = userStore.user.role;

  if (to.meta.requiresAuth && !token) {
    console.warn("需要登录才能访问:", to.path);
    next("/login");
  } else if (to.meta.role && userRole !== to.meta.role) {
    console.warn("用户角色不匹配，需要:", to.meta.role, "当前:", userRole);
    next("/");
  } else {
    next();
  }
});

export default router;
