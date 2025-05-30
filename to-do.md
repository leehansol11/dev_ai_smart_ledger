---
created: 2025-05-25
author: leehansol
source: Gemini 2.5 pro & leehansol
type: "[[🧑‍💻 Project Note]]"
tags:
  - "#AISmartLedger"
  - "#AI스마트가계부"
  - "#ThinVerticalSlice"
  - "#TVS"
  - "#PySide6"
  - "#PyQt5"
  - "#openpyxl"
  - "#SQLite"
  - "#QTableWidget"
  - "#OpenAIAPI"
  - "#ChatGPTAPI"
  - "#QComboBox"
  - "#QMessageBox"
  - "#내부이체"
  - "#분류자동화"
  - "#데이터시각화"
  - "#카테고리매칭"
---

# AI 스마트 가계부 개발 할 일 목록 (to-do.md)

> 이 문서는 "AI 스마트 가계부" MVP 개발을 위한 단계별 할 일 목록입니다.
> 
> Thin Vertical Slice (TVS) 방법론에 기반하여 작성되었으며, 각 항목은 PRD 문서의 관련 내용을 참조할 수 있도록 [PRD X.X] 형태로 표시합니다.
> 
> 완료된 항목은 - [x] 와 같이 표시합니다.

## 0단계: 프로젝트 준비 및 기본 환경 설정

- [x] Git 저장소 생성 및 초기 커밋 (`.gitignore` 파일 포함)
- [x] Python 개발 환경 구성 (권장: 가상환경 사용)
    - [x] PySide6 (또는 PyQt5) 설치
    - [x] `requests` 라이브러리 설치 (OpenAI API 연동용)
    - [x] `openpyxl` 라이브러리 설치 (Excel 파일 처리용)
- [x] 프로젝트 폴더 구조 기본 설계 (예: `ai_smart_ledger/app/(ui/, core/, db/, assets/), tests/, main.py`)

ai_smart_ledger/
├── app/
│   ├── ui/          # 사용자 인터페이스 관련 파일
│   ├── core/        # 핵심 로직 파일들
│   ├── db/          # 데이터베이스 관련 파일들
│   └── assets/      # 자원 파일들 (이미지, 아이콘 등)
├── tests/           # 테스트 파일들
└── main.py          # 메인 실행 파일

- [x] SQLite 데이터베이스 파일 (`AISmartLedger.db`) 생성 및 DB 연결 유틸리티 함수 작성 [PRD 3.2]
    - [x] `categories` 테이블 스키마 정의 및 생성 스크립트 작성 [PRD 3.2.5]
        - [x] 기본 카테고리 데이터(`3.2.5`의 트리 구조)를 `categories` 테이블에 삽입하는 초기화 스크립트 작성
    - [x] `transactions` 테이블 스키마 정의 및 생성 스크립트 작성 [PRD 3.2.1]
    - [x] `ai_learning_patterns` 테이블 스키마 정의 및 생성 스크립트 작성 [PRD 3.2.2]
    - [x] `settings` 테이블 스키마 정의 및 생성 스크립트 작성 [PRD 3.2.3]
- [x] 메인 애플리케이션 창 (`QMainWindow`) 기본 UI 틀 구현 [PRD 3.4]
    - [x] 프로그램 제목 설정 ("AI 스마트 가계부")
    - [x] 기본 메뉴 바 구조 (파일, 보기, 도구, 도움말 - 실제 기능은 나중에 연결)
    - [x] 주요 화면 영역을 위한 중앙 위젯 레이아웃 설정 (예: `QStackedWidget` 또는 유사 구조로 화면 전환 준비)

## 1단계: 파일 입력 기능 (PRD 2.1)

### 슬라이스 1.1: CSV 파일 선택 및 경로 표시

