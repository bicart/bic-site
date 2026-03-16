# A very simple Flask app to serve your beautiful HTML page
from flask import Flask, send_file, jsonify, request
import datetime
import json
import os

app = Flask(__name__)

# ========== 原来的网站部分 ==========
@app.route('/')
def serve_homepage():
    # 直接返回你的HTML文件
    return send_file('index.html')


# ========== 除夕祝福墙API ==========
# 使用绝对路径确保文件能正确保存
MESSAGES_FILE = '/home/bicart/mysite/new_year_messages.json'

def load_messages():
    """加载留言"""
    print(f"尝试加载文件: {MESSAGES_FILE}")  # 调试信息
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"成功加载 {len(data)} 条留言")  # 调试信息
                return data
        except Exception as e:
            print(f"加载文件出错: {e}")
            return []
    else:
        print("文件不存在，返回空列表")
        return []

def save_messages(messages):
    """保存留言"""
    print(f"尝试保存 {len(messages)} 条留言到: {MESSAGES_FILE}")  # 调试信息
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(MESSAGES_FILE), exist_ok=True)

        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        print("保存成功")
        return True
    except Exception as e:
        print(f"保存文件出错: {e}")
        return False

@app.route('/api/test')
def test():
    """测试API"""
    return jsonify({
        'message': 'API正常运行！除夕快乐！',
        'time': str(datetime.datetime.now())
    })

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """获取留言板"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))

        messages = load_messages()
        print(f"GET请求: 共 {len(messages)} 条留言")  # 调试信息

        # 按时间倒序
        messages.sort(key=lambda x: x['timestamp'], reverse=True)

        # 分页
        start = (page - 1) * limit
        end = start + limit
        page_messages = messages[start:end]

        return jsonify({
            'messages': page_messages,
            'total': len(messages),
            'page': page,
            'has_more': end < len(messages)
        })
    except Exception as e:
        print(f"GET请求出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages', methods=['POST'])
def post_message():
    """发布新留言"""
    try:
        data = request.json
        print(f"收到POST数据: {data}")  # 调试信息

        nickname = data.get('nickname', '').strip()
        content = data.get('content', '').strip()

        if not nickname or not content:
            return jsonify({'error': '昵称和内容不能为空'}), 400

        # 限制长度
        nickname = nickname[:20]
        content = content[:200]

        # 创建新留言
        now = datetime.datetime.now()
        new_message = {
            'id': str(int(now.timestamp() * 1000)),
            'nickname': nickname,
            'content': content,
            'timestamp': now.isoformat(),
            'time_str': now.strftime('%H:%M'),
            'date_str': now.strftime('%m-%d')
        }

        print(f"创建新留言: {new_message}")  # 调试信息

        # 加载并保存
        messages = load_messages()
        messages.append(new_message)

        # 只保留最近500条
        if len(messages) > 500:
            messages = messages[-500:]

        success = save_messages(messages)

        if success:
            return jsonify({
                'success': True,
                'message': new_message,
                'total': len(messages)
            })
        else:
            return jsonify({'error': '保存失败'}), 500

    except Exception as e:
        print(f"POST请求出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    try:
        messages = load_messages()
        return jsonify({
            'total': len(messages),
            'last_update': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        print(f"STATS请求出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug', methods=['GET'])
def debug():
    """调试接口：查看文件状态"""
    file_exists = os.path.exists(MESSAGES_FILE)
    file_size = os.path.getsize(MESSAGES_FILE) if file_exists else 0

    messages = load_messages()

    return jsonify({
        'file_exists': file_exists,
        'file_size': file_size,
        'file_path': MESSAGES_FILE,
        'messages_count': len(messages),
        'messages': messages[-5:] if messages else []  # 最近5条
    })
# 添加下载路由
@app.route('/download/aboxs')
def download_aboxs():
    """下载ABoxs程序"""
    try:
        # 文件路径（放在static文件夹）
        file_path = '/home/bicart/mysite/static/ABoxs-cx1.7z'

        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404

        # 获取文件大小
        file_size = os.path.getsize(file_path)

        # 发送文件
        return send_file(
            file_path,
            as_attachment=True,
            download_name='ABoxs除夕活动.7z',  # 下载时的文件名
            mimetype='application/x-7z-compressed'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 本地调试用（PythonAnywhere会忽略这个）
if __name__ == '__main__':
    app.run(debug=True)