"""
슬라이스 2.1 DB 기능 테스트
Author: leehansol
Created: 2025-05-25

테스트 목표:
- categories 테이블에서 기본 카테고리 목록을 가져오는 함수 구현 [PRD 3.2.5]
- "계좌 간 이체 (분석 제외)" 포함하여 카테고리 목록 제대로 반환
"""

import pytest
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉터리를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_smart_ledger.app.db.database import init_database, close_db_connection, get_db_connection


class TestSlice2_1_DB:
    """슬라이스 2.1 DB 기능 테스트 클래스"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """각 테스트 전후에 실행되는 설정"""
        # 테스트용 DB 초기화
        test_db_path = project_root / "test_AISmartLedger.db"
        
        # 기존 테스트 DB 파일이 있으면 삭제
        if test_db_path.exists():
            test_db_path.unlink()
        
        # 테스트용 DB 매니저 설정
        from ai_smart_ledger.app.db.database import db_manager
        db_manager.db_path = test_db_path
        
        # DB 초기화 (기본 카테고리 포함)
        init_result = init_database()
        assert init_result is True, "테스트 DB 초기화 실패"
        
        yield
        
        # 정리: DB 연결 종료 및 파일 삭제
        close_db_connection()
        if test_db_path.exists():
            test_db_path.unlink()
    
    def test_crud_module_exists(self):
        """crud.py 모듈이 존재하는지 확인"""
        # crud.py 파일이 없으면 import 에러가 발생해야 함
        # 이는 아직 구현되지 않았음을 의미
        try:
            from ai_smart_ledger.app.db import crud
            # 모듈이 존재하면 기본적인 함수가 있는지 확인
            assert hasattr(crud, 'get_all_categories'), "get_all_categories 함수가 없습니다"
        except ImportError:
            # 아직 crud.py가 없는 경우 - 이는 예상된 상황
            assert False, "crud.py 모듈이 아직 생성되지 않았습니다"
    
    def test_get_all_categories_function_exists(self):
        """get_all_categories 함수가 존재하는지 확인"""
        from ai_smart_ledger.app.db import crud
        
        # 함수가 존재하는지 확인
        assert hasattr(crud, 'get_all_categories'), "get_all_categories 함수가 없습니다"
        assert callable(crud.get_all_categories), "get_all_categories가 호출 가능한 함수가 아닙니다"
    
    def test_get_all_categories_returns_list(self):
        """get_all_categories 함수가 리스트를 반환하는지 확인"""
        from ai_smart_ledger.app.db import crud
        
        result = crud.get_all_categories()
        
        # 반환 타입이 리스트인지 확인
        assert isinstance(result, list), "get_all_categories 함수가 리스트를 반환하지 않습니다"
        
        # 빈 리스트가 아닌지 확인 (기본 카테고리가 있어야 함)
        assert len(result) > 0, "카테고리 목록이 비어있습니다"
    
    def test_categories_include_transfer_category(self):
        """카테고리 목록에 '계좌 간 이체 (분석 제외)' 항목이 포함되는지 확인"""
        from ai_smart_ledger.app.db import crud
        
        categories = crud.get_all_categories()
        
        # 카테고리명 리스트 추출 (튜플 또는 딕셔너리 구조 고려)
        category_names = []
        for category in categories:
            if isinstance(category, tuple):
                # (id, name, ...) 형태라고 가정
                category_names.append(category[1])  # name 위치
            elif isinstance(category, dict):
                # {'id': x, 'name': y, ...} 형태라고 가정
                category_names.append(category.get('category_name') or category.get('name'))
            else:
                # 단순 문자열이라고 가정
                category_names.append(str(category))
        
        # '계좌 간 이체 (분석 제외)' 항목이 있는지 확인
        assert "계좌 간 이체 (분석 제외)" in category_names, \
            f"'계좌 간 이체 (분석 제외)' 항목이 카테고리 목록에 없습니다. 현재 카테고리: {category_names}"
    
    def test_categories_include_basic_income_categories(self):
        """카테고리 목록에 기본 수입 카테고리들이 포함되는지 확인"""
        from ai_smart_ledger.app.db import crud
        
        categories = crud.get_all_categories()
        
        # 카테고리명 리스트 추출
        category_names = []
        for category in categories:
            if isinstance(category, tuple):
                category_names.append(category[1])
            elif isinstance(category, dict):
                category_names.append(category.get('category_name') or category.get('name'))
            else:
                category_names.append(str(category))
        
        # PRD 3.2.5의 기본 수입 카테고리들이 있는지 확인
        expected_income_categories = ["수입", "근로소득", "급여", "상여"]
        for expected_category in expected_income_categories:
            assert expected_category in category_names, \
                f"기본 수입 카테고리 '{expected_category}'가 목록에 없습니다"
    
    def test_categories_include_basic_expense_categories(self):
        """카테고리 목록에 기본 지출 카테고리들이 포함되는지 확인"""
        from ai_smart_ledger.app.db import crud
        
        categories = crud.get_all_categories()
        
        # 카테고리명 리스트 추출
        category_names = []
        for category in categories:
            if isinstance(category, tuple):
                category_names.append(category[1])
            elif isinstance(category, dict):
                category_names.append(category.get('category_name') or category.get('name'))
            else:
                category_names.append(str(category))
        
        # PRD 3.2.5의 기본 지출 카테고리들이 있는지 확인
        expected_expense_categories = ["지출", "식비", "주식", "외식", "간식"]
        for expected_category in expected_expense_categories:
            assert expected_category in category_names, \
                f"기본 지출 카테고리 '{expected_category}'가 목록에 없습니다"
    
    def test_get_categories_for_dropdown_function_exists(self):
        """드롭다운용 카테고리 리스트를 가져오는 함수가 존재하는지 확인"""
        from ai_smart_ledger.app.db import crud
        
        # 드롭다운에 사용할 수 있는 형태의 카테고리 리스트 함수
        assert hasattr(crud, 'get_categories_for_dropdown'), \
            "get_categories_for_dropdown 함수가 없습니다"
        assert callable(crud.get_categories_for_dropdown), \
            "get_categories_for_dropdown가 호출 가능한 함수가 아닙니다"
    
    def test_get_categories_for_dropdown_returns_proper_format(self):
        """드롭다운용 카테고리 함수가 적절한 형태를 반환하는지 확인"""
        from ai_smart_ledger.app.db import crud
        
        dropdown_categories = crud.get_categories_for_dropdown()
        
        # 리스트 형태인지 확인
        assert isinstance(dropdown_categories, list), \
            "get_categories_for_dropdown이 리스트를 반환하지 않습니다"
        
        # 빈 리스트가 아닌지 확인
        assert len(dropdown_categories) > 0, "드롭다운용 카테고리 목록이 비어있습니다"
        
        # 각 항목이 적절한 형태인지 확인 (문자열 또는 (id, name) 튜플)
        for item in dropdown_categories:
            assert isinstance(item, (str, tuple, dict)), \
                f"드롭다운 카테고리 항목이 예상된 형태가 아닙니다: {type(item)}"
    
    def test_categories_database_structure(self):
        """categories 테이블의 기본 구조가 올바른지 확인"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # categories 테이블이 존재하는지 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
        table_exists = cursor.fetchone()
        assert table_exists is not None, "categories 테이블이 존재하지 않습니다"
        
        # 테이블 구조 확인
        cursor.execute("PRAGMA table_info(categories)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]  # column name은 인덱스 1
        
        # 필수 컬럼들이 있는지 확인
        required_columns = ['category_id', 'category_name', 'parent_category_id', 'type']
        for col in required_columns:
            assert col in column_names, f"필수 컬럼 '{col}'이 categories 테이블에 없습니다"
        
        # 데이터가 존재하는지 확인
        cursor.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        assert count > 0, "categories 테이블에 데이터가 없습니다"


if __name__ == "__main__":
    pytest.main([__file__]) 