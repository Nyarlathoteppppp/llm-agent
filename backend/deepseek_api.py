# deepseek_api.py,source ai/bin/activate

"""
DeepSeek API 封装模块

支持：
- 普通聊天调用（deepseek-chat）
- 多轮对话（传入 history）
- 流式响应（stream=True）
- Prefix Chat（Beta）
- 函数调用（Function Calling）
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# ✅ 加载 .env 文件中的环境变量
load_dotenv()

# ✅ 从环境变量中读取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("❌ 未设置 DEEPSEEK_API_KEY 环境变量，请在 .env 中添加")

# ✅ 初始化 DeepSeek 客户端（官方要求 base_url）
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)


def chat(
    prompt: str,
    model: str = "deepseek-chat",
    stream: bool = False,
    max_tokens: int = None,
    temperature: float = 1.0,
    top_p: float = 1.0,
    frequency_penalty: float = 0.0,
    presence_penalty: float = 0.0,
    system_prompt: str = "You are a helpful assistant",
    history: list = None,
    **kwargs
):
    """
    普通聊天调用（支持多轮对话）

    参数:
        prompt (str): 当前用户输入内容
        model (str): 模型名称，默认 deepseek-chat
        stream (bool): 是否启用流式响应（True 返回生成器）
        system_prompt (str): 系统角色提示词
        history (list): 聊天历史，例如 [{"role": "user", "content": "你是谁？"}, {"role": "assistant", "content": "我是AI"}]
        其余参数透传给 API

    返回:
        非流式：OpenAI response 对象
        流式：生成器
    """

    # 构建完整的 messages 列表
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})

    # 调用 DeepSeek API（OpenAI 格式）
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        **kwargs
    )
    return response


def chat_prefix(prompt: str, prefix: str, stop: list = None, model: str = "deepseek-chat"):
    """
    Prefix Chat Completion（Beta）

    用于引导模型以指定前缀开始输出（如代码生成）

    参数:
        prompt (str): 用户输入内容
        prefix (str): 模型输出前缀，如 "```python\n"
        stop (list): 停止符号，例如 ["```"]
        model (str): 使用的模型，默认 deepseek-chat

    返回:
        OpenAI response 对象
    """
    client.beta_url = "https://api.deepseek.com/beta"

    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": prefix, "prefix": True}
        ],
        stop=stop
    )


def chat_with_funcs(prompt: str, tools: list, model: str = "deepseek-chat"):
    """
    支持函数调用（Function Calling）

    参数:
        prompt (str): 用户输入
        tools (list): 函数定义列表，遵循 OpenAI Function Calling 格式
        model (str): 模型名，推荐使用 deepseek-chat

    返回:
        OpenAI response 对象，包含是否触发函数调用的信息
    """
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        tools=tools,
        tool_choice="auto"
    )


# ✅ 测试入口：直接运行文件时触发
if __name__ == "__main__":
    print("🧪 测试 DeepSeek Chat 多轮对话调用")

    # 模拟聊天历史
    history = [
        {"role": "user", "content": "你是谁？"},
        {"role": "assistant", "content": "我是一个由 DeepSeek 提供的 AI 助手。"}
    ]

    # 当前提问
    prompt = "你能为我做什么？"

    # 调用 chat 接口
    try:
        res = chat(prompt, history=history)
        print("✅ 回复内容：\n")
        print(res.choices[0].message.content)
    except Exception as e:
        print(f"❌ 请求失败：{e}")
