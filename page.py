from flask import Flask, render_template, request

# 在 page.py 的頂部 (import 下方) 新增這個資料
# 每一筆資料都是一個字典 (dictionary)
mock_data = [
    {'id': 1, 'type': 'note', 'title': 'Flask 學習筆記', 'content': 'Flask 是一個輕量的 Python Web 框架。'},
    {'id': 2, 'type': 'note', 'title': 'Python 資料結構', 'content': '介紹串列 (List)、字典 (Dictionary) 的用法。'},
    {'id': 3, 'type': 'file', 'title': '常用指令.txt', 'content': 'git clone, git push, pip install...'},
    {'id': 4, 'type': 'about', 'title': '關於本站', 'content': '這是一個使用 Flask 和 PythonAnywhere 製作的網站。'}
]

app = Flask(__name__)

# ... (app = Flask(__name__) 和 mock_data 的程式碼) ...

# ... (其他路由 @app.route('/note') 等) ...

@app.route('/search')
def search():
    # 從網址取得 name='query' 的值
    query = request.args.get('query', '') # 如果沒有 query，預設為空字串

    search_results = []
    if query: # 如果使用者有輸入東西才搜尋
        # 遍歷我們的假資料庫
        for item in mock_data:
            # 不分大小寫的比對
            if query.lower() in item['title'].lower() or query.lower() in item['content'].lower():
                search_results.append(item)

    # 將搜尋關鍵字和結果傳遞給模板
    return render_template('search_results.html', query=query, results=search_results)

# ... (if __name__ == '__main__' 的部分) ...

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/note')
def note():
    return render_template('note.html')

@app.route('/file')
def file_page():
    return render_template('file.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)