- **🎯 목표:** 사용자가 '파일 선택' 버튼으로 CSV 파일을 고르면, 선택된 파일의 경로가 화면에 나타난다.
- [x] **UI:** 메인 창에 "거래내역 파일 불러오기" 버튼 (`QPushButton`) 추가 [PRD 2.1]
- [x] **UI:** 선택된 파일 경로를 표시할 레이블 (`QLabel`) 추가 [PRD 2.1]
- [x] **로직:** 버튼 클릭 시, 운영체제 파일 탐색기(CSV 필터 적용)를 열어 파일 경로를 가져오는 함수 구현 (`app/core/file_handler.py` 등에) [PRD 2.1]
- [x] **연결:** 가져온 파일 경로를 UI 레이블에 표시하는 로직 연결
- [x] **테스트:** 수동으로 CSV 파일 선택 시 경로가 잘 표시되는지, 취소 시 적절히 처리되는지 확인
- [x] **커밋:** "Feat: Implement CSV file selection and display path (Slice 1.1)"

### 슬라이스 1.2: 선택된 CSV 파일 내용(첫 5행) 파싱 및 콘솔 출력

- **🎯 목표:** 슬라이스 1.1에서 선택된 CSV 파일의 내용을 읽어, 첫 5행(헤더 포함)을 파싱하여 콘솔에 출력한다.
- [x] **로직:** CSV 파일 경로를 입력받아, 내용을 읽고 파싱하는 함수 구현 (`app/core/file_parser.py`) [PRD 2.1]
    - [x] 표준 CSV 모듈 사용, UTF-8 인코딩 기본 처리
    - [x] 헤더 행과 데이터 행 구분
    - [x] 첫 5행 데이터만 추출 (또는 지정된 수만큼)
- [x] **연결:** 파일 선택 완료 후, 위 파싱 함수 호출 및 결과 콘솔 출력
- [x] **테스트:** 다양한 CSV 파일(헤더 유무, 데이터 적은/많은 경우)로 콘솔 출력 확인
- [x] **커밋:** "Feat: Parse first 5 rows of selected CSV and print to console (Slice 1.2)"

### 슬라이스 1.3: 파싱된 CSV 데이터 화면 표에 표시 (기본)

- **🎯 목표:** 슬라이스 1.2에서 파싱된 CSV 데이터를 메인 창의 테이블 위젯에 표시한다.
- [x] **UI:** 메인 창에 거래내역을 표시할 테이블 위젯 (`QTableWidget`) 추가 [PRD 2.2, 3.4]
- [x] **연결:** 파싱된 CSV 데이터(헤더 및 첫 5행)를 `QTableWidget`에 채워 넣는 로직 구현
- [x] **테스트:** UI 테이블에 데이터가 올바르게 표시되는지 확인
- [x] **커밋:** "Feat: Display parsed CSV data (first 5 rows) in UI table (Slice 1.3)"

### 슬라이스 1.4: Excel 파일 (XLS, XLSX) 지원 추가

- **🎯 목표:** CSV 파일과 동일하게 Excel 파일도 선택하여 첫 5행을 파싱하고 화면 표에 표시한다.
- [x] **로직:** Excel 파일 파싱 함수 구현 (`app/core/file_parser.py`, `openpyxl` 사용) [PRD 2.1]
    - [x] 첫 번째 시트 데이터 읽기
    - [x] 헤더 및 데이터 행 추출 (첫 5행)
- [x] **로직:** 파일 선택 시 CSV/Excel 확장자 모두 허용하도록 수정
- [x] **연결:** 파일 확장자에 따라 적절한 파싱 함수 호출 및 UI 테이블 업데이트
- [x] **테스트:** XLS, XLSX 파일로 기능 검증
- [x] **커밋:** "Feat: Add Excel (XLS, XLSX) file parsing and display support (Slice 1.4)"

### 슬라이스 1.5: 파일 크기(50MB) 및 형식 검증, 오류 처리 강화

