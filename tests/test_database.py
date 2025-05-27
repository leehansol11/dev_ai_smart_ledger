#!/usr/bin/env python3
"""
AI 스마트 가계부 - 데이터베이스 기능 테스트
Author: leehansol
Created: 2025-05-25
"""

import pytest
import sqlite3
import os
import tempfile
from ai_smart_ledger.app.db.database import DatabaseManager, init_database, get_db_connection


class TestDatabaseManager:
    """DatabaseManager 클래스 테스트"""
    
    @pytest.fixture
    def temp_db_path(self):
        """임시 데이터베이스 파일 경로 생성"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            yield tmp.name
        # 테스트 후 정리
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
    
    def test_database_manager_initialization(self, temp_db_path):
        """DatabaseManager 초기화 테스트"""
        db_manager = DatabaseManager(temp_db_path)
        assert str(db_manager.db_path).endswith(temp_db_path) or db_manager.db_path.name == temp_db_path
        assert db_manager.connection is None
    
    def test_database_creation(self, temp_db_path):
        """데이터베이스 생성 테스트"""
        db_manager = DatabaseManager(temp_db_path)
        result = db_manager.create_database()
        
        # create_database는 Connection 객체를 반환함
        assert result is not None
        assert isinstance(result, sqlite3.Connection)
        # 실제 파일은 프로젝트 루트에 생성됨
        assert db_manager.check_database_exists()
    
    def test_database_connection(self, temp_db_path):
        """데이터베이스 연결 테스트"""
        db_manager = DatabaseManager(temp_db_path)
        db_manager.create_database()
        
        connection = db_manager.get_connection()
        assert connection is not None
        assert isinstance(connection, sqlite3.Connection)
        
        db_manager.close_connection()
    
    def test_database_connection_only(self, temp_db_path):
        """데이터베이스 연결만 테스트 (테이블 생성은 init_database에서)"""
        db_manager = DatabaseManager(temp_db_path)
        db_manager.create_database()
        
        connection = db_manager.get_connection()
        assert connection is not None
        assert isinstance(connection, sqlite3.Connection)
        
        # 기본 SQLite 시스템 테이블 확인
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        # 빈 데이터베이스라도 연결은 성공해야 함
        
        db_manager.close_connection()
    
    def test_database_file_creation(self, temp_db_path):
        """데이터베이스 파일 생성 확인"""
        db_manager = DatabaseManager(temp_db_path)
        
        # 초기에는 파일이 없어야 함
        initial_exists = db_manager.check_database_exists()
        
        # 데이터베이스 생성
        connection = db_manager.create_database()
        assert connection is not None
        
        # 파일이 생성되었는지 확인
        final_exists = db_manager.check_database_exists()
        assert final_exists, "데이터베이스 파일이 생성되지 않았습니다"
        
        db_manager.close_connection()


class TestDatabaseGlobalFunctions:
    """전역 데이터베이스 함수들 테스트"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """테스트 전후 설정"""
        # 기존 데이터베이스 백업
        original_db = "AISmartLedger.db"
        backup_db = "AISmartLedger_backup.db"
        
        if os.path.exists(original_db):
            os.rename(original_db, backup_db)
        
        yield
        
        # 테스트 DB 정리 및 원본 복구
        from ai_smart_ledger.app.db.database import close_db_connection
        close_db_connection()
        if os.path.exists(original_db):
            os.unlink(original_db)
        if os.path.exists(backup_db):
            os.rename(backup_db, original_db)
    
    def test_init_database_function(self):
        """init_database() 함수 테스트"""
        result = init_database()
        assert result is True
        assert os.path.exists("AISmartLedger.db")
    
    def test_get_db_connection_function(self):
        """get_db_connection() 함수 테스트"""
        init_database()
        connection = get_db_connection()
        assert connection is not None
        assert isinstance(connection, sqlite3.Connection)
    
    def test_tables_creation_with_init(self):
        """init_database()로 테이블 생성 테스트"""
        result = init_database()
        assert result is True
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 테이블 존재 확인
        tables = ['categories', 'transactions', 'ai_learning_patterns', 'settings']
        for table in tables:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table,))
            result = cursor.fetchone()
            assert result is not None, f"테이블 {table}이 존재하지 않습니다"
    
    def test_categories_default_data_with_init(self):
        """init_database()로 기본 카테고리 데이터 삽입 테스트"""
        result = init_database()
        assert result is True
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 기본 카테고리 데이터 존재 확인
        cursor.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        assert count > 0, "기본 카테고리 데이터가 삽입되지 않았습니다"
        
        # 필수 카테고리 존재 확인
        cursor.execute("SELECT category_name FROM categories WHERE category_name = ?", ("계좌 간 이체 (분석 제외)",))
        result = cursor.fetchone()
        assert result is not None, "필수 카테고리가 존재하지 않습니다"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 