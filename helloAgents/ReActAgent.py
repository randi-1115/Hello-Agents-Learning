#ReAct 提示词模板
REACT_PROMPT_TEMPLATE = """
请注意，你是⼀个有能⼒调⽤外部⼯具的智能助⼿。

可⽤⼯具如下:
{tools}

请严格按照以下格式进⾏回应:

Thought: 你的思考过程，⽤于分析问题、拆解任务和规划下⼀步⾏动。
Action: 你决定采取的⾏动，必须是以下格式之⼀:
- `{{tool_name}}[{{tool_input}}]`:调⽤⼀个可⽤⼯具。
- `Finish[最终答案]`:当你认为已经获得最终答案时。
- 当你收集到⾜够的信息，能够回答⽤户的最终问题时，你必须在Action:字段后使⽤ Finish[最
终答案] 来输出最终答案。

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""

class ReActAgent:
    def __init__(self,llm_client:HelloAgentsLLM,tool_executor:ToolExecutor,max_steps:int=5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def _parse_output(self,text:str):
        """解析LLM输出，提取Thought和Action"""
        #Thought:匹配到Action:或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)",text, re.DOTALL)
        #Action:匹配到文本末尾
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        """解析Action字符串，提取⼯具名称和输⼊。"""
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
                return match.group(1), match.group(2)
        return None, None

    def run(self,question:str):
        """
        运行ReAct智能体来回答一个问题
        """
        self.history = [] #每次运行时重置历史记录
        current_step = 0

        while current_step < self.max_steps:
            current_step +=1
            print(f"---第{current_step}步---")

            #1.格式化提示词
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)#将历史记录转换为字符串
            prompt= REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str
            )

            #2.调用LLM进行思考
            messages = [{"role":"user","content":prompt}]
            response_text = self.llm_client.think(messages=messages)

            if not response_text:
                print("错误：LLM未能返回有效响应")
                break
            #3.解析输出
            thought, action = self._parse_output(response_text)
            if thought :
                print(f"Thought: {thought}")

            if not action:
                print("错误：未能解析到Action")
                break

            #4.执行Action
            if action.startswith("Finish"):
                #如果是Finish，直接返回最终答案
                final_answer = re.match(r"Finish\[(.*)\]",action).group(1)
                print(f"最终答案: {final_answer}")
                return final_answer

            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                #...处理无效Action格式...
                continue

            print(f"Action: 调⽤工具 {tool_name}，输⼊: {tool_input}")

            tool_function = self.tool_executor.getTool(tool_name)#获取工具函数
            if not tool_function:
                print(f"错误：工具 {tool_name} 不存在")
            else:
                observation = tool_function(tool_input)#调⽤工具

            print(f"观察: {observation}")

            self.history.append(f"Action:{action}")
            self.history.append(f"Observation:{observation}")

            print("已达到最大步数，流程终止")
            return None
        
        

