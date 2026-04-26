"""AI学习助手模块 - 智谱AI接口"""
import os
from zhipuai import ZhipuAI

ZHIPU_API_KEY = os.environ.get('ZHIPU_API_KEY', 'fda5416ff6c648ee9a0b9cf1894ccd5d.EoxvApSUQd7Xi4Qz')


class AiService:
    """智谱AI服务类"""

    def __init__(self):
        self.client = ZhipuAI(api_key=ZHIPU_API_KEY)

    # 对话
    def chat(self, messages, model="glm-4-flash"):
        """
        发送对话请求

        Args:
            messages: 消息列表 [{"role": "user", "content": "你好"}]
            model: 模型名称，默认glm-4

        Returns:
            AI回复内容
        """
        try:
            response = self.client.chat.completions.create(
                model=model, # 模型名称
                messages=messages, # 消息列表
                temperature=0.85, # 随机性 - 0-1之间，越小越 deterministic，越大越随机
                max_tokens=2048 # 最大生成长度
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI请求失败: {e}")
            return f"抱歉，AI服务暂时不可用。错误信息：{str(e)}"

    # 流式对话
    def chat_stream(self, messages, model="glm-4-flash"):
        """
        流式对话（用于实时显示）

        Args:
            messages: 消息列表
            model: 模型名称

        Yields:
            AI回复的每个片段
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.85,
                max_tokens=2048,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"AI服务错误: {str(e)}"


# 创建全局实例
ai_service = AiService()


def get_system_prompt():
    """获取系统提示词"""
    return {
        "role": "system",
        "content": """你是成人再教育学习平台的AI学习助手，专门帮助学员解决学习中遇到的问题。

你的职责包括：
1. 解答学员的学习疑问
2. 提供学习方法和建议
3. 帮助理解课程内容
4. 解释专业概念和术语
5. 提供学习资源推荐

回答要求：
- 语言简洁明了，易于理解
- 针对成人学习者的特点，注重实用性
- 鼓励学员，保持积极正面的态度
- 如果不确定的问题，诚实说明并建议查阅相关资料"""
    }
