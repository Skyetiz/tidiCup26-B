# task2/nlp_parser.py
"""
自然语言解析器
"""
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from task2.db_utils import Database

# 指标映射（中文->字段名+表名）
METRIC_MAP = {
    '利润总额': ('total_profit', 'income_sheet'),
    '净利润': ('net_profit', 'income_sheet'),
    '营业收入': ('total_operating_revenue', 'income_sheet'),
    '每股收益': ('eps', 'core_performance_indicators_sheet'),
    '净资产收益率': ('roe', 'core_performance_indicators_sheet'),
    '总资产': ('asset_total_assets', 'balance_sheet'),
    '总负债': ('liability_total_liabilities', 'balance_sheet'),
    '现金及现金等价物': ('asset_cash_and_cash_equivalents', 'balance_sheet'),
    '经营活动现金流': ('operating_cf_net_amount', 'cash_flow_sheet'),
    # 可继续添加
}

class NLPParser:
    def __init__(self, db):
        self.db = db
        self.companies = self._load_companies()

    def _load_companies(self):
        """从数据库加载所有股票简称"""
        sql = "SELECT DISTINCT stock_abbr FROM core_performance_indicators_sheet WHERE stock_abbr IS NOT NULL"
        df = self.db.query(sql)
        if df is not None:
            return df['stock_abbr'].tolist()
        return []
    
    def _build_metric_map(self):
        """构建指标映射"""
        # 基础指标映射
        base_map = {
            '利润总额': ('total_profit', 'income_sheet'),
            '净利润': ('net_profit', 'income_sheet'),
            '营业收入': ('total_operating_revenue', 'income_sheet'),
            '每股收益': ('eps', 'core_performance_indicators_sheet'),
            '净资产收益率': ('roe', 'core_performance_indicators_sheet'),
            '总资产': ('asset_total_assets', 'balance_sheet'),
            '总负债': ('liability_total_liabilities', 'balance_sheet'),
            '现金及现金等价物': ('asset_cash_and_cash_equivalents', 'balance_sheet'),
            '经营活动现金流': ('operating_cf_net_amount', 'cash_flow_sheet'),
        }
        
        # 过滤实际存在的表和字段
        filtered_map = {}
        for cn, (field, table) in base_map.items():
            if self.db.table_exists(table):
                columns = self.db.get_table_columns(table)
                if field in columns:
                    filtered_map[cn] = (field, table)
        return filtered_map

    def parse(self, question, context=None):
        """
        解析自然语言问题，返回结构化的查询信息
        :param question: 用户输入字符串
        :param context: 前一轮对话的上下文（dict），用于继承缺失信息
        :return: dict包含 company, metric, time, agg, table, field
        """
        result = {
            'company': None,
            'metric': None,
            'time': None,      # 可解析的时间，如 '2025Q3' 或 '2023FY' 或 'recent_years'
            'agg': None,       # 聚合方式，如 'top10', 'sum', 'avg' 等
            'field': None,
            'table': None
        }

        # 1. 提取公司
        for comp in self.companies:
            if comp in question:
                result['company'] = comp
                break

        # 2. 提取指标
        for cn, (field, table) in METRIC_MAP.items():
            if cn in question:
                result['metric'] = cn
                result['field'] = field
                result['table'] = table
                break

        # 3. 提取时间
        time_patterns = [
            (r'(\d{4})年(\d{1,2})季度?', lambda m: f"{m.group(1)}Q{m.group(2)}"),
            (r'(\d{4})Q([1-4])', lambda m: f"{m.group(1)}Q{m.group(2)}"),
            (r'(\d{4})年(年报|年度)', lambda m: f"{m.group(1)}FY"),
            (r'(\d{4})FY', lambda m: m.group(0)),
            (r'近几年', lambda m: 'recent_years'),
            (r'最近(\d+)年', lambda m: f"last_{m.group(1)}_years"),
        ]
        for pattern, func in time_patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                result['time'] = func(match)
                break

        # 4. 提取聚合/排序（如top10）
        top_match = re.search(r'top\s*(\d+)', question, re.IGNORECASE)
        if top_match:
            result['agg'] = f"top_{top_match.group(1)}"

        # 继承上下文
        if context:
            if not result['company'] and 'company' in context:
                result['company'] = context['company']
            if not result['metric'] and 'metric' in context:
                result['metric'] = context['metric']
                result['field'] = context['field']
                result['table'] = context['table']
            if not result['time'] and 'time' in context:
                result['time'] = context['time']
            # 其他继承...

        return result

    def is_missing_info(self, parsed):
        """检查是否缺少关键信息，返回缺失的提示"""
        missing = []
        if not parsed['company']:
            missing.append("公司名称")
        if not parsed['metric']:
            missing.append("财务指标")
        if missing:
            return f"请补充以下信息：{', '.join(missing)}。"
        return None