from hello_agents.tools import RLTrainingTool

#创建训练工具
rl_tool = RLTrainingTool()

#SFT训练
result = rl_tool.run({
    #训练配置
    "action":"train",
    "algorithm":"sft",

    #模型配置
    "model_name":"Qwen/Qwen3-0.6B",
    "output_dir":"./models/sft_model",

    #数据配置
    "max_samples":100,#使用100个样本快速测试
    "batch_size":4,#批次大小
    "learnSing_rate":5e-5,#学习率

    #LoRA配置
    "use_lora":True,#使用LoRA
    "lora_rank":8,#LoRA秩值
    "lora_alpha":16,#LoRA alpha参数
})
print("\n✓ 训练完成!")
print("result =", result)
print("result类型 =", type(result))
