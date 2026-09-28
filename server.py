import os
import json
import random
import re
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

# 영어 성경 이름을 한글 성경 이름으로 변환 매핑
ENGLISH_TO_KOREAN = {
    # 구약 (39권)
    "Genesis": "창세기", 
    "Exodus": "출애굽기", 
    "Leviticus": "레위기", 
    "Numbers": "민수기", 
    "Deuteronomy": "신명기",
    "Joshua": "여호수아", 
    "Judges": "사사기", 
    "Ruth": "룻기", 
    "1Samuel": "사무엘상", 
    "2Samuel": "사무엘하", 
    "1Kings": "열왕기상", 
    "2Kings": "열왕기하", 
    "1Chronicles": "역대상", 
    "2Chronicles": "역대하", 
    "Ezra": "에스라", 
    "Nehemiah": "느헤미야", 
    "Esther": "에스더", 
    "Job": "욥기", 
    "Psalms": "시편", 
    "Psalm": "시편", 
    "Proverbs": "잠언", 
    "Ecclesiastes": "전도서", 
    "SongofSolomon": "아가", 
    "SongofSongs": "아가", 
    "Isaiah": "이사야", 
    "Jeremiah": "예레미야", 
    "Lamentations": "예레미야애가", 
    "Ezekiel": "에스겔", 
    "Daniel": "다니엘", 
    "Hosea": "호세아", 
    "Joel": "요엘", 
    "Amos": "아모스", 
    "Obadiah": "오바다", 
    "Jonah": "요나", 
    "Micah": "미가", 
    "Nahum": "나훔", 
    "Habakkuk": "하박국", 
    "Zephaniah": "스바냐", 
    "Haggai": "학개", 
    "Zechariah": "스가랴", 
    "Malachi": "말라기",

    # 신약 (27권)
    "Matthew": "마태복음", 
    "Mark": "마가복음", 
    "Luke": "누가복음", 
    "John": "요한복음", 
    "Acts": "사도행전", 
    "Romans": "로마서", 
    "1Corinthians": "고린도전서", 
    "2Corinthians": "고린도후서", 
    "Galatians": "갈라디아서", 
    "Ephesians": "에베소서", 
    "Philippians": "빌립보서", 
    "Colossians": "골로새서", 
    "1Thessalonians": "데살로니가전서", 
    "2Thessalonians": "데살로니가후서", 
    "1Timothy": "디모데전서", 
    "2Timothy": "디모데후서", 
    "Titus": "디도서", 
    "Philemon": "빌립보서", 
    "Hebrews": "히브리서", 
    "James": "야고보서", 
    "1Peter": "베드로전서", 
    "2Peter": "베드로후서", 
    "1John": "요한일서", 
    "2John": "요한이서", 
    "3John": "요한삼서", 
    "Jude": "유다서", 
    "Revelation": "요한계시록"
}

BIBLE_DATA = {}
QT_CACHE = {}
CACHE_FILE = "qt_cache.json"

# 캐시 파일 불러오기
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            QT_CACHE = json.load(f)
    except Exception:
        QT_CACHE = {}

