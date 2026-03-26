# task2/visualizer.py (修复版)
"""
可视化工具 - 修复图表生成问题
"""
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from task2.config import RESULT_DIR

# 设置中文字体，避免乱码
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class Visualizer:
    def __init__(self):
        self.output_dir = RESULT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 图片保存目录: {self.output_dir}")
    
    def generate_chart(self, data, question_id, seq_no, chart_type='auto'):
        """
        生成图表
        :param data: DataFrame，包含 report_period 和数值列
        :param question_id: 问题编号，如 'B1002'
        :param seq_no: 顺序号，如 1
        :param chart_type: 'line', 'bar', 'auto'
        :return: 图片保存路径
        """
        if data is None or data.empty:
            print("⚠️ 没有数据，无法生成图表")
            return None
        
        print(f"📊 生成图表 - 数据形状: {data.shape}")
        print(f"📊 数据列: {data.columns.tolist()}")
        
        # 准备数据
        if 'report_period' in data.columns:
            x_labels = data['report_period'].tolist()
        else:
            x_labels = list(range(len(data)))
        
        # 获取数值列（排除报告期列）
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            print("⚠️ 没有数值列，无法生成图表")
            return None
        
        # 取第一个数值列
        y_col = numeric_cols[0]
        y_values = data[y_col].values
        
        print(f"📊 X轴: {x_labels}")
        print(f"📊 Y轴: {y_values}")
        
        # 确定图表类型
        if chart_type == 'auto':
            if len(data) <= 12:
                chart_type = 'bar'  # 数据点少用柱状图
            else:
                chart_type = 'line'  # 数据点多用折线图
        
        print(f"📊 生成{chart_type}图")
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if chart_type == 'line':
            # 折线图
            ax.plot(range(len(x_labels)), y_values, marker='o', linewidth=2, markersize=6, color='blue')
            ax.set_xticks(range(len(x_labels)))
            ax.set_xticklabels(x_labels, rotation=45, ha='right')
            ax.set_title(f'{y_col} 趋势图', fontsize=14, fontweight='bold')
            ax.set_xlabel('报告期', fontsize=12)
            ax.set_ylabel(y_col, fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # 添加数值标签
            for i, v in enumerate(y_values):
                ax.text(i, v, f'{v:.0f}', ha='center', va='bottom', fontsize=9)
                
        elif chart_type == 'bar':
            # 柱状图
            bars = ax.bar(range(len(x_labels)), y_values, color='steelblue', alpha=0.8)
            ax.set_xticks(range(len(x_labels)))
            ax.set_xticklabels(x_labels, rotation=45, ha='right')
            ax.set_title(f'{y_col} 对比图', fontsize=14, fontweight='bold')
            ax.set_xlabel('报告期', fontsize=12)
            ax.set_ylabel(y_col, fontsize=12)
            ax.grid(True, alpha=0.3, axis='y')
            
            # 添加数值标签
            for bar, v in zip(bars, y_values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{v:.0f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # 保存图片
        filename = f"{question_id}_{seq_no}.jpg"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✅ 图表已保存: {filepath}")
        return str(filepath)