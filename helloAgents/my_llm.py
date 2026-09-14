import os
from typing import Optional
from openai import OpenAI
from hello_agents import HelloAgentsLLM

class MyLLM(HelloAgentsLLM):
    def __init__(
            self,
            model: Optional[str] = None,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            provider: Optional[str] = "auto",
            **kwargs
    ):
        if provider == "modelscope":
            print("正在使⽤⾃定义的 ModelScope Provider")
            self.provider = "modelscope"

            self.api_key = api_key or os.getenv("MODELSCOPE_API_KEY")
            self.base_url = base_url or "https://apiinference.modelscope.cn/v1/"

            if not self.api_key:
                raise ValueError("ModelScope API key not found.Please set MODELSCOPE_API_KEY environment variable .")

            self.model = model or os.getenv("LLM_MODEL_ID") or "Qwen/Qwen2.5-VL-72B-Instruct"
            self.temperature = kwargs.get("temperature", 0.7)
            self.max_tokens = kwargs.get('max_tokens')
            self.timeout = kwargs.get('timeout',60)

            self._client = OpenAI(api_key=self.api_key,base_url=self.base_url,timeout=self.timeout)

        else:
            super().__init__(model=model, apiKey=api_key, baseUrl=base_url, provider=provider, **kwargs)
            

    """
    一个自定义的LLM客户端, 通过继承增加了对ModelScope的支持
    """
    pass

