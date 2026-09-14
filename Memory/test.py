import sys

# 0. 中文 Windows 控制台是 GBK(936)，hello_agents 会打印 ✅/🔍 等 emoji，
#    不重设编码会抛 UnicodeEncodeError。必须在 import 库之前处理。
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

# 1. 加载 .env 配置（内含 NO_PROXY 直连配置，必须在创建客户端前生效）
load_dotenv()

# 配置好同级文件夹下.env中的大模型API
from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools import MemoryTool, RAGTool
from hello_agents.memory.embedding import get_text_embedder

# 自检：必须是 LocalTransformerEmbedding / 384 维
# （若显示 DashScope 或 1024，说明嵌入模型静默回退了，会导致向量库维度不匹配）
_embedder = get_text_embedder()
print(f"[自检] 嵌入模型 = {type(_embedder).__name__}, 维度 = {getattr(_embedder, 'dimension', '?')}")

# 创建LLM实例
llm = HelloAgentsLLM()

# 创建工具注册表（必须先建好，再传给 Agent 构造函数）
tool_registry = ToolRegistry()

# 添加记忆工具
memory_tool = MemoryTool(user_id="user123")
tool_registry.register_tool(memory_tool)

# 添加RAG工具
rag_tool = RAGTool(knowledge_base_path="./knowledge_base")
tool_registry.register_tool(rag_tool)

# 创建Agent（tool_registry 必须在这里传；构造后再赋值 agent.tool_registry 是无效的，
# 因为 enable_tool_calling 在构造时就被冻结为 False，工具永远不会被调用）
agent = SimpleAgent(
    name="智能助手",
    llm=llm,
    system_prompt="你是一个有记忆和知识检索能力的AI助手",
    tool_registry=tool_registry,
)

# 2. 灌知识库：RAGTool 不会自动索引 knowledge_base 目录，必须显式添加文档
print(rag_tool.run({"action": "add_document", "file_path": "./knowledge_base/hello_agents_知识库.md"}))

# 3. 写情景记忆：Agent 自己发起的 store= 调用默认只写工作记忆（内存态，退出即失），
#    要真正落库（SQLite + Qdrant）需显式指定 memory_type="episodic"
print(memory_tool.run({
    "action": "add",
    "content": "我叫张三，是一名Python开发者",
    "memory_type": "episodic",
}))

# 4. 开始对话
response = agent.run("你好！请记住我叫张三，我是一名Python开发者")
print(response)

# 5. 检索验证：确认记忆真的写进去了
print(memory_tool.run({"action": "search", "query": "张三"}))

# 6. 知识库检索验证（action="search" 比 "ask" 快，ask 会额外触发 MQE/HyDE 多次 LLM 调用）
print(rag_tool.run({"action": "search", "query": "hello_agents 有哪些核心类？"}))