- **🎯 목표:** 파일 업로드 시 크기 제한(50MB)을 적용하고, 지원하지 않는 파일 형식 또는 파싱 오류 발생 시 사용자에게 명확한 메시지를 보여준다.
- [x] **로직:** 파일 선택 후, 파일 크기 검증 로직 추가 (50MB 초과 시 오류) [PRD 2.1, 4.1]
- [x] **로직:** 지원하지 않는 파일 확장자 선택 시 오류 메시지 처리 [PRD 4.1]
- [x] **로직:** CSV/Excel 파싱 중 발생하는 주요 예외(형식 오류, 컬럼 없음 등) 처리 로직 보강 [PRD 4.1]
- [x] **UI:** 오류 발생 시 사용자에게 `QMessageBox` 등으로 명확한 알림 표시
- [x] **테스트:** 다양한 오류 상황 재현 및 메시지 확인
- [x] **커밋:** "Feat: Implement file size/format validation and enhance error handling (Slice 1.5)"

### 슬라이스 1.6: 파일 형식 안내 팝업 기능

- **🎯 목표:** 사용자가 파일 형식 가이드라인을 볼 수 있도록 안내 팝업 기능을 구현한다. (설정 연동은 나중에)
- [x] **UI:** 파일 형식 안내 팝업창(`QDialog` 또는 `QMessageBox`) 디자인 및 내용(텍스트, 예시 이미지 경로) 구성 [PRD 2.1, 2.5.G]
- [x] **UI:** 메인 메뉴 또는 특정 버튼에 "파일 형식 안내" 액션 추가
- [x] **로직:** 액션 클릭 시 안내 팝업창 표시
- [x] **테스트:** 팝업창이 잘 뜨고 내용이 올바른지 확인
- [x] **커밋:** "Feat: Implement file format guide popup (Slice 1.6)"

## 2단계: 거래내역 수동 분류 기능 (PRD 2.2)

### 슬라이스 2.1: 각 거래 행에 카테고리 선택 드롭다운 추가

- **🎯 목표:** 화면 표의 각 거래 내역 행에 사용자가 카테고리를 선택할 수 있는 드롭다운 메뉴를 표시한다.
- [x] **DB:** `categories` 테이블에서 기본 카테고리 목록("계좌 간 이체 (분석 제외)" 포함)을 가져오는 함수 구현 (`app/db/crud.py` 등) [PRD 3.2.5]
- [x] **UI:** `QTableWidget`의 특정 열(예: "사용자 확정 카테고리")에 `QComboBox`를 각 행마다 추가
- [x] **로직:** DB에서 가져온 카테고리 목록을 각 `QComboBox`에 채워 넣기
- [x] **테스트:** 모든 행에 드롭다운이 잘 생성되고 카테고리 목록이 올바르게 표시되는지 확인
- [x] **커밋:** "Feat: Add category selection dropdown to each transaction row (Slice 2.1)"

### 슬라이스 2.2: 선택된 카테고리 정보 저장 (내부 데이터) 및 UI 반영

- **🎯 목표:** 사용자가 드롭다운에서 카테고리를 선택하면, 그 선택이 내부적으로 (아직 DB 저장 전) 기록되고, UI에도 반영(선택된 값 표시)된다.
- [x] **로직:** `QComboBox`의 선택 변경 시그널(`currentIndexChanged` 또는 `currentTextChanged`)을 감지
- [x] **로직:** 선택된 카테고리명(또는 ID)을 해당 거래내역 객체(또는 내부 데이터 구조)에 임시 저장
- [x] **UI:** 선택된 카테고리가 드롭다운에 잘 표시되고, 필요시 해당 행의 다른 부분(예: 상태) 업데이트
- [x] **테스트:** 카테고리 변경 시 내부 데이터가 업데이트되는지 (디버깅/로깅으로) 확인
- [x] **커밋:** "Feat: Store selected category internally and reflect in UI (Slice 2.2)"

### 슬라이스 2.3: 분류된 카테고리 `transactions` DB에 저장

