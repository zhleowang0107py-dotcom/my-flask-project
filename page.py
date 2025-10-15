# ---------------------------------------------------------------------------
# 1. 引入所有必要的函式庫
# ---------------------------------------------------------------------------
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename

# ---------------------------------------------------------------------------
# 2. 初始化 Flask 應用程式與基本設定
# ---------------------------------------------------------------------------
app = Flask(__name__)

# 設定 session 用的密鑰，這是啟用登入功能的必需品
app.config['SECRET_KEY'] = 'a-very-long-and-random-secret-key-please-change-it'

# 設定檔案上傳/下載的資料夾 (使用相對路徑，最穩定、最推薦的作法)
# 這會自動找到你專案資料夾下的 'downloads' 子資料夾
project_root = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(project_root, 'downloads')
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# ---------------------------------------------------------------------------
# 3. 網站的靜態資料 (例如搜尋用的資料)
# ---------------------------------------------------------------------------
mock_data = [
    {'id': 1, 'type': 'note', 'title': 'Flask 學習筆記', 'content': 'Flask 是一個輕量的 Python Web 框架。'},
    {'id': 2, 'type': 'note', 'title': 'Python 資料結構', 'content': '介紹串列 (List)、字典 (Dictionary) 的用法。'},
    {'id': 3, 'type': 'file', 'title': '常用指令.txt', 'content': 'git clone, git push, pip install...'},
    {'id': 4, 'type': 'about', 'title': '關於本站', 'content': '這是一個使用 Flask 和 PythonAnywhere 製作的網站。'}
]

# ---------------------------------------------------------------------------
# 4. 網站的主要路由 (Routes)
# ---------------------------------------------------------------------------

# --- 基本頁面 ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/note')
def note():
    return render_template('note.html')

@app.route('/about')
def about():
    return render_template('about.html')

# page.py

# ... (在 @app.route('/about') 的函式後面) ...

@app.route('/learning_record')
def learning_record():
    return render_template('learning_record.html')

# ... (後面的登入功能等保持不變) ...

# --- 登入與登出功能 ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # 為了簡單起見，我們將使用者名稱和密碼寫死在這裡
        # 請將 'your_secret_password' 換成一個你自己的安全密碼
        if request.form['username'] == '114072504' and request.form['password'] == 'zxcvbnm910107':
            session['logged_in'] = True  # 登入成功，在 session 中做下記號
            return redirect(url_for('file_page'))
        else:
            error = '無效的使用者名稱或密碼'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # 從 session 中移除登入記號
    return redirect(url_for('index'))

# --- 檔案下載專用路由 ---
@app.route('/downloads/<path:filepath>')
def download_file(filepath):
    """安全地從設定好的 DOWNLOAD_FOLDER 提供檔案下載。"""
    # 檢查使用者是否登入 (可選，如果你想讓下載也需要登入的話)
    # if 'logged_in' not in session:
    #     return redirect(url_for('login'))
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filepath, as_attachment=True)


# --- 新增路由：專門處理檔案刪除 ---
@app.route('/delete_file', methods=['POST'])
def delete_file():
    # 1. 安全檢查：必須是登入狀態才能刪除
    if 'logged_in' not in session:
        # 如果沒登入就想刪除，直接踢回首頁，不執行任何操作
        return redirect(url_for('index'))

    # 2. 從 file.html 表單的隱藏欄位獲取檔案資訊
    category = request.form.get('category')
    filename = request.form.get('filename')

    # 3. 再次安全檢查：確保資訊完整且不包含惡意路徑字元
    if category and filename and '..' not in category and '/' not in category and '..' not in filename and '/' not in filename:

        # 4. 組合出檔案在伺服器上的完整路徑
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], category, filename)

        # 5. 執行刪除前，先用 os.path.exists() 確認檔案真的存在
        if os.path.exists(file_path):
            try:
                # 使用 os.remove() 刪除檔案
                os.remove(file_path)

                # (可選但推薦) 檢查分類資料夾是否為空，如果是空的就一併刪除
                category_path = os.path.dirname(file_path)
                if not os.listdir(category_path):
                    os.rmdir(category_path)

            except OSError as e:
                # 如果發生錯誤（例如權限問題），可以在後台伺服器終端機印出訊息以供除錯
                print(f"!!! ERROR DELETING FILE {file_path}: {e}")

    # 6. 無論刪除成功或失敗，最後都重新導向回檔案列表頁面
    return redirect(url_for('file_page'))

