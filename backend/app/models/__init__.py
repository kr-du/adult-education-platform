# 导入所有数据模型，方便在其他模块中统一使用
from app.models.user import User
from app.models.course import Course, Category, Lesson, Enrollment, LessonProgress
from app.models.assignment import Assignment, Submission
from app.models.announcement import Announcement, Discussion
from app.models.interaction import Review, Message, Question, Answer, CourseNotice
from app.models.ai import AiConversation, AiMessage
