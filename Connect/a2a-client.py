from hello_agents.protocols import A2AClient

#创建客户端连接到研究员Agent
client = A2AClient("http://localhost:5000")

#发送研究请求
response = client.execute_skill("research","research AI在医疗领域的应用")
print(f"收到响应：{response.get('result')}")

# 输出：
# 收到响应：{'topic': 'AI在医疗领域的应⽤', 'findings': '关于AI在医疗领域的应⽤的研究结果...', 'sources': ['来源1', '来源2', '来源3']}
