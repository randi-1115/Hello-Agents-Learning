# hello_agents 项目知识库（内部资料）

## 项目定位

hello_agents 是一个面向教学的 Python 多智能体框架，版本 0.2.0，要求 Python 3.10 以上。
它的设计目标是让初学者用很少的代码就能搭出「会调用工具、有记忆、能检索知识库」的智能体。
本机项目路径为 `c:\hello-agents`，实验脚本是 `Memory/test.py`。

## 核心类

- `HelloAgentsLLM`：统一的模型入口，自动识别 LLM 提供商。它读取 `LLM_MODEL_ID`、`LLM_API_KEY`、
  `LLM_BASE_URL`、`LLM_TIMEOUT` 四个通用环境变量，也支持按 `DEEPSEEK_API_KEY`、`DASHSCOPE_API_KEY`
  等厂商专有变量识别。本机使用的是 DeepSeek 的 `deepseek-flash` 模型，服务地址 `https://api.deepseek.com`。
- `SimpleAgent`：最基础的智能体实现，构造函数签名为
  `SimpleAgent(name, llm, system_prompt=None, config=None, tool_registry=None, enable_tool_calling=True)`。
  **注意**：`enable_tool_calling` 在构造时就等于 `enable_tool_calling and tool_registry is not None`，
  所以必须在构造时传入 `tool_registry`；构造完成后再赋值 `agent.tool_registry = registry` 不会生效，
  工具永远不会被调用。也可以改用 `agent.add_tool(tool)`，它会把开关重新打开。
- `ToolRegistry`：工具注册表，`register_tool()` 以工具的 `name` 为键登记，`get_tool(name)` 取出工具。

## 工具调用协议

SimpleAgent 不使用原生 function calling，而是把工具说明拼进 system prompt，要求模型输出
形如 `[TOOL_CALL:工具名:参数]` 的文本，再用正则 `\[TOOL_CALL:([^:]+):([^\]]+)\]` 解析。
框架内置了参数推断：对 `memory` 工具，`store=xxx` 等价于 `action=add, content=xxx`，
`recall=xxx` 等价于 `action=search, query=xxx`；对 `rag` 工具，`text=xxx` 等价于 `action=add_text`，
`search=xxx` 等价于 `action=search`。

## 记忆体系

`MemoryTool` 默认启用三类记忆：`working`（工作记忆，纯内存，进程退出即丢失）、
`episodic`（情景记忆，落 SQLite 与向量库）、`semantic`（语义记忆，依赖 Neo4j 知识图谱）。
可以通过 `MemoryTool(user_id="xxx", memory_types=["working"])` 只启用其中一部分。
Agent 通过 `store=` 发起的记忆写入默认落在 `working` 类型，因此不会持久化；
需要持久保存时必须显式传 `memory_type="episodic"`。

## 检索体系

`RAGTool` 基于 Qdrant 向量库实现，默认集合名为 `rag_knowledge_base`，向量维度 384。
它**不会自动索引** `knowledge_base_path` 目录，该目录只在 `add_document`、`add_text`
写入文档时作为临时存放处，所以必须显式调用 `add_document` 或 `add_text` 才能真正灌库。
`ask` 动作会启用 MQE 与 HyDE 两种查询增强，一次问答会额外产生多次大模型调用，速度较慢；
只想验证检索是否命中时，用 `search` 动作即可。

## 本机环境备注

本机的向量库集合（`hello_agents_vectors`、`rag_knowledge_base`）都是 384 维，
因此嵌入模型必须使用本地的 `sentence-transformers/all-MiniLM-L6-v2`（384 维）。
如果不小心切到 DashScope 的 `text-embedding-v3`（1024 维），写入和检索都会因维度不匹配而失败。
另外本机开着系统代理（Clash，127.0.0.1:7897），访问 Qdrant Cloud 与 Neo4j Aura 必须在
`NO_PROXY` 里放行对应域名，否则会报 SSL 连接中断。
