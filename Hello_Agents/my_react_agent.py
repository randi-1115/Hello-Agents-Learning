MY_REACT_PROMPT = """你是⼀个具备推理和⾏动能⼒的AI助⼿。你可以通过思考分析问题，然后
调⽤合适的⼯具来获取信息，最终给出准确的答案。

## 可⽤⼯具
{tools}

## ⼯作流程
请严格按照以下格式进⾏回应，每次只能执⾏⼀个步骤:

Thought: 分析当前问题，思考需要什么信息或采取什么⾏动。
Action: 选择⼀个⾏动，格式必须是以下之⼀:
- `{{tool_name}}[{{tool_input}}]` - 调⽤指定⼯具
- `Finish[最终答案]` - 当你有⾜够信息给出最终答案时

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. ⼯具调⽤的格式必须严格遵循:⼯具名[参数]3. 只有当你确信有⾜够信息回答问题时，才使⽤Finish
4. 如果⼯具返回的信息不够，继续使⽤其他⼯具或相同⼯具的不同参数

## 当前任务
**Question:** {question}

## 执⾏历史
{history}

现在开始你的推理和⾏动:
"""#默认提示词S
import re#用于解析工具调用
from typint import Optional,List,Tuple
from hello_agents import ReActAgent,HelloAgentsLLM,Config,Message,ToolRegistry

class MyReActAgent(ReActAgent):
    """
    重写的ReAct Agent - 推理与行动结合的智能体
    """

    def __init__(
        self,
        name:str,
        llm:HelloAgentsLLM,
        tool_registry:ToolRegistry,
        system_prompt:Optional[str] = None,
        config:Optional[Config] = None,
        max_steps:int =5,
        custom_prompt:Optional[str] = None
    ):
        super().__init__(name,llm,system_prompt,config)
        self.tool_registry = tool_registry
        self.max_steps = max_steps
        self.current_history : List[str] = []
        self.prompt_template = custom_prompt if custom_prompt else MY_REACT_PROMPT#使用自定义提示词或默认提示词
        print(f"{name}初始化完成，最大步数:{max_steps}")
        
    def run(self,input_text:str,**kwargs) -> str:
        """运行ReAct Agent"""
        self.current_history = []
        current_step = 0

        print(f"\n{self.name}开始运行，输入问题：{input_text}")

        while current_step < self.max_steps:
            current_step += 1
            print(f"第{current_step}步")#打印当前步数

             #1.构建提示词
            tools_desc = self.tool_registry.get_tools_description()
            history_str = "\n".join(self.current_history)
            prompt = self.prompt_template.format(
              tools=tools_desc,
              question=input_text,
              history=history_str
            )

            #2.调用LLM
            messages = [{"role":"user","content":prompt}]
            response_text = self.llm.invoke(messages,**kwargs)

            #3.解析输出
            thought,action = self._parse_output(response_text)

            #4.检查完成条件
            if action and action.startswith("Finish"):
                final_answer = self._parse_action_input(action)#解析最终答案
                self.add_message(Message(input_text,"user"))
                self.add_message(Message(final_answer,"assistant"))
                return final_answer

            #5.执行工具调用
            if action:
                tool_name,tool_input = self._parse_action(action)
                observation = self.tool_registry.execute_tool(tool_name,tool_input)
                self.current_history.append(f"Action:{action}")#记录工具调用
                self.current_history.append(f"Observation:{observation}")#记录工具调用结果

        #达到最大步数
        final_answer = "抱歉 ，我无法在限定步数内完成这个任务。"
        self.add_message(Message(input_text,"user"))
        self.add_message(Message(final_answer,"assistant"))
        return final_answer
    