# --- 核心功能：檔案管理頁面 (上傳與顯示) ---
@app.route('/file', methods=['GET', 'POST'])
def file_page():
    # --- 處理檔案上傳 (POST 請求) ---
    if request.method == 'POST':
        print("=" * 30)
        print("DEBUGGING FILE UPLOAD:")
        print(f"  Session Logged In: {session.get('logged_in')}")

        file_object = request.files.get('file_to_upload')
        print(f"  File Object Received: {file_object}")
        if file_object:
            print(f"  Filename: {file_object.filename}")

        print(f"  Category Received: {request.form.get('category')}")
        print(f"  Target Save Folder: {app.config['DOWNLOAD_FOLDER']}")
        print("=" * 30)
        # 伺服器端安全檢查：如果沒登入，就不允許上傳
        if 'logged_in' not in session:
            return redirect(url_for('login'))

        file = request.files.get('file_to_upload')
        category = request.form.get('category', '其他')

        if file and file.filename != '':
            # 直接使用原始檔名
            filename = file.filename

            # 【新增】做一個基本的安全檢查，防止路徑遍歷攻擊
            if '/' in filename or '..' in filename:
                # 如果檔名包含危險字元，就拒絕上傳
                # 這裡我們可以導向回原頁面，未來可以加上錯誤訊息
                return redirect(request.url)

            # 後續的儲存邏輯不變
            category_path = os.path.join(app.config['DOWNLOAD_FOLDER'], category)
            os.makedirs(category_path, exist_ok=True)
            file.save(os.path.join(category_path, filename))
            return redirect(url_for('file_page'))
        else:
            return redirect(request.url)

    # --- 準備要顯示的檔案列表 (GET 請求) ---
    categorized_files = {}
    if os.path.exists(app.config['DOWNLOAD_FOLDER']):
        for category_name in os.listdir(app.config['DOWNLOAD_FOLDER']):
            category_path = os.path.join(app.config['DOWNLOAD_FOLDER'], category_name)
            if os.path.isdir(category_path):
                files_in_category = os.listdir(category_path)
                if files_in_category:
                    categorized_files[category_name] = files_in_category
    else:
        # 如果 downloads 資料夾不存在，程式會自動建立它
        os.makedirs(app.config['DOWNLOAD_FOLDER'])

    return render_template('file.html', categorized_files=categorized_files)

# --- 搜尋功能 ---
# page.py

# --- 搜尋功能 (升級版) ---
@app.route('/search')
def search():
    query = request.args.get('query', '')
    search_results = []

    # --- ↓↓↓ 關鍵修改從這裡開始 ↓↓↓ ---

    # 1. 建立一個動態的、即時的搜尋索引
    #    先把 mock_data 裡的所有靜態內容加進來
    dynamic_search_index = list(mock_data)

    # 2. 掃描 downloads 資料夾，為每個找到的檔案都建立一張新的「索引卡片」
    downloads_path = app.config['DOWNLOAD_FOLDER']
    if os.path.exists(downloads_path):
        for category_name in os.listdir(downloads_path):
            category_path = os.path.join(downloads_path, category_name)
            if os.path.isdir(category_path):
                for filename in os.listdir(category_path):
                    # 為每個檔案建立一張卡片（一個字典）
                    file_card = {
                        'id': f'file_{filename}', # 給一個唯一的ID
                        'type': 'file',
                        'title': filename, # 標題就是檔名
                        'content': f'位於 {category_name} 分類下的檔案' # 內容可以自訂
                    }
                    # 把這張新卡片加入到我們的動態索引中
                    dynamic_search_index.append(file_card)

    # --- ↑↑↑ 關鍵修改在這裡結束 ↑↑↑ ---

    if query:
        # 3. 搜尋的對象不再是固定的 mock_data，而是我們剛剛建立的動態索引！
        for item in dynamic_search_index:
            if query.lower() in item['title'].lower() or query.lower() in item['content'].lower():
                search_results.append(item)

    return render_template('search_results.html', query=query, results=search_results)


# ---------------------------------------------------------------------------
# 5. 啟動伺服器的程式進入點
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
