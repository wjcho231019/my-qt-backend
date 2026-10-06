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

        /* 🟣 상단 보라색 로딩 바 스타일 */
        .top-loading-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background-color: #EEF2FF;
            overflow: hidden;
            display: none; /* 기본적으로 숨김 */
            z-index: 9999;
        }

        .top-loading-bar::before {
            content: '';
            position: absolute;
            left: -50%;
            height: 100%;
            width: 50%;
            background-color: var(--primary);
            animation: topLoadingAnim 1.2s infinite ease-in-out;
            border-radius: 2px;
        }

        @keyframes topLoadingAnim {
            0% { left: -50%; width: 30%; }
            50% { left: 25%; width: 50%; }
            100% { left: 100%; width: 30%; }
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
            display: flex;
            flex-direction: column;
            gap: 10px;
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

        /* 지난 말씀 보기 버튼 */
        .btn-history {
            width: 100%;
            background-color: #FFFFFF;
            color: var(--primary);
            border: 1px solid #C7D2FE;
            padding: 13px 20px;
            border-radius: 14px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-history:hover {
            background-color: #EEF2FF;
            border-color: var(--primary);
        }

        /* 지난 말씀 목록 */
        .history-panel {
            display: none;
            margin-bottom: 20px;
            padding: 18px;
            background-color: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 16px;
        }

        .history-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }

        .history-title {
            font-size: 16px;
            font-weight: 700;
            color: #111827;
        }

        .history-close {
            border: none;
            background: none;
            color: var(--text-sub);
            font-size: 13px;
            cursor: pointer;
        }

        .history-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .history-item {
            width: 100%;
            border: 1px solid #E5E7EB;
            background: #FFFFFF;
            border-radius: 12px;
            padding: 13px 14px;
            cursor: pointer;
            text-align: left;
            transition: all 0.2s ease;
        }

        .history-item:hover {
            border-color: #C7D2FE;
            background-color: #EEF2FF;
        }

        .history-date {
            display: block;
            font-size: 12px;
            color: var(--text-sub);
            margin-bottom: 4px;
        }

        .history-reference {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #111827;
        }

        .history-empty {
            text-align: center;
            color: var(--text-sub);
            font-size: 13px;
            padding: 20px 0;
        }

        .status-msg {
            font-size: 14px;
            color: var(--text-sub);
            text-align: center;
            margin: 16px 0;
            font-weight: 500;
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

    <!-- 🟣 화면 맨 최상단 보라색 로딩 바 -->
    <div id="topLoadingBar" class="top-loading-bar"></div>

    <div class="container">
        <!-- 헤더 영역 -->
        <div class="header">
            <span class="subtitle-tag">Daily Bible Devotional</span>
            <h1 class="title">오늘의 성경 QT</h1>
            <p class="description">오늘 나에게 주시는 말씀과<br>삶을 정돈하는 묵상</p>
        </div>

        <!-- 검색 입력 영역 -->
        <div class="search-area" style="margin-bottom: 12px; display: flex; gap: 8px;">
            <input type="text" id="topicInput" placeholder="예: 직장이 힘들 때, 마음이 불안할 때" 
                   style="flex: 1; padding: 14px; border-radius: 12px; border: 1px solid #D1D5DB; font-size: 14px; outline: none;">
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

            <button class="btn-history" id="historyBtn">
                📅 지난 말씀 보기
            </button>
        </div>

        <!-- 지난 말씀 목록 -->
        <div class="history-panel" id="historyPanel">
            <div class="history-header">
                <div class="history-title">📅 지난 말씀</div>

                <button class="history-close" id="closeHistoryBtn">
                    닫기 ✕
                </button>
            </div>

            <div class="history-list" id="historyList"></div>
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
        // ⚠️ 본인의 실제 Render 백엔드 주소로 변경하세요! (끝에 /는 뺍니다)
        const RENDER_SERVER_URL = "https://my-qt-backend.onrender.com"; 

        const fetchBtn = document.getElementById('fetchBtn');
        const topicInput = document.getElementById('topicInput');
        const topLoadingBar = document.getElementById('topLoadingBar'); // ⬅️ 로딩바 요소를 가져옴
        const statusMsg = document.getElementById('statusMsg');
        const verse = document.getElementById('verse');
        const interpretation = document.getElementById('interpretation');
        const questions = document.getElementById('questions');
        const prayer = document.getElementById('prayer');

        const historyBtn = document.getElementById('historyBtn');
        const historyPanel = document.getElementById('historyPanel');
        const historyList = document.getElementById('historyList');
        const closeHistoryBtn = document.getElementById('closeHistoryBtn');

        const QT_HISTORY_KEY = "dailyQtHistoryV1";


        function getKoreaDateKey() {
            const formatter = new Intl.DateTimeFormat("en-CA", {
                timeZone: "Asia/Seoul",
                year: "numeric",
                month: "2-digit",
                day: "2-digit"
            });

            const parts = formatter.formatToParts(new Date());

            const year = parts.find(p => p.type === "year").value;
            const month = parts.find(p => p.type === "month").value;
            const day = parts.find(p => p.type === "day").value;

            return `${year}-${month}-${day}`;
        }


        function formatDate(dateString) {
            if (!dateString) {
                return "";
            }

            return dateString.replaceAll("-", ".");
        }


        function getQtHistory() {
            try {
                const saved = localStorage.getItem(QT_HISTORY_KEY);

                if (!saved) {
                    return {};
                }

                const parsed = JSON.parse(saved);

                if (
                    parsed &&
                    typeof parsed === "object" &&
                    !Array.isArray(parsed)
                ) {
                    return parsed;
                }

                return {};

            } catch (error) {
                console.error("QT History Load Error:", error);
                return {};
            }
        }


        function saveDailyQt(data) {
            if (
                !data ||
                !data.date ||
                !data.reference ||
                !data.verse
            ) {
                return;
            }

            if (
                data.reference.includes("오류") ||
                data.reference.includes("실패")
            ) {
                return;
            }

            try {
                const history = getQtHistory();

                history[data.date] = {
                    date: data.date,
                    reference: data.reference,
                    verse: data.verse,
                    exposition: data.exposition || "",
                    questions: data.questions || [],
                    prayer: data.prayer || ""
                };

                localStorage.setItem(
                    QT_HISTORY_KEY,
                    JSON.stringify(history)
                );

            } catch (error) {
                console.error("QT History Save Error:", error);
            }
        }


        function getRecentReferences(limit = 30) {
            const history = getQtHistory();

            return Object.keys(history)
                .sort()
                .reverse()
                .map(date => history[date]?.reference)
                .filter(Boolean)
                .slice(0, limit);
        }


        function renderQt(data) {
            if (data.date) {
                statusMsg.innerText =
                    `📅 ${formatDate(data.date)} · 📖 ${data.reference}`;
            } else {
                statusMsg.innerText =
                    `📖 ${data.reference}`;
            }

            verse.innerText =
                data.verse ||
                "성경 본문을 불러오지 못했습니다.";

            interpretation.innerText =
                data.exposition ||
                "해석 내용을 불러오지 못했습니다.";

            let questionText = "";

            if (Array.isArray(data.questions)) {
                questionText = data.questions
                    .slice(0, 2)
                    .map((q, idx) => `${idx + 1}. ${q}`)
                    .join("\n\n");
            } else {
                questionText = data.questions || "";
            }

            questions.innerText =
                questionText ||
                "질문 내용을 불러오지 못했습니다.";

            prayer.innerText =
                data.prayer ||
                "기도문 내용을 불러오지 못했습니다.";
        }


        function renderHistory() {
            const history = getQtHistory();

            const dates = Object.keys(history)
                .sort()
                .reverse();

            historyList.replaceChildren();

            if (dates.length === 0) {
                const empty = document.createElement("div");

                empty.className = "history-empty";
                empty.innerText = "아직 저장된 말씀이 없습니다.";

                historyList.appendChild(empty);
                return;
            }

            dates.forEach(date => {
                const data = history[date];

                const button = document.createElement("button");

                button.type = "button";
                button.className = "history-item";

                const dateText = document.createElement("span");

                dateText.className = "history-date";
                dateText.innerText = formatDate(date);

                const referenceText = document.createElement("span");

                referenceText.className = "history-reference";
                referenceText.innerText = data.reference;

                button.appendChild(dateText);
                button.appendChild(referenceText);

                button.addEventListener("click", () => {
                    renderQt(data);

                    historyPanel.style.display = "none";
                    topicInput.value = "";

                    document.getElementById("resultArea").scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                });

                historyList.appendChild(button);
            });
        }


        historyBtn.addEventListener("click", () => {
            renderHistory();

            historyPanel.style.display = "block";

            historyPanel.scrollIntoView({
                behavior: "smooth",
                block: "nearest"
            });
        });


        closeHistoryBtn.addEventListener("click", () => {
            historyPanel.style.display = "none";
        });


        fetchBtn.addEventListener('click', async () => {
            const topic = topicInput.value.trim();

            /*
            * 검색어가 없으면 "오늘의 QT"
            * 오늘 이미 저장된 말씀이 있으면 서버 호출 없이 바로 출력
            */
            if (!topic) {
                const today = getKoreaDateKey();
                const history = getQtHistory();

                if (history[today]) {
                    renderQt(history[today]);

                    historyPanel.style.display = "none";

                    return;
                }
            }

            fetchBtn.disabled = true;
            fetchBtn.style.opacity = "0.7";
            topLoadingBar.style.display = "block";

            historyPanel.style.display = "none";

            statusMsg.innerText = topic
                ? `⏳ '${topic}' 관련 말씀을 찾는 중...`
                : "⏳ 오늘의 말씀과 묵상을 준비하고 있습니다...";

            try {
                let url;

                /*
                * 검색어가 있는 경우
                * 기존 고민/상황 검색 기능
                */
                if (topic) {
                    url =
                        `${RENDER_SERVER_URL}/api/daily-qt` +
                        `?topic=${encodeURIComponent(topic)}`;
                }

                /*
                * 검색어가 없는 경우
                * 오늘의 QT
                */
                else {
                    const recentReferences =
                        getRecentReferences(30);

                    if (recentReferences.length > 0) {
                        const recentParam =
                            recentReferences.join("|");

                        url =
                            `${RENDER_SERVER_URL}/api/daily-qt` +
                            `?recent=${encodeURIComponent(recentParam)}`;
                    } else {
                        url =
                            `${RENDER_SERVER_URL}/api/daily-qt`;
                    }
                }

                const response = await fetch(url);

                if (!response.ok) {
                    throw new Error(
                        `서버 응답 에러: ${response.status}`
                    );
                }

                const data = await response.json();

                /*
                * 고민 검색 결과는 저장하지 않고
                * 오늘의 QT만 히스토리에 저장
                */
                if (!topic) {
                    saveDailyQt(data);
                }

                renderQt(data);

            } catch (error) {
                console.error("Fetch Error:", error);

                statusMsg.innerText =
                    "❌ 불러오기에 실패했습니다. Render 서버 주소 및 서버 상태를 확인해주세요.";

            } finally {
                fetchBtn.disabled = false;
                fetchBtn.style.opacity = "1";
                topLoadingBar.style.display = "none";
            }
        });
    </script>
</body>
</html>