def save_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(QT_CACHE, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Cache save error:", e)

# bible.json 데이터 로드
try:
    with open("bible.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    for book_item in raw_data:
        raw_book = str(book_item.get("book", ""))
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
        return "요한복음 3:16", "16절: 하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니..."

    book = random.choice(list(BIBLE_DATA.keys()))
    chapter = random.choice(list(BIBLE_DATA[book].keys()))
    verses_dict = BIBLE_DATA[book][chapter]
    
    verse_numbers = [int(v) for v in verses_dict.keys() if str(v).isdigit()]
    if not verse_numbers:
        return "요한복음 3:16", "16절: 하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니..."
        
    verse_numbers.sort()
    max_v = max(verse_numbers)
    
    target_count = random.randint(8, 12)
    valid_starts = [v for v in verse_numbers if max_v - v + 1 >= 6]
    if not valid_starts:
        valid_starts = verse_numbers
        
    start_v = random.choice(valid_starts)
    end_v = min(start_v + target_count - 1, max_v)
    
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
    
    # 1. 이미 해석해 둔 구절(캐시)이 있는지 확인
    if reference in QT_CACHE:
        print(f"[Cache Hit] '{reference}' - 기존 생성된 해석을 재사용합니다.")
        cached_data = QT_CACHE[reference]
        return {
            "reference": reference,
            "verse": verse_text,
            "exposition": cached_data.get("exposition"),
            "questions": cached_data.get("questions"),
            "prayer": cached_data.get("prayer")
        }

    # 2. 캐시에 없으면 제미나이 API 호출
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "reference": reference,
            "verse": verse_text,
            "exposition": "GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.",
            "questions": ["Render 환경 변수를 확인해주세요.", "API Key 설정을 확인해주세요."],
            "prayer": "서버 환경변수 설정이 필요합니다."
        }
        
    try:
        genai.configure(api_key=api_key)
        
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7
        )
        
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=generation_config
        )
        
        prompt = f"""
        당신은 따뜻하고 신학적 깊이를 갖춘 성경 묵상 가이드입니다.
        아래 [성경 구절]을 바탕으로 QT 해설, 삶의 적용 질문, 기도문을 작성하세요.

        [성경 구절]
        구절 위치: {reference}
        본문 내용:
        {verse_text}

        [작성 지침 - 질문 작성 시 필독!]
        1. exposition: 본문의 핵심 메시지와 의미를 3-4문장으로 이해하기 쉽고 따뜻하게 해석하세요.
        2. questions (★삶의 성찰 및 적용 질문 2가지★):
           - ❌ [절대 금지] 본문 사실 확인, 역사적 퀴즈, 독해력 테스트 같은 질문은 하지 마세요.
             (예: "르호보암이 누구에게 침략을 받았나요?", "금방패 대신 만들어진 것은 무엇인가요?" 등 본문에서 답을 찾는 퀴즈 금지)
           - ⭕ [필수 반영] 본문 속 상황, 인물의 행동 및 태도를 바탕으로 "나 자신과 내 일상"을 돌아보게 만드는 질문을 만드세요.
             질문 형태 예시: "본문에서 ~한 상황이 나오는데, 만약 나 자신이라면 이 상황에서 어떻게 행동했을까요?", "본문의 ~ 모습처럼, 최근 내 삶에서 소홀히 하거나 타협하고 있는 영역은 어디인가요?"
        3. prayer: 본문의 교훈을 바탕으로 오늘 하루를 살아낼 다짐과 하나님께 드리는 결단의 기도문을 작성하세요.

        다음 JSON 구조로만 응답하세요:
        {{
          "exposition": "성경 구절 해설",
          "questions": [
            "삶의 적용 및 나를 돌아보는 질문 1",
            "삶의 적용 및 나를 돌아보는 질문 2"
          ],
          "prayer": "본문 맞춤 결단 기도문"
        }}
        """
        
        response = model.generate_content(prompt)
        
        res_text = response.text.strip()
        res_text = re.sub(r"^```json\s*", "", res_text)
        res_text = re.sub(r"^```\s*", "", res_text)
        res_text = re.sub(r"\s*```$", "", res_text)
        
        ai_result = json.loads(res_text)
        
        # 3. 결과를 캐시에 저장
        QT_CACHE[reference] = ai_result
        save_cache()
        
        return {
            "reference": reference,
            "verse": verse_text,
            "exposition": ai_result.get("exposition", ""),
            "questions": ai_result.get("questions", []),
            "prayer": ai_result.get("prayer", "")
        }
    except Exception as e:
        err_msg = str(e)
        print("Gemini API Error:", err_msg)
        return {
            "reference": reference,
            "verse": verse_text,
            "exposition": f"Gemini API 호출 중 에러 발생: {err_msg}",
            "questions": ["Render의 API 키를 확인해 주세요.", "Google AI Studio 할당량을 확인해 주세요."],
            "prayer": "오류가 해결되면 실시간 맞춤 묵상이 출력됩니다."
        }
