# Hello-Agents 学习实践

跟随 [Hello-Agents](https://github.com/datawhalechina/hello-agents) 教程学习 AI Agent 开发的工作目录，记录从 LLM 封装、Agent 框架、记忆系统、RAG 检索，到多智能体通信协议与 Agentic RL 的实践代码与踩坑经验。

## 目录结构

```
hello-agents/
├── Hello_Agents/          # 核心 Agent 框架：Agent / Message / Tool 体系
│   ├── Agent.py           # Agent 抽象基类
│   ├── Message.py         # 消息模型（pydantic）
│   ├── Config.py          # 配置模型 + from_env()
│   ├── Tool.py            # Tool / ToolParameter / ToolRegistry
│   ├── my_llm.py          # 给 HelloAgentsLLM 扩展 modelscope provider
│   ├── my_simple_agent.py # SimpleAgent 实践（含 [TOOL_CALL] 解析与流式输出）
│   ├── my_react_agent.py  # ReAct 实践
│   ├── my_calculator_tool.py  # 基于 AST 的安全计算器
│   └── test_*.py          # 验证脚本
│
├── AgentFrame/            # 多智能体框架横向对比
│   ├── AutoGen.py         # RoundRobinGroupChat 软件团队（PM/工程师/评审/用户代理）
│   ├── CAMEL.py           # RolePlaying 角色扮演（心理学家 + 作家合著电子书）
│   ├── LangGraph.py       # StateGraph 骨架
│   └── demoLangGraph.py   # 「理解 → 搜索 → 回答」智能搜索助手
│
├── helloAgents/           # 早期实验：LLM 封装与基础 Agent 实现
│   ├── HelloAgentsLLM.py  # LLM 客户端封装
│   ├── my_llm.py          # 自定义 LLM 调用
│   ├── my_main.py         # 主入口实验
│   ├── Plan and Solve.py  # Plan-and-Solve 范式实践
│   ├── ReActAgent.py      # ReAct 范式（Thought / Action / Observation 循环）
│   └── Reflection.py      # 反思循环（含内联的 Memory 与三套 prompt 模板）
│
├── Memory/                # 记忆系统 + RAG 检索
│   ├── first.py           # 示例 01：MemoryTool 基础操作（可运行）
│   ├── test.py            # 测试脚本
│   ├── second.py          # WIP：智能分块 + 混合检索（MQE / HyDE）
│   ├── Q & A.py           # WIP：PDF 文档问答助手
│   ├── tesst.py           # PDFLearningAssistant：MemoryTool + RAGTool + Gradio 界面
│   ├── think.txt          # 第 8 章四种记忆类型（工作/情景/语义/感知）思考题
│   ├── knowledge_base/    # 知识库文档
│   └── .env.example       # 环境变量模板（含踩坑注释）
│
├── Context/               # 上下文工程与长程任务
│   ├── demo.py            # Agentic 版代码库维护助手（FunctionCallAgent 自主选工具）
│   ├── CodebaseMaintainer.py  # 非 Agentic 版：预处理 + 单次 llm.invoke + 后处理
│   ├── ContextBuilder.py  # 上下文构建器拆解（收集/筛选/结构化/压缩）
│   ├── NoteTool.py        # ProjectAssitant 演示（NoteTool + MemoryTool + RAGTool）
│   ├── TerminalTool.py    # 终端工具片段
│   └── my_flask_app_notes/    # NoteTool 运行产出的笔记与索引（示例产物）
│
├── Connect/               # 智能体通信协议
│   ├── a2a-server.py      # A2A：单个 researcher 服务端
│   ├── a2a-client.py      # A2A：最小客户端
│   ├── a2a-agents.py      # A2A：研究员/写手/编辑三智能体流水线
│   ├── a2aagent.py        # A2A：两个专家服务 + 接待员路由
│   ├── demo-a2a-sdk.py    # A2A-SDK 计算器智能体
│   ├── anp-agent.py       # ANP：服务发现 + 计算节点调度
│   ├── demo-anp.py        # ANP：组网演示
│   ├── mcp_tooll.py       # MCP：计算器工具
│   └── hhh.py             # MCP：双智能体文档助手（report.md 即其产物）
│
└── RLAgents/              # Agentic RL
    ├── sft.py             # 最小 SFT 训练示例
    ├── demo.py            # SFT + GRPO 快速跑通（各 10 / 5 样本）
    └── demo-rl.py         # GSM8K 数据集构建 + 自定义奖励函数完整流程
```

> ⚠️ 本仓库是**学习过程的存档**，多个文件是边学边写的半成品，存在已知手误——例如 `Hello_Agents/Message.py` 把 `Literal` 拼成了 `Listeral`、`Context/ContextBuilder.py` 少写一个逗号导致 SyntaxError。这些**故意保留原样**以记录学习轨迹，不保证可直接运行。
>
> 另外 `Memory/second.py`、`Memory/Q & A.py` 依赖的函数尚未实现完整，同样属于 WIP。

## 环境要求

- Python 3.10+（必需）
- 依赖：`hello-agents` 框架、`python-dotenv`、`qdrant-client`、`neo4j`、`sentence-transformers`
- 分章节另有：`autogen-agentchat`、`camel-ai`、`langgraph`、`a2a-sdk`、`gradio`、`trl` / `transformers` / `datasets`（RL 章节，建议另建虚拟环境）

## 快速开始

1. 克隆仓库：

   ```bash
   git clone <本仓库地址>
   cd hello-agents
   ```

2. 配置环境变量。每个子目录都提供了 `.env.example` 模板，复制后填入自己的密钥：

   ```bash
   cp Memory/.env.example Memory/.env
   ```

   > `.env` 已被 `.gitignore` 排除，**不要提交自己的真实密钥**。

3. 运行示例：

   ```bash
   cd Memory
   python first.py
   ```

## 踩坑记录

以下是配置过程中踩过的坑，模板 `.env.example` 里保留着同样的注释：

### 网络代理（改错会连带把大模型调用弄挂）

开启系统代理时需要注意三个变量必须**一起**设置：

```bash
HTTP_PROXY=...
HTTPS_PROXY=...
NO_PROXY=...
```

- `qdrant-client` 经代理访问 Qdrant Cloud 会 TLS 中断（`SSL: UNEXPECTED_EOF_WHILE_READING`）
- 而部分 LLM 服务（如 `api.deepseek.com`）直连会命中拒连的 IP，必须走代理
- ⚠️ `urllib.getproxies()` 的逻辑是「环境变量里有任何代理项就完全忽略注册表」，只写 `NO_PROXY` 会让 `HTTP(S)_PROXY` 一起失效，所有请求变直连

### 嵌入维度必须与向量集合匹配

云端 Qdrant 上的集合是 **384 维**，因此必须使用本地 `all-MiniLM-L6-v2`（384 维）。若换成 dashscope 的 `text-embedding-v3`（1024 维），写入会直接失败。

⚠️ `EMBED_MODEL_TYPE` / `EMBED_MODEL_NAME` 必须一起改：只改 `TYPE` 而留着 `MODEL_NAME=text-embedding-v3`，`LocalTransformerEmbedding` 会构造失败并被静默回退成 dashscope(1024)，维度又不匹配。

### Neo4j 证书

若系统证书库中安装了自签名根证书，Python 3.13 用系统库校验 `neo4j+s://` 会失败（`SSLCertVerificationError: self-signed certificate in certificate chain`），需改用 `neo4j+ssc://`（自签名证书模式）。

### 本地嵌入模型离线

本地嵌入模型缓存后建议设置 `HF_HUB_OFFLINE=1`，禁止联网校验，避免 HuggingFace 超时拖慢启动。

### RL 章节的依赖冲突

`RLAgents/` 那章需要 `trl` / `transformers`。环境里若装了 TensorFlow，会触发 `trl` 导入报错；本机做法是**卸载 TensorFlow**，并把 `torch` 固定为纯 CPU 版（没有 GPU，训练大模型不现实，示例统一用小模型如 `Qwen3-0.6B`）。

### 模型 id 失效 ≠ 代码问题

在 ModelScope 上遇到 `has no provider supported` 说明**模型 id 已经失效**；遇到 `only available to verified accounts`（403）则是**账号没做邮箱验证**。两者都不是调用代码写错了，别在代码里绕。

## 备注

- `Context/my_flask_app/`（待维护的目标代码库）和 `RLAgents/models/` 是**空目录**，Git 不会跟踪空目录，所以克隆下来看不到它们，属于预期行为。
- 仓库不收录 20MB 的教材 PDF（`Memory/*.pdf` 已加入 `.gitignore`），需要的话请自行获取。

## 声明

本仓库为个人学习记录，部分示例代码参考自 Hello-Agents 教程，版权归原作者所有。仅供学习交流使用。
