"""
多Agent协作的智能文档助手

使用两个SimpleAgent分工协作：
-Agent1：Github搜索专家
-Agent2：文档生成专家
"""
from hello_agents import SimpleAgent,HelloAgentsLLM
from hello_agents.tools import MCPTool
from dotenv import load_dotenv
load_dotenv()

print("="*70)
print("多Agent协作的智能文档助手")
print("="*70)

# ============================================================
# Agent 1: GitHub搜索专家
# ============================================================
print("\n【步骤1】创建GitHub搜索专家...")

github_searcher = SimpleAgent(
    name = "GitHub搜索专家",
    llm = HelloAgentsLLM(),
    system_prompt = """
你是⼀个GitHub搜索专家。
你的任务是搜索GitHub仓库并返回结果。
请返回清晰、结构化的搜索结果，包括：
- 仓库名称
- 简短描述

保持简洁，不要添加额外的解释。"""
)

#添加Github工具
github_tool = MCPTool(
    name = "gh",
    server_command = ["npx","-y","@modelcontextprotocol/server-github"]
)
github_searcher.add_tool(github_tool)

# ============================================================
# Agent 2: ⽂档⽣成专家
# ============================================================
print("\n【步骤2】创建⽂档⽣成专家...")

document_writer = SimpleAgent(
    name="⽂档⽣成专家",
    llm=HelloAgentsLLM(),
    system_prompt="""你是⼀个⽂档⽣成专家。你的任务是根据提供的信息⽣成结构化的Markdown报告。

报告应该包括：
- 标题
- 简介
- 主要内容（分点列出，包括项⽬名称、描述等）
- 总结请直接输出完整的Markdown格式报告内容，不要使⽤⼯具保存。"""
) 

#添加⽂件系统⼯具
fs_tool = MCPTool(
name="fs",
server_command=["npx", "-y", "@modelcontextprotocol/serverfilesystem", "."]
)
document_writer.add_tool(fs_tool)

# ============================================================
# 执⾏任务
# ============================================================
print("\n" + "="*70)
print("开始执⾏任务...")
print("="*70)

try:
    #步骤一：搜索GitHub仓库
    print("\n【步骤3】搜索GitHub仓库...")
    search_task = "搜索关于'AI agent'的GitHub仓库，返回前5个最相关的结果"

    search_results = github_searcher.run(search_task)

    print("\n搜索结果:")
    print("-"*70)
    print(search_results)
    print("-"*70)

    #步骤二：生成报告
    print("\n【步骤4】Agent2 生成报告...")
    report_task = f"""根据以下GitHub搜索结果，⽣成⼀份Markdown格式的研究报告：
{search_results}

报告要求：
1. 标题：# AI Agent框架研究报告
2. 简介：说明这是关于AI Agent的GitHub项⽬调研
3. 主要发现：列出找到的项⽬及其特点（包括名称、描述等）
4. 总结：总结这些项⽬的共同特点

请直接输出完整的Markdown格式报告。
"""
    report_content = document_writer.run(report_task)
    print("\n报告内容:")
    print("=" * 70)
    print(report_content)
    print("=" * 70)

    #步骤三：保存报告
    print("\n【步骤5】Agent2 保存报告...")
    import os
    try:
        with open("report.md","w",encoding="utf-8") as f:
            f.write(report_content)
        print("报告已保存为report.md")

        #验证文件
        file_size = os.path.getsize("report.md")
        print(f"报告文件大小: {file_size}字节")
    except Exception as e:
        print("保存报告失败:", e)

    print("\n" + "="*70)
    print("任务完成！")
    print("="*70)

except Exception as e:
    print("任务执行失败:", e)
    import traceback
    traceback.print_exc()#打印详细的异常信息，包括错误位置、错误类型等。

