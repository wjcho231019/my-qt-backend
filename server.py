import os
import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from fastapi import FastAPI, Query
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
    "Philemon": "빌레몬서", 
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

def get_korea_date_info():
    """
    한국 시간 기준 오늘 날짜 / 요일 / 계절 반환
    """
    now = datetime.now(ZoneInfo("Asia/Seoul"))

    weekday_names = [
        "월요일",
        "화요일",
        "수요일",
        "목요일",
        "금요일",
        "토요일",
        "일요일"
    ]

    month = now.month

    if 3 <= month <= 5:
        season = "봄"
    elif 6 <= month <= 8:
        season = "여름"
    elif 9 <= month <= 11:
        season = "가을"
    else:
        season = "겨울"

    return (
        now.strftime("%Y-%m-%d"),
        weekday_names[now.weekday()],
        season
    )


def get_bible_passage(book, chapter, start_verse, end_verse):
    """
    AI가 선택한 장절을 실제 bible.json에서 가져온다.
    AI가 성경 본문 자체를 작성하지 않도록 하기 위한 함수.
    """

    book_data = BIBLE_DATA.get(book)

    if not book_data:
        return None

    chapter_data = book_data.get(str(chapter))

    if not chapter_data:
        return None

    if start_verse > end_verse:
        return None

    passage_text = []

    for verse_num in range(start_verse, end_verse + 1):
        text = chapter_data.get(str(verse_num))

        # 실제 bible.json에 존재하지 않는 절이면 실패 처리
        if not text:
            return None

        passage_text.append(f"{verse_num}절: {text}")

    reference = f"{book} {chapter}:{start_verse}-{end_verse}"
    full_text = "\n".join(passage_text)

    return reference, full_text


def get_recent_daily_references(limit=30):
    """
    날짜별로 저장된 최근 QT 본문을 가져온다.
    같은 말씀이 자주 반복되는 것을 방지하기 위한 용도.
    """

    daily_items = []

    for key, data in QT_CACHE.items():

        # 2026-10-06 형태의 날짜 Key만 확인
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(key)):
            continue

        if not isinstance(data, dict):
            continue

        reference = data.get("reference")

        if reference:
            daily_items.append((key, reference))

    # 최근 날짜부터 정렬
    daily_items.sort(key=lambda x: x[0], reverse=True)

    return [
        reference
        for _, reference in daily_items[:limit]
    ]


