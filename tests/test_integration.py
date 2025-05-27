#!/usr/bin/env python3
"""
AI 스마트 가계부 - 0단계 통합 테스트
Author: leehansol
Created: 2025-05-25
"""

import pytest
import sys
import os
from PySide6.QtWidgets import QApplication

from ai_smart_ledger.app.db.database import init_database, close_db_connection, get_db_connection
from ai_smart_ledger.app.ui.main_window import MainWindow


class TestIntegration:
    """0단계 통합 테스트"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """QApplication 인스턴스 생성"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        yield app
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """테스트 전후 설정"""
        # 기존 데이터베이스 백업
        original_db = "AISmartLedger.db"
        backup_db = "AISmartLedger_integration_backup.db"
        
        if os.path.exists(original_db):
            os.rename(original_db, backup_db)
        
        yield
        
        # 테스트 DB 정리 및 원본 복구
        close_db_connection()
        if os.path.exists(original_db):
            os.unlink(original_db)
        if os.path.exists(backup_db):
            os.rename(backup_db, original_db)
    
    def test_database_initialization_before_ui(self, app):
        """UI 시작 전 데이터베이스 초기화 테스트"""
        # 데이터베이스 초기화
        result = init_database()
        assert result is True
        assert os.path.exists("AISmartLedger.db")
        
        # 데이터베이스 연결 확인
        connection = get_db_connection()
        assert connection is not None
    
    def test_ui_startup_with_database(self, app):
        """데이터베이스와 함께 UI 시작 테스트"""
        # 데이터베이스 초기화
        init_database()
        
        # UI 생성
        main_window = MainWindow()
        assert main_window is not None
        assert main_window.windowTitle() == "AI 스마트 가계부"
        
        # 데이터베이스 연결 상태 확인
        connection = get_db_connection()
        assert connection is not None
        
        main_window.close()
    
    def test_main_application_flow(self, app):
        """메인 애플리케이션 전체 흐름 테스트"""
        # 1. 데이터베이스 초기화
        db_result = init_database()
        assert db_result is True
        
        # 2. UI 생성 및 설정
        main_window = MainWindow()
        assert main_window.windowTitle() == "AI 스마트 가계부"
        
        # 3. 메뉴 바 기능 확인
        menu_bar = main_window.menuBar()
        assert menu_bar is not None
        
        # 4. 화면 전환 시스템 확인
        central_widget = main_window.centralWidget()
        assert central_widget.currentIndex() == main_window.SCREEN_WELCOME
        
        # 5. 데이터베이스에서 카테고리 데이터 조회 가능한지 확인
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        assert count > 0, "카테고리 데이터가 없습니다"
        
        main_window.close()
    
    def test_database_cleanup(self):
        """데이터베이스 정리 테스트"""
        init_database()
        connection = get_db_connection()
        assert connection is not None
        
        # 연결 정리
        close_db_connection()
        
        # 데이터베이스 파일은 여전히 존재해야 함
        assert os.path.exists("AISmartLedger.db")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 