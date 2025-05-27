"""
데이터베이스 테이블 모델 정의
Author: leehansol
Created: 2025-05-25
"""

from .database import db_manager


def create_categories_table():
    """
    categories 테이블을 생성합니다
    
    테이블 구조:
    - category_id: 기본키 (자동증가)
    - category_name: 카테고리명 (NOT NULL)
    - parent_category_id: 부모 카테고리 ID (외래키, 최상위는 NULL)
    - type: 카테고리 타입 ('수입', '지출', '이체')
    - level: 계층 레벨 (1=최상위, 2=중간, 3=하위)
    - is_default: 기본 제공 카테고리 여부 (TRUE=기본, FALSE=사용자 추가)
    - created_at: 생성일시
    - updated_at: 수정일시
    """
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL,
        parent_category_id INTEGER,
        type TEXT NOT NULL CHECK (type IN ('수입', '지출', '이체')),
        level INTEGER NOT NULL CHECK (level >= 1 AND level <= 3),
        is_default BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- 외래키 제약조건
        FOREIGN KEY (parent_category_id) REFERENCES categories(category_id),
        
        -- 유니크 제약조건 (같은 부모 아래 동일한 이름 불가)
        UNIQUE(category_name, parent_category_id)
    );
    """
    
    try:
        cursor = db_manager.execute_query(create_table_query)
        if cursor:
            print("✅ categories 테이블이 성공적으로 생성되었습니다!")
            return True
        else:
            print("❌ categories 테이블 생성에 실패했습니다!")
            return False
            
    except Exception as e:
        print(f"❌ categories 테이블 생성 중 오류가 발생했습니다: {e}")
        return False


def create_transactions_table():
    """
    transactions 테이블을 생성합니다
    
    테이블 구조:
    - transaction_id: 기본키 (자동증가)
    - account_id: 계좌 식별자 (나중에 accounts 테이블과 연동 예정)
    - timestamp: 거래일시
    - description: 거래 내용/적요
    - amount_in: 입금액 (NULL 가능)
    - amount_out: 출금액 (NULL 가능) 
    - category_id: 카테고리 ID (외래키, categories 테이블 참조)
    - is_transfer: 계좌 간 이체 여부
    - source_file: 원본 CSV 파일명
    - source_row_id: 원본 파일의 행 번호
    - created_at: 생성일시
    - updated_at: 수정일시
    """
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id TEXT,
        timestamp TIMESTAMP NOT NULL,
        description TEXT NOT NULL,
        amount_in DECIMAL(15,2),
        amount_out DECIMAL(15,2),
        category_id INTEGER,
        is_transfer BOOLEAN NOT NULL DEFAULT FALSE,
        source_file TEXT,
        source_row_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- 외래키 제약조건
        FOREIGN KEY (category_id) REFERENCES categories(category_id),
        
        -- 체크 제약조건 (입금 또는 출금 중 하나는 반드시 있어야 함)
        CHECK (
            (amount_in IS NOT NULL AND amount_out IS NULL) OR 
            (amount_in IS NULL AND amount_out IS NOT NULL)
        )
    );
    """
    
    try:
        cursor = db_manager.execute_query(create_table_query)
        if cursor:
            print("✅ transactions 테이블이 성공적으로 생성되었습니다!")
            return True
        else:
            print("❌ transactions 테이블 생성에 실패했습니다!")
            return False
            
    except Exception as e:
        print(f"❌ transactions 테이블 생성 중 오류가 발생했습니다: {e}")
        return False


