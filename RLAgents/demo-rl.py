from hello_agents.tools import RLTrainingTool
from datasets import Dataset
from hello_agents.rl import format_math_dataset
from typing import List
import re
import json

#1.准备原始数据
custom_data = [
    {
        "question":"What is 2+2?",
        "answer":"2+2. ### 4"
    },
    {
        "question":"what is 5*3",
        "answer":"5*3=15. #### 15"
    },
    {
        "question":"What is 10+7?",
        "answer":"10+7=17. #### 17"
    }
]
#2.转换为Dataset对象
raw_dataset = Dataset.from_list(custom_data)

#3.转换为SFT格式
sft_dataset = format_math_dataset(
    dataset=raw_dataset,
    format_type = "sft",
    model_name="Qwen/Qwen3-0.6B"
)
print(f"SFT数据集：{len(sft_dataset)}个样本")
print(f"字段:{sft_dataset.column_names}")

#4.转换为RL格式
rl_dataset = format_math_dataset(
    dataset=raw_dataset,
    format_type = "rl",
    model_name="Qwen/Qwen3-0.6B"
)
print(f"RL数据集：{len(rl_dataset)}个样本")
print(f"字段:{rl_dataset.column_names}")

rl_tool = RLTrainingTool()

#SFT训练
result = rl_tool.run({
    "action":"train",
    "algorithm":"sft",#使用SFT算法
    "model_name":"Qwen/Qwen3-0.6B",#模型名称
    "output_dir":"./models/custom_sft",#输出目录
    "num_epochs":3,#训练轮数
    "batch_size":4,#批量大小
    "use_lora":True,#是否使用LORA,LORA是低秩参数共享技术,用于减少模型参数量
    "custom_dataset":sft_dataset,#自定义数据集
})

#GRPO训练
result = rl_tool.run({
    "action":"train",
    "algorithm":"grpo",#使用GRPO算法
    "model_name":"Qwen/Qwen3-0.6B",#模型名称
    "output_dir":"./models/custom_grpo",#输出目录
    "num_epochs":2,#训练轮数
    "batch_size":2,#批量大小
    "use_lora":True,#是否使用LORA,LORA是低秩参数共享技术,用于减少模型参数量
    "custom_dataset":rl_dataset,#自定义数据集
})

#1.注册数据集
rl_tool.register_dataset("my_math_dataset", rl_dataset)

#2.使用注册的数据集
result = rl_tool.run({
    "action":"train",
    "algorithm":"grpo",#使用GRPO算法
    "dataset":"my_math_dataset",#使⽤注册的数据集名称
    "output_dir":"./models/custom_grpo",#输出目录
    "num_epochs":2,#训练轮数
    "use_lora":True,#是否使用LORA,LORA是低秩参数共享技术,用于减少模型参数量
   })

def custom_reward_function(
        completions:List[str],
        **kwargs
) -> List[float]:
    """
    自定义奖励函数

    Args：
        completions: 模型生成的完成文本列表
        **kwargs:其他参数，通常包括：
           -ground_truth:正确答案列表
           -其他数据集字段

    Returns:
        奖励值列表（每个值在0.0到1.0之间）
    """
    ground_truths = kwargs.get("ground_truth", [])
    rewards = []

    for completion,truth in zip(completions,ground_truths):
        reward = 0.0

        #提取答案
        numbers = re.findall(r'-?\d+\.?\d*',completion)
        if numbers:
            try:
                pred = float(numbers[-1])
                truth_num = float(truth)
                error = abs(pred - truth_num)

                #根据误差给予不同奖励
                if error < 0.01:
                    reward = 1.0#完全正确
                elif error < 1.0:
                    reward = 0.8 #非常接近
                elif error < 5.0:
                    reward = 0.5 #接近

                #额外奖励：鼓励展示推理步骤
                if "step" in completion.lower() or "=" in completion:
                    reward += 0.0
            except ValueError:
                reward = 0.0

        rewards.append(min(reward,1.0)) #限制最大值为1.0

    return rewards
"""
#创建准确率奖励函数
reward_result = rl_tool.run({
    "action":"create_reward",
    "reward_function":"accuracy"#准确率奖励函数
})
reward_data = json.loads(reward_result)#将奖励函数转换为json格式

print(f"奖励类型: {reward_data['reward_type']}")
print(f"描述: {reward_data['description']}")

# 注意: RLTrainingTool的create_reward操作返回的是配置信息,
# 实际的奖励函数会在训练时⾃动创建和使⽤

reward_result=rl_tool.run({
    "action":"create_reward",
    "reward_type":"length_penalty",
    "max_length":1024,#最大输出长度
    "penalty_weight":0.001#长度惩罚权重
})
reward_data = json.loads(reward_result)
print(f"奖励类型: {reward_data['reward_type']}")
print(f"描述: {reward_data['description']}")
print(f"最大长度: {reward_data['max_length']}")
print(f"长度惩罚权重: {reward_data['penalty_weight']}")

#创建步骤奖励函数
reward_result=rl_tool.run({
    "action":"create_reward",
    "reward_type":"step",
    "step_bonus":0.1#步骤奖励权重
})
reward_data = json.loads(reward_result)
print(f"奖励类型: {reward_data['reward_type']}")
print(f"描述: {reward_data['description']}")
print(f"步骤奖励: {reward_data['step_bonus']}")
"""
