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
    3. 设计精细化搜索词（Search Query）：
       - **国内维度**（如国内种植生产、国内库存等）：使用精准的**中文**关键词构建 Query。
       - **国际维度**（如“国际种植生产”等英文关键词维度）：必须使用**英文**构建 `google_search` 检索词（例如 `"Brazil sugarcane crush rain delay"` 或 `"India sugar export quota"`），以获取彭博、路透、Czarnikow 等全球权威机构的一手资讯。
       - 结合价格敏感动词：英文加入如 "drought", "rain delay", "export ban", "yield loss", "crush halt" 等高敏感词。
    4. 对这 4 个维度分别调用 `google_search` 工具执行检索。
    5. 收集各维度的检索结果，剔除重复、陈旧（非近期发表）的新闻以及单纯的每日报价数据。
    6. 将搜集到的英文国际资讯**翻译并精炼为中文** ，筛选出每个维度最具价格传导逻辑、最值得关注的 1-5 条核心最新新闻（包含对应的主题和 URL），并将其结构化返回给上级。

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
