"""
데이터베이스 CRUD 연산 함수들
Author: leehansol
Created: 2025-05-25

슬라이스 2.1에서 필요한 categories 테이블 관련 함수들을 구현합니다.
"""

from typing import List, Tuple, Dict, Optional
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