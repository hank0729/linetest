import os
from flask import Flask
import sqlite3
import time
import threading
import requests

app = Flask(__name__)

@app.route('/<float:temp_value>')
def temp(temp_value):
    con = sqlite3.connect('temp.db')
    cursor = con.cursor()
    cursor.execute("INSERT INTO employees (temp) VALUES (?)", (temp_value,))
    con.commit()
    con.close()
    return "Temperature logged."

def notify_temp():
    while True:
        try:
            con = sqlite3.connect('temp.db')
            cursor = con.cursor()
            cursor.execute('SELECT temp FROM employees ORDER BY id DESC LIMIT 1')
            last_record = cursor.fetchone()
            if last_record:
                temp = last_record[0]  # Get the first element of the tuple
                url = 'https://notify-api.line.me/api/notify'
                token = 'HAEEGV152YwCuL8tknqHwNs0OFhnUfhyUnoLd75S6wp'
                headers = {'Authorization': 'Bearer ' + token}
                data = {'message': f"目前溫度: {temp}"}
                requests.post(url, headers=headers, data=data)
            con.close()
            time.sleep(30)  # Adjust the sleep time as needed
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)  # Adjust the sleep time as needed

if __name__ == '__main__':
    threading.Thread(target=notify_temp).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
