import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
# 선생님의 모듈을 불러옵니다
from compose_neis_note_module import compose_neis_note

PORT = int(os.environ.get("PORT", 10000))

# 웹 화면 (HTML/JS)
HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NEIS 기록 생성기</title>
    <style>
        body { font-family: sans-serif; padding: 20px; background: #f4f7f9; }
        .box { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }
        input, textarea, button { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { background: #007bff; color: white; border: none; font-weight: bold; cursor: pointer; }
        #output { background: #e9ecef; padding: 15px; border-radius: 5px; min-height: 100px; white-space: pre-wrap; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>📝 NEIS 기록 생성기</h2>
        <input type="text" id="event_name" placeholder="활동명 (예: 진로캠프)">
        <input type="date" id="event_date">
        <textarea id="sentences" rows="5" placeholder="핵심 문장들을 입력하세요 (엔터로 구분)"></textarea>
        <button onclick="generate()">기록 조합하기</button>
        <div id="output">결과가 여기에 표시됩니다.</div>
    </div>

    <script>
        async function generate() {
            const out = document.getElementById('output');
            out.innerText = "조합 중...";
            
            const data = {
                event_name: document.getElementById('event_name').value,
                date: document.getElementById('event_date').value,
                sentences: document.getElementById('sentences').value.split('\\n')
            };

            const res = await fetch('/api/compose', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await res.json();
            out.innerText = result.text;
        }
    </script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_UI.encode('utf-8'))

    def do_POST(self):
        if self.path == '/api/compose':
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length).decode())
            
            # 선생님의 모듈 함수 호출
            result_text = compose_neis_note(
                event_name=post_data['event_name'],
                date_obj=post_data['date'],
                ranked_sentences=post_data['sentences']
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"text": result_text}).encode())

if __name__ == "__main__":
    server = HTTPServer(('', PORT), Handler)
    print(f"Server started on {PORT}")
    server.serve_forever()