- **🎯 목표:** 사용자가 선택한 카테고리 정보를 실제 `transactions` 테이블의 해당 거래 내역에 업데이트한다. (예: "분류 완료" 버튼 클릭 또는 자동 저장)
- [x] **UI:** (선택적) "분류 완료/저장" 버튼 추가 또는 자동 저장 방식 결정
- [x] **DB:** 특정 거래 ID에 대해 확정된 카테고리 ID를 `transactions` 테이블에 업데이트하는 함수 구현 (`app/db/crud.py`) [PRD 3.2.1]
- [x] **로직:** 버튼 클릭 또는 특정 조건 만족 시, 내부적으로 임시 저장된 사용자 확정 카테고리 정보를 DB에 일괄 또는 개별 저장
- [x] **테스트:** DB Browser 등으로 실제 `transactions` 테이블의 `category_id`가 업데이트되었는지 확인
- [x] **커밋:** "Feat: Save user-confirmed categories to transactions database (Slice 2.3)"

### 슬라이스 2.4: "실행 취소(Undo)" 기능 (최근 1개 카테고리 변경)

- **🎯 목표:** 사용자가 가장 최근에 변경한 카테고리 선택을 이전 상태로 되돌릴 수 있다.
- [x] **로직:** 카테고리 변경 시, 이전 선택값과 현재 선택값을 스택(stack) 등에 저장하는 로직 추가
- [x] **UI:** "실행 취소" 버튼 추가 및 클릭 시그널 연결
- [x] **로직:** "실행 취소" 시, 스택에서 이전 상태를 가져와 현재 카테고리 선택 복원 (UI 및 내부 데이터, 필요시 DB도 업데이트)
- [x] **테스트:** 카테고리 변경 후 실행 취소 시 이전 선택으로 돌아가는지 확인
- [x] **커밋:** "Feat: Implement single-step undo for category selection (Slice 2.4)"

### 슬라이스 2.5: "중간 저장" 기능 (분류 진행 상태)

- **🎯 목표:** 현재까지의 분류 작업 상태(어떤 파일, 어떤 행까지 어떤 카테고리로 분류했는지 등)를 저장하고, 나중에 이어할 수 있도록 한다.
- [x] **로직:** 현재 작업 중인 파일 정보, 각 거래별 확정 카테고리(아직 DB에 최종 저장 전이라도), 현재 작업 위치 등을 저장할 데이터 구조 정의
- [x] **UI:** "중간 저장" 버튼 추가
- [x] **로직:** "중간 저장" 시, 위 데이터를 특정 파일(예: JSON) 또는 `settings` 테이블에 저장
- [x] **로직:** 프로그램 시작 시 또는 파일 재로드 시, 저장된 작업 내용이 있으면 불러와서 UI에 복원하는 기능 (0단계 기본 환경 설정과 연계)
- [x] **테스트:** 중간 저장 후 프로그램 종료/재시작 시 작업 내용 복원 확인
- [x] **커밋:** "Feat: Implement 'Save Progress' for classification (Slice 2.5)"

## 3단계: OpenAI API 연동 및 AI 자동 분류 (PRD 2.2, 3.3)

### 슬라이스 3.1: ChatGPT API 키 입력 UI 및 저장

- **🎯 목표:** 사용자가 설정 화면에서 자신의 ChatGPT API 키를 입력하고 저장할 수 있다.
- [X] **UI:** 설정 창(`QDialog` 또는 별도 화면)에 API 키 입력 필드 (`QLineEdit`) 및 저장 버튼 추가 [PRD 2.5.E]
- [X] **로직:** 입력된 API 키를 `settings` 테이블에 안전하게 저장/업데이트하는 로직 (`app/db/crud.py`)
- [X] **로직:** 프로그램 시작 시 `settings` 테이블에서 API 키를 로드하여 내부 변수에 보관
- [X] **테스트:** API 키 입력 및 저장 후, 재시작 시에도 키가 유지되는지 확인 (DB 확인)
- [X] **커밋:** "Feat: Implement UI and logic to save ChatGPT API key in settings (Slice 3.1)"

