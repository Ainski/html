from flask import Flask, request, jsonify, redirect, session, render_template
from flask_cors import CORS  # type: ignore
import pymysql
import random
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import hashlib
from datetime import datetime
import re
import ssl
import sys
import os
import cryptography
import base64

# 设置文件编码
if sys.platform.startswith('win'):
    sys.stdin.recoding = 'utf-8'
    sys.stdout.recoding = 'utf-8'

app = Flask(__name__, template_folder='templates')
CORS(app, supports_credentials=True)
app.secret_key = 'your_secret_key_here'

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'passwd': 'chr3928700',
    'charset': 'utf8',
    'db': 'online_forum'
}

# 邮件配置
SMTP_CONFIG = {
    'server': "smtp.tongji.edu.cn",
    'port': 465,
    'sender': "2351579@tongji.edu.cn",
    'password': "CHAAAo05S"
}

#api接口
#检查当前用户是否登录,前端用fetch获取数据
@app.route('/api/check_login', methods=['POST', 'OPTIONS'])
def check_login():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    email = data.get('email')

    if 'email' in session:
        if email == session['email']:
            return jsonify({'status': 'ok', 'data': True})
        else:
            return jsonify({'status': 'ok', 'data': False})
    else:
        return jsonify({'status': 'ok', 'data': False})

#获取当前用户
@app.route('/api/get_current_user', methods=['POST', 'OPTIONS'])
def get_current_user():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    email = data.get('email')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        return jsonify({'status': 'ok', 'data': user})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

    finally:
        cursor.close()
        conn.close()

@app.route('/api/get_posts', methods=['POST', 'OPTIONS'])#获取帖子列表
def get_posts():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    page = data.get('page')
    limit = data.get('limit')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM posts LIMIT %s, %s", (page, limit))
        posts = cursor.fetchall()
        return jsonify({'status': 'success', 'data': posts})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

    finally:
        cursor.close()
        conn.close()

