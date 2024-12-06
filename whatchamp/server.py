from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
import subprocess
import logging
from riot_name_api import *
from model_req import *
import os

# Flask 앱 생성
app = Flask(__name__, static_folder='build')

# CORS 설정 추가
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "https://www.jepetolee.p-e.kr"}})


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

@app.route('/api/starter', methods=['POST'])
def starter():
    data = request.get_json()
    username = data.get('username')
    tag = data.get('tag', 'KR1')  # tag가 없으면 기본값 'KR1' 사용

    if not username:
        logger.warning("Invalid request: Missing username")
        return jsonify({"message": "Invalid request: username is required"}), 400

    logger.debug(f"Sending to Python script: {data}")

    try:
        response = checking_response(username,tag)
        # 조건부 /api/result 호출
        if response["success"]:  # 예: 응답 데이터에 'success' 필드가 있으면 전달
            new_result_url = f"http://localhost:5000/api/result/{username}/{tag}"

            logger.info(f"Forwarding to /api/result for user: {username}, tag: {tag}")

            logger.info(f"response: {response}")

            # # /api/result로 데이터 전송
            # result_response = jsonify(response.json()), response.status_code

            # return result_response
            # /api/result로 데이터 전송
            result_response = jsonify(response), 200  # 이미 dict이므로 jsonify로 바로 변환

            return result_response
        else:
            logger.info("No success response from riot_name_api; not forwarding to /api/new_result")
            return jsonify({"message": "Processing completed, but no further action required"}), 200

    except Exception as e:
        logger.error(f"Failed to start Python process: {str(e)}")
        return jsonify({"message": "Failed to start Python process", "error": str(e)}), 500

# /api/result/<username>/<tag> 엔드포인트 정의
@app.route('/api/result/<username>/<tag>', methods=['GET','POST'])
def get_result(username, tag):
    try:
        champions_data = get_champions_name(username, tag)
        # {'message': 'Data received successfully', 'champions': ['렝가', '럭스', '제라스']}

        # champions_data가 튜플(데이터, 상태 코드)인 경우 처리
        if isinstance(champions_data, dict):
            data = champions_data['champions']
            # status_code, data = champions_data
            return jsonify(data), 200

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

    try:
        # Python 스크립트 실행
        process = subprocess.Popen(
            ['python', script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        logger.debug(f"Started Python process: {script_path}")

        # JSON 데이터를 UTF-8로 인코딩하여 Python 스크립트의 stdin으로 전달
        json_string = json.dumps(question_map, ensure_ascii=False)
        logger.debug(f"Sending to Python script: {json_string}")
        stdout, stderr = process.communicate(input=json_string)
        logger.debug(f"cossim's output: {stdout.strip()}")

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
