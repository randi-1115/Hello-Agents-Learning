# Hello-Agents 学习实践

跟随 [Hello-Agents](https://github.com/datawhalechina/hello-agents) 教程学习 AI Agent 开发的工作目录，记录从 LLM 封装、记忆系统到 RAG 检索的实践代码与踩坑经验。

## 目录结构

```
hello-agents/
├── helloAgents/          # 早期实验：LLM 封装与基础 Agent 实现
│   ├── HelloAgentsLLM.py # LLM 客户端封装
│   ├── my_llm.py         # 自定义 LLM 调用
│   ├── my_main.py        # 主入口实验
│   ├── Memory.py         # 记忆模块初探
│   └── Plan and Solve.py # Plan-and-Solve 范式实践
│
├── Memory/               # 记忆系统 + RAG 检索（主要工作区）
│   ├── first.py          # 示例 01：MemoryTool 基础操作（可运行）
│   ├── test.py           # 测试脚本
│   ├── second.py         # WIP：智能分块 + 混合检索（MQE / HyDE）
│   ├── Q & A.py          # WIP：PDF 文档问答助手
│   ├── knowledge_base/   # 知识库文档
│   └── .env.example      # 环境变量模板（含踩坑注释）
│
└── PyAgengts/            # 最早期的 Agent 概念验证
```

> `second.py` 和 `Q & A.py` 是跟随教程边学边写的半成品，依赖的函数尚未实现完整，暂不可直接运行。保留是为了记录学习过程。

## 环境要求

- Python 3.10+（必需）
- 依赖：`hello-agents` 框架、`python-dotenv`、`qdrant-client`、`neo4j`、`sentence-transformers`

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

## 声明

本仓库为个人学习记录，部分示例代码参考自 Hello-Agents 教程，版权归原作者所有。仅供学习交流使用。