### 슬라이스 3.2: 선택된 거래 내역 1건에 대해 API로 카테고리 추천 요청 (콘솔 출력)

- **🎯 목표:** 분류 작업 창에서 특정 거래 내역 선택 시, 해당 거래 내용으로 OpenAI API에 카테고리 추천을 요청하고, 그 결과를 콘솔에 출력한다.
- [x] **로직:** 저장된 API 키를 사용하여 OpenAI API와 통신하는 기본 모듈 작성 (`app/core/ai_classifier.py`, `requests` 사용) [PRD 3.3]
- [x] **로직:** 거래 내역 문자열(적요)과 기본 카테고리 목록을 포함하는 프롬프트 구성 로직 (1차 - 매우 단순하게)
- [x] **로직:** 특정 거래 내역 선택 시 (또는 버튼 클릭 시) 위 프롬프트로 API 호출 및 응답(추천 카테고리 텍스트) 수신
- [x] **연결:** 수신된 추천 카테고리 텍스트를 콘솔에 출력
- [x] **테스트:** 실제 거래 내역으로 API 호출이 성공하고 추천 결과가 콘솔에 찍히는지 확인
- [x] **커밋:** "Feat: Request category suggestion from OpenAI API for one transaction and print to console (Slice 3.2)"

### 슬라이스 3.3: API 추천 카테고리 UI 반영 및 사용자 확인/수동 지정 로직 연결

- **🎯 목표:** API 추천 결과를 "AI 추천 카테고리" 열에 표시하고, 사용자가 이를 확인(Y/N)하거나 직접 수정하여 최종 확정할 수 있도록 한다.
- [x] **UI:** "AI 추천 카테고리" 열에 API 응답 텍스트 표시
- [x] **UI:** 신뢰도에 따른 배경색 변경 (신호등 시스템 - 초기에는 더미 신뢰도로)
- [x] **UI:** AI 제안 "예(Y)" / "아니요(N)" 버튼 또는 유사 인터페이스 추가 (선택적, 드롭다운 직접 수정도 가능)
- [x] **로직:** "예" 선택 시 AI 추천 카테고리를 사용자 확정 카테고리로 설정, "아니요" 또는 직접 수정 시 해당 내용으로 설정 (내부 데이터 업데이트)
- [x] **연결:** 확정된 카테고리는 슬라이스 2.3의 DB 저장 로직과 연동
- [x] **테스트:** API 추천 결과 표시, Y/N 및 수동 수정에 따른 내부 데이터 및 DB 업데이트 확인
- [ ] **커밋:** "Feat: Display API suggested category in UI and allow user confirmation/correction (Slice 3.3)"

#### [세부 구현 및 UX 자동화 요구]
- [ ] "예" 버튼 클릭 시, AI 추천 카테고리가 사용자 확정 카테고리 열에 자동 반영되고, 내부 데이터 및 DB까지 즉시 연동(저장)됨을 보장
- [ ] "아니요" 클릭 시, 드롭다운이 생성되어 사용자가 직접 카테고리를 선택할 수 있고, 이 선택도 내부 데이터 및 DB에 즉시 반영됨
- [ ] Y/N 버튼 클릭, 드롭다운 직접 선택 등 모든 경로에서 확정 카테고리 변경이 완전히 자동화되어야 함(사용자 입력 최소화)
- [ ] 신호등(신뢰도) 색상은 추천 함수가 신뢰도 값을 반환할 경우 실제 값에 따라, 아니면 기본값(HIGH)으로 표시
- [ ] 테스트: "예" 클릭, "아니요" 클릭 후 드롭다운 선택, 직접 드롭다운 선택 등 모든 경로에서 내부 데이터/DB/화면이 동기화되는지 확인

---

