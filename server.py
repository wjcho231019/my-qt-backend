import os
import json
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# 영어 성경 이름을 한글 성경 이름으로 변환하는 매핑 (공백 제거 대응)
ENGLISH_TO_KOREAN = {
    "Genesis": "창세기", "Exodus": "출애굽기", "Leviticus": "레위기", "Numbers": "민수기", "Deuteronomy": "신명기",
    "Joshua": "여호수아", "Judges": "사사기", "Ruth": "룻기", 
    "1Samuel": "사무엘상", "2Samuel": "사무엘하", "1Kings": "열왕기상", "2Kings": "열왕기하", 
    "1Chronicles": "역대상", "2Chronicles": "역대하", "Ezra": "에스라", "Nehemiah": "느헤미야", 
    "Esther": "에스더", "Job": "욥기", "Psalms": "시편", "Psalm": "시편", "Proverbs": "잠언", 
    "Ecclesiastes": "전도서", "SongofSolomon": "아가", "SongofSongs": "아가", "Isaiah": "이사야", 
    "Jeremiah": "예레미야", "Lamentations": "예레미야애가", "Ezekiel": "에스겔", "Daniel": "다니엘", 
    "Hosea": "호세아", "Joel": "요엘", "Amos": "아모스", "Obadiah": "오바다", "Jonah": "요나", 
    "Micah": "미가", "Nahum": "나훔", "Habakkuk": "하박국", "Zephaniah": "스파냐", "Haggai": "학개", 
    "Zechariah": "스카리아", "Malachi": "말라기", "Matthew": "마태복음", "Mark": "마가복음", 
    "Luke": "누가복음", "John": "요한복음", "Acts": "사도행전", "Romans": "로마서", 
    "1Corinthians": "고린도전서", "2Corinthians": "고린도후서", "Galatians": "갈라디아서", 
    "Ephesians": "에베소서", "Philippians": "빌립보서", "Colossians": "골로새서", 
    "1Thessalonians": "데살로니가전서", "2Thessalonians": "데살로니가후서", 
    "1Timothy": "디모데전서", "2Timothy": "디모데후서", "Titus": "디도서", 
    "Philemon": "빌레몬서", "Hebrews": "히브리서", "James": "야고보서", 
    "1Peter": "베드로전서", "2Peter": "베드로후서", "1John": "요한1서", 
    "2John": "요한2서", "3John": "요한3서", "Jude": "유다서", "Revelation": "요한계시록"
}

BIBLE_DATA = {}

# bible.json 파싱 로직
try:
    with open("bible.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    for book_item in raw_data:
        raw_book = str(book_item.get("book", ""))
        # 공백 제거 후 한글 매핑 찾기
        clean_key = raw_book.replace(" ", "")
        book_name = ENGLISH_TO_KOREAN.get(clean_key, raw_book)
        
        if book_name not in BIBLE_DATA:
            BIBLE_DATA[book_name] = {}
            
        for ch_item in book_item.get("chapters", []):
            ch_num = str(ch_item.get("chapter", ""))
            if ch_num not in BIBLE_DATA[book_name]:
                BIBLE_DATA[book_name][ch_num] = {}
                
            for v_item in ch_item.get("verses", []):
                v_num = str(v_item.get("verse", ""))
                v_text = str(v_item.get("text", ""))
                BIBLE_DATA[book_name][ch_num][v_num] = v_text
except Exception as e:
    print("JSON Load Error:", e)

@app.get("/")
def read_root():
    return {"status": "QT Backend Server is Running!"}

def get_random_bible_passage():
    if not BIBLE_DATA:
        return "요한복음 3:16", "16절: 하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니 이는 그를 믿는 자마다 멸망하지 않고 영생을 얻게 하려 하심이라"

    book = random.choice(list(BIBLE_DATA.keys()))
    chapter = random.choice(list(BIBLE_DATA[book].keys()))
    verses_dict = BIBLE_DATA[book][chapter]
    
    verse_numbers = [int(v) for v in verses_dict.keys() if str(v).isdigit()]
    if not verse_numbers:
        return "요한복음 3:16", "16절: 하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니..."
        
    verse_numbers.sort()
    
    start_v = random.choice(verse_numbers)
    end_v = min(start_v + random.randint(1, 3), max(verse_numbers))
    
    passage_text = []
    for v_num in range(start_v, end_v + 1):
        text = verses_dict.get(str(v_num), "")
        if text:
            passage_text.append(f"{v_num}절: {text}")
            
    reference = f"{book} {chapter}:{start_v}" if start_v == end_v else f"{book} {chapter}:{start_v}-{end_v}"
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
        print("AI generation error:", e)
        return {
            "reference": reference,
            "verse": verse_text,
            "exposition": f"'{reference}' 말씀에 담긴 뜻을 깊이 묵상해 보세요.",
            "questions": ["오늘 말씀에서 가장 마음에 와닿은 단어는 무엇인가요?", "오늘 이 말씀을 내 삶에 어떻게 적용할 수 있을까요?"],
            "prayer": "주님, 오늘 주신 말씀을 마음에 품고 살아가게 하옵소서. 예수님의 이름으로 기도합니다. 아멘."
        }
