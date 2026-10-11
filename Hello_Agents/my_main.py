from dotenv import load_dotenv
from my_llm import MyLLM

# 加载环境变量
load_dotenv()

#实例化我们要重写的客户端，并指定provider
llm = MyLLM(provider="modelscope")

#准备消息
messages = [{"role": "user", "content": "你好,请介绍一下自己"}]

response_stream = llm.think(messages)

print("ModelScope Response:")
for chunk in response_stream:
    # chunk在my_llm库中已经打印过⼀遍，这⾥只需要pass即可
    # print(chunk, end="", flush=True)
    pass