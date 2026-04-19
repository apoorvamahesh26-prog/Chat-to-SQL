# nl_to_sql.py
# Converts natural language questions to SQL queries.
# Supports TWO modes:
#   1. Rule-based (no API key needed) — for common patterns
#   2. OpenAI GPT (needs API key)    — for complex queries

import re
import os


# ─────────────────────────────────────────────────────────────
# MODE 1: RULE-BASED NL → SQL (works without any API key)
# ─────────────────────────────────────────────────────────────

RULE_PATTERNS = [
    # Count queries
    (r"how many employees", "SELECT COUNT(*) AS total_employees FROM employees;"),
    (r"count.*employees", "SELECT COUNT(*) AS total_employees FROM employees;"),
    (r"number of employees", "SELECT COUNT(*) AS total_employees FROM employees;"),

    # Average salary
    (r"average salary", "SELECT AVG(salary) AS avg_salary FROM employees;"),
    (r"avg salary", "SELECT AVG(salary) AS avg_salary FROM employees;"),
    (r"mean salary", "SELECT AVG(salary) AS avg_salary FROM employees;"),

    # Highest / max salary
    (r"highest salary|maximum salary|max salary|top earner",
     "SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 1;"),

    # Lowest salary
    (r"lowest salary|minimum salary|min salary",
     "SELECT name, salary FROM employees ORDER BY salary ASC LIMIT 1;"),

    # Top N earners
    (r"top (\d+) earners?|top (\d+) highest salary",
     None),  # handled dynamically below

    # All employees
    (r"show all employees|list all employees|all employees",
     "SELECT * FROM employees;"),

    # Employees by department
    (r"employees in engineering",
     "SELECT e.name, e.salary, e.city FROM employees e JOIN departments d ON e.dept_id=d.dept_id WHERE d.dept_name='Engineering';"),
    (r"employees in sales",
     "SELECT e.name, e.salary, e.city FROM employees e JOIN departments d ON e.dept_id=d.dept_id WHERE d.dept_name='Sales';"),
    (r"employees in marketing",
     "SELECT e.name, e.salary, e.city FROM employees e JOIN departments d ON e.dept_id=d.dept_id WHERE d.dept_name='Marketing';"),
    (r"employees in hr",
     "SELECT e.name, e.salary, e.city FROM employees e JOIN departments d ON e.dept_id=d.dept_id WHERE d.dept_name='HR';"),
    (r"employees in finance",
     "SELECT e.name, e.salary, e.city FROM employees e JOIN departments d ON e.dept_id=d.dept_id WHERE d.dept_name='Finance';"),

    # Department list
    (r"list.*departments|show.*departments|all departments",
     "SELECT dept_name, location, budget FROM departments;"),

    # Sales data
    (r"show.*sales|all sales|list.*sales",
     "SELECT s.sale_id, e.name AS employee, s.product, s.amount, s.sale_date, s.region FROM sales s JOIN employees e ON s.emp_id=e.emp_id;"),
    (r"total sales",
     "SELECT SUM(amount) AS total_sales FROM sales;"),
    (r"highest sale|biggest sale|max sale",
     "SELECT e.name, s.product, s.amount, s.sale_date FROM sales s JOIN employees e ON s.emp_id=e.emp_id ORDER BY s.amount DESC LIMIT 1;"),
    (r"sales by region",
     "SELECT region, SUM(amount) AS total, COUNT(*) AS num_sales FROM sales GROUP BY region;"),
    (r"sales by product",
     "SELECT product, SUM(amount) AS total, COUNT(*) AS num_sales FROM sales GROUP BY product ORDER BY total DESC;"),

    # City
    (r"employees (in|from) bangalore",
     "SELECT name, salary, dept_id FROM employees WHERE city='Bangalore';"),
    (r"employees (in|from) mumbai",
     "SELECT name, salary, dept_id FROM employees WHERE city='Mumbai';"),
    (r"employees (in|from) delhi",
     "SELECT name, salary, dept_id FROM employees WHERE city='Delhi';"),
    (r"employees (in|from) hyderabad",
     "SELECT name, salary, dept_id FROM employees WHERE city='Hyderabad';"),
    (r"employees (in|from) chennai",
     "SELECT name, salary, dept_id FROM employees WHERE city='Chennai';"),

    # Gender
    (r"female employees",
     "SELECT name, age, salary, city FROM employees WHERE gender='Female';"),
    (r"male employees",
     "SELECT name, age, salary, city FROM employees WHERE gender='Male';"),

    # Salary range
    (r"salary (above|more than|greater than) (\d+)",
     None),  # dynamic
    (r"salary (below|less than) (\d+)",
     None),  # dynamic

    # Age
    (r"employees (above|older than|over) (\d+) years",
     None),  # dynamic
    (r"employees (below|younger than|under) (\d+) years",
     None),  # dynamic

    # Department salary stats
    (r"average salary (by|per|for each) department",
     "SELECT d.dept_name, AVG(e.salary) AS avg_salary, COUNT(*) AS num_employees FROM employees e JOIN departments d ON e.dept_id=d.dept_id GROUP BY d.dept_name ORDER BY avg_salary DESC;"),

    # Recently joined
    (r"recently joined|latest joined|newest employees",
     "SELECT name, join_date, city FROM employees ORDER BY join_date DESC LIMIT 5;"),

    # Oldest employees
    (r"oldest employees|senior employees",
     "SELECT name, age, join_date FROM employees ORDER BY age DESC LIMIT 5;"),

    # Budget
    (r"department budget|budget of each department",
     "SELECT dept_name, budget FROM departments ORDER BY budget DESC;"),
]


