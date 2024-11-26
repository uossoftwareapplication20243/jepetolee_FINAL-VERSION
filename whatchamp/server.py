from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
import subprocess
import os
import logging
import json

# Flask 앱 생성
app = Flask(__name__, static_folder='build')

# CORS 설정 추가
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://www.jepetolee.p-e.kr"}})

# 로그 설정
log_directory = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(
    level=logging.DEBUG if os.environ.get('FLASK_ENV') == 'development' else logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_directory, 'combined.log')),
        logging.FileHandler(os.path.join(log_directory, 'error.log'), mode='a')
    ]
)
logger = logging.getLogger()

# Preflight 요청 처리
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

# /api/starter 엔드포인트 정의
@app.route('/api/starter', methods=['POST'])
def starter():
    data = request.get_json()
    username = data.get('username')
    tag = data.get('tag', 'KR1')  # tag가 없으면 기본값 'KR1' 사용

    if not username:
        logger.warning("Invalid request: Missing username")
        return jsonify({"message": "Invalid request: username is required"}), 400

    script_path = os.path.join(os.path.dirname(__file__), 'riot_name_api.py')
    logger.debug(f"Sending to Python script: {data}")

    try:
        # Python 스크립트 실행
        process = subprocess.Popen(
            ['python', script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=json.dumps(data))

        # Python 스크립트 오류 확인
        if stderr:
            logger.error(f"Python script error: {stderr.strip()}")
            return jsonify({"message": "Python script error occurred", "error": stderr.strip()}), 500

        # Python 응답 데이터 처리
        try:
            response_data = json.loads(stdout.strip())
            logger.info(f"Sending response to client: {response_data}")
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from Python script :{stdout.strip()}")
            return jsonify({"message": "Failed to decode JSON response"}), 500

        if response_data.get('data', 0) > 50:
            return jsonify({"message": "Data processed successfully", "record-based": True}), 200
        else:
            return jsonify({"message": "Data processed, but without record", "record-based": False}), 200

    except Exception as e:
        logger.error(f"Failed to start Python process: {str(e)}")
        return jsonify({"message": "Failed to start Python process", "error": str(e)}), 500

# /api/result/<username>/<tag> 엔드포인트 정의
@app.route('/api/result/<username>/<tag>', methods=['GET'])
def get_result(username, tag):
    line = request.args.get('line')

    if not line:
        logger.warning("Invalid request: Missing line parameter")
        return jsonify({"message": "Invalid request: line parameter is required"}), 400

    user_info = {
        "username": username,
        "tag": tag,
        "line": line
    }

    script_path = os.path.join(os.path.dirname(__file__), 'model_req.py')
    logger.debug(f"Sending to Python script with user_info: {user_info}")

    try:
        # Python 스크립트 실행
        process = subprocess.Popen(
            ['python', script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        json_string = json.dumps(user_info)
        logger.debug(f"Sending to Python script: {json_string}")
        stdout, stderr = process.communicate(input=json_string)

        # Python 스크립트 오류 확인
        if stderr:
            logger.error(f"Python script error: {stderr.strip()}")
            return jsonify({"message": "Python script error", "error": stderr.strip()}), 500

        # Python 응답 데이터 처리
        try:
            response_data = json.loads(stdout.strip())
            logger.info(f"Sending response to client: {json.dumps(response_data, ensure_ascii=False)}")
            return jsonify(response_data), 200
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from Python script")
            return jsonify({"message": "Failed to decode JSON response"}), 500

    except Exception as e:
        logger.error(f"Failed to start Python process: {str(e)}")
        return jsonify({"message": "Failed to start Python process", "error": str(e)}), 500

# /api/new/result 엔드포인트 정의
@app.route('/api/new/result', methods=['POST'])
def new_result():
    question_map = request.get_json()

    if not question_map:
        logger.warning("Invalid request: Missing question map data")
        return jsonify({"message": "Invalid request: question map data is required"}), 400

    logger.info(f"Received questionMap: {json.dumps(question_map, ensure_ascii=False)}")

    script_path = os.path.join(os.path.dirname(__file__), 'cossim.py')
    logger.debug(f"Python script path: {script_path}")

    try:
        # Python 스크립트 실행
        process = subprocess.Popen(
            ['python', script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # JSON 데이터를 UTF-8로 인코딩하여 Python 스크립트의 stdin으로 전달
        json_string = json.dumps(question_map)
        logger.debug(f"Sending to Python script: {json_string}")
        stdout, stderr = process.communicate(input=json_string)

        # Python 스크립트 오류 확인
        if stderr:
            logger.error(f"Python script error: {stderr.strip()}")
            return jsonify({"message": "Python script error occurred", "error": stderr.strip()}), 500

        # Python 응답 데이터 처리
        try:
            response_data = json.loads(stdout.strip())
            logger.info(f"Sending response to client: {json.dumps(response_data, ensure_ascii=False)}")
            return jsonify(response_data), 200
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from Python script")
            return jsonify({"message": "Failed to decode JSON response"}), 500

    except Exception as e:
        logger.error(f"Failed to start Python process: {str(e)}")
        return jsonify({"message": "Failed to start Python process", "error": str(e)}), 500

# /favicon.ico 처리
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.static_folder, 'assets'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

# 정적 파일 라우팅
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# 서버 실행
if __name__ == '__main__':
    port = 5000
    logger.info(f"Server is running on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')

