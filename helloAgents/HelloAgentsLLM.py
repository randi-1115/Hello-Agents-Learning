import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from typing import List,Dict,Any
from serpapi import SerpApiClient


load_dotenv()

class HelloAgentsLLM:
    def __init__(self,model:str = None,apiKey: str = None, baseUrl: str = None,timeout: int = None):
        #读取配置文件
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        self.timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        if not all([self.model , apiKey , baseUrl]):
            raise ValueError("模型ID,API密钥和服务地址必须被提供或在.env文件中定义。")
        
        self.client = OpenAI(api_key=apiKey,base_url=baseUrl,timeout=self.timeout)


    def think(self,messages: List[Dict[str,str]],temperature: float = 0) -> str:
        #向大模型发送请求并获取回答
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages = messages,
                temperature = temperature,
                stream = True,#边生成边输出
            )
            print("✅ 大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content,end="",flush=True)
                collected_content.append(content)
            print()
            return "".join(collected_content)
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None
        
'''
if __name__ == "__main__":
        try:
            llmClient = HelloAgentsLLM()

            exampleMessages = [
                {"role": "system", "content": "You are a helpful assistant that writes Python code."},
                {"role": "user", "content": "写一个快速排序算法"}
            ]

            print("---调用LLM---")
            responseText = llmClient.think(exampleMessages)
            if responseText:
                print("\n\n--- 完整模型响应 ---")
                print(responseText)

        except ValueError as e:
            print(e)

'''
def search(query: str) -> str:
    #执行网页搜索工具
    print(f"🔍 正在执行 [SerpApi] 网页搜: {query}")
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
          return "错误:SERPAPI_API_KEY 未在 .env 文件中配置。"
    
        params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "gl": "cn",
        "hl":"zh-cn",
        } 

        client = SerpApiClient(params)
        results = client.get_dict()

        if "answer_box_list" in results:
           return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
           return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
           return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
           snippets = [
            f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
            for i,res in enumerate(results["organic_results"][:3])
            ]
           return "\n\n".join(snippets)
    
        return f"对不起，没有找到关于 '{query}' 的信息。"
    except Exception as e:
       return f"搜索时发生错误: {e}"


class ToolExecutor:
    #工具管理器，用于注册和调用工具的执行函数

    def __init__(self):
        self.tools: Dict[str,Dict[str,Any]] = {}

    def registerTool(self,name: str, description: str,func: callable):
        #注册工具
        if name in self.tools:
            print(f"警告:工具 '{name}' 已存在，将被覆盖。")
        self.tools[name] = {"description": description,"func":func}
        print(f"工具 '{name}' 已注册。")
        
    def getTools(self,name: str) -> callable:
        #工具热插拔，以后新增工具根本不用改 Agent。
        return self.tools.get(name,{}).get("func")
    
    def getAvailableTools(self) -> str:
        return "\n".join([
            f"- {name}: {info['description']}"
            for name,info in self.tools.items()
        ])
'''
if __name__ == '__main__':
    toolExecutor = ToolExecutor()

    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    toolExecutor.registerTool("Search",search_description,search)
    
    print("\n--- 可用的工具 ---")
    print(toolExecutor.getAvailableTools())

    print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
    tool_name = "Search"
    tool_input = "英伟达最新的GPU型号是什么"

    tool_function = toolExecutor.getTools(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- 观察 (Observation) ---")
        print(observation)
    else:
        print(f"错误:未找到名为 '{tool_name}' 的工具。")
'''

#ReAct 提示词模板
REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下:
{tools}

请严格按照以下格式进行回应:

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一:
- `{{tool_name}}[{{tool_input}}]`:调用一个可用工具。
- `Finish[最终答案]`:当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在Action:字段后使用 Finish[最终答案] 来输
出最终答案。

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""
class ReActAgent:
    def __init__(self,llm_client:HelloAgentsLLM,tool_executor:ToolExecutor,max_steps:int = 5):
        #保存配置参数
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps#最大思考次数
        self.history = []#Agent短期记忆
    
    def run(self,question:str):
        #1.初始化 清空记忆
        self.history = []
        current_step = 0
        
        #2.主循环
        while current_step < self.max_steps:#Thought，Action，Observation...
            current_step += 1
            print(f"--- 第 {current_step} 步 ---")

            #3.拼Prompt词
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str
            )#历史塞回Prompt？因为 LLM 没有状态

            messages = [{"role":"user","content":prompt}]
            #4.调模型
            response_text = self.llm_client.think(messages=messages)

            if not response_text:
                print("错误:LLM未能返回有效响应。")
                break
            #5.解析输出
            thought,action = self._parse_output(response_text)
            if thought:
                print(f"思考: {thought}")
            if not action:
                print("警告：未能解析出有效的Action，流程终止。")
                break

            #6.判断是否结束
            if action.startswith("Finish"):
                final_answer = re.match(r"Finish\[(.*)\]",action).group(1)
                print(f"🎉 最终答案: {final_answer}")
                return final_answer
            
            #7.执行工具
            tool_name,tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                continue
            

            print(f"🎬 行动: {tool_name}[{tool_input}]")

            tool_function = self.tool_executor.getTools(tool_name)
            if not tool_function:
                observation = f"错误:未找到名为 '{tool_name}' 的工具。"
            else:
                observation = tool_function(tool_input)
        
            print(f"👀 观察: {observation}")

            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print("已达到最大步数，流程终止。")
        return None


    def _parse_output(self,text: str):
        #LLM输出解析器
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)",text,re.DOTALL)
        action_match=re.search(r"Action:\s*(.*?)$", text, re.DOTALL)     
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought,action
    
    def _parse_action(self,action_text:str):
        match = re.match(r"(\w+)\[(.*)\]",action_text,re.DOTALL)
        if match:
            return match.group(1),match.group(2)
        return None,None
    
if __name__ == '__main__':
    llm = HelloAgentsLLM()
    tool_executor = ToolExecutor()
    search_desc = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    tool_executor.registerTool("Search", search_desc, search)
    agent = ReActAgent(llm_client=llm, tool_executor=tool_executor)
    question = "华为最新的手机是哪一款？它的主要卖点是什么？"
    agent.run(question)
    







