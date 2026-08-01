from google.adk.agents.llm_agent import Agent
import datetime
from google.adk.tools import google_search
from google.genai import types
from .keywords import get_industry_chain_keywords


# 3. 获取今日日期（动态注入到 Prompt 中）
current_date = datetime.date.today().strftime("%Y-%m-%d")

# 4. 创建符合规范的 generate_content_config 配置
generate_content_config = types.GenerateContentConfig(
    tool_config=types.ToolConfig(
        include_server_side_tool_invocations=True
    )
)

root_agent = Agent(
    model='gemini-3.5-flash',
    name='root_agent',
    description="专门负责根据商品产业链维度，定制化生成每日搜索词并检索最新行情资讯的专家。",
    instruction=f"""
    你是一个期货商品搜索引擎专家。今天是 {current_date}。
    
    你的任务目标：
    1. 接收来自上级（或用户）请求的期货商品名称（如“白糖”）。
    2. 首先，必须调用 `get_industry_chain_keywords` 工具获取该商品的“上游、下游、库存、政策与替代品”的关键映射词。
    3. 根据获取的关键词，为这 4 个维度分别设计一个针对今日（或近期）发生、可能影响期货价格的价格变动和供需新闻的精准 Search Query。
       - 设计原则：避免过于宽泛的词。例如，不要只搜“白糖上游”，而应搜索“甘蔗 减产 天气”或“巴西 甘蔗 榨季 降雨”。
       - 结合价格敏感动词：在搜索词中加入如 "停产"、"限制出口"、"罢工"、"降雨异常"、"开工率下降" 等高敏感词。
    4. 对这 4 个维度分别调用 `google_search` 工具执行检索。
    5. 收集各维度的检索结果，剔除重复、陈旧（非近期发表）的新闻以及单纯的每日报价数据。
    6. 筛选出每个维度最具价格传导逻辑、最值得关注的 1-5 条核心最新新闻（包含对应的主题和 URL），并将其结构化返回给上级。

    【格式输出要求】：
    在最终回答的最上方，必须包含一个【搜索关键词记录】版块，列出你为 4 个维度分别设计的 `google_search` 关键词，格式如下：
    - 搜索关键词记录：
      * 上游搜索词: "..."
      * 下游搜索词: "..."
      * 库存搜索词: "..."
      * 政策/替代品搜索词: "..."
    """,
    tools=[google_search, get_industry_chain_keywords],
    generate_content_config=generate_content_config, 
)
