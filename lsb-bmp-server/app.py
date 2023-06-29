from flask import Flask, send_from_directory
from flask_cors import CORS
from blueprints import *
import os



app = Flask(__name__)
CORS(app, supports_credentials=True)  # 允许跨域
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'uploads')

# 注册蓝图
app.register_blueprint(editor_bp)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    app.run()