def create_ai_learning_patterns_table():
    """
    ai_learning_patterns 테이블을 생성합니다
    
    테이블 구조:
    - pattern_id: 기본키 (자동증가)
    - text_pattern: 거래 내용 핵심 패턴 (텍스트)
    - assigned_category_id: 사용자가 확정한 카테고리 ID (외래키)
    - confirmation_count: 확정 횟수 (신뢰도 계산용)
    - confidence_score: 신뢰도 점수 (0.0 ~ 1.0)
    - last_updated: 마지막 사용일
    - created_at: 생성일시
    """
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ai_learning_patterns (
        pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
        text_pattern TEXT NOT NULL,
        assigned_category_id INTEGER NOT NULL,
        confirmation_count INTEGER NOT NULL DEFAULT 1,
        confidence_score REAL NOT NULL DEFAULT 0.5 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- 외래키 제약조건
        FOREIGN KEY (assigned_category_id) REFERENCES categories(category_id),
        
        -- 유니크 제약조건 (같은 패턴과 카테고리 조합은 중복 불가)
        UNIQUE(text_pattern, assigned_category_id)
    );
    """
    
    try:
        cursor = db_manager.execute_query(create_table_query)
        if cursor:
            print("✅ ai_learning_patterns 테이블이 성공적으로 생성되었습니다!")
            return True
        else:
            print("❌ ai_learning_patterns 테이블 생성에 실패했습니다!")
            return False
            
    except Exception as e:
        print(f"❌ ai_learning_patterns 테이블 생성 중 오류가 발생했습니다: {e}")
        return False


def create_settings_table():
    """
    settings 테이블을 생성합니다
    
    테이블 구조:
    - setting_key: 설정 키 (기본키)
    - setting_value: 설정 값 (텍스트)
    - setting_type: 설정 타입 ('string', 'integer', 'boolean', 'float')
    - description: 설정 설명
    - created_at: 생성일시
    - updated_at: 수정일시
    
    저장될 설정들:
    - openai_api_key: OpenAI API 키
    - transfer_time_range: 계좌 간 이체 시간 허용 범위 (분)
    - ai_learning_version: AI 학습 데이터 현재 활성 버전 정보
    - window_width: 마지막 창 너비
    - window_height: 마지막 창 높이
    - window_x: 마지막 창 X 위치
    - window_y: 마지막 창 Y 위치
    - show_file_format_popup: 파일 형식 안내 팝업 표시 여부
    """
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS settings (
        setting_key TEXT PRIMARY KEY,
        setting_value TEXT,
        setting_type TEXT NOT NULL CHECK (setting_type IN ('string', 'integer', 'boolean', 'float')),
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        cursor = db_manager.execute_query(create_table_query)
        if cursor:
            print("✅ settings 테이블이 성공적으로 생성되었습니다!")
            return True
        else:
            print("❌ settings 테이블 생성에 실패했습니다!")
            return False
            
    except Exception as e:
        print(f"❌ settings 테이블 생성 중 오류가 발생했습니다: {e}")
        return False


def create_all_tables():
    """
    모든 테이블을 생성합니다
    """
    print("🏗️ 데이터베이스 테이블 생성을 시작합니다...")
    
    success_count = 0
    total_count = 4  # categories, transactions, ai_learning_patterns, settings
    
    # categories 테이블 생성
    if create_categories_table():
        success_count += 1
    
    # transactions 테이블 생성
    if create_transactions_table():
        success_count += 1
        
    # ai_learning_patterns 테이블 생성
    if create_ai_learning_patterns_table():
        success_count += 1
        
    # settings 테이블 생성
    if create_settings_table():
        success_count += 1
    
    print(f"📊 테이블 생성 완료: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 모든 테이블이 성공적으로 생성되었습니다!")
        return True
    else:
        print("⚠️ 일부 테이블 생성에 실패했습니다.")
        return False


if __name__ == "__main__":
    """이 파일을 직접 실행할 때 테이블을 생성합니다"""
    print("🏁 테이블 생성 테스트를 시작합니다...")
    
    # 데이터베이스 연결 확인
    if db_manager.get_connection():
        # 테이블 생성
        if create_all_tables():
            print("🎉 테스트 성공!")
        else:
            print("💥 테스트 실패!")
    else:
        print("❌ 데이터베이스 연결에 실패했습니다!") 