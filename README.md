# Sprint Reader

一個以 **FastAPI** 為後端的學習模組閱讀器，提供計時衝刺（Sprint）閱讀體驗，並透過閃卡（Flashcard）頁面呈現學習內容，同時追蹤每次學習的進度狀態。

---

## 功能特色

### ⏱ 衝刺閱讀（Sprint Reading）
每次學習以 **7 分鐘（420 秒）** 為一個衝刺單位。倒數計時器在閱讀器頁面持續運作，時間歸零後會自動觸發「時間到」完成狀態（`timed_out`），並跳轉至交接頁。使用者也可在讀完所有閃卡後點擊「完成閱讀」提前結束，系統會記錄為「提前完成」（`finished_early`）。

### 🗂 閃卡頁面（Flashcard Pages）
模組內容拆分為多張結構化閃卡，每張閃卡包含：
- **領域標籤（Domain Tag）**：標示本頁所屬知識領域
- **頁面標題（Title）**：簡明說明本頁主題
- **內文（Content）**：支援純文字與條列式清單兩種格式

使用者可透過「上一張」／「下一張」按鈕翻頁，行動裝置上也支援**左右滑動手勢（Swipe）**切換卡片。頁面頂部顯示類似 Instagram Stories 的進度條，直觀呈現目前閱讀進度。

### 🔄 切換分頁自動暫停計時
當使用者切換至其他瀏覽器分頁或將視窗最小化時，系統會透過 `visibilitychange` 事件**自動暫停倒數計時**，並呼叫 API 將會話標記為暫停（`is_paused = 1`），同時累加分頁切換次數（`tab_switch_count`）。回到閱讀器頁面後，計時器會自動恢復。這樣可確保計時器真實反映使用者實際在頁面上的時間。

### 💾 定時同步進度
計時器每運作 **10 秒**，系統會自動將當前剩餘時間同步回伺服器（`PATCH /api/sessions/{id}/progress`），避免因意外關閉頁面而導致進度遺失。

### 📋 會話管理（Session Management）
完整記錄每次學習的生命週期：
- `start`：建立會話、記錄開始時間（UTC+8 台灣時區）
- `pause` / `resume`：暫停與繼續，並更新剩餘時間
- `progress`：定時更新剩餘秒數
- `complete`：結束會話，記錄完成狀態與結束時間

### 🗺 學習旅程記錄（Learning Journey Map）
每次衝刺會話結束後，系統會在 `LearningJourney_Map` 資料表中建立一筆記錄，將衝刺 `sprint_id` 與後續測驗的 `quiz_session_id` 串聯，形成完整的學習歷程。

---

## 技術架構

| 層次 | 技術 |
|------|------|
| Web 框架 | FastAPI |
| 資料庫 ORM | SQLAlchemy |
| 資料庫 | SQLite（本機開發） |
| 模板引擎 | Jinja2 |
| 前端 | 原生 HTML / CSS / JavaScript |
| 伺服器 | Uvicorn |

---

## 專案結構

```
project3_sprint_reader/
├── app/
│   ├── main.py              # FastAPI 應用程式入口
│   ├── database.py          # 資料庫連線設定
│   ├── models.py            # SQLAlchemy 資料模型
│   ├── schemas.py           # Pydantic 請求／回應 Schema
│   ├── create_tables.py     # 建立資料表腳本
│   ├── seed_data.py         # 初始資料填充腳本
│   └── routers/
│       ├── metadata.py      # 模組後設資料 API
│       ├── flashcards.py    # 閃卡頁面 API
│       └── sessions.py      # 衝刺會話 API
│   └── services/
│       └── session_service.py  # 會話業務邏輯
├── templates/
│   ├── presprint.html       # 衝刺前準備頁
│   ├── reader.html          # 閱讀器主頁
│   ├── handoff.html         # 交接頁（完成後）
│   └── error.html           # 錯誤頁
├── static/
│   ├── css/style.css
│   └── js/
│       ├── presprint.js
│       ├── reader.js
│       └── handoff.js
├── data/                    # 資料檔案目錄
├── requirements.txt
└── README.md
```

---

## 資料模型

### `ModuleMetadata`（模組後設資料）
| 欄位 | 類型 | 說明 |
|------|------|------|
| `module_id` | String (PK) | 模組唯一識別碼 |
| `source_document` | String | 來源文件名稱 |
| `source` | String | 來源描述 |
| `domain_tags_json` | Text (JSON) | 領域標籤清單 |
| `warning_text` | Text | 警告說明文字 |

### `FlashcardPages`（閃卡頁面）
| 欄位 | 類型 | 說明 |
|------|------|------|
| `page_id` | String (PK) | 頁面唯一識別碼 |
| `module_id` | String | 所屬模組 |
| `sequence_number` | Integer | 頁面順序編號 |
| `page_title` | String | 頁面標題 |
| `domain_tag` | String | 領域標籤 |
| `page_content_json` | Text (JSON) | 頁面內容 |

### `SprintSessions`（衝刺會話）
| 欄位 | 類型 | 說明 |
|------|------|------|
| `sprint_id` | String (PK) | 會話唯一識別碼 |
| `agent_id` | String | 使用者 / 代理人 ID |
| `module_id` | String | 學習模組 |
| `start_timestamp` | String | 開始時間（UTC+8） |
| `end_timestamp` | String | 結束時間 |
| `remaining_time` | Integer | 剩餘秒數（預設 420） |
| `tab_switch_count` | Integer | 分頁切換次數 |
| `is_paused` | Integer | 是否暫停（0/1） |
| `completion_status` | String | 完成狀態 |

### `LearningJourneyMap`（學習旅程記錄）
| 欄位 | 類型 | 說明 |
|------|------|------|
| `journey_id` | String (PK) | 旅程唯一識別碼 |
| `sprint_id` | String | 對應衝刺會話 |
| `quiz_session_id` | String | 對應測驗會話 |

---

## API 端點

### 頁面路由

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/` | 衝刺前準備頁 |
| GET | `/reader` | 閱讀器主頁 |
| GET | `/handoff` | 完成後交接頁 |

### 模組後設資料

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/modules/{module_id}/metadata` | 取得模組後設資料 |

### 閃卡頁面

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/modules/{module_id}/flashcards` | 取得模組所有閃卡（依序排列） |

### 衝刺會話

| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | `/api/sessions/start` | 建立新的衝刺會話 |
| PATCH | `/api/sessions/{sprint_id}/pause` | 暫停會話 |
| PATCH | `/api/sessions/{sprint_id}/resume` | 繼續會話 |
| PATCH | `/api/sessions/{sprint_id}/progress` | 更新剩餘時間 |
| PATCH | `/api/sessions/{sprint_id}/complete` | 完成會話 |

---

## 安裝與執行

### 1. 建立虛擬環境並安裝套件

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 建立資料表

```bash
python -m app.create_tables
```

### 3. 填入初始資料（選用）

```bash
python -m app.seed_data
```

### 4. 啟動伺服器

```bash
uvicorn app.main:app --reload
```

啟動後，開啟瀏覽器前往：[http://localhost:8000](http://localhost:8000)

互動式 API 文件請前往：[http://localhost:8000/docs](http://localhost:8000/docs)

---

## 學習流程

```
[準備頁 /]
    ↓  選擇模組、建立會話（POST /api/sessions/start）
[閱讀器 /reader]
    ↓  閱讀閃卡、倒數計時、偵測分頁切換
    ↓  完成或時間到（PATCH /api/sessions/{id}/complete）
[交接頁 /handoff]
    ↓  顯示學習摘要，銜接後續測驗
```