#### [업데이트 이력 및 배경]
- **2025-05-25, 사용자 요청에 의한 업데이트**
    - 실제 사용자 경험(UX)과 업무 효율성을 극대화하기 위해, 단순히 "AI 추천 카테고리"를 표시하는 것에 그치지 않고 **Y/N 버튼 클릭 시 자동으로 사용자 확정 카테고리 및 DB까지 즉시 반영**, **신호등(신뢰도) 색상 시각화**, **드롭다운 직접 선택 시도 내부 데이터/DB 자동 동기화** 등 모든 경로에서 사용자 입력을 최소화하고, 확정/수정/저장이 완전히 자동화되도록 세부 요구사항을 명확히 추가함.
    - 이는 실제 현업 사용자가 "AI 추천값을 보고 일일이 복사/입력하는 비효율"을 지적한 데 따른 개선 요청이며, **실제 업무 흐름에서 클릭 한 번, 선택 한 번으로 모든 데이터가 즉시 반영**되는 직관적이고 빠른 UX를 보장하기 위함임.

### 슬라이스 3.4: 로컬 학습 DB 연동 (간단한 패턴-카테고리 매칭)

- **🎯 목표:** 사용자가 확정한 (거래 내용 패턴 - 카테고리) 쌍을 `ai_learning_patterns` DB에 저장하고, API 요청 전 이 DB를 먼저 참조하여 동일/유사 패턴 발견 시 API 호출 없이 즉시 추천한다.
- [ ] **DB:** 사용자 확정 (거래 패턴, 카테고리 ID, 확정 횟수 등) 정보를 `ai_learning_patterns` 테이블에 저장/업데이트하는 함수 (`app/db/crud.py`) [PRD 3.2.2]
- [ ] **로직:** 카테고리 확정 시 위 DB 저장 함수 호출
- [ ] **로직:** API 요청 전, 현재 거래 내용과 정확히 일치하는 패턴이 `ai_learning_patterns`에 있는지 검색하는 로직 (`app/core/ai_classifier.py`)
- [ ] **로직:** 일치 패턴 발견 시 해당 카테고리를 즉시 AI 추천으로 사용 (API 호출 건너뜀)
- [ ] **테스트:** 동일 거래 내용 반복 시 DB 기반 추천이 API보다 우선하는지 확인
- [ ] **커밋:** "Feat: Implement local learning DB for exact pattern matching before API call (Slice 3.4)"

### 슬라이스 3.5: API 연동 오류 처리 및 수동 모드 전환

- **🎯 목표:** 인터넷 연결, API 키 오류 등 발생 시 사용자에게 안내하고 수동 분류 모드로 원활히 전환되도록 한다.
- [ ] **로직:** API 호출 전/중 네트워크 연결 상태 확인 (선택적, 기본 예외처리 우선)
- [ ] **로직:** API 호출 관련 주요 예외(`requests.exceptions.ConnectionError`, API 키 오류 응답 등) 처리 [PRD 4.2]
- [ ] **UI:** 오류 발생 시 `QMessageBox` 등으로 사용자 안내 메시지 표시 (예: "인터넷 연결 확인", "API 키 확인", "AI 서비스 일시 오류")
- [ ] **UI:** 오류 안내와 함께 "수동으로 계속", "(설정으로 이동)", "(재시도)" 등의 버튼 제공
- [ ] **로직:** "AI 추천 카테고리" 필드를 비우거나 "AI 추천 불가"로 표시하고, 사용자가 수동으로 카테고리를 선택/입력할 수 있도록 보장
- [ ] **테스트:** 인터넷 연결 끊기, 잘못된 API 키 입력 등 상황 재현 및 정상적 수동 모드 전환 확인
- [ ] **커밋:** "Feat: Enhance API error handling and ensure smooth fallback to manual classification (Slice 3.5)"

## 4단계: 계좌 간 이체 처리 기능 (PRD 2.3)

### 슬라이스 4.1: "계좌 간 이체 자동 찾기" 기본 로직 (단일 파일 내, 동일 금액)

