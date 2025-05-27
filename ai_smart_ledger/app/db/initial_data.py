"""
기본 카테고리 데이터 초기화 스크립트
PRD 3.2.5에 정의된 카테고리 트리 구조를 데이터베이스에 삽입

Author: leehansol
Created: 2025-05-25
"""

from .database import db_manager


def insert_default_categories():
    """
    PRD 3.2.5에 정의된 기본 카테고리 데이터를 삽입합니다.
    
    트리 구조:
    가계부
    ├── 수입
    ├── 지출  
    └── 계좌 간 이체 (분석 제외)
    """
    
    # 기본 카테고리 데이터 정의
    categories_data = [
        # 레벨 1: 최상위 카테고리
        (None, "수입", "수입", 1),
        (None, "지출", "지출", 1),
        (None, "계좌 간 이체 (분석 제외)", "이체", 1),
        
        # 레벨 2: 수입 하위 카테고리
        ("수입", "근로소득", "수입", 2),
        ("수입", "사업소득", "수입", 2),
        ("수입", "재산소득", "수입", 2),
        ("수입", "이전소득", "수입", 2),
        ("수입", "부수입", "수입", 2),
        ("수입", "전월이월", "수입", 2),
        ("수입", "저축/보험 (자산관리용)", "수입", 2),
        
        # 레벨 3: 근로소득 하위 카테고리
        ("근로소득", "급여", "수입", 3),
        ("근로소득", "상여", "수입", 3),
        ("근로소득", "연차수당", "수입", 3),
        ("근로소득", "기타 수당", "수입", 3),
        
        # 레벨 3: 재산소득 하위 카테고리
        ("재산소득", "이자", "수입", 3),
        ("재산소득", "배당", "수입", 3),
        ("재산소득", "임대료", "수입", 3),
        
        # 레벨 3: 이전소득 하위 카테고리
        ("이전소득", "정부지원금", "수입", 3),
        ("이전소득", "연금", "수입", 3),
        
        # 레벨 3: 부수입 하위 카테고리
        ("부수입", "보험금", "수입", 3),
        ("부수입", "공모주·배당금", "수입", 3),
        ("부수입", "캐시백·앱테크 수익", "수입", 3),
        
        # 레벨 2: 지출 하위 카테고리
        ("지출", "식비", "지출", 2),
        ("지출", "주거/통신", "지출", 2),
        ("지출", "생활용품", "지출", 2),
        ("지출", "의류/미용", "지출", 2),
        ("지출", "건강/문화", "지출", 2),
        ("지출", "교육/육아", "지출", 2),
        ("지출", "교통/차량", "지출", 2),
        ("지출", "경조사비/회비", "지출", 2),
        ("지출", "세금/이자", "지출", 2),
        ("지출", "용돈/기타", "지출", 2),
        ("지출", "카드대금", "지출", 2),
        ("지출", "저축/보험", "지출", 2),
        
        # 레벨 3: 식비 하위 카테고리
        ("식비", "주식", "지출", 3),
        ("식비", "부식", "지출", 3),
        ("식비", "외식", "지출", 3),
        ("식비", "간식", "지출", 3),
        ("식비", "커피/음료", "지출", 3),
        ("식비", "술/유흥", "지출", 3),
        ("식비", "기타", "지출", 3),
        
        # 레벨 3: 주거/통신 하위 카테고리
        ("주거/통신", "월세/전세보증금이자·관리비", "지출", 3),
        ("주거/통신", "수도/전기/가스", "지출", 3),
        ("주거/통신", "통신비", "지출", 3),
    ]
    
    try:
        print("🏗️ 기본 카테고리 데이터 삽입을 시작합니다...")
        
        # 중복 체크: 이미 데이터가 있는지 확인
        check_query = "SELECT COUNT(*) FROM categories WHERE is_default = TRUE"
        cursor = db_manager.execute_query(check_query)
        
        if cursor:
            existing_count = cursor.fetchone()[0]
            if existing_count > 0:
                print(f"⚠️ 이미 기본 카테고리 데이터가 존재합니다 ({existing_count}개)")
                return True
        
        # 카테고리 ID 매핑 (부모-자식 관계 설정용)
        category_id_map = {}
        
        # 트랜잭션 시작
        db_manager.get_connection().execute("BEGIN")
        
        # 레벨 순서대로 삽입 (부모가 먼저 삽입되어야 함)
        for level in range(1, 4):
            level_categories = [cat for cat in categories_data if cat[3] == level]
            
            for parent_name, category_name, category_type, category_level in level_categories:
                # 부모 카테고리 ID 찾기
                parent_id = None
                if parent_name:
                    parent_id = category_id_map.get(parent_name)
                    if parent_id is None:
                        print(f"❌ 부모 카테고리를 찾을 수 없습니다: {parent_name}")
                        continue
                
                # 카테고리 삽입
                insert_query = """
                INSERT INTO categories (category_name, parent_category_id, type, level, is_default)
                VALUES (?, ?, ?, ?, TRUE)
                """
                
                cursor = db_manager.execute_query(insert_query, (category_name, parent_id, category_type, category_level))
                
                if cursor:
                    # 삽입된 카테고리의 ID를 매핑에 저장
                    category_id = cursor.lastrowid
                    category_id_map[category_name] = category_id
                    print(f"✅ 삽입 완료: {category_name} (ID: {category_id})")
                else:
                    print(f"❌ 삽입 실패: {category_name}")
                    raise Exception(f"카테고리 삽입 실패: {category_name}")
        
        # 트랜잭션 커밋
        db_manager.get_connection().commit()
        
        print(f"🎉 기본 카테고리 데이터 삽입 완료! 총 {len(categories_data)}개 카테고리")
        return True
        
    except Exception as e:
        print(f"❌ 기본 카테고리 데이터 삽입 중 오류 발생: {e}")
        
        # 트랜잭션 롤백
        try:
            db_manager.get_connection().rollback()
            print("🔄 트랜잭션이 롤백되었습니다.")
        except:
            pass
            
        return False