@app.route('/api/create_post', methods=['POST', 'OPTIONS'])#创建帖子
def create_post():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    title = data.get('title')
    content = data.get('content')
    user_id = data.get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO posts (title, content, user_id, created_at) VALUES (%s, %s, %s, %s)", (title, content, user_id, datetime.now()))
        conn.commit()
        return jsonify({'status': 'success', 'message': '创建成功'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

    finally:
        cursor.close()
        conn.close()

@app.route('/api/get_post', methods=['POST', 'OPTIONS'])#获取帖子详情
def get_post():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    post_id = data.get('post_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
        post = cursor.fetchone()
        return jsonify({'status': 'success', 'data': post})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

    finally:
        cursor.close()
        conn.close()

@app.route('/api/update_post', methods=['POST', 'OPTIONS'])#更新帖子
def update_post():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    post_id = data.get('post_id')
    title = data.get('title')
    content = data.get('content')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE posts SET title = %s, content = %s WHERE id = %s", (title, content, post_id))
        conn.commit()
        return jsonify({'status': 'success', 'message': '更新成功'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

    finally:
        cursor.close()
        conn.close()

@app.route('/api/delete_post', methods=['POST', 'OPTIONS'])#删除帖子
def delete_post():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    post_id = data.get('post_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        conn.commit()
        return jsonify({'status': 'success', 'message': '删除成功'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

    finally:
        cursor.close()
        conn.close()

@app.route('/api/create_comment', methods=['POST', 'OPTIONS'])#创建评论
def create_comment():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    post_id = data.get('post_id')
    content = data.get('content')
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    print(user_name)
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO comments (post_id, content, user_id, created_at, user_name) VALUES (%s, %s, %s, %s,%s)", (post_id, content, user_id, datetime.now(), user_name))
        conn.commit()
        return jsonify({'status': 'success', 'message': '创建成功'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

    finally:
        cursor.close()
        conn.close()

#获取用户名
@app.route('/api/get_username', methods=['POST', 'OPTIONS'])
def get_username():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    email = data.get('email')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT username FROM users WHERE email = %s", (email,))
        username = cursor.fetchone()
        return jsonify({'status': 'ok', 'data': username})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

    finally:
        cursor.close()
        conn.close()


def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


def send_verification_code(email):
    verification_code = str(random.randint(100000, 999999))
    print(verification_code)
    message = MIMEText(f'您的验证码是: {verification_code}', 'plain', 'utf-8')
    message['Subject'] = Header('验证码', 'utf-8')
    message['From'] = SMTP_CONFIG['sender']
    message['To'] = email

    try:
        with smtplib.SMTP_SSL(SMTP_CONFIG['server'], 465) as server:
            server.set_debuglevel(1)
            print(f"正在连接到SMTP服务器...")

            print(f"正在尝试登录...")
            server.login(SMTP_CONFIG['sender'], SMTP_CONFIG['password'])
            print(f"登录成功")

            print(f"正在发送邮件到 {email}")
            result = server.sendmail(
                from_addr=SMTP_CONFIG['sender'],
                to_addrs=[email],
                msg=message.as_string()
            )

            # 检查发送结果
            if not result:
                print(f"邮件发送成功")
                session[f'verification_code_{email}'] = verification_code
                return True
            else:
                print(f"邮件发送失败: {result}")
                return False

    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP认证失败: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP错误: {e}")
        return False
    except Exception as e:
        print(f"发送邮件时发生错误: {e}")
        return False
    finally:
        print("邮件发送流程完成")


def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login.html')
def login_page():
    return render_template('login.html')


@app.route('/send_code', methods=['POST', 'OPTIONS'])
def send_code():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': '无效的请求数据'}), 400

    email = data.get('email')
    is_register = data.get('is_register', False)  # 新增参数，用于区分是注册还是登录验证码

    if not email or not validate_email(email):
        return jsonify({'status': 'error', 'message': '无效的邮箱地址'})

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        user_exists = cursor.fetchone() is not None

        # 注册时检查邮箱是否已存在
        if is_register and user_exists:
            return jsonify({'status': 'error', 'message': '该邮箱已注册'})

        # 登录时检查邮箱是否存在
        if not is_register and not user_exists:
            return jsonify({'status': 'error', 'message': '该邮箱未注册'})

        if send_verification_code(email):
            return jsonify({'status': 'success', 'message': '验证码发送成功'})
        return jsonify({'status': 'error', 'message': '未知错误'})

    finally:
        cursor.close()
        conn.close()

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    email = data.get('email')
    code = data.get('code')
    username = data.get('username')
    password = data.get('password')

    stored_code = session.get(f'verification_code_{email}')
    if not stored_code or code != stored_code:
        return jsonify({'status': 'error', 'message': '验证码无效'})

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        hashed_password = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password, email, created_at) VALUES (%s, %s, %s, %s)",
            (username, hashed_password, email, datetime.now())
        )
        conn.commit()
        session.pop(f'verification_code_{email}', None)
        return jsonify({'status': 'success', 'message': '注册成功'})
    except pymysql.err.IntegrityError:
        return jsonify({'status': 'error', 'message': '用户名或邮箱已存在'})
    finally:
        cursor.close()
        conn.close()


@app.route('/login', methods=['POST', 'OPTIONS', 'GET'])
def login():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    email = data.get('email')
    password = data.get('password')
    verification_code = data.get('verification_code')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 首先检查邮箱是否存在
        cursor.execute("SELECT username FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'status': 'error', 'message': '邮箱不存在'})

        if verification_code:
            stored_code = session.get(f'verification_code_{email}')
            if not stored_code or verification_code != stored_code:
                return jsonify({'status': 'error', 'message': '验证码无效'})
            session.pop(f'verification_code_{email}', None)  # 使用后删除验证码
        else:
            hashed_password = hash_password(password)
            cursor.execute("SELECT username FROM users WHERE email = %s AND password = %s", (email, hashed_password))
            if not cursor.fetchone():
                return jsonify({'status': 'error', 'message': '邮箱或密码错误'})

        #cursor.execute("UPDATE users SET last_login = %s WHERE email = %s", (datetime.now(), email))
        #更新登录时间和登录状态
        cursor.execute("UPDATE users SET is_login = 1 WHERE email = %s", (email,))
        conn.commit()
        session['is_login']=1
        session['email'] = email
        return jsonify({'status': 'success', 'redirect': '/forum'})
    finally:
        cursor.close()
        conn.close()

@app.route('/logout', methods=['GET'])
def logout():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    email = session.get('email')
    session.pop('email', None)
    session.pop('is_login', None)
    #数据库中更新登录状态
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET is_login = 0 WHERE email = %s", (email,))
        conn.commit()
        return jsonify({'status': 'success', 'message': '注销成功'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': '注销失败: ' + str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/this_is_only_a_test')
def test_page():
    if 'email' not in session:
        return redirect('/login.html')
    return "登录成功，欢迎访问测试页面！"

#写一个论坛
@app.route('/forum')
def forum():
    if 'email' not in session:
        return redirect('/login.html')
    return render_template('forum.html')

@app.route('/get_user_status', methods=['GET'])
def get_user_status():
    # 获取用户ID（假设用户ID通过SESSION或其他方式获取）
    user_email = session.get('email')
    if user_email:
        # 连接到数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询用户登录状态和用户名
        query = "SELECT username, is_login,email FROM users WHERE email = %s"
        cursor.execute(query, (user_email,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            response = {
                     'email': result[2],
                    'is_login': result[1],
                    'username': result[0]
            }
        else:
            response = {
                    'email': None,
                'is_login': False,
                'username': None
            }
    else:
        response = {
                'email': None,
            'is_login': False,
            'username': None
        }

    return jsonify(response)



@app.route('/post_topic', methods=['POST', 'OPTIONS'])
def post_topic():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json

    title = data.get('title')
    content = data.get('content')
    user_email = session.get('email')
    #利用title和时间生成一个唯一的topic_id

    topic_id = hashlib.sha256((title+str(datetime.now())).encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        #cursor.execute("INSERT INTO topics (title, content, user_email, created_at) VALUES (%s, %s, %s, %s)", (title, content, user_email, datetime.now()))
        cursor.execute("INSERT INTO topics (topic_id, title, content, user_email, created_at) VALUES (%s, %s, %s, %s, %s)", (topic_id, title, content, user_email, datetime.now()))
        conn.commit()
        return jsonify({'status': 'success', 'message': '发帖成功'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': '发帖失败: ' + str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/get_topics')
def get_topics():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT topic_id, title, content, user_email, created_at FROM topics")
        topics = cursor.fetchall()
        return jsonify({'status': 'success', 'topics': topics})
    except Exception as e:
        return jsonify({'status': 'error', 'message': '获取帖子失败: ' + str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/get_topic_comments/<string:topic_id>')
def get_topic_comments(topic_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT comment_id, content, user_email, created_at, user_name FROM comments WHERE topic_id = %s", (topic_id,))
        comments = cursor.fetchall()

        return jsonify({
            'status': 'success',
            'comments': comments
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': '获取评论失败: ' + str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/post_comment/<string:topic_id>', methods=['POST', 'OPTIONS'])
def post_comment(topic_id):
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    content = data.get('content')
    user_email = session.get('email')
    #利用topic_id和时间生成一个唯一的comment_id
    comment_id = hashlib.sha256((topic_id+str(datetime.now())).encode()).hexdigest()
    user_name = ''
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username FROM users WHERE email = %s", (user_email,))
        user_name = cursor.fetchone()[0]

    except Exception as e:
        return jsonify({'status': 'error', 'message': '获取用户名失败: ' + str(e)})
    finally:
        cursor.close()
        conn.close()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO comments (comment_id, topic_id, content, user_email, created_at, user_name) VALUES (%s, %s, %s, %s, %s,%s)", (comment_id, topic_id, content, user_email, datetime.now(), user_name))
        conn.commit()
        return jsonify({'status': 'success', 'message': '评论成功'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': '评论失败: ' + str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/get_user_topics', methods=['POST'])
def get_user_topics():
    user_email = session.get('email')

    if not user_email:
        return jsonify({'status': 'error', 'message': '缺少用户邮箱'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT topic_id, title, content, user_email, created_at FROM topics WHERE user_email = %s", (user_email,))
        topics = cursor.fetchall()
        return jsonify({'status': 'success', 'topics': topics})
    except Exception as e:
        return jsonify({'status': 'error', 'message': '获取帖子失败: ' + str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/get_user_comments')
def get_user_comments():
    user_email = session.get('email')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT comment_id, content, user_email, created_at FROM comments WHERE user_email = %s ", (user_email,))
        comments = cursor.fetchall()
        return jsonify({'status': 'success', 'comments': comments})
    except Exception as e:
        return jsonify({'status': 'error', 'message': '获取评论失败: ' + str(e)})
    finally:
        cursor.close()
        conn.close()


@app.route('/personal_page/<string:email>',methods=['GET'])
def personal_page(email):
    print(email)
    print(session.get('email'))
    # 若用户未登录，则跳转到登录页面
    if 'email' not in session:
        return redirect('/login.html')

    # 若用户已登录，则获取用户ID
    user_email = email

    # 连接数据库，获取用户数据
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 获取用户信息
        cursor.execute("SELECT * FROM users WHERE email = %s", (user_email,))
        user = cursor.fetchone()

        # 获取用户发布的帖子
        cursor.execute("SELECT * FROM topics WHERE user_email = %s", (user_email,))
        posts = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    # 将数据传递给模板
    return render_template('personal_page.html', user=user, posts=posts)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)