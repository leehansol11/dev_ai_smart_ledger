"""
데이터베이스 CRUD 연산 함수들
Author: leehansol
Created: 2025-05-25

슬라이스 2.1에서 필요한 categories 테이블 관련 함수들을 구현합니다.
"""

from typing import List, Tuple, Dict, Optional, Any
from .database import get_db_connection


def get_all_categories() -> List[Tuple]:
    """
    categories 테이블에서 모든 카테고리 목록을 가져옵니다.
    
    Returns:
        List[Tuple]: 카테고리 정보 리스트. 각 튜플은 (category_id, category_name, parent_category_id, type, level) 형태
    
    Raises:
        Exception: 데이터베이스 조회 중 오류 발생 시
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 모든 카테고리를 계층 구조 순서로 조회 (level, parent_category_id, category_name 순)
        query = """
        SELECT category_id, category_name, parent_category_id, type, level
        FROM categories 
        ORDER BY level ASC, parent_category_id ASC, category_name ASC
        """
        
        cursor.execute(query)
        categories = cursor.fetchall()
        
        if not categories:
            print("⚠️ categories 테이블에 데이터가 없습니다")
            return []
        
        print(f"✅ categories 테이블에서 {len(categories)}개 카테고리를 조회했습니다")
        return categories
        
    except Exception as e:
        print(f"❌ 카테고리 목록 조회 중 오류 발생: {e}")
        raise


def get_categories_for_dropdown() -> List[str]:
    """
    드롭다운 UI에서 사용할 수 있는 형태로 카테고리 목록을 반환합니다.
    계층 구조를 고려하여 "상위카테고리 > 하위카테고리" 형태로 포맷팅합니다.
    
    Returns:
        List[str]: 드롭다운용 카테고리 문자열 리스트
    
    Raises:
        Exception: 데이터베이스 조회 중 오류 발생 시
    """
    try:
        # 모든 카테고리 정보 가져오기
        all_categories = get_all_categories()
        
        # 카테고리를 딕셔너리로 변환 (ID를 키로, 카테고리 정보를 값으로)
        category_dict = {}
        for cat in all_categories:
            category_dict[cat[0]] = {  # category_id를 키로
                'name': cat[1],        # category_name
                'parent_id': cat[2],   # parent_category_id
                'type': cat[3],        # type
                'level': cat[4]        # level
            }
        
        # 드롭다운용 리스트 생성
        dropdown_list = []
        
        for cat_id, cat_info in category_dict.items():
            # 계층 구조를 따라 전체 경로 생성
            path_parts = []
            current_id = cat_id
            
            # 상위 카테고리로 거슬러 올라가며 경로 구성
            while current_id is not None:
                current_cat = category_dict.get(current_id)
                if current_cat:
                    path_parts.insert(0, current_cat['name'])  # 앞쪽에 삽입
                    current_id = current_cat['parent_id']
                else:
                    break
            
            # 경로를 " > "로 연결
            if len(path_parts) > 1:
                full_path = " > ".join(path_parts)
            else:
                full_path = path_parts[0] if path_parts else "알 수 없음"
            
            dropdown_list.append(full_path)
        
        # 중복 제거 및 정렬
        dropdown_list = sorted(list(set(dropdown_list)))
        
        print(f"✅ 드롭다운용 카테고리 목록 {len(dropdown_list)}개 생성 완료")
        return dropdown_list
        
    except Exception as e:
        print(f"❌ 드롭다운용 카테고리 목록 생성 중 오류 발생: {e}")
        raise


def get_category_by_id(category_id: int) -> Optional[Tuple]:
    """
    특정 ID의 카테고리 정보를 조회합니다.
    
    Args:
        category_id (int): 조회할 카테고리 ID
    
    Returns:
        Optional[Tuple]: 카테고리 정보 튜플 또는 None (찾지 못한 경우)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT category_id, category_name, parent_category_id, type, level
        FROM categories 
        WHERE category_id = ?
        """
        
        cursor.execute(query, (category_id,))
        category = cursor.fetchone()
        
        if category:
            print(f"✅ 카테고리 ID {category_id} 조회 성공: {category[1]}")
        else:
            print(f"⚠️ 카테고리 ID {category_id}를 찾을 수 없습니다")
        
        return category
        
    except Exception as e:
        print(f"❌ 카테고리 ID {category_id} 조회 중 오류 발생: {e}")
        raise


def get_categories_by_type(category_type: str) -> List[Tuple]:
    """
    특정 타입의 카테고리들을 조회합니다.
    
    Args:
        category_type (str): 카테고리 타입 ('수입', '지출', '이체')
    
    Returns:
        List[Tuple]: 해당 타입의 카테고리 정보 리스트
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT category_id, category_name, parent_category_id, type, level
        FROM categories 
        WHERE type = ?
        ORDER BY level ASC, category_name ASC
        """
        
        cursor.execute(query, (category_type,))
        categories = cursor.fetchall()
        
        print(f"✅ '{category_type}' 타입 카테고리 {len(categories)}개 조회 완료")
        return categories
        
    except Exception as e:
        print(f"❌ '{category_type}' 타입 카테고리 조회 중 오류 발생: {e}")
        raise


def search_categories_by_name(name_pattern: str) -> List[Tuple]:
    """
    카테고리명으로 검색합니다.
    
    Args:
        name_pattern (str): 검색할 카테고리명 (부분 매치 지원)
    
    Returns:
        List[Tuple]: 검색 결과 카테고리 정보 리스트
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT category_id, category_name, parent_category_id, type, level
        FROM categories 
        WHERE category_name LIKE ?
        ORDER BY level ASC, category_name ASC
        """
        
        cursor.execute(query, (f'%{name_pattern}%',))
        categories = cursor.fetchall()
        
        print(f"✅ '{name_pattern}' 패턴으로 {len(categories)}개 카테고리 검색 완료")
        return categories
        
    except Exception as e:
        print(f"❌ '{name_pattern}' 패턴 카테고리 검색 중 오류 발생: {e}")
        raise


if __name__ == "__main__":
    """이 파일을 직접 실행할 때 테스트"""
    print("🧪 CRUD 함수 테스트를 시작합니다...")
    
    try:
        # 데이터베이스 초기화 (필요한 경우)
        from .database import init_database
        init_database()
        
        # 전체 카테고리 목록 조회 테스트
        print("\n1. 전체 카테고리 목록 조회 테스트:")
        categories = get_all_categories()
        print(f"총 {len(categories)}개 카테고리")
        for cat in categories[:5]:  # 처음 5개만 출력
            print(f"  - {cat}")
        
        # 드롭다운용 목록 생성 테스트
        print("\n2. 드롭다운용 카테고리 목록 테스트:")
        dropdown_categories = get_categories_for_dropdown()
        print(f"총 {len(dropdown_categories)}개 드롭다운 항목")
        for item in dropdown_categories[:10]:  # 처음 10개만 출력
            print(f"  - {item}")
        
        # 특정 타입 조회 테스트
        print("\n3. '수입' 타입 카테고리 조회 테스트:")
        income_categories = get_categories_by_type('수입')
        for cat in income_categories:
            print(f"  - {cat[1]} (Level: {cat[4]})")
        
        # 검색 테스트
        print("\n4. '식비' 패턴 검색 테스트:")
        food_categories = search_categories_by_name('식비')
        for cat in food_categories:
            print(f"  - {cat[1]} (Type: {cat[3]})")
        
        print("\n✅ 모든 CRUD 함수 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
    
    finally:
        from .database import close_db_connection
        close_db_connection()


# =============================================================================
# 슬라이스 2.3: Transactions 테이블 관련 CRUD 함수들
# =============================================================================

def update_transaction_category(transaction_id: int, category_id: int) -> bool:
    """
    특정 거래내역의 카테고리를 업데이트합니다.
    
    Args:
        transaction_id (int): 업데이트할 거래내역 ID
        category_id (int): 새로 할당할 카테고리 ID
    
    Returns:
        bool: 업데이트 성공 여부
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 거래내역 존재 여부 확인
        check_query = "SELECT transaction_id FROM transactions WHERE transaction_id = ?"
        cursor.execute(check_query, (transaction_id,))
        transaction = cursor.fetchone()
        
        if not transaction:
            print(f"⚠️ 거래내역 ID {transaction_id}를 찾을 수 없습니다")
            return False
        
        # 카테고리 존재 여부 확인
        check_category_query = "SELECT category_id FROM categories WHERE category_id = ?"
        cursor.execute(check_category_query, (category_id,))
        category = cursor.fetchone()
        
        if not category:
            print(f"⚠️ 카테고리 ID {category_id}를 찾을 수 없습니다")
            return False
        
        # 카테고리 업데이트
        update_query = """
        UPDATE transactions 
        SET category_id = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE transaction_id = ?
        """
        
        cursor.execute(update_query, (category_id, transaction_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ 거래내역 ID {transaction_id}의 카테고리가 ID {category_id}로 업데이트되었습니다")
            return True
        else:
            print(f"⚠️ 거래내역 ID {transaction_id} 업데이트에 실패했습니다")
            return False
        
    except Exception as e:
        print(f"❌ 거래내역 카테고리 업데이트 중 오류 발생: {e}")
        return False


def update_multiple_transactions_categories(updates: List[Dict[str, int]]) -> bool:
    """
    여러 거래내역의 카테고리를 일괄 업데이트합니다.
    트랜잭션을 사용하여 전체 성공 또는 전체 실패를 보장합니다.
    
    Args:
        updates (List[Dict[str, int]]): 업데이트할 거래내역 목록
            각 딕셔너리는 {'transaction_id': int, 'category_id': int} 형태
    
    Returns:
        bool: 일괄 업데이트 성공 여부
    """
    if not updates:
        print("⚠️ 업데이트할 거래내역이 없습니다")
        return False
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 트랜잭션 시작
        cursor.execute("BEGIN TRANSACTION")
        
        update_query = """
        UPDATE transactions 
        SET category_id = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE transaction_id = ?
        """
        
        for update in updates:
            transaction_id = update.get('transaction_id')
            category_id = update.get('category_id')
            
            if transaction_id is None or category_id is None:
                print(f"⚠️ 잘못된 업데이트 데이터: {update}")
                cursor.execute("ROLLBACK")
                return False
            
            # 개별 업데이트 실행
            cursor.execute(update_query, (category_id, transaction_id))
            
            if cursor.rowcount == 0:
                print(f"⚠️ 거래내역 ID {transaction_id} 업데이트 실패")
                cursor.execute("ROLLBACK")
                return False
        
        # 트랜잭션 커밋
        cursor.execute("COMMIT")
        print(f"✅ {len(updates)}개 거래내역의 카테고리가 일괄 업데이트되었습니다")
        return True
        
    except Exception as e:
        print(f"❌ 일괄 카테고리 업데이트 중 오류 발생: {e}")
        try:
            cursor.execute("ROLLBACK")
        except:
            pass
        return False


def get_uncategorized_transactions() -> List[Dict[str, Any]]:
    """
    미분류 거래내역(category_id가 NULL인 거래)을 조회합니다.
    
    Returns:
        List[Dict[str, Any]]: 미분류 거래내역 목록
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT transaction_id, account_id, timestamp, description, 
               amount_in, amount_out, category_id, is_transfer,
               source_file, source_row_id, created_at, updated_at
        FROM transactions 
        WHERE category_id IS NULL
        ORDER BY timestamp DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # 딕셔너리 형태로 변환
        transactions = []
        columns = ['transaction_id', 'account_id', 'timestamp', 'description',
                  'amount_in', 'amount_out', 'category_id', 'is_transfer',
                  'source_file', 'source_row_id', 'created_at', 'updated_at']
        
        for row in rows:
            transaction = dict(zip(columns, row))
            transactions.append(transaction)
        
        print(f"✅ 미분류 거래내역 {len(transactions)}개 조회 완료")
        return transactions
        
    except Exception as e:
        print(f"❌ 미분류 거래내역 조회 중 오류 발생: {e}")
        return []


def get_categorized_transactions() -> List[Dict[str, Any]]:
    """
    분류 완료된 거래내역(category_id가 NULL이 아닌 거래)을 조회합니다.
    
    Returns:
        List[Dict[str, Any]]: 분류 완료 거래내역 목록
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT t.transaction_id, t.account_id, t.timestamp, t.description, 
               t.amount_in, t.amount_out, t.category_id, t.is_transfer,
               t.source_file, t.source_row_id, t.created_at, t.updated_at,
               c.category_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.category_id
        WHERE t.category_id IS NOT NULL
        ORDER BY t.timestamp DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # 딕셔너리 형태로 변환
        transactions = []
        columns = ['transaction_id', 'account_id', 'timestamp', 'description',
                  'amount_in', 'amount_out', 'category_id', 'is_transfer',
                  'source_file', 'source_row_id', 'created_at', 'updated_at',
                  'category_name']
        
        for row in rows:
            transaction = dict(zip(columns, row))
            transactions.append(transaction)
        
        print(f"✅ 분류 완료 거래내역 {len(transactions)}개 조회 완료")
        return transactions
        
    except Exception as e:
        print(f"❌ 분류 완료 거래내역 조회 중 오류 발생: {e}")
        return []


def get_transaction_by_id(transaction_id: int) -> Optional[Dict[str, Any]]:
    """
    특정 ID의 거래내역을 조회합니다.
    
    Args:
        transaction_id (int): 조회할 거래내역 ID
    
    Returns:
        Optional[Dict[str, Any]]: 거래내역 정보 또는 None
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT t.transaction_id, t.account_id, t.timestamp, t.description, 
               t.amount_in, t.amount_out, t.category_id, t.is_transfer,
               t.source_file, t.source_row_id, t.created_at, t.updated_at,
               c.category_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.category_id
        WHERE t.transaction_id = ?
        """
        
        cursor.execute(query, (transaction_id,))
        row = cursor.fetchone()
        
        if row:
            columns = ['transaction_id', 'account_id', 'timestamp', 'description',
                      'amount_in', 'amount_out', 'category_id', 'is_transfer',
                      'source_file', 'source_row_id', 'created_at', 'updated_at',
                      'category_name']
            
            transaction = dict(zip(columns, row))
            print(f"✅ 거래내역 ID {transaction_id} 조회 성공")
            return transaction
        else:
            print(f"⚠️ 거래내역 ID {transaction_id}를 찾을 수 없습니다")
            return None
        
    except Exception as e:
        print(f"❌ 거래내역 ID {transaction_id} 조회 중 오류 발생: {e}")
        return None


def insert_transaction(transaction_data: Dict[str, Any]) -> Optional[int]:
    """
    새로운 거래내역을 삽입합니다.
    
    Args:
        transaction_data (Dict[str, Any]): 거래내역 데이터
    
    Returns:
        Optional[int]: 삽입된 거래내역의 ID 또는 None
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO transactions (
            account_id, timestamp, description, amount_in, amount_out,
            category_id, is_transfer, source_file, source_row_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(insert_query, (
            transaction_data.get('account_id'),
            transaction_data.get('timestamp'),
            transaction_data.get('description'),
            transaction_data.get('amount_in'),
            transaction_data.get('amount_out'),
            transaction_data.get('category_id'),
            transaction_data.get('is_transfer', False),
            transaction_data.get('source_file'),
            transaction_data.get('source_row_id')
        ))
        
        conn.commit()
        transaction_id = cursor.lastrowid
        
        print(f"✅ 새로운 거래내역이 삽입되었습니다 (ID: {transaction_id})")
        return transaction_id
        
    except Exception as e:
        print(f"❌ 거래내역 삽입 중 오류 발생: {e}")
        return None


def save_setting(key: str, value: Any) -> bool:
    """
    설정 값을 settings 테이블에 저장하거나 업데이트합니다.
    
    Args:
        key (str): 설정 키 (예: 'chatgpt_api_key'). settings 테이블의 setting_key 컬럼에 해당합니다.
        value (Any): 설정 값. settings 테이블의 setting_value 컬럼에 해당합니다.
                     SQLite는 TEXT, INTEGER, REAL, BLOB, NULL 타입을 지원합니다.
                     복잡한 객체는 JSON 등으로 직렬화하여 저장해야 합니다.
    
    Returns:
        bool: 저장 성공 시 True, 실패 시 False
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # UPSERT 기능 사용: setting_key가 이미 존재하면 setting_value 업데이트, 없으면 새 행 삽입
        # setting_type은 일단 'string'으로 하드코딩하거나 기본값 사용
        query = """
        INSERT INTO settings (setting_key, setting_value, setting_type)
        VALUES (?, ?, ?)
        ON CONFLICT(setting_key) DO UPDATE SET
        setting_value = excluded.setting_value,
        updated_at = CURRENT_TIMESTAMP
        """
        
        # SQLite는 자동으로 일부 타입을 변환하지만, 명시적으로 문자열로 저장하는 것이 안전합니다.
        # setting_type은 일단 'string'으로 저장합니다.
        cursor.execute(query, (key, str(value), 'string'))
        conn.commit()
        
        print(f"✅ 설정 '{key}' 저장/업데이트 성공")
        return True
        
    except Exception as e:
        print(f"❌ 설정 '{key}' 저장/업데이트 중 오류 발생: {e}")
        return False


def get_setting(key: str) -> Optional[str]:
    """
    settings 테이블에서 설정 값을 조회합니다.
    
    Args:
        key (str): 조회할 설정 키. settings 테이블의 setting_key 컬럼에 해당합니다.
    
    Returns:
        Optional[str]: 설정 값 (문자열 형태) 또는 None (키가 없는 경우)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT setting_value FROM settings WHERE setting_key = ?"
        
        cursor.execute(query, (key,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ 설정 '{key}' 조회 성공: {result[0]}")
            return result[0] # 값 반환 (TEXT 형태)
        else:
            print(f"⚠️ 설정 '{key}'를 찾을 수 없습니다")
            return None
        
    except Exception as e:
        print(f"❌ 설정 '{key}' 조회 중 오류 발생: {e}")
        # 오류 발생 시에도 None을 반환하거나, 필요에 따라 예외를 다시 발생시킬 수 있습니다. 