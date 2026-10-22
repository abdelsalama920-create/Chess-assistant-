from flask import Flask, request, render_template_string
import openai
import re
import markdown
import os

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://api.groq.com/openai/v1"

with open("All_Videos_Merged.txt", "r", encoding="utf-8") as f:
    content = f.read()
videos = re.split(r'=== عنوان الفيديو: ', content)
videos = [v for v in videos if v.strip()]

HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مساعد قناة أحمد عبد السلام</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, sans-serif; 
            background-color: #1e1e2f;
            background-image: linear-gradient(45deg, #2a2a40 25%, transparent 25%), 
                              linear-gradient(-45deg, #2a2a40 25%, transparent 25%), 
                              linear-gradient(45deg, transparent 75%, #2a2a40 75%), 
                              linear-gradient(-45deg, transparent 75%, #2a2a40 75%);
            background-size: 80px 80px;
            background-position: 0 0, 0 40px, 40px -40px, -40px 0px;
            color: #fff; margin: 0; padding: 20px; display: flex; justify-content: center;
        }
        .container { 
            width: 100%; max-width: 600px; 
            background: rgba(42, 42, 64, 0.95);
            backdrop-filter: blur(5px); padding: 20px; border-radius: 15px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1);
        }
        h1 { text-align: center; color: #4CAF50; margin-bottom: 5px; }
        .channel-btn {
            display: block; text-align: center; background: #cc0000; color: white;
            text-decoration: none; padding: 10px; border-radius: 8px; margin-bottom: 20px;
            font-weight: bold; transition: 0.3s;
        }
        .channel-btn:hover { background: #ff0000; }
        .input-group { display: flex; gap: 10px; margin-bottom: 15px; }
        input[type="text"] { 
            flex: 1; padding: 12px; border: none; border-radius: 8px; 
            box-sizing: border-box; font-size: 16px; background: #fff; color: #000; 
        }
        .mic-btn {
            background: #555; color: white; border: none; border-radius: 8px;
            padding: 0 15px; font-size: 20px; cursor: pointer; transition: 0.3s;
        }
        .mic-btn.recording { background: #e74c3c; animation: pulse 1s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        button[type="submit"] { 
            width: 100%; padding: 12px; background: #4CAF50; color: white; 
            border: none; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: bold; 
        }
        button[type="submit"]:hover { background: #45a049; }
        .answer { 
            margin-top: 20px; padding: 15px; background: rgba(59, 59, 92, 0.9); 
            border-radius: 8px; line-height: 1.8; font-size: 16px; border-right: 4px solid #4CAF50; 
            position: relative;
        }
        .speak-btn {
            background: #2980b9; color: white; border: none; border-radius: 5px;
            padding: 8px 12px; cursor: pointer; font-size: 16px; margin-bottom: 10px;
            display: flex; align-items: center; gap: 5px;
        }
        .answer h1, .answer h2, .answer h3 { color: #4CAF50; margin-top: 10px; margin-bottom: 5px; }
        .answer table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .answer th, .answer td { border: 1px solid #4CAF50; padding: 8px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>♟️ مساعد قناة أحمد عبد السلام</h1>
        <a href="https://youtube.com/@ahmedabdelsalam-53" target="_blank" class="channel-btn">
            ▶️ مشاهدة القناة على يوتيوب
        </a>

        <form method="POST" id="questionForm">
            <div class="input-group">
                <input type="text" name="question" id="questionInput" placeholder="اسأل عن الشطرنج أو فيديوهات القناة..." required autocomplete="off">
                <button type="button" class="mic-btn" id="micBtn" title="التحدث بالسؤال">🎤</button>
            </div>
            <button type="submit">إرسال السؤال</button>
        </form>
        
        {% if answer %}
        <div class="answer" id="answerBox">
            <button class="speak-btn" id="speakBtn">🔊 استمع للإجابة</button>
            <div id="answerContent">{{ answer|safe }}</div>
        </div>
        {% endif %}
    </div>

    <script>
        const micBtn = document.getElementById('micBtn');
        const questionInput = document.getElementById('questionInput');

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.lang = 'ar-SA';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            micBtn.addEventListener('click', () => {
                recognition.start();
                micBtn.classList.add('recording');
                micBtn.textContent = '🔴';
            });

            recognition.onresult = (event) => {
                const speechResult = event.results[0][0].transcript;
                questionInput.value = speechResult;
            };

            recognition.onend = () => {
                micBtn.classList.remove('recording');
                micBtn.textContent = '🎤';
            };

            recognition.onerror = (event) => {
                alert('حدث خطأ في التعرف على الصوت: ' + event.error);
                micBtn.classList.remove('recording');
                micBtn.textContent = '🎤';
            };
        } else {
            micBtn.style.display = 'none';
        }

        const speakBtn = document.getElementById('speakBtn');
        const answerContent = document.getElementById('answerContent');

        if (speakBtn) {
            speakBtn.addEventListener('click', () => {
                const textToSpeak = answerContent.innerText;
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(textToSpeak);
                utterance.lang = 'ar-SA';
                utterance.rate = 1;
                window.speechSynthesis.speak(utterance);
            });
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    if request.method == 'POST':
        q = request.form['question']
        relevant = ""
        for v in videos:
            if any(word in v for word in q.split() if len(word) > 2):
                relevant += "=== عنوان الفيديو: " + v + "\n"
        if not relevant:
            relevant = "لا يوجد نص مطابق في القناة."
        relevant = relevant[:4000]
        
        try:
            response = openai.ChatCompletion.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "أنت مساعد شطرنج خبير لقناة أحمد عبد السلام. أجب بالعربية بناءً على النصوص المرفقة أو من معرفتك العامة إن لم تجد نصاً."},
                    {"role": "user", "content": f"نصوص القناة:\n{relevant}\n\nسؤال: {q}"}
                ]
            )
            answer = markdown.markdown(response.choices[0].message.content)
        except Exception as e:
            answer = f"حدث خطأ: {str(e)}"
    return render_template_string(HTML, answer=answer)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
