# task2/visualizer.py
"""
可视化工具
"""
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from task2.config import RESULT_DIR

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class Visualizer:
    def __init__(self):
        self.output_dir = RESULT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_chart(self, data, question_id, seq_no, chart_type='auto'):
        """生成图表"""
        if data is None or data.empty:
            return None
        
        # 确定图表类型
        if chart_type == 'auto':
            if len(data) == 1:
                return None
            elif len(data) <= 10:
                chart_type = 'bar'
            else:
                chart_type = 'line'
        
        # 准备数据
        if 'report_period' in data.columns:
            x = data['report_period']
        else:
            x = data.index
        
        # 获取数值列
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            return None
        
        y_col = numeric_cols[0]
        y = data[y_col]
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == 'line':
            ax.plot(x, y, marker='o', linewidth=2)
            ax.set_title(f'{y_col} 趋势图')
            ax.set_xlabel('报告期')
            ax.set_ylabel(y_col)
            plt.xticks(rotation=45)
        elif chart_type == 'bar':
            ax.bar(x, y)
            ax.set_title(f'{y_col} 对比图')
            ax.set_xlabel('报告期')
            ax.set_ylabel(y_col)
            plt.xticks(rotation=45)
        elif chart_type == 'pie':
            if len(data) > 0:
                ax.pie(y, labels=x, autopct='%1.1f%%')
                ax.set_title(f'{y_col} 构成图')
        
        plt.tight_layout()
        
        # 保存图片
        filename = f"{question_id}_{seq_no}.jpg"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return str(filepath)