def insert_default_settings():
    """
    기본 설정 데이터를 삽입합니다
    """
    
    # 기본 설정 데이터
    default_settings = [
        ("openai_api_key", "", "string", "OpenAI API 키"),
        ("transfer_time_range", "60", "integer", "계좌 간 이체 시간 허용 범위 (분)"),
        ("ai_learning_version", "1.0", "string", "AI 학습 데이터 현재 활성 버전 정보"),
        ("window_width", "1200", "integer", "마지막 창 너비"),
        ("window_height", "800", "integer", "마지막 창 높이"),
        ("window_x", "100", "integer", "마지막 창 X 위치"),
        ("window_y", "100", "integer", "마지막 창 Y 위치"),
        ("show_file_format_popup", "true", "boolean", "파일 형식 안내 팝업 표시 여부"),
    ]
    
    try:
        print("🔧 기본 설정 데이터 삽입을 시작합니다...")
        
        # 중복 체크: 이미 데이터가 있는지 확인
        check_query = "SELECT COUNT(*) FROM settings"
        cursor = db_manager.execute_query(check_query)
        
        if cursor:
            existing_count = cursor.fetchone()[0]
            if existing_count > 0:
                print(f"⚠️ 이미 설정 데이터가 존재합니다 ({existing_count}개)")
                return True
        
        # 트랜잭션 시작
        db_manager.get_connection().execute("BEGIN")
        
        # 설정 데이터 삽입
        insert_query = """
        INSERT INTO settings (setting_key, setting_value, setting_type, description)
        VALUES (?, ?, ?, ?)
        """
        
        success_count = 0
        for setting_key, setting_value, setting_type, description in default_settings:
            cursor = db_manager.execute_query(insert_query, (setting_key, setting_value, setting_type, description))
            
            if cursor:
                print(f"✅ 설정 삽입 완료: {setting_key} = {setting_value}")
                success_count += 1
            else:
                print(f"❌ 설정 삽입 실패: {setting_key}")
                raise Exception(f"설정 삽입 실패: {setting_key}")
        
        # 트랜잭션 커밋
        db_manager.get_connection().commit()
        
        print(f"🎉 기본 설정 데이터 삽입 완료! 총 {success_count}개 설정")
        return True
        
    except Exception as e:
        print(f"❌ 기본 설정 데이터 삽입 중 오류 발생: {e}")
        
        # 트랜잭션 롤백
        try:
            db_manager.get_connection().rollback()
            print("🔄 트랜잭션이 롤백되었습니다.")
        except:
            pass
            
        return False