- **🎯 목표:** 현재 로드된 단일 거래내역 파일 내에서, 사용자가 설정한 시간 범위 내 동일 금액의 입/출금 쌍을 찾아 콘솔에 출력한다. (설정 연동은 다음 슬라이스)
- [ ] **UI:** "계좌 간 이체 자동 찾기" 버튼 추가 [PRD 2.3]
- [ ] **로직:** 현재 `transactions` 테이블에 로드된 (아직 미분류 또는 분류된) 거래내역 중 동일 금액의 입금과 출금 쌍을 찾는 함수 (`app/core/transfer_detector.py`)
    - [ ] 시간 차이 허용 범위는 우선 하드코딩 (예: 5분)
    - [ ] 이미 "계좌 간 이체 (분석 제외)"로 지정된 항목은 검색 제외
- [ ] **연결:** 버튼 클릭 시 위 함수 호출 및 결과(찾아낸 쌍 정보) 콘솔 출력
- [ ] **테스트:** 동일 금액 입/출금 쌍이 있는 CSV 파일로 콘솔 출력 확인
- [ ] **커밋:** "Feat: Find and print potential internal transfers (same amount, single file) to console (Slice 4.1)"

### 슬라이스 4.2: 사용자 확인 UI 및 "계좌 간 이체 (분석 제외)" 처리

- **🎯 목표:** 슬라이스 4.1에서 찾은 잠재적 이체 거래 쌍을 사용자에게 보여주고, 확인 시 해당 거래들을 "계좌 간 이체 (분석 제외)"로 확정한다.
- [ ] **UI:** 잠재적 이체 거래 쌍 목록을 보여줄 `QDialog` 또는 유사 UI 구현 (출금내역/입금내역 표시)
- [ ] **UI:** 각 쌍에 대해 "예 (이체 처리)" / "아니요" 버튼 제공
- [ ] **로직:** "예" 선택 시, 해당 출금/입금 거래들을 `transactions` 테이블에서 "계좌 간 이체 (분석 제외)" 카테고리 ID로 업데이트 (또는 특수 플래그 사용)
- [ ] **연결:** 자동 찾기 실행 후, 결과가 있으면 위 확인 UI 표시
- [ ] **UI:** 분류 작업 창에서 "계좌 간 이체 (분석 제외)"로 처리된 항목 시각적 구분 (예: 다른 배경색, 취소선 등)
- [ ] **테스트:** UI에서 확인/취소에 따라 DB 및 표 업데이트 확인
- [ ] **커밋:** "Feat: Implement user confirmation UI for detected transfers and mark as 'Internal Transfer' (Slice 4.2)"

## 5단계: 데이터 시각화 대시보드 (PRD 2.4) - (각 차트는 개별 슬라이스로 분리 가능)

### 슬라이스 5.1: 월별/연도별 수입 및 지출 요약 정보 표시

- **🎯 목표:** 사용자가 선택한 월/연도의 총수입, 총지출, 순이익을 계산하여 화면에 텍스트로 표시한다.
- [ ] **UI:** "대시보드" 화면 기본 레이아웃 및 연/월 선택 `QComboBox` 추가
- [ ] **DB:** 특정 기간의 확정된 거래내역(`transactions` 테이블, "계좌 간 이체 (분석 제외)" 제외)을 가져와 수입/지출 합계 계산하는 함수 (`app/db/analytics.py`)
- [ ] **로직:** 연/월 선택 변경 시 위 함수 호출 및 결과 UI 레이블에 업데이트
- [ ] **테스트:** 샘플 데이터로 기간별 합계 정확성 확인
- [ ] **커밋:** "Feat: Display monthly/yearly income/expense summary on Dashboard (Slice 5.1)"

### 슬라이스 5.2: 카테고리별 지출 비중 원형 차트

