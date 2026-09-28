<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>오늘의 성경 QT</title>
    <!-- 구글 폰트 -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4F46E5;
            --primary-hover: #4338CA;
            --bg-color: #F3F4F6;
            --card-bg: #FFFFFF;
            --text-main: #1F2937;
            --text-sub: #6B7280;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 480px;
            background: var(--card-bg);
            border-radius: 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
            padding: 32px 24px;
        }

        .header {
            text-align: center;
            margin-bottom: 28px;
        }

        .subtitle-tag {
            display: inline-block;
            font-size: 12px;
            font-weight: 600;
            color: var(--primary);
            background-color: #EEF2FF;
            padding: 4px 12px;
            border-radius: 20px;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }

        .title {
            font-size: 24px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 8px;
        }

        .description {
            font-size: 14px;
            color: var(--text-sub);
            line-height: 1.5;
        }

        .action-area {
            margin-bottom: 24px;
        }

        .btn-fetch {
            width: 100%;
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 16px 20px;
            border-radius: 14px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
        }

        .btn-fetch:hover {
            background-color: var(--primary-hover);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(79, 70, 229, 0.3);
        }

        .btn-fetch svg {
            width: 20px;
            height: 20px;
            fill: none;
            stroke: currentColor;
            stroke-width: 2;
        }

        .status-msg {
            font-size: 15px;
            color: var(--primary);
            text-align: center;
            margin: 16px 0;
            font-weight: 700;
        }

        .content-section {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .card {
            background-color: #F9FAFB;
            border: 1px solid #F3F4F6;
            border-radius: 16px;
            padding: 20px;
            transition: all 0.2s ease;
        }

        .card-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 16px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 10px;
        }

        .card-body {
            font-size: 14px;
            color: #4B5563;
            line-height: 1.6;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>

    <div class="container">
        <!-- 헤더 영역 -->
        <div class="header">
            <span class="subtitle-tag">Daily Bible Devotional</span>
            <h1 class="title">오늘의 성경 QT</h1>
            <p class="description">오늘 나에게 주시는 말씀과<br>삶을 정돈하는 묵상</p>
        </div>

        <!-- 버튼 영역 -->
        <div class="action-area">
            <button class="btn-fetch" id="fetchBtn">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                </svg>
                오늘의 말씀 읽기
            </button>
        </div>

        <!-- 로딩/상태 메시지 -->
        <div class="status-msg" id="statusMsg">버튼을 눌러 오늘의 말씀을 확인하세요.</div>

        <!-- 결과 카드 영역 -->
        <div class="content-section" id="resultArea">
            <div class="card">
                <div class="card-title">📖 성경 본문</div>
                <div class="card-body" id="verse">버튼을 누르면 오늘의 성경 말씀이 여기에 출력됩니다.</div>
            </div>

            <div class="card">
                <div class="card-title">💡 말씀 해석</div>
                <div class="card-body" id="interpretation">본문 내용이 여기에 표시됩니다.</div>
            </div>

            <div class="card">
                <div class="card-title">❓ 오늘 삶에 던지는 질문</div>
                <div class="card-body" id="questions">본문 내용이 여기에 표시됩니다.</div>
            </div>

            <div class="card">
                <div class="card-title">🙏 오늘의 마무리 기도</div>
                <div class="card-body" id="prayer">본문 내용이 여기에 표시됩니다.</div>
            </div>
        </div>
    </div>

    <!-- 자바스크립트 연동 코드 -->
    <script>
        // ⚠️ [필수] 본인의 실제 Render 백엔드 주소로 입력하세요! (예: https://my-qt-app.onrender.com)
        const RENDER_SERVER_URL = "https://your-app-name.onrender.com"; 

        const fetchBtn = document.getElementById('fetchBtn');
        const statusMsg = document.getElementById('statusMsg');
        const verse = document.getElementById('verse');
        const interpretation = document.getElementById('interpretation');
        const questions = document.getElementById('questions');
        const prayer = document.getElementById('prayer');

        fetchBtn.addEventListener('click', async () => {
            fetchBtn.disabled = true;
            fetchBtn.style.opacity = "0.7";
            statusMsg.innerText = "⏳ 말씀과 묵상을 불러오는 중입니다... (약 5~10초 소요)";

            try {
                const response = await fetch(`${RENDER_SERVER_URL}/api/daily-qt`);
                
                if (!response.ok) {
                    throw new Error(`서버 응답 에러: ${response.status}`);
                }

                const data = await response.json();

                statusMsg.innerText = `📖 ${data.reference}`;
                verse.innerText = data.verse || "성경 본문을 불러오지 못했습니다.";
                
                let questionText = "";
                if (Array.isArray(data.questions)) {
                    questionText = data.questions.map((q, idx) => `${idx + 1}. ${q}`).join("\n\n");
                } else {
                    questionText = data.questions;
                }

                interpretation.innerText = data.exposition || "해석 내용을 불러오지 못했습니다.";
                questions.innerText = questionText || "질문 내용을 불러오지 못했습니다.";
                prayer.innerText = data.prayer || "기도문 내용을 불러오지 못했습니다.";

            } catch (error) {
                console.error("Fetch Error:", error);
                statusMsg.innerText = "❌ 불러오기에 실패했습니다. Render 서버 주소 및 서버 상태를 확인해주세요.";
            } finally {
                fetchBtn.disabled = false;
                fetchBtn.style.opacity = "1";
            }
        });
    </script>
</body>
</html>