def view_categories_tree():
    """
    삽입된 카테고리를 트리 구조로 출력합니다 (확인용)
    """
    try:
        print("\n🌳 카테고리 트리 구조:")
        print("=" * 50)
        
        # 레벨 1 카테고리들 조회
        query_level1 = """
        SELECT category_id, category_name, type 
        FROM categories 
        WHERE level = 1 AND is_default = TRUE
        ORDER BY category_id
        """
        
        cursor = db_manager.execute_query(query_level1)
        if not cursor:
            print("❌ 카테고리 조회에 실패했습니다.")
            return
            
        level1_categories = cursor.fetchall()
        
        for cat_id, cat_name, cat_type in level1_categories:
            print(f"📁 {cat_name} ({cat_type})")
            
            # 레벨 2 카테고리들 조회
            query_level2 = """
            SELECT category_id, category_name, type 
            FROM categories 
            WHERE parent_category_id = ? AND level = 2
            ORDER BY category_id
            """
            
            cursor2 = db_manager.execute_query(query_level2, (cat_id,))
            if cursor2:
                level2_categories = cursor2.fetchall()
                
                for i, (cat_id2, cat_name2, cat_type2) in enumerate(level2_categories):
                    is_last_level2 = (i == len(level2_categories) - 1)
                    prefix = "└── " if is_last_level2 else "├── "
                    print(f"    {prefix}{cat_name2}")
                    
                    # 레벨 3 카테고리들 조회
                    query_level3 = """
                    SELECT category_id, category_name, type 
                    FROM categories 
                    WHERE parent_category_id = ? AND level = 3
                    ORDER BY category_id
                    """
                    
                    cursor3 = db_manager.execute_query(query_level3, (cat_id2,))
                    if cursor3:
                        level3_categories = cursor3.fetchall()
                        
                        for j, (cat_id3, cat_name3, cat_type3) in enumerate(level3_categories):
                            is_last_level3 = (j == len(level3_categories) - 1)
                            
                            if is_last_level2:
                                prefix3 = "    └── " if is_last_level3 else "    ├── "
                            else:
                                prefix3 = "│   └── " if is_last_level3 else "│   ├── "
                            
                            print(f"        {prefix3}{cat_name3}")
        
        print("=" * 50)
        
        # 통계 정보
        stats_query = """
        SELECT 
            level,
            COUNT(*) as count
        FROM categories 
        WHERE is_default = TRUE
        GROUP BY level
        ORDER BY level
        """
        
        cursor = db_manager.execute_query(stats_query)
        if cursor:
            stats = cursor.fetchall()
            print("📊 카테고리 통계:")
            for level, count in stats:
                print(f"   레벨 {level}: {count}개")
            
            total = sum(count for level, count in stats)
            print(f"   전체: {total}개")
        
    except Exception as e:
        print(f"❌ 카테고리 트리 출력 중 오류 발생: {e}")


if __name__ == "__main__":
    """이 파일을 직접 실행할 때 기본 데이터를 삽입합니다"""
    print("🏁 기본 카테고리 데이터 삽입 테스트를 시작합니다...")
    
    # 데이터베이스 연결 확인
    if db_manager.get_connection():
        # 기본 데이터 삽입
        if insert_default_categories():
            print("🎉 기본 데이터 삽입 성공!")
            
            # 결과 확인
            view_categories_tree()
        else:
            print("💥 기본 데이터 삽입 실패!")
    else:
        print("❌ 데이터베이스 연결에 실패했습니다!") 