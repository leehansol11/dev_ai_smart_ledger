import sqlite3
import os
from pathlib import Path

class DatabaseManager:
    """SQLite 데이터베이스 관리 클래스"""
    
    def __init__(self, db_name="AISmartLedger.db"):
        """
        데이터베이스 매니저 초기화
        
        Args:
            db_name: 데이터베이스 파일명 (기본값: AISmartLedger.db)
        """
        # 프로젝트 최상위 폴더에 DB 파일 생성
        project_root = Path(__file__).parent.parent.parent.parent
        self.db_path = project_root / db_name
        self.connection = None
    
    def create_database(self):
        """
        AISmartLedger.db 파일을 생성하고 연결합니다
        
        Returns:
            sqlite3.Connection: 데이터베이스 연결 객체
        """
        try:
            # 데이터베이스 파일 생성 및 연결
            self.connection = sqlite3.connect(self.db_path)
            print(f"✅ 데이터베이스 파일이 생성되었습니다: {self.db_path}")
            
            # 외래키 제약조건 활성화 (데이터 무결성을 위해)
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            return self.connection
            
        except sqlite3.Error as e:
            print(f"❌ 데이터베이스 생성 중 오류가 발생했습니다: {e}")
            return None
    
    def get_connection(self):
        """
        데이터베이스 연결을 반환합니다
        연결이 없으면 새로 생성합니다
        
        Returns:
            sqlite3.Connection: 데이터베이스 연결 객체
        """
        if self.connection is None:
            self.connection = self.create_database()
        return self.connection
    
    def close_connection(self):
        """데이터베이스 연결을 닫습니다"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("🔐 데이터베이스 연결이 닫혔습니다")
    
    def execute_query(self, query, params=None):
        """
        SQL 쿼리를 실행합니다
        
        Args:
            query: 실행할 SQL 쿼리
            params: 쿼리 매개변수 (선택사항)
        
        Returns:
            cursor: 쿼리 실행 결과
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            connection.commit()
            return cursor
            
        except sqlite3.Error as e:
            print(f"❌ 쿼리 실행 중 오류가 발생했습니다: {e}")
            return None
    
    def check_database_exists(self):
        """
        데이터베이스 파일이 존재하는지 확인합니다
        
        Returns:
            bool: 파일 존재 여부
        """
        return self.db_path.exists()


# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()


def get_db_connection():
    """
    데이터베이스 연결을 가져오는 편의 함수
    
    Returns:
        sqlite3.Connection: 데이터베이스 연결 객체
    """
    return db_manager.get_connection()


def close_db_connection():
    """데이터베이스 연결을 닫는 편의 함수"""
    db_manager.close_connection()


def init_database():
    """
    데이터베이스를 초기화하는 함수
    프로그램 시작 시 호출됩니다
    """
    print("🗃️ 데이터베이스 초기화를 시작합니다...")
    
    # 첫 실행 여부 확인
    is_first_run = not db_manager.check_database_exists()
    
    if is_first_run:
        print("📁 새로운 데이터베이스 파일을 생성합니다...")
        connection = db_manager.create_database()
        if not connection:
            print("❌ 데이터베이스 초기화에 실패했습니다!")
            return False
    else:
        print("📂 기존 데이터베이스 파일을 사용합니다...")
        db_manager.get_connection()
    
    # 테이블 생성 (이미 존재하면 무시됨)
    try:
        from .models import create_all_tables
        from .initial_data import insert_default_categories, insert_default_settings
        
        # 테이블 생성
        create_all_tables()
        
        # 첫 실행 시 기본 데이터 삽입
        if is_first_run:
            print("📋 기본 카테고리 데이터를 삽입합니다...")
            insert_default_categories()
            
            print("🔧 기본 설정 데이터를 삽입합니다...")
            insert_default_settings()
        
        print("✅ 데이터베이스 초기화가 완료되었습니다!")
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 중 오류 발생: {e}")
        return False


if __name__ == "__main__":
    """이 파일을 직접 실행할 때 데이터베이스를 생성합니다"""
    print("🏁 데이터베이스 생성 테스트를 시작합니다...")
    
    # 데이터베이스 초기화
    if init_database():
        print("🎉 테스트 성공!")
        
        # 연결 테스트
        conn = get_db_connection()
        if conn:
            print("🔗 데이터베이스 연결 테스트 성공!")
            
            # 간단한 테스트 쿼리
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()
            print(f"📊 SQLite 버전: {version[0]}")
        
        # 연결 종료
        close_db_connection()
    else:
        print("💥 테스트 실패!") 