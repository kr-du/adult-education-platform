import axios from "axios";
import { useUserStore } from "@/store/user";
import { ElMessage } from "element-plus";
import router from "@/router";

let authExpiredTimer = null;
export function handleAuthExpired() {
  if (authExpiredTimer) return;
  authExpiredTimer = setTimeout(() => {
    authExpiredTimer = null;
  }, 1000);
  const userStore = useUserStore();
  userStore.logout();
  router.push("/login");
  ElMessage.error("登录已过期，请重新登录");
}

// 创建axios实例
const api = axios.create({
  baseURL: "/api",
  timeout: 30000,
});

// 请求拦截器，自动添加Authorization头
api.interceptors.request.use((config) => {
  const userStore = useUserStore();
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`;
  }
  return config;
});

// 响应拦截器，处理401错误，自动跳转到登录页并清除用户信息
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API请求错误:", error);

    if (error.response?.status === 401) {
      handleAuthExpired();
    } else if (error.response?.status >= 500) {
      ElMessage.error("服务器错误，请稍后重试");
    } else if (!error.response) {
      ElMessage.error("网络连接失败，请检查网络");
    }
    // 403和404错误由调用方自行处理，不在此统一显示

    return Promise.reject(error);
  },
);

// 定义API接口
export const authApi = {
  login: (data) => api.post("/auth/login", data),
  register: (data) => api.post("/auth/register", data),
  resetPassword: (data) => api.post("/auth/reset-password", data),
  getProfile: () => api.get("/auth/profile"),
  updateProfile: (data) => api.put("/auth/profile", data),
};

// 定义课程API接口
export const courseApi = {
  getCourses: (params) => api.get("/courses/", { params }),
  getCourse: (id) => api.get(`/courses/${id}`),
  createCourse: (data) => api.post("/courses/", data),
  updateCourse: (id, data) => api.put(`/courses/${id}`, data),
  deleteCourse: (id) => api.delete(`/courses/${id}`),
  addLesson: (courseId, data) => api.post(`/courses/${courseId}/lessons`, data),
  enrollCourse: (courseId) => api.post(`/courses/enroll/${courseId}`),
  getMyEnrollments: () => api.get("/courses/my-enrollments"),
  updateProgress: (lessonId, data) =>
    api.post(`/courses/progress/${lessonId}`, data),
  getCategories: () => api.get("/courses/categories"),
  createCategory: (data) => api.post("/courses/categories", data),
  updateCategory: (id, data) => api.put(`/courses/categories/${id}`, data),
  deleteCategory: (id) => api.delete(`/courses/categories/${id}`),
};

// 定义作业API接口
export const assignmentApi = {
  // 教师端
  getTeacherAssignments: () => api.get("/assignments/teacher"),
  getCourseAssignments: (courseId) =>
    api.get(`/assignments/course/${courseId}`),
  getAssignment: (id) => api.get(`/assignments/${id}`),
  createAssignment: (data) => api.post("/assignments/", data),
  updateAssignment: (id, data) => api.put(`/assignments/${id}`, data),
  deleteAssignment: (id) => api.delete(`/assignments/${id}`),
  getSubmissions: (assignmentId) =>
    api.get(`/assignments/submissions/${assignmentId}`),
  gradeSubmission: (id, data) => api.post(`/assignments/grade/${id}`, data),

  // 学生端
  getStudentAssignments: () => api.get("/assignments/student"),
  submitAssignment: (id, data) => api.post(`/assignments/submit/${id}`, data),
  getMySubmissions: () => api.get("/assignments/my-submissions"),
};

// 定义用户API接口
export const userApi = {
  getLearningRecords: () => api.get("/users/learning-records"),
  getGrades: () => api.get("/users/grades"),
  getTeacherStudents: () => api.get("/users/teacher/students"),
  getTeacherStatistics: () => api.get("/users/teacher/statistics"),
};

// 添加管理员API接口
export const adminApi = {
  getUsers: (params) => api.get("/admin/users", { params }),
  createUser: (data) => api.post("/admin/users", data),
  updateUser: (id, data) => api.put(`/admin/users/${id}`, data),
  approveUser: (id) => api.post(`/admin/users/${id}/approve`),
  rejectUser: (id) => api.post(`/admin/users/${id}/reject`),
  deleteUser: (id) => api.delete(`/admin/users/${id}`),
  getTeachers: () => api.get("/admin/teachers"),
  getAnnouncements: () => api.get("/admin/announcements"),
  createAnnouncement: (data) => api.post("/admin/announcements", data),
  updateAnnouncement: (id, data) => api.put(`/admin/announcements/${id}`, data),
  deleteAnnouncement: (id) => api.delete(`/admin/announcements/${id}`),
  getStatistics: () => api.get("/admin/statistics"),
  getAllCourses: (params) => api.get("/admin/courses", { params }),
  // 审核管理
  getReviewStatistics: () => api.get("/reviews/statistics"),
  getAdminReviews: (params) => api.get("/admin/reviews", { params }),
  approveReview: (id) => api.put(`/admin/reviews/${id}/approve`),
  rejectReview: (id) => api.put(`/admin/reviews/${id}/reject`),
  deleteReview: (id) => api.delete(`/admin/reviews/${id}`),
  deleteAllApprovedReviews: () =>
    api.delete("/admin/reviews/delete-all-approved"),
  getAdminQuestions: (params) => api.get("/admin/questions", { params }),
  approveQuestion: (id) => api.put(`/admin/questions/${id}/approve`),
  rejectQuestion: (id) => api.put(`/admin/questions/${id}/reject`),
  deleteQuestion: (id) => api.delete(`/admin/questions/${id}`),
  deleteAllApprovedQuestions: () =>
    api.delete("/admin/questions/delete-all-approved"),
  getAdminAnswers: (params) => api.get("/admin/answers", { params }),
  approveAnswer: (id) => api.put(`/admin/answers/${id}/approve`),
  rejectAnswer: (id) => api.put(`/admin/answers/${id}/reject`),
  deleteAnswer: (id) => api.delete(`/admin/answers/${id}`),
  deleteAllApprovedAnswers: () =>
    api.delete("/admin/answers/delete-all-approved"),
  getAdminDiscussions: (params) => api.get("/admin/discussions", { params }),
  approveDiscussion: (id) => api.put(`/admin/discussions/${id}/approve`),
  rejectDiscussion: (id) => api.put(`/admin/discussions/${id}/reject`),
  deleteDiscussion: (id) => api.delete(`/admin/discussions/${id}`),
  deleteAllApprovedDiscussions: () =>
    api.delete("/admin/discussions/delete-all-approved"),
};

// 定义上传API接口
export const uploadApi = {
  uploadAvatar: (formData) =>
    api.post("/uploads/avatar", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  uploadCourseImage: (formData) =>
    api.post("/uploads/course-image", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  uploadVideo: (formData) =>
    api.post("/uploads/video", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
};

// 添加互动API接口
export const interactionApi = {
  // 课程评价
  getCourseReviews: (courseId) => api.get(`/reviews/course/${courseId}`),
  createReview: (data) => api.post("/reviews/", data),
  deleteReview: (id) => api.delete(`/reviews/${id}`),

  // 消息通知
  getMessages: () => api.get("/messages/"),
  markMessageRead: (id) => api.put(`/messages/${id}/read`),
  markAllMessagesRead: () => api.put("/messages/read-all"),
  getUnreadCount: () => api.get("/messages/unread-count"),

  // 答疑互动
  getCourseQuestions: (courseId) => api.get(`/questions/course/${courseId}`),
  createQuestion: (data) => api.post("/questions/", data),
  getQuestionAnswers: (questionId) =>
    api.get(`/questions/${questionId}/answers`),
  createAnswer: (questionId, data) =>
    api.post(`/questions/${questionId}/answers`, data),
  resolveQuestion: (questionId) => api.put(`/questions/${questionId}/resolve`),

  // 课程公告
  getCourseNotices: (courseId) => api.get(`/notices/course/${courseId}`),
  createNotice: (data) => api.post("/notices/", data),
  deleteNotice: (id) => api.delete(`/notices/${id}`),

  // 教师统计
  getCourseStudents: (courseId) =>
    api.get(`/teacher/course/${courseId}/students`),
  getCourseStatistics: (courseId) =>
    api.get(`/teacher/course/${courseId}/statistics`),
};

// AI助手API
export const aiApi = {
  getConversations: () => api.get("/ai/conversations"),
  createConversation: (data) => api.post("/ai/conversations", data),
  getConversationMessages: (id) => api.get(`/ai/conversations/${id}`),
  deleteConversation: (id) => api.delete(`/ai/conversations/${id}`),
  chat: (data) => api.post("/ai/chat", data),
  chatStream: (data, onMessage, onDone, onError) => {
    const userStore = useUserStore();
    fetch("/api/ai/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${userStore.token}`,
      },
      body: JSON.stringify(data),
    })
      .then((response) => {
        if (response.status === 401) {
          handleAuthExpired();
          return;
        }
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        // 获取conversation_id
        const conversationId = response.headers.get("Conversation-Id");
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        function read() {
          reader
            .read()
            .then(({ done, value }) => {
              if (done) {
                onDone(conversationId);
                return;
              }
              buffer += decoder.decode(value, { stream: true });
              const lines = buffer.split("\n");
              buffer = lines.pop() || "";
              for (const line of lines) {
                if (line.startsWith("data: ")) {
                  const data = line.slice(6);
                  if (data === "[DONE]") {
                    onDone(conversationId);
                    return;
                  }
                  try {
                    const parsed = JSON.parse(data);
                    if (parsed.text !== undefined) {
                      onMessage(parsed.text);
                    }
                  } catch {
                    onMessage(data);
                  }
                }
              }
              read();
            })
            .catch((err) => {
              onError(err);
            });
        }
        read();
      })
      .catch((err) => {
        onError(err);
      });
  },
};

// 讨论区API
export const discussionApi = {
  getCourseDiscussions: (courseId) =>
    api.get(`/discussions/course/${courseId}`),
  createDiscussion: (data) => api.post("/discussions/", data),
  getReplies: (discussionId) => api.get(`/discussions/${discussionId}/replies`),
  deleteDiscussion: (id) => api.delete(`/discussions/${id}`),
  getTeacherDiscussions: () => api.get("/discussions/teacher"),
};

// 导出API实例
export default api;
