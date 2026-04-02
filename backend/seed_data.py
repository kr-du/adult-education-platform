"""添加示例教师和课程数据"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.course import Course, Category

app = create_app()

with app.app_context():
    # 创建分类
    categories_data = [
        {'name': 'IT技术', 'description': '编程、开发、网络安全等技术课程'},
        {'name': '人工智能', 'description': '机器学习、深度学习、AI应用等课程'},
        {'name': '数据分析', 'description': '大数据、Python分析、数据可视化等课程'},
        {'name': '语言学习', 'description': '英语、日语、商务英语等语言课程'},
        {'name': '职业技能', 'description': '办公软件、项目管理、沟通技巧等课程'},
        {'name': '学历提升', 'description': '考研、专升本、成人高考等课程'},
    ]

    categories = {}
    for cat_data in categories_data:
        cat = Category.query.filter_by(name=cat_data['name']).first()
        if not cat:
            cat = Category(**cat_data)
            db.session.add(cat)
            db.session.flush()
        categories[cat_data['name']] = cat.id
    print('分类创建完成')

    # 创建教师（三国演义人物）
    teachers_data = [
        {'username': 'zhugeliang', 'email': 'zgl@edu.com', 'real_name': '诸葛亮', 'phone': '13800001001', 'role': 'teacher'},
        {'username': 'guanyu', 'email': 'gy@edu.com', 'real_name': '关羽', 'phone': '13800001002', 'role': 'teacher'},
        {'username': 'zhangfei', 'email': 'zf@edu.com', 'real_name': '张飞', 'phone': '13800001003', 'role': 'teacher'},
        {'username': 'zhaoyun', 'email': 'zy@edu.com', 'real_name': '赵云', 'phone': '13800001004', 'role': 'teacher'},
        {'username': 'simayi', 'email': 'smy@edu.com', 'real_name': '司马懿', 'phone': '13800001005', 'role': 'teacher'},
        {'username': 'zhouyu', 'email': 'zy2@edu.com', 'real_name': '周瑜', 'phone': '13800001006', 'role': 'teacher'},
        {'username': 'huangyueying', 'email': 'hyy@edu.com', 'real_name': '黄月英', 'phone': '13800001007', 'role': 'teacher'},
        {'username': 'caocao', 'email': 'cc@edu.com', 'real_name': '曹操', 'phone': '13800001008', 'role': 'teacher'},
    ]

    teachers = {}
    for t_data in teachers_data:
        teacher = User.query.filter_by(username=t_data['username']).first()
        if not teacher:
            teacher = User(**t_data, status='approved')
            teacher.set_password('123456')
            db.session.add(teacher)
            db.session.flush()
        teachers[t_data['real_name']] = teacher.id
    print('教师创建完成')

    # 创建课程
    courses_data = [
        {
            'title': 'Python编程从入门到精通',
            'description': '本课程从Python基础语法讲起，逐步深入到面向对象编程、文件处理、网络编程等高级主题。适合零基础学员系统学习Python编程语言，掌握实际开发技能。',
            'teacher_name': '诸葛亮',
            'category_name': 'IT技术',
            'price': 199,
            'duration': 48,
            'status': 'published'
        },
        {
            'title': '人工智能入门与实践',
            'description': '全面介绍人工智能的基本概念、发展历程和核心技术。涵盖机器学习、深度学习、自然语言处理等领域的基础知识和实践案例。',
            'teacher_name': '司马懿',
            'category_name': '人工智能',
            'price': 299,
            'duration': 64,
            'status': 'published'
        },
        {
            'title': '深度学习及其应用',
            'description': '深入讲解卷积神经网络(CNN)、循环神经网络(RNN)、Transformer等深度学习核心架构，结合图像识别、语音处理等实际应用案例。',
            'teacher_name': '周瑜',
            'category_name': '人工智能',
            'price': 399,
            'duration': 72,
            'status': 'published'
        },
        {
            'title': '大数据技术原理与应用',
            'description': '系统讲解大数据生态系统，包括Hadoop、Spark、Hive等核心技术，以及数据采集、存储、处理和分析的完整流程。',
            'teacher_name': '曹操',
            'category_name': '数据分析',
            'price': 259,
            'duration': 56,
            'status': 'published'
        },
        {
            'title': 'Python数据分析实战',
            'description': '使用Python进行数据清洗、分析和可视化，掌握Pandas、NumPy、Matplotlib等数据分析核心库的使用方法。',
            'teacher_name': '黄月英',
            'category_name': '数据分析',
            'price': 179,
            'duration': 40,
            'status': 'published'
        },
        {
            'title': '机器学习算法与实战',
            'description': '深入讲解常用机器学习算法原理，包括决策树、随机森林、支持向量机、聚类算法等，配合实际项目案例。',
            'teacher_name': '诸葛亮',
            'category_name': '人工智能',
            'price': 329,
            'duration': 58,
            'status': 'published'
        },
        {
            'title': 'Web前端开发全栈课程',
            'description': '从HTML/CSS基础到Vue/React框架，系统学习前端开发技术栈，掌握现代Web应用开发能力。',
            'teacher_name': '赵云',
            'category_name': 'IT技术',
            'price': 239,
            'duration': 60,
            'status': 'published'
        },
        {
            'title': 'Java企业级开发',
            'description': '讲解Java核心技术、Spring Boot框架、微服务架构，培养企业级应用开发能力。',
            'teacher_name': '关羽',
            'category_name': 'IT技术',
            'price': 279,
            'duration': 66,
            'status': 'published'
        },
        {
            'title': '商务英语精讲',
            'description': '针对职场人士设计的商务英语课程，涵盖商务邮件、会议沟通、谈判技巧等实用场景。',
            'teacher_name': '张飞',
            'category_name': '语言学习',
            'price': 159,
            'duration': 36,
            'status': 'published'
        },
        {
            'title': '项目管理实战',
            'description': '系统学习项目管理知识体系，掌握项目规划、执行、监控的全流程管理方法。',
            'teacher_name': '司马懿',
            'category_name': '职业技能',
            'price': 189,
            'duration': 42,
            'status': 'published'
        },
        {
            'title': '数据可视化与商业智能',
            'description': '学习使用Tableau、Power BI等工具进行数据可视化，掌握商业智能分析方法。',
            'teacher_name': '周瑜',
            'category_name': '数据分析',
            'price': 219,
            'duration': 44,
            'status': 'published'
        },
        {
            'title': '网络安全基础',
            'description': '介绍网络安全基础知识，包括常见攻击类型、防御策略、安全工具使用等。',
            'teacher_name': '关羽',
            'category_name': 'IT技术',
            'price': 199,
            'duration': 38,
            'status': 'published'
        },
    ]

    for c_data in courses_data:
        existing = Course.query.filter_by(title=c_data['title']).first()
        if not existing:
            course = Course(
                title=c_data['title'],
                description=c_data['description'],
                teacher_id=teachers[c_data['teacher_name']],
                category_id=categories[c_data['category_name']],
                price=c_data['price'],
                duration=c_data['duration'],
                status=c_data['status']
            )
            db.session.add(course)

    db.session.commit()
    print('课程创建完成')
    print(f'共创建 {len(teachers_data)} 位教师，{len(courses_data)} 门课程')
