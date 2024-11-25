# front-back 사전준비

whatchamp/src/const/url.js 에서 url 수정해주세요!
port도 수정할 시 whatchamp/server.js 에서 port도 수정해주세요!

# react, nodejs 실행 및 구조

## 실행
0. 프로젝트 위치에 이동, npm install
1. npm run build (react set build)
2. node server
3. 생각해보니 저도 node server로 했을때 프론트-백 통신이 항상 되지는 않았습니다. </br>
npm install -g pm2 </br>
pm2 start server.js --name test </br>
pm2로 서버 실행하면 프론트-백 통신이 아마 항상 가능할 것 같습니다. </br>
근데 이러면 debug가 불편하지만? whatchamp/logs/combined.log 에서 볼 수 있긴 합니다. </br>

## 구조

https://youtu.be/j_b7MY0R1G4

### 1. whatchamp/src/pages/main_page.js 에서 Hide on bush#KR1일 경우, Hide on bush, KR1을 입력한다.

### 2. main_page.js에서 post 통신을 보낸다. url은 whatchamp/src/const/url.js에서 수정한다.
```javascript
    const response = await fetch(
      url+"/api/starter", 
      {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({username: username, tag: tag})
      }
    );
```

이러한 통신은 whatchamp/server.js에서 
```javascript
// API 엔드포인트 설정
app.post('/api/starter', (req, res) => {
  const { username, tag } = req.body;
  
  if (!username || !tag) {
    // 잘못된 요청일 때 (예: 필수 데이터가 없을 때)
    return res.status(400).json({ message: "Invalid request: username and tag are required" });
  }

  const scriptPath = path.join(__dirname, 'python', 'riot_name_api.py');  // 예시: 현재 디렉토리 기준으로 python 폴더 내부
  const pythonProcess = spawn('python', [scriptPath], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  // JSON 데이터를 UTF-8로 인코딩하여 Python 스크립트의 stdin으로 전달
  const jsonString = JSON.stringify(req.body);
  logger.debug(`Sending to Python script: ${jsonString}`); // Python으로 보내는 데이터 확인

  pythonProcess.stdin.write(jsonString, 'utf-8');
  pythonProcess.stdin.end();

  // Python 스크립트 결과 수신
  let data = '';
  pythonProcess.stdout.on('data', (chunk) => {
    const chunkStr = chunk.toString();
    logger.debug(`Python response chunk: ${chunkStr}`);
    data += chunkStr;
  });

  pythonProcess.stdout.on('end', () => {
    try {
      const responseData = JSON.parse(data);
      logger.info(`Sending response to client: ${JSON.stringify(responseData)}`);

      if (data > 50) {
        res.status(200).json({ 
          message: "Data processed successfully",
          "record-based": true });
      } else {
        res.status(200).json({ message: "Data processed, but without record", "record-based": false });
      }
    } catch (err) {
      logger.error(`Error parsing Python response: ${err.message}`);
      res.status(500).json({ message: 'Python script error', error: err.message });
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    const errorStr = data.toString();
    logger.error(`Python error: ${errorStr}`);
  });

  pythonProcess.on('error', (err) => {
    logger.error(`Failed to start Python process: ${err.message}`);
    res.status(500).json({ message: 'Failed to start Python process', error: err.message });
  });
});
```

로 받고 있으며, 특히

```javascript
pythonProcess.stdout.on('end', () => {
    try {
      const responseData = JSON.parse(data);
      logger.info(`Sending response to client: ${JSON.stringify(responseData)}`);

      if (data > 50) {
        res.status(200).json({ 
          message: "Data processed successfully",
          "record-based": true });
      } else {
        res.status(200).json({ message: "Data processed, but without record", "record-based": false });
      }
    } catch (err) {
      logger.error(`Error parsing Python response: ${err.message}`);
      res.status(500).json({ message: 'Python script error', error: err.message });
    }
  });
```

에서  res.status(200).json으로 react로 보내게 된다.

