#!/usr/bin/env python3
"""
AI 스마트 가계부 - 슬라이스 1.5 통합 테스트
Author: leehansol
Created: 2025-05-25

테스트 목표:
1. UI와 파일 핸들러 통합 테스트
2. 실제 사용자 시나리오 테스트
3. 오류 상황에서의 전체 시스템 동작 확인
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, Mock
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

from ai_smart_ledger.app.ui.main_window import MainWindow
from ai_smart_ledger.app.core.file_handler import FileHandler
from ai_smart_ledger.app.core.file_parser import FileParser


class TestSlice15Integration:
    """슬라이스 1.5: 통합 테스트"""
    
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
    
    @pytest.fixture
    def valid_small_csv(self):
        """유효한 작은 CSV 파일 생성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("날짜,내용,금액,카테고리\n")
            f.write("2023-01-01,스타벅스 커피,4500,식비\n")
            f.write("2023-01-02,버스 요금,1350,교통비\n")
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def large_csv_file(self):
        """50MB가 넘는 큰 CSV 파일 생성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("날짜,내용,금액\n")
            temp_path = f.name
        
        # 약 51MB 분량의 데이터 추가
        with open(temp_path, 'a', encoding='utf-8') as f:
            # 1KB 정도의 라인을 52000개 추가 (약 52MB)
            dummy_line = "2023-01-01," + "a" * 1000 + ",1000\n"
            for _ in range(52000):
                f.write(dummy_line)
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def unsupported_file(self):
        """지원하지 않는 확장자 파일"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("이것은 지원하지 않는 파일입니다.")
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_successful_file_loading_workflow(self, main_window, valid_small_csv):
        """성공적인 파일 로딩 워크플로 테스트"""
        # QFileDialog.getOpenFileName을 mock하여 테스트 파일 반환
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = (valid_small_csv, "")
            
            # 파일 로드 버튼 클릭 시뮬레이션
            initial_text = main_window.file_path_label.text()
            main_window.on_load_file_clicked()
            
            # 파일 경로가 UI에 표시되었는지 확인
            assert main_window.file_path_label.text() != initial_text
            assert "선택된 파일" in main_window.file_path_label.text()
            
            # 선택된 파일 경로가 저장되었는지 확인
            assert main_window.selected_file_path == valid_small_csv
    
    def test_file_size_validation_in_ui(self, main_window, large_csv_file):
        """UI에서 파일 크기 검증 테스트"""
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = (large_csv_file, "")
            
            # QMessageBox.critical이 호출되는지 확인
            with patch('PySide6.QtWidgets.QMessageBox.critical') as mock_msg:
                main_window.on_load_file_clicked()
                
                # 오류 메시지가 표시되었는지 확인
                mock_msg.assert_called_once()
                args = mock_msg.call_args[0]
                assert "파일 크기" in args[2]
                
                # 파일 경로가 업데이트되지 않았는지 확인
                assert main_window.selected_file_path != large_csv_file
    
    def test_unsupported_file_format_in_ui(self, main_window, unsupported_file):
        """UI에서 지원하지 않는 파일 형식 테스트"""
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = (unsupported_file, "")
            
            with patch('PySide6.QtWidgets.QMessageBox.critical') as mock_msg:
                main_window.on_load_file_clicked()
                
                # 오류 메시지가 표시되었는지 확인
                mock_msg.assert_called_once()
                args = mock_msg.call_args[0]
                assert "지원하지 않는 파일 형식" in args[2]
    
    def test_file_selection_cancellation(self, main_window):
        """파일 선택 취소 시 처리 테스트"""
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            # 사용자가 취소를 눌렀을 때 (빈 문자열 반환)
            mock_dialog.return_value = ("", "")
            
            initial_text = main_window.file_path_label.text()
            main_window.on_load_file_clicked()
            
            # 파일 경로 레이블이 변경되지 않았는지 확인
            assert main_window.file_path_label.text() == initial_text
            assert main_window.selected_file_path is None
    
    def test_file_parsing_integration(self, main_window, valid_small_csv):
        """파일 파싱 통합 테스트"""
        # 실제 파일 파싱이 올바르게 수행되는지 확인
        main_window.parse_and_display_preview(valid_small_csv)
        
        # 선택된 파일 경로가 저장되었는지 확인
        assert main_window.selected_file_path == valid_small_csv
        
        # 테이블에 데이터가 표시되었는지 확인
        if main_window.transactions_table is not None:
            assert main_window.transactions_table.rowCount() > 0
            assert main_window.transactions_table.columnCount() > 0
    
    def test_error_handling_during_parsing(self, main_window):
        """파싱 중 오류 발생 시 처리 테스트"""
        # 존재하지 않는 파일로 테스트
        nonexistent_file = "/path/to/nonexistent/file.csv"
        
        # 파싱이 실패해도 프로그램이 크래시되지 않는지 확인
        try:
            main_window.parse_and_display_preview(nonexistent_file)
            # 오류가 발생해도 selected_file_path가 업데이트되지 않아야 함
            assert main_window.selected_file_path != nonexistent_file
        except Exception:
            pytest.fail("파싱 오류가 적절히 처리되지 않음")
    
    def test_ui_state_consistency(self, main_window, valid_small_csv):
        """UI 상태 일관성 테스트"""
        # 초기 상태 확인
        assert main_window.selected_file_path is None
        assert "파일을 선택해주세요" in main_window.file_path_label.text()
        
        # 파일 로드 후 상태 확인
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = (valid_small_csv, "")
            main_window.on_load_file_clicked()
            
            # 상태가 올바르게 업데이트되었는지 확인
            assert main_window.selected_file_path == valid_small_csv
            assert "선택된 파일" in main_window.file_path_label.text()
    
    def test_file_handler_integration(self, main_window):
        """FileHandler 통합 테스트"""
        # FileHandler가 MainWindow에 올바르게 초기화되었는지 확인
        assert hasattr(main_window, 'file_handler')
        assert isinstance(main_window.file_handler, FileHandler)
        
        # FileHandler의 상수들이 올바르게 설정되었는지 확인
        assert main_window.file_handler.MAX_FILE_SIZE == 50 * 1024 * 1024
        assert '.csv' in main_window.file_handler.SUPPORTED_EXTENSIONS
        assert '.xlsx' in main_window.file_handler.SUPPORTED_EXTENSIONS
    
    def test_file_parser_integration(self, main_window):
        """FileParser 통합 테스트"""
        # FileParser가 MainWindow에 올바르게 초기화되었는지 확인
        assert hasattr(main_window, 'file_parser')
        assert isinstance(main_window.file_parser, FileParser)
        
        # FileParser의 메서드들이 사용 가능한지 확인
        assert hasattr(main_window.file_parser, 'parse_csv_preview')
        assert hasattr(main_window.file_parser, 'parse_excel_preview')
        assert hasattr(main_window.file_parser, 'print_csv_preview')
    
    def test_complete_user_workflow(self, main_window, valid_small_csv):
        """완전한 사용자 워크플로 테스트"""
        # 1. 사용자가 파일 로드 버튼을 클릭
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = (valid_small_csv, "")
            
            # 2. 파일 선택 및 검증
            initial_screen = main_window.central_widget.currentIndex()
            main_window.on_load_file_clicked()
            
            # 3. 파일이 성공적으로 로드되고 UI가 업데이트됨
            assert main_window.selected_file_path == valid_small_csv
            assert "선택된 파일" in main_window.file_path_label.text()
            
            # 4. 거래내역 화면으로 자동 전환 확인
            # (실제 화면 전환은 파싱 성공 후 발생)
            # 화면 전환이 발생했는지는 별도로 확인할 수 있음
    
    def test_error_recovery(self, main_window, large_csv_file, valid_small_csv):
        """오류 발생 후 복구 테스트"""
        # 1. 먼저 큰 파일로 오류 발생
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = (large_csv_file, "")
            
            with patch('PySide6.QtWidgets.QMessageBox.critical'):
                main_window.on_load_file_clicked()
                
                # 오류 후 상태 확인
                assert main_window.selected_file_path != large_csv_file
        
        # 2. 이후 유효한 파일로 정상 처리
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = (valid_small_csv, "")
            main_window.on_load_file_clicked()
            
            # 정상 복구 확인
            assert main_window.selected_file_path == valid_small_csv
            assert "선택된 파일" in main_window.file_path_label.text() 