import openai
import re
import arabic_reshaper
from bidi.algorithm import get_display

# دالة لإصلاح الحروف العربية في الطرفية
def fix_ar(text):
    return get_display(arabic_reshaper.reshape(str(text)))

# مفتاح Groq الخاص بك
openai.api_key = "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"
openai.api_base = "https://api.groq.com/openai/v1"

# ألوان للواجهة
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

print(CYAN + "=====================================" + RESET)
print(YELLOW + fix_ar(" جاري قراءة أرشيف الفيديوهات...") + RESET)

try:
    with open("All_Videos_Merged.txt", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print(fix_ar("خطأ: لم يتم العثور على ملف All_Videos_Merged.txt"))
    exit()

videos = re.split(r'=== عنوان الفيديو: ', content)
videos = [v for v in videos if v.strip()]
print(GREEN + fix_ar(f"تم تحميل {len(videos)} فيديو بنجاح!") + RESET)
print(CYAN + "=====================================" + RESET)

while True:
    try:
        q = input(YELLOW + "\n" + fix_ar("سؤالك (أو اكتب 'خروج' للإنهاء): ") + RESET)
        if q == 'خروج':
            break
        if not q.strip():
            continue

        relevant = ""
        for v in videos:
            if any(word in v for word in q.split() if len(word) > 2):
                relevant += "=== عنوان الفيديو: " + v + "\n"

        if not relevant:
            relevant = "لم أجد نصاً مطابقاً تماماً، هذه معلومات عامة."

        relevant = relevant[:4000]

        print(CYAN + fix_ar("جاري التفكير...") + RESET)
        
        response = openai.ChatCompletion.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "أنت مساعد شطرنج خبير. أجب على سؤال المستخدم باللغة العربية بناءً على النصوص المرفقة فقط. كن دقيقاً في ذكر النقلات إن وجدت."},
                {"role": "user", "content": f"النصوص:\n{relevant}\n\nالسؤال: {q}"}
            ]
        )
        print(GREEN + "\n" + fix_ar("الإجابة:") + RESET)
        print(fix_ar(response.choices[0].message.content))
        print(CYAN + "-" * 40 + RESET)
    except Exception as e:
        print("\033[91m" + fix_ar("حدث خطأ: ") + str(e) + RESET)