### 3. react의 main_page.js에서 
```javascript
    if (response.status === 200) {
      const data = await response.json();
    
      if (data["record-based"]) {
        navigate('/result');
      } else {
        // Navigate to the page for a negative result
        navigate('/question1');
      }
    } else {
      console.error("Request failed with status:", response.status);
      navigate('/question1');
    }
```
형태로 record-based 값이 true면 비전적 기반 content-based를 위해 question1_page.js로 이동한다. (4번에서 설명)
false면 전적기반 CF를 위해 result_page.js로 이동한다 (5번에서 설명)

### 4. react의 question1_page.js에서 question8_page.js까지 질문 응답 받으면 new_result_page.js로 이동하며
```javascript
  useEffect(() => {
    async function fetchChampionData() {
      try {
        const response = await fetch(
          url+`/api/new/result`,
          { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(questionMap) }
        );

        if (response.status === 200) {
          const data = await response.json();
          setChampionList(data.champions); 
        } else {
          console.error('Request failed with status:', response.status);
        }
      } catch (error) {
        console.error('Error fetching champions:', error);
      }
    }

    if (username && tag) {
      fetchChampionData();
    }
  }, [username, tag, line]);
```

의 형태로 post 통신을 보내고
server.js에서도 
```javascript
// API 엔드포인트 설정
app.post('/api/new/result', (req, res) => {
  // 클라이언트에서 전달된 JSON 데이터 (questionMap)를 받아옴
  const questionMap = req.body;
  logger.info(`Received questionMap: ${JSON.stringify(questionMap)}`); // 클라이언트로부터 받은 데이터 확인

  const scriptPath = path.join(__dirname, 'python', 'cossim.py');  // 예시: 현재 디렉토리 기준으로 python 폴더 내부
  const pythonProcess = spawn('python', [scriptPath], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  // JSON 데이터를 UTF-8로 인코딩하여 Python 스크립트의 stdin으로 전달
  const jsonString = JSON.stringify(questionMap);
  logger.debug(`Sending to Python script: ${jsonString}`); // Python으로 보내는 데이터 확인

  pythonProcess.stdin.write(jsonString, 'utf-8');
  pythonProcess.stdin.end();

  // Python 스크립트 결과 수신
  let data = '';
  pythonProcess.stdout.on('data', (chunk) => {
    const chunkStr = chunk.toString();
    logger.debug(`Python response chunk: ${chunkStr}`);
    data += chunkStr;
    // data += iconv.decode(chunk, 'euc-kr');
  });

  pythonProcess.stdout.on('end', () => {
    try {
      const responseData = JSON.parse(data.toString('utf-8'));
      logger.info(`Sending response to client: ${JSON.stringify(responseData)}`);
      res.json(responseData);
    } catch (err) {
      logger.error(`Error parsing Python response: ${err.message}`);
      res.status(500).json({ message: 'Python script error', error: err.message });
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    const errorStr = data.toString();
    logger.error(`Python error: ${errorStr}`);
  });

  pythonProcess.on('error', (err) => {
    logger.error(`Failed to start Python process: ${err.message}`);
    res.status(500).json({ message: 'Failed to start Python process', error: err.message });
  });
});
```

의 형태로 response한다. 중간중간에 console.log()를 찍어보는 것도 좋을 것 같습니다.

### 5. react의 result_page.js에서

```javascript
  // Use useEffect to fetch data
  useEffect(() => {
    async function fetchChampionData() {
      try {
        const response = await fetch(
          url+`/api/result/${username}/${tag}?line=${line}`,
          { method: 'GET', headers: { 'Content-Type': 'application/json' } }
        );

        if (response.status === 200) {
          const data = await response.json();
          setChampionList(data.champions); 
        } else {
          console.error('Request failed with status:', response.status);
        }
      } catch (error) {
        console.error('Error fetching champions:', error);
      }
    }

    if (username && tag) {
      fetchChampionData();
    }
  }, [username, tag, line]);
```
에서 get 통신을 보내고 server.js에서

