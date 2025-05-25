# 🏦 AI 스마트 가계부

**AI 기반 거래내역 자동 분류 가계부 애플리케이션**

## 📋 프로젝트 개요

AI 스마트 가계부는 은행 거래내역 파일(CSV/Excel)을 AI를 활용하여 자동으로 카테고리별로 분류하고, 개인의 지출 내역을 손쉽게 관리 및 분석할 수 있는 데스크톱 애플리케이션입니다.

### 🎯 주요 기능
- 📁 은행 거래내역 파일 가져오기 (CSV, Excel 지원)
- 🤖 AI 기반 거래내역 자동 분류
- ✏️ 수동 분류 및 AI 학습 개선
- 🔄 계좌 간 이체 자동 감지
- 📊 데이터 시각화 대시보드
- ⚙️ 개인화된 설정 관리

## 🛠 기술 스택

- **GUI Framework**: PySide6
- **언어**: Python 3.10
- **데이터베이스**: SQLite
- **AI API**: OpenAI ChatGPT API
- **데이터 처리**: pandas, openpyxl
- **시각화**: matplotlib

## 🚀 설치 및 실행

### 1. 환경 요구사항
- Python 3.8 이상 (권장: 3.10)
- macOS 또는 Windows

### 2. Conda 환경 설정

```bash
# Conda 환경 생성
conda create -n AI_smart_ledger python=3.10 -y

# 환경 활성화
conda activate AI_smart_ledger
```

### 3. 의존성 설치

```bash
# 패키지 설치
pip install -r requirements.txt
```

또는 개별 설치:

```bash
pip install PySide6 requests openpyxl matplotlib pandas
```

### 4. 애플리케이션 실행

```bash
python main.py
```

## 📁 프로젝트 구조

```
ai_smart_ledger/
├── app/
│   ├── ui/          # 사용자 인터페이스 관련 파일
│   ├── core/        # 핵심 로직 파일들
│   ├── db/          # 데이터베이스 관련 파일들
│   └── assets/      # 자원 파일들 (이미지, 아이콘 등)
├── tests/           # 테스트 파일들
├── main.py          # 메인 실행 파일
├── requirements.txt # 의존성 목록
└── README.md        # 프로젝트 문서
```

## 🔧 개발 환경 설정

### 개발자용 환경 설정

1. **저장소 클론** (있을 경우)
```bash
git clone <repository-url>
cd ai_smart_ledger
```

2. **가상환경 설정**
```bash
conda create -n AI_smart_ledger python=3.10 -y
conda activate AI_smart_ledger
```

3. **개발 의존성 설치**
```bash
pip install -r requirements.txt
```

4. **환경 테스트**
```bash
python main.py
```

## 📝 개발 계획

이 프로젝트는 Thin Vertical Slice (TVS) 방법론을 기반으로 단계별로 개발됩니다.

### 현재 단계: 0단계 - 환경 설정 ✅
- [x] Conda 환경 생성
- [x] Python 3.10 설치
- [x] PySide6, requests, openpyxl 설치
- [x] 프로젝트 폴더 구조 생성
- [x] 기본 실행 파일 생성

### 다음 단계: 1단계 - 파일 입력 기능
- [ ] CSV 파일 선택 UI
- [ ] 파일 파싱 기능
- [ ] 기본 테이블 표시

자세한 개발 계획은 `250525_AI 스마트 가계부 개발 to-do.md.md` 파일을 참조하세요.

## 🤝 기여하기

이 프로젝트는 개인 학습 및 연구 목적으로 개발되고 있습니다.

## 📄 라이선스

이 프로젝트는 개인 사용 목적으로 개발되었습니다.

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

**Created by**: leehansol  
**Created on**: 2025-05-25  
**Last Updated**: 2025-05-25 