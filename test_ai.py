import os
from openai import OpenAI
print("⏳ 正在呼叫 DeepSeek 大模型，请稍候...")
api_key = os.environ.get("DEEPSEEK_API_KEY", "")
# 初始化客户端
client = OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com"
)

try:
    # 发送一个最基础的对话
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个智慧园区监控系统的AI助手。"},
            {"role": "user", "content": "如果一辆车牌号为京A88888的车进入了望京科技园，请用专业且简短的语气生成一条告警通知。"}
        ]
    )
    print("\n✅ 测试成功！AI 的回复是：")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"\n❌ 测试失败，报错信息：{e}")
