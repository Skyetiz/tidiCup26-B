# task2/main.py (修改版 - 保存SQL到输出)
"""
任务二主程序入口
"""
import pandas as pd
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from task2.assistant import SmartAssistant
from task2.config import QUESTION_FILES, RESULT_DIR

def load_questions(file_path):
    """加载问题文件"""
    try:
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            return []
        
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"✅ 成功读取文件: {file_path.name}, 共 {len(df)} 个问题")
        
        questions = []
        for idx, row in df.iterrows():
            try:
                # 解析问题JSON
                q_json = json.loads(row['问题'])
                questions.append({
                    '编号': row['编号'],
                    '问题类型': row['问题类型'],
                    '问题': q_json
                })
                print(f"  📋 加载问题: {row['编号']} - {row['问题类型']}")
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON解析错误: {row['编号']}, 错误: {e}")
                print(f"   原始数据: {row['问题']}")
                continue
            except Exception as e:
                print(f"⚠️ 处理问题 {row['编号']} 失败: {e}")
                continue
        
        return questions
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def format_sql_for_excel(sql_list):
    """格式化SQL语句用于Excel显示"""
    if not sql_list:
        return ""
    
    # 如果是多轮对话，将多个SQL用分号连接
    sqls = [sql for sql in sql_list if sql]
    if len(sqls) == 1:
        return sqls[0]
    elif len(sqls) > 1:
        return ";\n".join(sqls)
    else:
        return ""

def save_result(results, output_file):
    """保存结果"""
    try:
        df = pd.DataFrame(results)
        cols = ['编号', '问题', 'SQL查询语句', '图形格式', '回答']
        # 确保列存在
        for col in cols:
            if col not in df.columns:
                df[col] = ''
        df = df[cols]
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✅ 结果已保存至: {output_file}")
        
        # 打印前几个结果供检查
        print("\n📊 结果预览:")
        for idx, row in df.head(2).iterrows():
            print(f"  问题编号: {row['编号']}")
            print(f"  SQL: {row['SQL查询语句'][:100]}...")
            print(f"  回答: {row['回答'][:100]}...")
            print()
        
        return True
    except Exception as e:
        print(f"❌ 保存结果失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("🎯 任务二：智能问数助手")
    print("=" * 60)
    
    # 初始化助手
    assistant = None
    try:
        assistant = SmartAssistant()
        print("✅ 智能助手初始化成功")
    except Exception as e:
        print(f"❌ 初始化助手失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 加载问题
    questions = load_questions(QUESTION_FILES['task2'])
    if not questions:
        print("❌ 没有找到有效的问题，程序退出")
        assistant.close()
        return
    
    # 处理问题
    results = []
    for q in questions:
        print(f"\n📝 处理问题: {q['编号']} ({q['问题类型']})")
        try:
            # 获取多轮回答
            conversation = assistant.start_conversation(q['问题'], q['编号'])
            print(f"   ✅ 生成回答，共 {len(conversation)} 轮")
            
            # 获取SQL语句
            sql_list = assistant.get_conversation_sqls()
            sql_text = format_sql_for_excel(sql_list)
            
            # 显示回答内容
            for i, turn in enumerate(conversation, 1):
                print(f"      轮次{i}: {turn['Q']}")
                print(f"        回答: {turn['A']['content'][:100]}...")
                if i <= len(sql_list) and sql_list[i-1]:
                    print(f"        SQL: {sql_list[i-1]}")
            
            # 判断图形格式
            chart_type = "无"
            if conversation and len(conversation) > 0:
                last_answer = conversation[-1]["A"]
                if "image" in last_answer and last_answer["image"]:
                    chart_type = "折线图"
            
            # 回答JSON
            answer_json = json.dumps(conversation, ensure_ascii=False)
            
            results.append({
                '编号': q['编号'],
                '问题': json.dumps(q['问题'], ensure_ascii=False),
                'SQL查询语句': sql_text,  # 现在包含实际的SQL
                '图形格式': chart_type,
                '回答': answer_json
            })
            
        except Exception as e:
            print(f"   ❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # 保存结果
    output_file = RESULT_DIR / 'result_2.xlsx'
    if results:
        save_result(results, output_file)
        print(f"\n🎉 任务二完成！共处理 {len(results)} 个问题")
    else:
        print("\n❌ 没有生成任何结果")
    
    # 关闭连接
    assistant.close()

if __name__ == "__main__":
    main()