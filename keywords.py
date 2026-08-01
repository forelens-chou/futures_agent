# 1. 产业链映射字典（可扩展为数据库查询）
COMMODITY_MAPPING = {
    "白糖": {
        "upstream": ["甘蔗", "甜菜", "巴西天气", "印度减产", "榨季"],
        "downstream": ["食品加工", "饮料行业", "淀粉糖", "代糖价格"],
        "inventory": ["国内糖厂库存", "中糖协库存", "交易所仓单", "进口糖数量"],
        "policy_substitutes": ["关税政策", "国家储备糖投放", "高果糖浆"]
    },
    "纸浆": {
        "upstream": ["针叶浆", "阔叶浆", "木片成本", "芬兰/加拿大纸浆出口"],
        "downstream": ["双胶纸", "铜版纸", "白卡纸", "生活用纸需求"],
        "inventory": ["青岛/常熟港口库存", "浆厂库存", "交易所仓单"],
        "policy_substitutes": ["禁废令", "限塑令", "废纸回收率", "竹浆替代"]
    },
    "烧碱": {
        "upstream": ["原盐价格", "原煤价格", "电价/电力限制", "氯碱装置开工率"],
        "downstream": ["氧化铝产量", "粘胶短纤", "造纸印染", "印染开工率"],
        "inventory": ["液碱企业库存", "片碱库存", "周度库存波动"],
        "policy_substitutes": ["环保督察", "能效双控限制"]
    },
    "纯碱": {
        "upstream": ["原盐", "合成氨", "动力煤", "碱厂检修"],
        "downstream": ["平板玻璃开工", "光伏玻璃装机", "碳酸锂生产"],
        "inventory": ["纯碱企业周度库存", "碱厂仓单", "社会库存"],
        "policy_substitutes": ["保交楼政策", "光伏发电装机政策", "产能新增置换"]
    }
}

# 2. 定义产业链查询 Tool
def get_industry_chain_keywords(commodity: str) -> dict:
    """
    根据输入的期货商品（如：白糖、纸浆、烧碱、纯碱），返回其上下游、库存、政策四个维度的专业研究关键词。
    """
    return COMMODITY_MAPPING.get(
        commodity, 
        {
            "upstream": [commodity + " 生产原材料", commodity + " 生产成本"],
            "downstream": [commodity + " 消费", commodity + " 下游"],
            "inventory": [commodity + " 库存", commodity + " 仓单"],
            "policy_substitutes": [commodity + " 政策", commodity + " 替代品"]
        }
    )