def select_daily_passage_by_ai(
    api_key,
    today_date,
    weekday,
    season,
    extra_recent=None
):
    """
    Gemini가 오늘 묵상하기 적절한 성경 '장절만' 선택한다.

    실제 성경 본문은 Gemini가 작성하지 않고
    bible.json에서 가져온다.
    """

    genai.configure(api_key=api_key)

    # 서버에 남아 있는 최근 QT 기록
    recent_references = get_recent_daily_references(30)

    # 추후 HTML localStorage에서 최근 기록을 전달할 경우 같이 사용
    if extra_recent:
        for reference in extra_recent:
            if reference not in recent_references:
                recent_references.append(reference)

    recent_text = (
        "\n".join(f"- {ref}" for ref in recent_references)
        if recent_references
        else "없음"
    )

    available_books = ", ".join(BIBLE_DATA.keys())

    generation_config = genai.GenerationConfig(
        response_mime_type="application/json",
        temperature=0.4
    )

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config
    )

    prompt = f"""
당신은 성경 전체의 문맥을 이해하고
매일 묵상할 본문을 선정하는 성경 QT 가이드입니다.

오늘 날짜와 최근 선정 기록을 참고하여
오늘 하루 묵상하기 가장 적절한 성경 본문 하나를 선택하세요.

[오늘 정보]

날짜: {today_date}
요일: {weekday}
계절: {season}

[최근 사용한 본문]

{recent_text}

[사용 가능한 성경 책]

{available_books}

[본문 선정 원칙]

1. 반드시 하나의 성경 책, 하나의 장 안에서 선택하세요.

2. 본문의 시작과 끝이 자연스러운 하나의 문맥 또는 의미 단위가 되도록 하세요.

3. 이야기의 중간, 예수님의 말씀 중간,
   논리 전개의 중간에서 갑자기 시작하거나 끝내지 마세요.

4. 본문 길이는 6~15절이어야 합니다.

5. 가능하면 8~12절 정도를 우선하세요.

6. 단순히 절 수를 맞추는 것보다
   문맥이 자연스럽게 완결되는 것을 더 중요하게 생각하세요.

7. 오늘 날짜, 요일, 계절은 참고할 수 있지만
   억지로 의미를 연결하지 마세요.

8. 성탄절, 부활절, 고난주간 등
   날짜상 명확하게 관련된 기독교 절기가 있다면
   자연스럽게 고려할 수 있습니다.

9. 최근 사용한 본문은 가급적 다시 선택하지 마세요.

10. 시편, 잠언, 이사야, 요한복음 등
    일부 유명한 성경에 지나치게 편중되지 않도록 하고,
    성경 전체를 다양하게 활용하세요.

11. 존재하지 않는 장이나 절을 만들지 마세요.

12. book 값은 반드시 위 [사용 가능한 성경 책]에 있는
    한글 책 이름을 정확하게 사용하세요.

성경 본문 내용 자체는 작성하지 마세요.
장절 정보만 선택하세요.

다음 JSON 구조로만 응답하세요.

{{
    "book": "로마서",
    "chapter": 8,
    "start_verse": 31,
    "end_verse": 39
}}
"""

    # AI가 잘못된 장절을 선택할 가능성에 대비하여 최대 2번 검증
    last_error = None

    for attempt in range(2):

        try:
            print("[Gemini 1/2] 오늘의 본문 선정 요청 시작")

            response = model.generate_content(
                prompt,
                request_options={"timeout": 25}
            )

            print("[Gemini 1/2] 오늘의 본문 선정 응답 완료")

            res_text = response.text.strip()

            res_text = re.sub(r"^```json\s*", "", res_text)
            res_text = re.sub(r"^```\s*", "", res_text)
            res_text = re.sub(r"\s*```$", "", res_text)
            res_text = re.sub(r',\s*([\]}])', r'\1', res_text)

            selected = json.loads(res_text)

            book = str(selected.get("book", "")).strip()
            chapter = int(selected.get("chapter"))
            start_verse = int(selected.get("start_verse"))
            end_verse = int(selected.get("end_verse"))

            verse_count = end_verse - start_verse + 1

            # 최소 6절 ~ 최대 15절만 허용
            if verse_count < 6 or verse_count > 15:
                last_error = (
                    f"본문 길이가 기준을 벗어났습니다: "
                    f"{verse_count}절"
                )
                continue

            # 실제 bible.json에 존재하는 본문인지 검증
            passage = get_bible_passage(
                book,
                chapter,
                start_verse,
                end_verse
            )

            if passage:
                return passage

            last_error = (
                f"bible.json에서 본문을 찾을 수 없습니다: "
                f"{book} {chapter}:{start_verse}-{end_verse}"
            )

        except Exception as e:
            last_error = str(e)

    raise ValueError(
        f"AI가 유효한 오늘의 본문을 선정하지 못했습니다. "
        f"마지막 오류: {last_error}"
    )