```javascript
app.get('/api/result/:username/:tag', (req, res) => {
  const { username, tag } = req.params;
  const { line } = req.query;

  if (!username || !tag || !line) {
    return res.status(400).json({ message: 'Invalid request: username, tag, and line are required' });
  }

  let champions = ['아트록스', '아리', '그라가스'];


  // python spawn



  res.status(200).json({
    message: 'Data processed successfully',
    champions: champions, // 클라이언트로 전송할 champions 데이터
    'record-based': true, // 예시로 추가한 필드
  });
});
```

를 보내고 있다.

# collaborate filtering python 적용

whatchamp/server.js 에서

```javascript
app.get('/api/result/:username/:tag', (req, res) => {
  const { username, tag } = req.params;
  const { line } = req.query;

  if (!username || !tag || !line) {
    return res.status(400).json({ message: 'Invalid request: username, tag, and line are required' });
  }

  const userInfo = {
    username: username,
    tag: tag,
    line: line
  };

  const scriptPath = path.join(__dirname, 'python', 'temp.py');  // 예시: 현재 디렉토리 기준으로 python 폴더 내부
  const pythonProcess = spawn('python', [scriptPath], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  // JSON 데이터를 UTF-8로 인코딩하여 Python 스크립트의 stdin으로 전달
  const jsonString = JSON.stringify(userInfo);
  logger.debug(`Sending to Python script: ${jsonString}`); // Python으로 보내는 데이터 확인

  pythonProcess.stdin.write(jsonString, 'utf-8');
  pythonProcess.stdin.end();

  // Python 스크립트 결과 수신
  let data = '';
  pythonProcess.stdout.on('data', (chunk) => {
    const chunkStr = chunk.toString();
    logger.debug(`Python response chunk: ${chunkStr}`);
    data += chunkStr;
    // data += iconv.decode(chunk, 'euc-kr');
  });

  pythonProcess.stdout.on('end', () => {
    try {
      const responseData = JSON.parse(data.toString('utf-8'));
      logger.info(`Sending response to client: ${JSON.stringify(responseData)}`);
      res.status(200).json(responseData);
    } catch (err) {
      logger.error(`Error parsing Python response: ${err.message}`);
      res.status(500).json({ message: 'Python script error', error: err.message });
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    const errorStr = data.toString();
    logger.error(`Python error: ${errorStr}`);
  });

  pythonProcess.on('error', (err) => {
    logger.error(`Failed to start Python process: ${err.message}`);
    res.status(500).json({ message: 'Failed to start Python process', error: err.message });
  });
});
```

로, username, tag, line을 묶어 userInfo를 </br>
  pythonProcess.stdin.write(jsonString, 'utf-8'); </br>
  pythonProcess.stdin.end(); </br>
의 형태로 인풋을 주고 있음.

이는 파이썬 temp.py에서

```python
import numpy as np
import pandas as pd
import json
import sys
import re
import io
import os

# stdin의 인코딩을 UTF-8로 재설정
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

current_dir = os.path.dirname(os.path.abspath(__file__))

def main():
    try:
        # JSON 데이터 직접 로드
        json_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", file=sys.stderr)
        sys.exit(1)


    """
    input으로 json_data가 들어갑니다. 
    json_data는 username, tag, line 세 가지 정보를 가지고 있습니다.

    이 사이에 파이썬 추가 하시거나 아니면 직접 만드셔도 되고,

    아웃풋으로 champions를 주시면 바로 작동 가능할 것 같습니다.
    """

    
    # 챔피언 정보를 JSON으로 출력
    response_data = {
        "message": "Data received successfully",
        "champions": ['가렌', '갈리오', '갱플랭크']
        # "champions": champions
    }
    if json_data['tag'] == "KR3":
        response_data['champions'] = ['알리스타', '브라움', '마오카이']
    
    # ensure_ascii=False를 사용하여 한글이 제대로 출력되도록 함
    print(json.dumps(response_data, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

로 json_data를 받아 response_data의 champions를 수정하면 끝임. </br>
예시로 json_data['tag'] == "KR3"일 경우 </br>
제 서버에서는 잘 동작했습니다. </br>
# jepetolee_FINAL-VERSION
# jepetolee_FINAL-VERSION
