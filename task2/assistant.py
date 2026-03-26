# task2/assistant.py (修复版 - 处理重复数据)
"""
智能助手主类 - 处理重复数据
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from task2.db_utils import Database
from task2.nlp_parser import NLPParser
from task2.sql_builder import SQLBuilder
from task2.visualizer import Visualizer

class SmartAssistant:
    def __init__(self):
        self.db = Database()
        self.parser = NLPParser(self.db)
        self.sql_builder = SQLBuilder(self.db)
        self.visualizer = Visualizer()
        self.context = {}
        self.conversation = []
        self.conversation_sqls = []
    
    def ask(self, question, question_id=None, seq_no=1):
        """处理单轮问题"""
        try:
            # 解析问题
            parsed = self.parser.parse(question, self.context)
            
            # 检查缺失信息
            missing = self.parser.is_missing_info(parsed)
            if missing:
                content = missing
                self.context = parsed
                return {"content": content, "sql": None}
            
            # 构建SQL
            sql = self.sql_builder.build_query(parsed)
            if not sql:
                return {"content": "无法生成查询语句，请检查问题", "sql": None}
            
            print(f"📝 生成SQL: {sql}")
            
            # 执行查询
            df = self.db.query(sql)
            if df is None or df.empty:
                return {"content": "未找到相关数据，请检查查询条件", "sql": sql}
            
            # 去重：按报告期去重，保留第一条
            if 'report_period' in df.columns:
                df = df.drop_duplicates(subset=['report_period'], keep='first')
                df = df.sort_values('report_period')
            
            print(f"📊 查询结果: {len(df)} 行")
            print(df.to_string())
            
            # 更新上下文
            self.context = parsed
            
            # 根据问题类型决定图表类型
            chart_type = self._determine_chart_type(question, df)
            
            # 格式化输出
            content, images = self._format_output(df, parsed, question_id, seq_no, chart_type)
            
            return {"content": content, "image": images, "sql": sql}
            
        except Exception as e:
            print(f"处理问题出错: {e}")
            import traceback
            traceback.print_exc()
            return {"content": f"处理出错: {str(e)}", "sql": None}
    
    def _determine_chart_type(self, question, df):
        """根据问题内容和数据量决定图表类型"""
        # 如果是趋势类问题，用折线图
        if '趋势' in question or '变化' in question or '近几年' in question:
            return 'line'
        
        # 如果数据点较多，用折线图
        if len(df) > 10:
            return 'line'
        
        # 默认用柱状图
        return 'bar'
    
    def _format_output(self, df, parsed, question_id, seq_no, chart_type='auto'):
        """格式化输出结果"""
        try:
            metric = parsed['metric']
            company = parsed['company']
            
            if len(df) == 1:
                # 单一数值
                value = df.iloc[0, -1]
                period = df.iloc[0, 0] if 'report_period' in df.columns else ""
                content = f"{company}{period}的{metric}为{value:.2f}万元。"
                return content, None
            else:
                # 时间序列数据 - 生成图表
                # 确保数据按时间排序
                if 'report_period' in df.columns:
                    df = df.sort_values('report_period')
                
                img_path = self.visualizer.generate_chart(df, question_id, seq_no, chart_type)
                
                # 生成文字分析
                values = df.iloc[:, -1]
                periods = df['report_period'].tolist() if 'report_period' in df.columns else list(range(len(df)))
                
                # 计算趋势（使用第一个和最后一个非零值）
                non_zero_indices = [i for i, v in enumerate(values) if v != 0]
                if len(non_zero_indices) >= 2:
                    first_idx = non_zero_indices[0]
                    last_idx = non_zero_indices[-1]
                    first_val = values.iloc[first_idx]
                    last_val = values.iloc[last_idx]
                    first_period = periods[first_idx]
                    last_period = periods[last_idx]
                    
                    if last_val > first_val:
                        trend = "上升"
                        change_pct = ((last_val - first_val) / first_val) * 100 if first_val != 0 else 0
                    else:
                        trend = "下降"
                        change_pct = ((last_val - first_val) / first_val) * 100 if first_val != 0 else 0
                    
                    content = f"{company}的{metric}在报告期内呈{trend}趋势"
                    if change_pct != 0:
                        content += f"（{change_pct:.1f}%）"
                    content += f"。\n最新值（{last_period}）为{last_val:.2f}万元，"
                    content += f"较{first_period}的{first_val:.2f}万元{trend}了{abs(change_pct):.1f}%。\n\n"
                else:
                    content = f"{company}的{metric}数据：\n"
                
                # 添加详细数据表格
                content += "详细数据如下：\n"
                for period, val in zip(periods, values):
                    if val != 0:  # 只显示非零值
                        content += f"  • {period}: {val:.2f}万元\n"
                    else:
                        content += f"  • {period}: 数据缺失\n"
                
                return content, [str(img_path)] if img_path else None
                
        except Exception as e:
            print(f"格式化输出出错: {e}")
            import traceback
            traceback.print_exc()
            return "数据查询成功，但格式化输出出错", None
    
    def start_conversation(self, question_list, question_id):
        """处理多轮对话"""
        self.context = {}
        self.conversation = []
        self.conversation_sqls = []
        
        for idx, q_item in enumerate(question_list, 1):
            q_text = q_item["Q"]
            print(f"  处理第{idx}轮问题: {q_text}")
            answer = self.ask(q_text, question_id, idx)
            
            a_dict = {"content": answer["content"]}
            if "image" in answer and answer["image"]:
                a_dict["image"] = answer["image"]
            
            self.conversation.append({"Q": q_text, "A": a_dict})
            self.conversation_sqls.append(answer.get("sql", ""))
        
        return self.conversation
    
    def get_conversation_sqls(self):
        """获取多轮对话的SQL语句列表"""
        return self.conversation_sqls
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()