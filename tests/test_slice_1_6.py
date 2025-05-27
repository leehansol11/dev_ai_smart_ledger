#!/usr/bin/env python3
"""
AI 스마트 가계부 - 슬라이스 1.6 테스트
Author: leehansol
Created: 2025-05-25

테스트 목표:
1. 파일 형식 안내 팝업창 생성 및 표시 기능
2. 메뉴에서 파일 형식 안내 액션 클릭 시 팝업 표시
3. 팝업창 내용 및 디자인 검증
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

from ai_smart_ledger.app.ui.main_window import MainWindow


class TestSlice16:
    """슬라이스 1.6: 파일 형식 안내 팝업 기능 테스트"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """QApplication 인스턴스 생성 (클래스별 한 번만)"""
        if not QApplication.instance():
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def main_window(self, app):
        """MainWindow 인스턴스 생성"""
        window = MainWindow()
        return window
    
    def test_file_format_guide_action_exists_in_menu(self, main_window):
        """메뉴에 파일 형식 안내 액션이 존재하는지 테스트"""
        # 메뉴 바에서 도움말 메뉴 찾기
        menubar = main_window.menuBar()
        help_menu = None
        
        for action in menubar.actions():
            if "도움말" in action.text():
                help_menu = action.menu()
                break
        
        assert help_menu is not None, "도움말 메뉴가 존재하지 않습니다"
        
        # 도움말 메뉴에서 파일 형식 안내 액션 찾기
        file_format_action = None
        for action in help_menu.actions():
            if "파일 형식 안내" in action.text():
                file_format_action = action
                break
        
        assert file_format_action is not None, "파일 형식 안내 액션이 메뉴에 존재하지 않습니다"
        assert "지원되는 파일 형식" in file_format_action.statusTip()
    
    def test_show_file_format_guide_method_exists(self, main_window):
        """MainWindow에 show_file_format_guide 메서드가 존재하는지 테스트"""
        assert hasattr(main_window, 'show_file_format_guide'), "show_file_format_guide 메서드가 존재하지 않습니다"
        assert callable(getattr(main_window, 'show_file_format_guide')), "show_file_format_guide가 호출 가능하지 않습니다"
    
    def test_file_format_guide_action_connected(self, main_window):
        """파일 형식 안내 액션이 적절한 메서드에 연결되었는지 테스트"""
        # 메뉴에서 파일 형식 안내 액션 찾기
        menubar = main_window.menuBar()
        help_menu = None
        
        for action in menubar.actions():
            if "도움말" in action.text():
                help_menu = action.menu()
                break
        
        file_format_action = None
        for action in help_menu.actions():
            if "파일 형식 안내" in action.text():
                file_format_action = action
                break
        
        # 액션이 연결되었는지 확인
        assert file_format_action is not None
        
        # 대안적으로 액션 트리거가 실제로 작동하는지 테스트
        # show_file_format_guide 메서드를 mock하여 호출되는지 확인
        with patch.object(main_window, 'show_file_format_guide') as mock_show:
            file_format_action.trigger()
            mock_show.assert_called_once()  # 액션이 연결되어 있다면 메서드가 호출됨
    
    @patch('PySide6.QtWidgets.QDialog.exec')
    def test_show_file_format_guide_creates_dialog(self, mock_exec, main_window):
        """show_file_format_guide 메서드가 대화상자를 생성하고 표시하는지 테스트"""
        # 대화상자 생성 모킹
        mock_exec.return_value = QDialog.Accepted
        
        # 메서드 호출
        main_window.show_file_format_guide()
        
        # 대화상자의 exec()가 호출되었는지 확인
        mock_exec.assert_called_once()
    
    def test_file_format_guide_dialog_content(self, main_window):
        """파일 형식 안내 대화상자의 내용이 적절한지 테스트"""
        # QDialog.exec을 패치하여 실제 대화상자가 표시되지 않도록 함
        with patch('PySide6.QtWidgets.QDialog.exec') as mock_exec:
            mock_exec.return_value = QDialog.Accepted
            
            # 대화상자 생성 및 내용 확인을 위해 create_file_format_dialog 메서드 직접 호출
            if hasattr(main_window, 'create_file_format_dialog'):
                dialog = main_window.create_file_format_dialog()
                
                # 대화상자 제목 확인
                assert dialog.windowTitle() == "파일 형식 안내"
                
                # 대화상자가 QDialog 인스턴스인지 확인
                assert isinstance(dialog, QDialog)
                
                # 대화상자에 필수 내용이 포함되어 있는지 확인 (텍스트 위젯 내용 검사)
                dialog_text = self._extract_dialog_text(dialog)
                
                # CSV 파일 형식 안내 포함 여부
                assert "CSV" in dialog_text or "csv" in dialog_text
                
                # Excel 파일 형식 안내 포함 여부  
                assert "Excel" in dialog_text or "XLSX" in dialog_text or "XLS" in dialog_text
                
                # 파일 크기 제한 안내 포함 여부
                assert "50MB" in dialog_text or "크기" in dialog_text
    
    def _extract_dialog_text(self, dialog):
        """대화상자에서 모든 텍스트 내용을 추출하는 헬퍼 메서드"""
        dialog_text = ""
        
        # QTextEdit 위젯에서 텍스트 추출
        from PySide6.QtWidgets import QTextEdit, QLabel
        
        text_widgets = dialog.findChildren(QTextEdit)
        for text_widget in text_widgets:
            if hasattr(text_widget, 'toPlainText'):
                dialog_text += text_widget.toPlainText() + " "
        
        # QLabel 위젯에서 텍스트 추출
        label_widgets = dialog.findChildren(QLabel)
        for label_widget in label_widgets:
            if hasattr(label_widget, 'text'):
                dialog_text += label_widget.text() + " "
        
        return dialog_text
    
    def test_file_format_guide_action_trigger(self, main_window):
        """메뉴의 파일 형식 안내 액션을 트리거했을 때 대화상자가 표시되는지 테스트"""
        # 실제 대화상자 표시를 막기 위해 show_file_format_guide 메서드를 모킹
        with patch.object(main_window, 'show_file_format_guide') as mock_show:
            # 메뉴에서 파일 형식 안내 액션 찾기
            menubar = main_window.menuBar()
            help_menu = None
            
            for action in menubar.actions():
                if "도움말" in action.text():
                    help_menu = action.menu()
                    break
            
            file_format_action = None
            for action in help_menu.actions():
                if "파일 형식 안내" in action.text():
                    file_format_action = action
                    break
            
            # 액션 트리거
            file_format_action.trigger()
            
            # show_file_format_guide 메서드가 호출되었는지 확인
            mock_show.assert_called_once()
    
    def test_dialog_has_proper_styling(self, main_window):
        """대화상자가 적절한 스타일링을 가지고 있는지 테스트"""
        with patch('PySide6.QtWidgets.QDialog.exec') as mock_exec:
            mock_exec.return_value = QDialog.Accepted
            
            if hasattr(main_window, 'create_file_format_dialog'):
                dialog = main_window.create_file_format_dialog()
                
                # 대화상자 크기가 적절한지 확인
                assert dialog.width() > 400, "대화상자 너비가 너무 작습니다"
                assert dialog.height() > 300, "대화상자 높이가 너무 작습니다"
                
                # 대화상자가 모달인지 확인
                assert dialog.isModal(), "대화상자가 모달이어야 합니다"
    
    def test_dialog_closes_properly(self, main_window):
        """대화상자가 적절히 닫히는지 테스트"""
        with patch('PySide6.QtWidgets.QDialog.exec') as mock_exec:
            # 사용자가 대화상자를 닫았을 때
            mock_exec.return_value = QDialog.Rejected
            
            # 메서드 호출이 오류 없이 완료되는지 확인
            try:
                main_window.show_file_format_guide()
            except Exception as e:
                pytest.fail(f"대화상자 닫기 중 오류 발생: {e}") 