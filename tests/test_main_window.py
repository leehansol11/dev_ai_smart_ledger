#!/usr/bin/env python3
"""
AI 스마트 가계부 - 메인 윈도우 UI 테스트
Author: leehansol
Created: 2025-05-25
"""

import pytest
import sys
from PySide6.QtWidgets import QApplication, QStackedWidget
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

from ai_smart_ledger.app.ui.main_window import MainWindow


class TestMainWindow:
    """MainWindow 클래스 테스트"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """QApplication 인스턴스 생성"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        yield app
        # 테스트 후 정리는 하지 않음 (다른 테스트에서도 사용할 수 있음)
    
    @pytest.fixture
    def main_window(self, app):
        """MainWindow 인스턴스 생성"""
        window = MainWindow()
        yield window
        window.close()
    
    def test_window_title(self, main_window):
        """윈도우 제목 테스트"""
        assert main_window.windowTitle() == "AI 스마트 가계부"
    
    def test_window_size(self, main_window):
        """윈도우 크기 테스트"""
        geometry = main_window.geometry()
        assert geometry.width() == 1200
        assert geometry.height() == 800
    
    def test_central_widget_type(self, main_window):
        """중앙 위젯 타입 테스트"""
        central_widget = main_window.centralWidget()
        assert isinstance(central_widget, QStackedWidget)
    
    def test_menu_bar_exists(self, main_window):
        """메뉴 바 존재 테스트"""
        menu_bar = main_window.menuBar()
        assert menu_bar is not None
        
        # 메뉴 항목들 존재 확인
        actions = menu_bar.actions()
        menu_titles = [action.text() for action in actions]
        
        expected_menus = ['파일(&F)', '보기(&V)', '도구(&T)', '도움말(&H)']
        for expected_menu in expected_menus:
            assert expected_menu in menu_titles, f"메뉴 '{expected_menu}'가 존재하지 않습니다"
    
    def test_file_menu_actions(self, main_window):
        """파일 메뉴 액션들 테스트"""
        menu_bar = main_window.menuBar()
        file_menu = None
        
        for action in menu_bar.actions():
            if action.text() == '파일(&F)':
                file_menu = action.menu()
                break
        
        assert file_menu is not None, "파일 메뉴가 존재하지 않습니다"
        
        # 파일 메뉴 액션들 확인
        file_actions = [action.text() for action in file_menu.actions() if action.text()]
        expected_actions = ['거래내역 파일 열기...', '내보내기...', '종료(&X)']
        
        for expected_action in expected_actions:
            assert expected_action in file_actions, f"파일 메뉴 액션 '{expected_action}'이 존재하지 않습니다"
    
    def test_view_menu_actions(self, main_window):
        """보기 메뉴 액션들 테스트"""
        menu_bar = main_window.menuBar()
        view_menu = None
        
        for action in menu_bar.actions():
            if action.text() == '보기(&V)':
                view_menu = action.menu()
                break
        
        assert view_menu is not None, "보기 메뉴가 존재하지 않습니다"
        
        # 보기 메뉴 액션들 확인
        view_actions = [action.text() for action in view_menu.actions() if action.text()]
        expected_actions = ['대시보드', '거래내역', '새로고침']
        
        for expected_action in expected_actions:
            assert expected_action in view_actions, f"보기 메뉴 액션 '{expected_action}'이 존재하지 않습니다"
    
    def test_screen_constants(self, main_window):
        """화면 식별자 상수 테스트"""
        assert hasattr(main_window, 'SCREEN_WELCOME')
        assert hasattr(main_window, 'SCREEN_TRANSACTIONS')
        assert hasattr(main_window, 'SCREEN_DASHBOARD')
        assert hasattr(main_window, 'SCREEN_SETTINGS')
        
        assert main_window.SCREEN_WELCOME == 0
        assert main_window.SCREEN_TRANSACTIONS == 1
        assert main_window.SCREEN_DASHBOARD == 2
        assert main_window.SCREEN_SETTINGS == 3
    
    def test_initial_screen(self, main_window):
        """초기 화면 테스트"""
        central_widget = main_window.centralWidget()
        assert central_widget.currentIndex() == main_window.SCREEN_WELCOME
    
    def test_screen_transition_methods(self, main_window):
        """화면 전환 메서드 존재 테스트"""
        assert hasattr(main_window, 'show_welcome_screen')
        assert hasattr(main_window, 'show_transactions_screen')
        assert hasattr(main_window, 'show_dashboard_screen')
        assert hasattr(main_window, 'show_settings_screen')
        
        # 메서드들이 호출 가능한지 확인
        assert callable(main_window.show_welcome_screen)
        assert callable(main_window.show_transactions_screen)
        assert callable(main_window.show_dashboard_screen)
        assert callable(main_window.show_settings_screen)
    
    def test_welcome_screen_transition(self, main_window):
        """환영 화면 전환 테스트"""
        main_window.show_welcome_screen()
        central_widget = main_window.centralWidget()
        assert central_widget.currentIndex() == main_window.SCREEN_WELCOME
    
    def test_welcome_widget_creation(self, main_window):
        """환영 위젯 생성 테스트"""
        assert hasattr(main_window, 'welcome_widget')
        assert main_window.welcome_widget is not None
        
        # 중앙 위젯에 추가되었는지 확인
        central_widget = main_window.centralWidget()
        assert central_widget.count() >= 1
        assert central_widget.widget(0) == main_window.welcome_widget


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 