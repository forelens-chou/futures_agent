from google.adk.agents.llm_agent import Agent
import datetime
from google.adk.tools import google_search
from google.genai import types
from google.adk.tools.agent_tool import AgentTool
from .keywords import get_industry_chain_keywords


# 配置配置项
generate_content_config = types.GenerateContentConfig(
    tool_config=types.ToolConfig(
        include_server_side_tool_invocations=True
    )
)

def get_current_date_str() -> str:
    """动态获取今日日期，避免模块加载时的静态卡死"""
    return datetime.date.today().strftime("%Y-%m-%d")

# ==========================================
# 1. [Context Stack 拆分] 子 Agent：专门负责构建精准 Search Queries
# ==========================================
query_planner_agent = Agent(
    model='gemini-3.5-flash',
    name='query_planner_agent',
    description="专门负责根据产业链映射词，设计中英文搜索词（Query）的专家。",
    instruction="""
    你是一个搜索词优化专家。
    你的唯一任务：接收商品名称和 `get_industry_chain_keywords` 查到的映射词，为以下 4 个维度生成最精准的 google_search 查询词：
    1. 上游 (Upstream)
    2. 下游 (Downstream)
    3. 库存 (Inventory)
    4. 政策/替代品 (Policy/Substitutes)

    要求：
    - 国内维度使用精准中文；国际维度必须用英文（并加入 drought, rain delay, export restriction, crush halt 等行情高敏感词）。
    - 针对每个维度只生成 1 个最精炼的搜索引擎 Query 字符串。
    """,
    tools=[get_industry_chain_keywords],
    generate_content_config=generate_content_config
)

# ==========================================
# 2. [Context Stack 拆分] 子 Agent：专门负责执行搜索、清洗与翻译摘要
# ==========================================
researcher_agent = Agent(
    model='gemini-3.5-flash',
    name='researcher_agent',
    description="专门执行 Google Search 并过滤、翻译、总结最新行情资讯的专家。",
    instruction="""
    你是一个期货研报分析师。
    你的任务：
    1. 使用 `google_search` 工具执行传入的搜索词。
    2. 过滤掉陈旧新闻和纯每日报价数据。
    3. 将检索到的英文国际资讯**翻译并精炼为中文**。
    4. 提炼出最具价格传导逻辑的 1-3 条核心最新新闻（包含主题、逻辑摘要和 URL）。
    【原则】：
    - 绝对保持客观！只提供事实（如产量、天气、库存数据、政策条文），**严禁加入任何主观行情预测或观点**。
    """,
    tools=[google_search],
    generate_content_config=generate_content_config
)

# ==========================================
# 3. [Context Stack 顶层] Root Agent：工作流编排与最终 Output Shaping
# ==========================================
# 注意：在 ADK 中，可以将 Agent 实例直接作为子 Agent/Tools 挂载给 Root Agent
root_agent = Agent(
    model='gemini-3.5-flash',
    name='root_agent',
    description="期货商品产业链情报收集专家总指挥。",
    instruction=f"""
    你是期货商品产业链资讯收集总指挥。今天的日期是：{get_current_date_str()}。

    你必须严格按照以下 4 个步骤连续执行，不得中途停止：

    Step 1: 调用 `query_planner_agent` 工具，根据用户输入的商品生成 4 个维度的搜索词。
    Step 2: 调用 `researcher_agent` 工具，将 Step 1 生成的搜索词传给它，获取过滤翻译后的客观事实摘要。
    Step 3: **核心分析（必须亲自执行）**：仔细阅读 Step 2 返回的事实，运用你的期货交易逻辑进行推演，得出“当前市场判断”以及“后市预测与触发条件”。
    Step 4: 汇总 Step 1、Step 2 和 Step 3 的所有内容，按照【最终输出格式要求】生成完整报告。

    【最终输出格式要求】：
    必须严格按以下格式展示，**不得缺失任何板块**：

    ## 1. 搜索关键词记录
    - 上游搜索词: "..."
    - 下游搜索词: "..."
    - 库存搜索词: "..."
    - 政策/替代品搜索词: "..."

    ## 2. 核心产业链资讯汇总
    ### [上游维度]
    - **新闻标题/主题**: ...
      * 核心逻辑: ...
      * 来源链接: ...
    ### [下游维度]
    ...
    ### [库存维度]
    ...
    ### [政策/替代品维度]
    ...

    ## 3. 当前市场判断与后市分析
    - **当前主导逻辑**：[结合 Step 2 的事实，说明目前市场是由供给端、需求端还是政策驱动]
    - **多空力量对比**：[利多因素 vs 利空因素分析]

    ## 4. 后市预测与触发条件（Scenario Analysis）
    - **基准预测（概率较大）**：[对未来价格走势的区间或方向判断]
    - **推演与关键触发条件**：
      * 触发条件 A(如:若巴西中南部降雨持续超预期导致榨季提前结束） -> **推演结果**：供给趋紧，价格突破高点。
      * 触发条件 B(如:若国内消费不及预期，库存累积） -> **推演结果**：上行受阻，转为震荡回调。
    """,
    # 注意：这里使用 AgentTool 将子 Agent 转为常规工具，而不是放在 sub_agents 中！
    tools=[
        AgentTool(agent=query_planner_agent),
        AgentTool(agent=researcher_agent)
    ],
    generate_content_config=generate_content_config,
)
