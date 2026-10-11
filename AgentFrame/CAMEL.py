from colorama import Fore
from camel.societies import RolePlaying
from camel.utils import print_text_animated
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from dotenv import load_dotenv
import os

load_dotenv()
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL")

#创建模型，在这里以Qwen为例 调用的百炼大模型平台API
model = ModelFactory.create(
    model_platform=ModelPlatformType.QWEN,
    model_type = LLM_MODEL,
    url=LLM_BASE_URL,
    api_key=LLM_API_KEY
)

#定义协作任务
task_prompt = """
创作⼀本关于"拖延症⼼理学"的短篇电⼦书，⽬标读者是对⼼理学感兴趣的普通⼤众。
要求：
1. 内容科学严谨，基于实证研究
2. 语⾔通俗易懂，避免过多专业术语
3. 包含实⽤的改善建议和案例分析
4. 篇幅控制在8000-10000字
5. 结构清晰，包含引⾔、核⼼章节和总结
"""

print(Fore.YELLOW + f"协作任务:\n{task_prompt}\n")

#初始化角色扮演会话
#AI作家作为“User”，负责提出写作结构和要求
#AI心理学家作为“Assistant”，负责提供科学依据和心理学知识
role_play_session = RolePlaying(
    assistant_role_name="心理学家",
    user_role_name="作家",
    task_prompt=task_prompt,
    model=model,
    with_task_specify=False,
)

#开始角色扮演
chat_turn_limit, n = 30, 0  # 最大轮数，当前轮数
#调用init_chat()来获得由AI生成的初始对话消息
input_msg = role_play_session.init_chat()  # 获取初始对话消息

while n < chat_turn_limit:
    n+= 1
    #step()方法驱动一轮完整对话，AI用户和AI助理各发言一次
    assistant_response , user_response = role_play_session.step(input_msg)

    #检查是否有消息返回，防止对话提前结束
    if assistant_response is None or user_response is None:
        break

    print_text_animated(Fore.BLUE + f"作家(AI Assistant):\n\n{assistant_response.msg.content}\n")
    print_text_animated(Fore.GREEN + f"心理学家(AI Assistant):\n\n{user_response.msg.content}\n")


    #检查任务完成标志

    if "<CAMEL_TASK_DONE>" in user_response.msg.content or "<CAMEL_TASK_DONE>" in assistant_response.msg.content:
        print_text_animated(Fore.MAGENTA + "✅ 电⼦书创作完成！")
        break

    #将助理的回复作为下一轮用户的输入
    input_msg = assistant_response.msg

print(Fore.YELLOW + f"总共进⾏了 {n} 轮协作对话")

