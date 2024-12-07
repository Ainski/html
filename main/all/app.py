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


def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


def send_verification_code(email):
    verification_code = str(random.randint(100000, 999999))

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
            return jsonify({'status': 'success', 'message': '验证码发送失败'})
        return jsonify({'status': 'error', 'message': '验证码已发送'})

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
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
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
            cursor.execute("SELECT user_id FROM users WHERE email = %s AND password = %s", (email, hashed_password))
            if not cursor.fetchone():
                return jsonify({'status': 'error', 'message': '邮箱或密码错误'})

        cursor.execute("UPDATE users SET last_login = %s WHERE email = %s", (datetime.now(), email))
        conn.commit()

        session['user_email'] = email
        return jsonify({'status': 'success', 'redirect': '/this_is_only_a_test'})
    finally:
        cursor.close()
        conn.close()

@app.route('/logout', methods=['POST', 'OPTIONS'])
def logout():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    session.pop('user_email', None)
    return jsonify({'status': 'success'})

@app.route('/this_is_only_a_test')
def test_page():
    if 'user_email' not in session:
        return redirect('/login.html')
    return "登录成功，欢迎访问测试页面！"

#写一个论坛
@app.route('/forum')
def forum():
    if 'user_email' not in session:
        return redirect('/login.html')
    return render_template('forum.html')

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
    user_email = session.get('user_email')
    #利用title和content生成一个唯一的topic_id
    topic_id = hashlib.sha256((title+content).encode()).hexdigest()

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

@app.route('/get_topic_comments/<int:topic_id>')
def get_topic_comments(topic_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT comment_id, content, user_email, created_at FROM comments WHERE topic_id = %s", (topic_id,))
        comments = cursor.fetchall()
        return jsonify({'status': 'success', 'comments': comments})
    except Exception as e:
        return jsonify({'status': 'error', 'message': '获取评论失败: ' + str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/post_comment/<int:topic_id>', methods=['POST', 'OPTIONS'])
def post_comment(topic_id):
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.json
    content = data.get('content')
    user_email = session.get('user_email')
    #利用topic_id和content生成一个唯一的comment_id
    comment_id = hashlib.sha256((str(topic_id)+content).encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO comments (comment_id, topic_id, content, user_email, created_at) VALUES (%s, %s, %s, %s, %s)", (comment_id, topic_id, content, user_email, datetime.now()))
        conn.commit()
        return jsonify({'status': 'success', 'message': '评论成功'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': '评论失败: ' + str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/get_user_topics')#由用户获取自己的帖子，有待改进
def get_user_topics():
    user_email = session.get('user_email')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT topic_id, title, content, user_email, created_at FROM topics WHERE user_email = %s", (user_email,))
        topics = cursor.fetchall()
        return jsonify({'status': 'success', 'topics': topics})
    except Exception as e:
        return jsonify({'status': 'error', 'message': '获取帖子失败: ' + str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/get_user_comments')
def get_user_comments():
    user_email = session.get('user_email')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT comment_id, content, user_email, created_at FROM comments WHERE user_email = %s", (user_email,))
        comments = cursor.fetchall()
        return jsonify({'status': 'success', 'comments': comments})
    except Exception as e:
        return jsonify({'status': 'error', 'message': '获取评论失败: ' + str(e)})
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)