- **🎯 목표:** 선택된 기간의 지출 내역을 카테고리별로 집계하여 원형 차트로 표시한다.
- [ ] **로직:** 선택된 기간의 카테고리별 지출 합계 계산 로직 (`app/db/analytics.py`)
- [ ] **UI:** 원형 차트 표시 영역 추가 (PySide 내장 차트 또는 Matplotlib 연동)
- [ ] **연결:** 계산된 데이터를 차트에 바인딩하여 표시
- [ ] **테스트:** 차트가 데이터에 맞게 정확히 그려지는지 확인
- [ ] **커밋:** "Feat: Implement category-wise expense pie chart on Dashboard (Slice 5.2)"

### 슬라이스 5.3: 월별 수입/지출 추이 막대/선 그래프 (선택)

- **🎯 목표:** 최근 N개월 또는 선택된 연도의 월별 수입/지출 추이를 막대 또는 선 그래프로 표시한다.
- [ ] **로직:** 월별 수입/지출 집계 로직 (`app/db/analytics.py`)
- [ ] **UI:** 막대/선 그래프 표시 영역 추가
- [ ] **연결:** 데이터를 그래프에 바인딩
- [ ] **테스트:** 그래프 추이 정확성 확인
- [ ] **커밋:** "Feat: Implement monthly income/expense trend chart (Slice 5.3)"

## 6단계: 기본 설정 및 관리 기능 (PRD 2.5) - (각 설정 항목은 개별 슬라이스)

### 슬라이스 6.1: (A) 계좌 간 이체 시간 허용 범위 설정

- **🎯 목표:** 사용자가 설정 창에서 계좌 간 이체 자동 식별 시의 시간 차이 허용 범위를 설정하고 저장할 수 있다.
- [ ] **UI:** 설정 창에 "계좌 간 이체 시간 허용 범위" 입력 필드(예: `QSpinBox` 1~60분) 및 저장 버튼 추가 [PRD 2.5.A]
- [ ] **로직:** 설정 값을 `settings` 테이블에 저장/로드하는 로직 (`app/db/crud.py`)
- [ ] **연결:** 슬라이스 4.1의 자동 이체 탐지 로직이 이 설정 값을 사용하도록 수정
- [ ] **테스트:** 설정 변경 후 자동 이체 탐지 결과가 달라지는지 확인
- [ ] **커밋:** "Feat: Allow user to configure time window for auto transfer detection (Slice 6.1)"

### 슬라이스 6.X: (B~G) 나머지 설정 기능들 (각각 작은 슬라이스로 나누어 구현)

- [ ] B. AI 학습 데이터 버전 관리 및 롤백 UI 및 로직 [PRD 2.5.B]
- [ ] C. 데이터 자동 백업(변경 시) 로직 및 수동 복원 UI 및 로직 [PRD 2.5.C]
    - [ ] 자동 백업 시 프로그레스 바 및 화면 비활성화 UI 구현
- [ ] D. 데이터 CSV 내보내기 기능 [PRD 2.5.D]
- [ ] E. (이미 일부 구현됨) ChatGPT API 키 입력/저장/삭제 UI 및 로직 + 연결 테스트 버튼 [PRD 2.5.E]
- [ ] F. 프로그램 데이터 전체 초기화 UI 및 로직 (2단계 확인 포함) [PRD 2.5.F]
- [ ] G. 파일 형식 안내 팝업 표시 여부 설정 UI 및 저장/적용 로직 [PRD 2.5.G]

## 7단계: 최종 검토, 테스트 및 문서화

- [ ] 주요 기능별 통합 테스트 및 버그 수정
- [ ] 다양한 예외 상황 시나리오 테스트 (PRD 4 전체 항목 점검)
- [ ] UI/UX 사용성 최종 검토 및 개선 (PRD 3.4 기반 일관성, 명확성 등)
- [ ] (선택적) 간단한 사용자 매뉴얼 또는 README.md 업데이트 (프로그램 실행 방법, 주요 기능 사용법 등)
- [ ] 최종 빌드 및 OS별 (macOS, Windows) 실행 파일 생성 준비 (pyinstaller 등 사용 고려)