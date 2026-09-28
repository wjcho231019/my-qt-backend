import os
import json
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

app = FastAPI()

# Vercel 프론트엔드 통신 허용 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# 1. bible.json 로드 및 데이터 구조 통일
BIBLE_DATA = {}

with open("bible.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# JSON 형식이 배열/객체 어떤 형태든 대응
if isinstance(raw_data, list):
    for item in raw_data:
        book_name = item.get("name") or item.get("book") or "성경"
        chapters = item.get("chapters", [])
        BIBLE_DATA[book_name] = {}
        for c_idx, verses in enumerate(chapters):
            c_num = str(c_idx + 1)
            BIBLE_DATA[book_name][c_num] = {}
            for v_idx, verse_text in enumerate(verses):
                v_num = str(v_idx + 1)
                BIBLE_DATA[book_name][c_num][v_num] = verse_text
elif isinstance(raw_data, dict):
    BIBLE_DATA = raw_data

def get_random_bible_passage():
    """파이썬에서 랜덤으로 책, 장, 절을 추출하는 함수"""
    book = random.choice(list(BIBLE_DATA.keys()))
    chapter = random.choice(list(BIBLE_DATA[book].keys()))
    verses_dict = BIBLE_DATA[book][chapter]
    
    verse_numbers = [int(v) for v in verses_dict.keys()]
    verse_numbers.sort()
    
    # 연속된 3~5개 절 추출
    start_v = random.choice(verse_numbers)
    end_v = min(start_v + random.randint(2, 4), max(verse_numbers))
    
    passage_text = []
    for v_num in range(start_v, end_v + 1):
        text = verses_dict.get(str(v_num), "")
        if text:
            passage_text.append(f"{v_num}절: {text}")
            
    reference = f"{book} {chapter}:{start_v}-{end_v}"
    full_text = "\n".join(passage_text)
    
    return reference, full_text

@app.get("/api/daily-qt")
async def get_daily_qt():
    reference, verse_text = get_random_bible_passage()
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    당신은 친절한 성경 묵상 도우미입니다. 
    아래 주어진 [성경 구절]을 읽고, 요구사항에 맞춰 답변을 작성해 주세요.

    [성경 구절]
    구절 위치: {reference}
    본문 내용:
    {verse_text}

    [요구사항]
    다른 추가 설명 없이 오직 아래 JSON 형식을 그대로 지켜서 응답하세요:
    {{
      "exposition": "이 말씀이 주는 핵심 메시지와 현대적 의미 (3-4문장으로 친절하게 설명)",
      "questions": [
        "오늘 나의 삶을 돌아볼 첫 번째 질문",
        "일상에서 실천할 수 있는 두 번째 질문"
      ],
      "prayer": "오늘 하루를 시작하거나 마무리할 때 드릴 따뜻한 기도문"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_json = response.text.replace("```json", "").replace("```", "").strip()
        ai_result = json.loads(cleaned_json)
        
        return {
            "reference": reference,
            "verse": verse_text,
            "exposition": ai_result.get("exposition"),
            "questions": ai_result.get("questions"),
            "prayer": ai_result.get("prayer")
        }
    except Exception as e:
        return {
            "reference": reference,
            "verse": verse_text,
            "exposition": "말씀을 묵상하며 마음속에 주시는 메시지를 생각해보세요.",
            "questions": ["오늘 말씀에서 가장 마음에 와닿은 단어는 무엇인가요?", "오늘 누구에게 사랑을 전할 수 있을까요?"],
            "prayer": "주님, 오늘 주신 말씀을 마음에 품고 살아가게 하옵소서. 예수님의 이름으로 기도합니다. 아멘."
        }