# text = "溫度上限設定 40"
# parts = text.split()
# if len(parts) == 2:
#     keyword = parts[0]
#     limit = int(parts[1])  # 將字符串轉換為整數
#     print("關鍵詞:", keyword)
#     print("上限:", limit)
# else:
#     print("無法拆分字符串成兩部分")

import sqlite3


con = sqlite3.connect('f.db')
cursorObj = con.cursor()

# cursorObj.execute('''
# #      CREATE TABLE IF NOT EXISTS employees (
# #          id INTEGER PRIMARY KEY,
# #          f STRING
# #      )
# #  ''')
cursorObj.execute("INSERT INTO employees (f) VALUES (?)", (30,))

con.commit()
# cursorObj.execute("SELECT * FROM employees")
# data = cursorObj.fetchall()

# for row in data:
#     print(row)
con.close()