@app.get("/api/daily-qt")
async def get_daily_qt(
    topic: Optional[str] = Query(None),
    recent: Optional[str] = Query(None)
):
    api_key = os.environ.get("GEMINI_API_KEY")

    # -------------------------------------------------------------
    # 1. 사용자가 검색어(topic)를 입력한 경우
    # -------------------------------------------------------------
    if topic:
        if not api_key:
            return {
                "reference": "검색 실패",
                "verse": "GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.",
                "exposition": "API 키 설정을 확인해주세요.",
                "questions": ["Render 환경 변수를 확인해주세요."],
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
            당신은 신학적 깊이와 따뜻한 마음을 가진 성경 묵상 가이드입니다.
            사용자가 제시한 아래 고민/상황에 가장 어울리고 위로와 힘이 되는 성경 구절(개역개정) 1개를 추천하고, 그에 맞는 본문과 묵상을 작성하세요.

            [사용자의 고민/상황]
            "{topic}"

            [작성 조건]
            1. reference: 추천한 성경 장절 (예: 이사야 41:10)
            2. verse: 추천한 성경 본문 전체 텍스트 (절 번호 포함)
            3. exposition: 위 성경 구절의 핵심 메시지와 구체적 의미를 3-4문장으로 따뜻하게 해석하세요.
            4. questions: 성경 지식을 묻는 시험 문제(예: ~은 무엇인가요?, ~의 순서는?)가 절대 아니라, 독자가 자신의 삶과 마음을 돌아볼 수 있는 '개인적 묵상 및 적용 질문' 2가지를 작성하세요. (~했나요?, ~하고 계신가요? 등 개인의 삶에 비추어보게 질문할 것)
            5. prayer: 위 성경 구절의 메시지를 담아 하나님께 드리는 결단의 기도문을 작성하세요.

            다음 JSON 구조로만 응답하세요:
            {{
              "reference": "성경 장절",
              "verse": "성경 본문 텍스트",
              "exposition": "성경 구절 해설",
              "questions": [
                "개인적 묵상 및 적용 질문 1",
                "개인적 묵상 및 적용 질문 2"
              ],
              "prayer": "본문 맞춤 기도문"
            }}
            """

            print("[Gemini 1/2] 오늘의 본문 선정 요청 시작")

            response = model.generate_content(
                prompt,
                request_options={"timeout": 25}
            )

            print("[Gemini 1/2] 오늘의 본문 선정 응답 완료")
            res_text = response.text.strip()
            res_text = re.sub(r"^```json\s*", "", res_text)
            res_text = re.sub(r"^```\s*", "", res_text)
            res_text = re.sub(r"\s*```$", "", res_text)

            # ⬇️ 아래 한 줄을 새로 추가하세요! (불필요한 쉼표 제거)
            res_text = re.sub(r',\s*([\]}])', r'\1', res_text)

            ai_result = json.loads(res_text)

            return {
                "reference": ai_result.get("reference", "추천 말씀"),
                "verse": ai_result.get("verse", ""),
                "exposition": ai_result.get("exposition", ""),
                "questions": ai_result.get("questions", []),
                "prayer": ai_result.get("prayer", "")
            }
        except Exception as e:
            err_msg = str(e)
            print("Gemini API Error (Topic Search):", err_msg)
            return {
                "reference": "검색 오류",
                "verse": "말씀을 불러오는 중 오류가 발생했습니다.",
                "exposition": f"Gemini API 호출 중 에러 발생: {err_msg}",
                "questions": ["잠시 후 다시 시도해 주세요."],
                "prayer": "오류가 해결되면 실시간 맞춤 묵상이 출력됩니다."
            }

        # -------------------------------------------------------------
    # 2. 검색어가 없는 일반 '오늘의 QT' 모드
    #    날짜 기준 고정 + AI 본문 선정 + bible.json 실제 본문 사용
    # -------------------------------------------------------------

    today_date, weekday, season = get_korea_date_info()

    # -------------------------------------------------------------
    # 1) 오늘 이미 만들어진 QT가 있으면 그대로 반환
    # -------------------------------------------------------------
    cached_data = QT_CACHE.get(today_date)

    if isinstance(cached_data, dict):

        if cached_data.get("reference") and cached_data.get("verse"):

            print(
                f"[Daily Cache Hit] {today_date} "
                f"- {cached_data.get('reference')}"
            )

            return {
                "date": today_date,
                "reference": cached_data.get("reference", ""),
                "verse": cached_data.get("verse", ""),
                "exposition": cached_data.get("exposition", ""),
                "questions": cached_data.get("questions", []),
                "prayer": cached_data.get("prayer", "")
            }

    # -------------------------------------------------------------
    # 2) API Key 확인
    # -------------------------------------------------------------
    if not api_key:
        return {
            "date": today_date,
            "reference": "오늘의 말씀 생성 실패",
            "verse": "",
            "exposition": "GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.",
            "questions": [
                "Render 환경 변수를 확인해주세요.",
                "API Key 설정을 확인해주세요."
            ],
            "prayer": "서버 환경변수 설정이 필요합니다."
        }

    # -------------------------------------------------------------
    # 3) 브라우저가 보내준 최근 본문이 있으면 읽기
    #
    #    예:
    #    recent=시편 23:1-6|마태복음 6:25-34
    #
    #    현재 HTML에서는 아직 보내지 않아도 정상 작동함.
    # -------------------------------------------------------------
    extra_recent = []

    if recent:
        extra_recent = [
            item.strip()
            for item in recent.split("|")
            if item.strip()
        ]

    try:
        # ---------------------------------------------------------
        # 4) Gemini에게 오늘 묵상할 성경 장절 선정 요청
        #
        #    여기서는 성경 본문을 Gemini가 작성하지 않는다.
        #    Gemini는 오직 범위만 선정한다.
        # ---------------------------------------------------------
        reference, verse_text = select_daily_passage_by_ai(
            api_key=api_key,
            today_date=today_date,
            weekday=weekday,
            season=season,
            extra_recent=extra_recent
        )

        print(
            f"[Daily Passage Selected] "
            f"{today_date} / {weekday} / {reference}"
        )

        # ---------------------------------------------------------
        # 5) 선정된 실제 bible.json 본문을 가지고
        #    QT 해설 / 질문 / 기도 생성
        # ---------------------------------------------------------
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
당신은 신학적 깊이와 따뜻한 마음을 가진
성경 묵상 가이드입니다.

아래 주어진 성경 본문을 직접 읽고 분석하여
이 본문 내용에 충실한 오늘의 QT를 작성하세요.

[오늘 정보]

날짜: {today_date}
요일: {weekday}
계절: {season}

[성경 본문]

구절 위치:
{reference}

본문 내용:

{verse_text}

[작성 조건]

1. exposition

본문의 역사적·문맥적 의미를 훼손하지 않으면서
핵심 메시지를 설명하세요.

단순히 본문을 다시 요약하는 데 그치지 말고
오늘을 살아가는 사람이 이해할 수 있도록
3~4문장으로 따뜻하고 구체적으로 작성하세요.

2. questions

성경 지식을 묻는 시험 문제가 아니라
독자가 자신의 삶과 마음을 돌아보게 하는
개인적인 묵상 및 적용 질문 2개를 작성하세요.

본문 내용과 직접 연결된 질문이어야 합니다.

3. prayer

본문의 핵심 메시지를 바탕으로
하나님께 드리는 짧고 자연스러운
결단의 기도문을 작성하세요.

4. 본문에 없는 내용을
마치 성경에 기록되어 있는 것처럼 만들지 마세요.

다음 JSON 구조로만 응답하세요.

{{
    "exposition": "성경 구절 해설",
    "questions": [
        "개인적 묵상 및 적용 질문 1",
        "개인적 묵상 및 적용 질문 2"
    ],
    "prayer": "본문 맞춤 기도문"
}}
"""

        print("[Gemini 2/2] QT 해설 생성 요청 시작")

        response = model.generate_content(
            prompt,
            request_options={"timeout": 30}
        )

        print("[Gemini 2/2] QT 해설 생성 응답 완료")

        res_text = response.text.strip()

        res_text = re.sub(r"^```json\s*", "", res_text)
        res_text = re.sub(r"^```\s*", "", res_text)
        res_text = re.sub(r"\s*```$", "", res_text)
        res_text = re.sub(r',\s*([\]}])', r'\1', res_text)

        ai_result = json.loads(res_text)

        # ---------------------------------------------------------
        # 6) 오늘 날짜를 Key로 전체 QT 저장
        #
        # 기존:
        # QT_CACHE["로마서 8:31-39"]
        #
        # 변경:
        # QT_CACHE["2026-10-06"]
        # ---------------------------------------------------------
        raw_questions = ai_result.get("questions", [])

        if not isinstance(raw_questions, list):
            raw_questions = []

        clean_questions = raw_questions[:2]

        daily_result = {
            "date": today_date,
            "reference": reference,
            "verse": verse_text,
            "exposition": ai_result.get("exposition", ""),
            "questions": clean_questions,
            "prayer": ai_result.get("prayer", "")
        }

        QT_CACHE[today_date] = daily_result

        save_cache()

        return daily_result

    except Exception as e:

        err_msg = str(e)

        print(
            "Gemini Daily QT Error:",
            err_msg
        )

        return {
            "date": today_date,
            "reference": "오늘의 말씀 생성 오류",
            "verse": "",
            "exposition": (
                f"오늘의 말씀을 준비하는 중 "
                f"오류가 발생했습니다: {err_msg}"
            ),
            "questions": [
                "잠시 후 다시 시도해 주세요."
            ],
            "prayer": (
                "오류가 해결되면 "
                "오늘의 묵상이 출력됩니다."
            )
        }
