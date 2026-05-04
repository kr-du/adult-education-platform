"""AI学习助手API"""
import json
from flask import Blueprint, request, jsonify, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.ai import AiConversation, AiMessage
from app.services.ai_service import ai_service, get_system_prompt
from app.utils.auth import get_current_user

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """获取用户的对话列表"""
    user = get_current_user()
    conversations = AiConversation.query.filter_by(user_id=user.id).order_by(
        AiConversation.updated_at.desc()
    ).all()

    return jsonify({
        'conversations': [c.to_dict() for c in conversations]
    })


@ai_bp.route('/conversations', methods=['POST'])
@jwt_required()
def create_conversation():
    """创建新对话"""
    user = get_current_user()
    data = request.get_json() or {}

    conversation = AiConversation(
        user_id=user.id,
        title=data.get('title', '新对话')
    )
    db.session.add(conversation)
    db.session.commit()

    return jsonify({
        'message': '创建成功',
        'conversation': conversation.to_dict()
    }), 201


@ai_bp.route('/conversations/<int:conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation_messages(conversation_id):
    """获取对话的消息列表"""
    user = get_current_user()
    conversation = AiConversation.query.get_or_404(conversation_id)

    if conversation.user_id != user.id:
        return jsonify({'error': '无权访问'}), 403

    messages = AiMessage.query.filter_by(
        conversation_id=conversation_id
    ).order_by(AiMessage.created_at.asc()).all()

    return jsonify({
        'conversation': conversation.to_dict(),
        'messages': [m.to_dict() for m in messages]
    })


@ai_bp.route('/conversations/<int:conversation_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conversation_id):
    """删除对话"""
    user = get_current_user()
    conversation = AiConversation.query.get_or_404(conversation_id)

    if conversation.user_id != user.id:
        return jsonify({'error': '无权访问'}), 403

    db.session.delete(conversation)
    db.session.commit()

    return jsonify({'message': '删除成功'})


@ai_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    """发送消息并获取AI回复"""
    user = get_current_user()
    data = request.get_json()

    conversation_id = data.get('conversation_id')
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': '消息不能为空'}), 400

    # 获取或创建对话
    if conversation_id:
        conversation = AiConversation.query.get(conversation_id)
        if not conversation or conversation.user_id != user.id:
            return jsonify({'error': '对话不存在'}), 404
    else:
        # 创建新对话
        conversation = AiConversation(
            user_id=user.id,
            title=user_message[:20] + '...' if len(user_message) > 20 else user_message
        )
        db.session.add(conversation)
        db.session.flush()

    # 保存用户消息
    user_msg = AiMessage(
        conversation_id=conversation.id,
        role='user',
        content=user_message
    )
    db.session.add(user_msg)

    # 获取历史消息（最近10条）
    history_messages = AiMessage.query.filter_by(
        conversation_id=conversation.id
    ).order_by(AiMessage.created_at.desc()).limit(10).all()

    # 构建请求消息
    messages = [get_system_prompt()]
    for msg in reversed(history_messages):
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_message})

    # 调用AI
    ai_reply = ai_service.chat(messages)

    # 保存AI回复
    ai_msg = AiMessage(
        conversation_id=conversation.id,
        role='assistant',
        content=ai_reply
    )
    db.session.add(ai_msg)

    # 更新对话时间
    conversation.updated_at = db.func.now()
    db.session.commit()

    # 刷新消息以获取完整数据
    db.session.refresh(ai_msg)

    return jsonify({
        'conversation_id': conversation.id,
        'user_message': user_msg.to_dict(),
        'ai_message': ai_msg.to_dict()
    })


@ai_bp.route('/chat/stream', methods=['POST'])
@jwt_required()
def chat_stream():
    """流式对话"""
    user = get_current_user()
    data = request.get_json()

    conversation_id = data.get('conversation_id')
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': '消息不能为空'}), 400

    # 获取或创建对话
    if conversation_id:
        conversation = AiConversation.query.get(conversation_id)
        if not conversation or conversation.user_id != user.id:
            return jsonify({'error': '对话不存在'}), 404
    else:
        conversation = AiConversation(
            user_id=user.id,
            title=user_message[:20] + '...' if len(user_message) > 20 else user_message
        )
        db.session.add(conversation)
        db.session.flush()

    # 保存用户消息
    user_msg = AiMessage(
        conversation_id=conversation.id,
        role='user',
        content=user_message
    )
    db.session.add(user_msg)

    # 获取历史消息
    history_messages = AiMessage.query.filter_by(
        conversation_id=conversation.id
    ).order_by(AiMessage.created_at.desc()).limit(10).all()

    # 构建请求消息
    messages = [get_system_prompt()]
    for msg in reversed(history_messages):
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_message})

    def generate():
        full_reply = []
        for chunk in ai_service.chat_stream(messages):
            full_reply.append(chunk)
            json_string = json.dumps({"text": chunk})
            yield f"data: {json_string}\n\n"

        # 保存完整回复
        ai_msg = AiMessage(
            conversation_id=conversation.id,
            role='assistant',
            content=''.join(full_reply)
        )
        db.session.add(ai_msg)
        conversation.updated_at = db.func.now()
        db.session.commit()

        yield f"data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Conversation-Id': str(conversation.id)
        }
    )
