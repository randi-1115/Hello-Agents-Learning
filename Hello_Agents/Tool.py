class Tool(ABC):
    """工具基类"""
    def __init__(self,name:str,description:str):
        self.name=name
        self.description=description

    @abstractmethod
    def run(self,parameters:Dict[str,Any]) -> str:
        """执行工具"""
        pass

    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        """获取工具参数定义"""
        pass

class ToolParameter:
    """工具参数定义"""
    name:str
    type:str
    description:str
    required:bool = True
    default:Any=None

class ToolRegistry:
    """HelloAgents工具注册表"""

    def __init__(self):
        self._tools:dict[str,Tool] = {}#工具注册表
        self._functions:dict[str,dict[str,Any]] = {} 

    def register_tool(self,tool:Tool):#适合复杂⼯具，⽀持完整的参数定义和验证
        """注册Tool对象"""
        if tool.name in self._tools:
            print(f"工具{tool.name}已注册，将被覆盖")
        self._tools[tool.name] = tool
        print(f"工具{tool.name}注册成功")

    def register_function(self,name:str,description:str,func:Callable[[str],str]):
        #适合简单⼯具，快速集成现有函数
        """
        直接注册函数作为工具（简便方式）

        Args：
           name:工具名称
           description:工具描述
           func：工具函数，接受字符串参数，返回字符串结果
        """
        if name in self._functions:
            print(f"⚠ 警告:⼯具 '{name}' 已存在，将被覆盖。")

        self._functions[name] = {
            "description":description,
            "func":func
        }
        print(f"✅ ⼯具 '{name}' 已注册。")

    def get_tools_description(self) -> str:
        """获取所有可用工具的格式化描述字符串"""
        descriptions = []

        #Tool对象描述
        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")

        #函数工具描述
        for name,info in self._functions.items():
            descriptions.append(f"- {name}: {info['description']}")

        return "\n".join(descriptions) if descriptions else "暂无工具注册。"#返回格式化后的工具描述字符串

    def to_openai_schema(self) -> Dict[str,Any]:
        """转换为OpenAI function calling schema 格式
        用于FunctionCallAgent，使工具能够被OpenAI原生function calling 使用

        Returns：
            符合OpenAI function calling 标准的 schema
        """
        parameters = self.get_parameters()

        #构建properties
        properties = {}
        required = []

        for param in parameters:
            #基础属性定义
            prop = {
                "type":param.type,
                "description":param.description
            }

            #如果有默认值，添加到描述中（OpenAI schema 不支持 default字段）
            if param.default is not None:
                prop["description"] = f"{param.description} (默认值: {param.default})"

            #如果是数组类型，添加items定义
            if param.type == "array":
                prop["items"] = {"type":"string"}#默认字符串数组

            properties[param.name] = prop

            #收集必需参数
            if param.required:
                required.append(param.name)

        return {
            "type":"function",
            "function":{
                "name":self.name,
                "description":self.description,
                "parameters":{
                    "type":"object",
                    "properties":properties,
                    "required":required
                }
            }
               }
    





