"""
app.py  ·  自然语言 → SQL → 查询结果
依赖：pip install flask flask-cors pymysql
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from deepseek_api import chat          # deepseek_api 内部已写死 API_KEY
import pymysql

# ───── 数据库连接信息（请填写真实值） ─────
DB_HOST     = "YOUR_DB_HOST"      # 例: "172.29.235.18"
DB_PORT     = 33006               # 例: 33006
DB_USER     = "YOUR_DB_USER"      # 例: "readonly"
DB_PASSWORD = "YOUR_DB_PASSWORD"  # 例: "passw0rd"
DB_NAME     = "YOUR_DB_NAME"      # 例: "hr_data"
# -----------------------------------------

# ───── 三张表结构（示例，请按实际表填） ─────
TABLE_SCHEMA = """
### 数据库表结构
table: employees
  - id            (INT)         员工ID，主键
  - name          (VARCHAR)     姓名
  - gender        (CHAR)        性别: 'M' | 'F'
  - join_year     (INT)         入职年份
  - first_school  (VARCHAR)     第一学历学校
  - first_degree  (VARCHAR)     第一学历级别
  - is_985        (TINYINT)     是否985

table: departments
  - dept_id       (INT)         部门ID，主键
  - dept_name     (VARCHAR)     部门名称
  - leader_id     (INT)         负责人员工ID

table: leave_records
  - leave_id      (INT)         离职记录ID
  - emp_id        (INT)         员工ID
  - leave_date    (DATE)        离职日期
  - leave_type    (VARCHAR)     离职类型
"""
# -----------------------------------------

def execute_sql(sql: str):
    """执行 SQL，返回 list[dict] 形式的结果。"""
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


# ► 规训提示词：表结构 + 只输出 SQL
SQL_PROMPT = f"""{TABLE_SCHEMA}

你是 SQL 生成助手，请根据用户问题生成 SQL 查询语句。
⚠️ 情况1:只返回一行 SQL，末尾带分号；不要解释、不要注释、不要换行。情况2:若没有此表，或与查询无关，则返回查询无结果。下面是表结构：
"""

app = Flask(__name__)
CORS(app)   # 解决前端跨域

@app.route("/generate_sql", methods=["POST"])
def generate_sql():
    question = (request.get_json(silent=True) or {}).get("query", "").strip()
    if not question:
        return jsonify({"error": "query 不能为空"}), 400

    # 1. LLM 生成 SQL
    try:
        resp = chat(f"{SQL_PROMPT}\n\n用户问题：{question}")
        sql  = resp.choices[0].message.content.strip()
    except Exception as e:
        return jsonify({"error": f"生成 SQL 失败：{e}"}), 500

    # 2. 执行 SQL
    try:
         result = execute_sql(sql)
         return jsonify({"generated_sql": sql, "query_result": result})
    except Exception as e:
         return jsonify({
             "generated_sql": sql,
             "query_result": [],
             "error": f"执行 SQL 失败：{e}"
    })   # 不再返回 500


    # 3. 返回
    return jsonify({"generated_sql": sql, "query_result": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5678, debug=True)