def rule_based_nl_to_sql(question: str):
    """
    Tries to match the question against known patterns.
    Returns (sql, explanation) or (None, None) if no match.
    """
    q = question.lower().strip()

    # Dynamic: top N earners
    m = re.search(r"top (\d+) (earners?|highest salary)", q)
    if m:
        n = m.group(1)
        sql = f"SELECT name, salary FROM employees ORDER BY salary DESC LIMIT {n};"
        return sql, f"Showing top {n} employees by salary."

    # Dynamic: salary above X
    m = re.search(r"salary (above|more than|greater than) (\d+)", q)
    if m:
        val = m.group(2)
        sql = f"SELECT name, salary, city FROM employees WHERE salary > {val} ORDER BY salary DESC;"
        return sql, f"Employees with salary above {val}."

    # Dynamic: salary below X
    m = re.search(r"salary (below|less than) (\d+)", q)
    if m:
        val = m.group(2)
        sql = f"SELECT name, salary, city FROM employees WHERE salary < {val} ORDER BY salary ASC;"
        return sql, f"Employees with salary below {val}."

    # Dynamic: age above X
    m = re.search(r"employees? (above|older than|over) (\d+) years?", q)
    if m:
        val = m.group(2)
        sql = f"SELECT name, age, city FROM employees WHERE age > {val} ORDER BY age DESC;"
        return sql, f"Employees older than {val}."

    # Dynamic: age below X
    m = re.search(r"employees? (below|younger than|under) (\d+) years?", q)
    if m:
        val = m.group(2)
        sql = f"SELECT name, age, city FROM employees WHERE age < {val} ORDER BY age ASC;"
        return sql, f"Employees younger than {val}."

    # Static patterns
    for pattern, sql in RULE_PATTERNS:
        if sql and re.search(pattern, q):
            return sql, f"Matched pattern: '{pattern}'"

    return None, None


# ─────────────────────────────────────────────────────────────
# MODE 2: OpenAI GPT NL → SQL (needs OPENAI_API_KEY)
# ─────────────────────────────────────────────────────────────

def openai_nl_to_sql(question: str, schema: str, api_key: str):
    """
    Uses OpenAI GPT to convert NL question to SQL.
    Returns (sql, explanation) or (None, error_msg).
    """
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        system_prompt = f"""You are an expert SQLite SQL query generator.
Given the database schema below, convert the user's natural language question into a valid SQLite SELECT query.

RULES:
1. Output ONLY the SQL query — no explanations, no markdown, no backticks.
2. Only generate SELECT statements — never DROP, DELETE, UPDATE, INSERT.
3. Use proper SQLite syntax.
4. Use table aliases for clarity.
5. Always end the query with a semicolon.

{schema}
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0,
            max_tokens=300
        )

        sql = response.choices[0].message.content.strip()
        # Clean up any accidental markdown
        sql = sql.replace("```sql", "").replace("```", "").strip()
        return sql, "Generated by OpenAI GPT"

    except ImportError:
        return None, "openai package not installed. Run: pip install openai"
    except Exception as e:
        return None, f"OpenAI API Error: {str(e)}"


# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION (auto-selects mode)
# ─────────────────────────────────────────────────────────────

def convert_nl_to_sql(question: str, schema: str, api_key: str = None):
    """
    Main entry point.
    1. First tries rule-based matching (fast, no API key needed).
    2. Falls back to OpenAI if api_key is provided and rules don't match.
    Returns: (sql, explanation, mode_used)
    """
    # Try rule-based first
    sql, explanation = rule_based_nl_to_sql(question)
    if sql:
        return sql, explanation, "Rule-Based"

    # Try OpenAI if key available
    if api_key and api_key.strip().startswith("sk-"):
        sql, explanation = openai_nl_to_sql(question, schema, api_key)
        if sql:
            return sql, explanation, "OpenAI GPT"
        else:
            return None, explanation, "OpenAI GPT (failed)"

    # Nothing worked
    return None, "No rule matched and no OpenAI API key provided. Try a simpler question or add your API key.", "None"


if __name__ == "__main__":
    from sample_data import get_schema_description
    schema = get_schema_description()

    test_questions = [
        "How many employees are there?",
        "Show me the top 5 earners",
        "What is the average salary?",
        "List employees in Engineering",
        "Show sales by region",
        "Employees with salary above 80000",
        "Female employees",
    ]

    for q in test_questions:
        sql, exp, mode = convert_nl_to_sql(q, schema)
        print(f"\nQ: {q}")
        print(f"   Mode: {mode}")
        print(f"   SQL: {sql}")