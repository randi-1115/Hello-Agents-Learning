
from hello_agents.tools import MCPTool
#注意：MCPTool 主要⽤于 Stdio 和 Memory 传输
# 对于 HTTP/SSE 等远程传输，建议使⽤底层的 MCPClient
#from hello_agents.tools import MCPClient
import asyncio
from hello_agents import SimpleAgent,HelloAgentsLLM
from dotenv import load_dotenv
load_dotenv()

agent = SimpleAgent(name="助手",llm=HelloAgentsLLM())

#无需任何配置，自动使用内置演示服务器
mcp_tool = MCPTool(name="calculator")
agent.add_tool(mcp_tool)
#✅ MCP⼯具 'calculator' 已展开为 6 个独⽴⼯具

# 智能体可以直接使⽤展开后的⼯具
response = agent.run("计算25乘以16")
print(response)

"""
async def test_sse_transport():
    #连接到SSE MCP 服务器
    client = MCPClient(
        "http://localhost:8080/sse",
        transport_type = "sse"
    )

    async with client:
        #SSE 特别适合流式处理
        result = await client.call_tool("stream_process",{
            "input":"大量数据处理请求",
            "stream":True
        })
        print(result)
  # 注意：需要⽀持 SSE 的 MCP 服务器
# asyncio.run(test_sse_transport())      
"""

"""
async def  test_http_transport():
    #连接到远程HTTP MCP 服务器
    client = MCPClient("http://api.example.com/mcp")

    async with client:
        #获取服务器信息
        tools = await client.list_tools()
        print(f"远程服务器工具：{len(tools)}个")

        #调⽤远程工具
        result = await client.call_tool("process_data",{
            "data":"Hello,World!",
            "operation":"uppercase"
        })
        print(f"远程处理结果: {result}")
# 注意：需要实际的 HTTP MCP 服务器
        #asyncio.run(test_http_transport())

"""


"""
#使用内置演示服务器（Memory传输）
mcp_tool = MCPTool()

#列出可用工具
result = mcp_tool.run({"action":"list_tools"})
print(result)

#调⽤工具
result = mcp_tool.run({
    "action":"call_tool",
    "tool_name":"add",
    "arguments":{"a":1,"b":2}
})

print(result)
"""


"""
#创建GitHub MCP工具
github_tool = MCPTool(
    server_command=["npx","-y","@modelcontextprotocol/server-github"]
)

#1.列出可用工具
print("可用工具: ")
result = github_tool.run({"action":"list_tools"})
print(result)

#2.搜索仓库
print("搜索仓库: ")
result = github_tool.run({
    "action":"call_tool",
    "tool_name":"search_repositories",
    "arguments":{
        "query": "AI agents language:python",
        "page": 1,
        "perPage": 3
    }#搜索参数
})
print(result)
"""


"""
async def connect_to_server():
    #方式1：连接到社区提供的文件系统服务器
    # npx会⾃动下载并运⾏@modelcontextprotocol/server-filesystem包
    client = MCPClient([
        "npx","-y",
        "@modelcontextprotocol/server-filesystem",
        "."#指定根目录
    ])

    #使用async with确保连接正确关闭
    async with client:
        #在这里使用client
        tools = await client.get_tools()
        print(f"可⽤⼯具: {[t['name'] for t in tools]}")

    #方式2：连接到自定义的Python MCP服务器
    client = MCPClient([
        "python",
        "mcp_server.py"
    ])
    async with client:
        #在这里使用client
        pass

#运行异步函数
asyncio.run(connect_to_server())
"""
