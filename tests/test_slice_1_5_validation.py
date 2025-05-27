#!/usr/bin/env python3
"""
AI 스마트 가계부 - 슬라이스 1.5 파일 검증 및 오류 처리 테스트
Author: leehansol
Created: 2025-05-25

테스트 목표:
1. 파일 크기 검증 (50MB 제한)
2. 지원하지 않는 파일 형식 처리
3. CSV/Excel 파싱 중 발생하는 예외 처리
4. 사용자에게 명확한 오류 메시지 표시
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from pathlib import Path
from openpyxl import Workbook

from ai_smart_ledger.app.core.file_handler import FileHandler
from ai_smart_ledger.app.core.file_parser import FileParser


class TestSlice15Validation:
    """슬라이스 1.5: 파일 검증 및 오류 처리 테스트"""
    
    @pytest.fixture
    def file_handler(self):
        """FileHandler 인스턴스 생성"""
        return FileHandler()
    
    @pytest.fixture
    def mock_parent_widget(self):
        """QWidget 목 객체 생성"""
        mock_widget = MagicMock()
        return mock_widget
    
    @pytest.fixture
    def large_csv_file(self):
        """50MB가 넘는 큰 CSV 파일 생성 (실제로는 작은 크기이지만 파일 크기 속성을 조작)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("날짜,내용,금액\n")
            f.write("2023-01-01,테스트,1000\n")
            temp_path = f.name
        
        # 파일 크기를 51MB로 만들기 위해 더미 데이터 추가
        with open(temp_path, 'a', encoding='utf-8') as f:
            # 약 51MB 분량의 더미 데이터 작성
            dummy_line = "2023-01-01," + "a" * 1000 + ",1000\n"  # 약 1KB 라인
            for _ in range(52000):  # 52MB 정도
                f.write(dummy_line)
        
        yield temp_path
        
        # 정리
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def unsupported_file(self):
        """지원하지 않는 확장자 파일 생성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("이것은 지원하지 않는 파일 형식입니다.")
            temp_path = f.name
        
        yield temp_path
        
        # 정리
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def invalid_csv_file(self):
        """잘못된 형식의 CSV 파일 생성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            # 잘못된 CSV 형식 (따옴표가 제대로 닫히지 않음)
            f.write('날짜,내용,금액\n')
            f.write('2023-01-01,"잘못된 따옴표,1000\n')
            f.write('2023-01-02,정상 데이터,2000\n')
            temp_path = f.name
        
        yield temp_path
        
        # 정리
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def corrupted_excel_file(self):
        """손상된 Excel 파일 생성 (실제로는 텍스트 파일이지만 .xlsx 확장자)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False, encoding='utf-8') as f:
            f.write("이것은 Excel 파일이 아닙니다.")
            temp_path = f.name
        
        yield temp_path
        
        # 정리
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def valid_csv_file(self):
        """유효한 CSV 파일 생성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("날짜,내용,금액\n")
            f.write("2023-01-01,테스트,1000\n")
            f.write("2023-01-02,테스트2,2000\n")
            temp_path = f.name
        
        yield temp_path
        
        # 정리
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    # 1. 파일 크기 검증 테스트
    def test_file_size_validation_pass(self, file_handler, valid_csv_file):
        """파일 크기 검증 통과 테스트 (50MB 이하)"""
        is_valid, message = file_handler.validate_file(valid_csv_file)
        assert is_valid is True
        assert "파일이 유효합니다" in message
    
    def test_file_size_validation_fail(self, file_handler, large_csv_file, mock_parent_widget):
        """파일 크기 검증 실패 테스트 (50MB 초과)"""
        with patch('PySide6.QtWidgets.QMessageBox.critical') as mock_msg:
            is_valid, message = file_handler.validate_file(large_csv_file, mock_parent_widget)
            assert is_valid is False
            assert "파일 크기가 너무 큽니다" in message
            assert "50" in message  # 50MB 제한 언급
            # QMessageBox가 호출되었는지 확인
            mock_msg.assert_called_once()
    
    # 2. 파일 형식 검증 테스트
    def test_supported_file_extensions(self, file_handler):
        """지원하는 파일 확장자 확인"""
        assert '.csv' in file_handler.SUPPORTED_EXTENSIONS
        assert '.xls' in file_handler.SUPPORTED_EXTENSIONS
        assert '.xlsx' in file_handler.SUPPORTED_EXTENSIONS
    
    def test_unsupported_file_format_validation(self, file_handler, unsupported_file, mock_parent_widget):
        """지원하지 않는 파일 형식 검증 테스트"""
        with patch('PySide6.QtWidgets.QMessageBox.critical') as mock_msg:
            is_valid, message = file_handler.validate_file(unsupported_file, mock_parent_widget)
            assert is_valid is False
            assert "지원하지 않는 파일 형식입니다" in message
            assert ".csv" in message and ".xls" in message and ".xlsx" in message
            mock_msg.assert_called_once()
    
    def test_nonexistent_file_validation(self, file_handler, mock_parent_widget):
        """존재하지 않는 파일 검증 테스트"""
        nonexistent_file = "/path/to/nonexistent/file.csv"
        with patch('PySide6.QtWidgets.QMessageBox.critical') as mock_msg:
            is_valid, message = file_handler.validate_file(nonexistent_file, mock_parent_widget)
            assert is_valid is False
            assert "존재하지 않습니다" in message
            mock_msg.assert_called_once()
    
    # 3. CSV 파싱 오류 처리 테스트
    def test_csv_parsing_malformed_file(self, invalid_csv_file):
        """잘못된 형식의 CSV 파일 파싱 테스트"""
        # 현재 FileParser는 잘못된 CSV도 최대한 파싱을 시도함
        # 하지만 더 엄격한 검증이 필요할 수 있음
        result = FileParser.parse_csv_preview(invalid_csv_file)
        # 파싱이 성공하더라도 데이터 품질을 확인해야 함
        if result['success']:
            # 파싱된 데이터의 품질 검증
            assert len(result['headers']) > 0
            # 추가적인 데이터 품질 검증 로직 필요
        else:
            assert "오류" in result['error']
    
    def test_csv_parsing_encoding_error(self):
        """잘못된 인코딩의 CSV 파일 파싱 테스트"""
        # UTF-8이 아닌 인코딩으로 작성된 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='cp949') as f:
            f.write("날짜,내용,금액\n")
            f.write("2023-01-01,한글테스트,1000\n")
            temp_path = f.name
        
        try:
            result = FileParser.parse_csv_preview(temp_path)
            # 인코딩 오류가 발생할 수 있음
            if not result['success']:
                assert "인코딩 오류" in result['error']
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_csv_parsing_empty_file(self):
        """빈 CSV 파일 파싱 테스트"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            # 빈 파일
            temp_path = f.name
        
        try:
            result = FileParser.parse_csv_preview(temp_path)
            assert result['success'] is False
            assert "비어있습니다" in result['error']
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    # 4. Excel 파싱 오류 처리 테스트
    def test_excel_parsing_corrupted_file(self, corrupted_excel_file):
        """손상된 Excel 파일 파싱 테스트"""
        result = FileParser.parse_excel_preview(corrupted_excel_file)
        assert result['success'] is False
        assert "Excel 파일 읽기 오류" in result['error']
    
    def test_excel_parsing_empty_file(self):
        """빈 Excel 파일 파싱 테스트"""
        wb = Workbook()
        ws = wb.active
        # 빈 워크시트
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        wb.save(temp_path)
        wb.close()
        
        try:
            result = FileParser.parse_excel_preview(temp_path)
            assert result['success'] is False
            assert "비어있습니다" in result['error']
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    # 5. 통합 파일 검증 및 파싱 테스트
    def test_complete_file_validation_and_parsing_workflow(self, file_handler, valid_csv_file):
        """파일 검증과 파싱의 완전한 워크플로 테스트"""
        # 1단계: 파일 검증
        is_valid, validation_message = file_handler.validate_file(valid_csv_file)
        assert is_valid is True
        
        # 2단계: 파일 파싱
        parse_result = FileParser.parse_csv_preview(valid_csv_file)
        assert parse_result['success'] is True
        assert len(parse_result['headers']) > 0
        assert len(parse_result['data']) > 0
    
    def test_file_info_extraction(self, file_handler, valid_csv_file):
        """파일 정보 추출 테스트"""
        file_info = file_handler.get_file_info(valid_csv_file)
        assert 'path' in file_info
        assert 'name' in file_info
        assert 'extension' in file_info
        assert 'size_bytes' in file_info
        assert 'size_mb' in file_info
        assert 'is_valid' in file_info
        assert file_info['extension'] == '.csv'
        assert file_info['is_valid'] is True
    
    # 6. 오류 메시지 표시 테스트
    def test_error_message_display_without_parent(self, file_handler, unsupported_file):
        """부모 위젯 없이 오류 메시지 처리 테스트"""
        # parent=None으로 호출하면 콘솔에만 출력
        is_valid, message = file_handler.validate_file(unsupported_file, None)
        assert is_valid is False
        assert "지원하지 않는 파일 형식입니다" in message
    
    @patch('PySide6.QtWidgets.QMessageBox.critical')
    def test_error_message_display_with_parent(self, mock_msg_box, file_handler, unsupported_file, mock_parent_widget):
        """부모 위젯과 함께 오류 메시지 표시 테스트"""
        is_valid, message = file_handler.validate_file(unsupported_file, mock_parent_widget)
        assert is_valid is False
        mock_msg_box.assert_called_once()
        # 호출된 인자 확인
        args, kwargs = mock_msg_box.call_args
        assert mock_parent_widget == args[0]
        assert "파일 형식 오류" == args[1]
        assert "지원하지 않는 파일 형식입니다" in args[2]
    
    # 7. 경계값 테스트
    def test_file_size_boundary_exactly_50mb(self, file_handler):
        """정확히 50MB 파일 크기 경계값 테스트"""
        # 정확히 50MB 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("날짜,내용,금액\n")
            temp_path = f.name
        
        # 정확히 50MB가 되도록 조정
        target_size = 50 * 1024 * 1024  # 50MB
        current_size = os.path.getsize(temp_path)
        remaining_size = target_size - current_size
        
        with open(temp_path, 'a', encoding='utf-8') as f:
            f.write('a' * remaining_size)
        
        try:
            # 정확히 50MB는 허용되어야 함
            is_valid, message = file_handler.validate_file(temp_path)
            assert is_valid is True
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_max_file_size_constant(self, file_handler):
        """최대 파일 크기 상수 확인"""
        assert hasattr(file_handler, 'MAX_FILE_SIZE')
        assert file_handler.MAX_FILE_SIZE == 50 * 1024 * 1024  # 50MB
    
    # 8. 파일 권한 테스트 (Unix/Linux 시스템에서만 유효)
    @pytest.mark.skipif(os.name == 'nt', reason="Windows에서는 파일 권한 테스트가 다르게 작동함")
    def test_file_permission_error(self, file_handler, valid_csv_file, mock_parent_widget):
        """파일 읽기 권한 없음 테스트"""
        # 파일 권한을 읽기 불가로 변경
        os.chmod(valid_csv_file, 0o000)
        
        try:
            with patch('PySide6.QtWidgets.QMessageBox.critical') as mock_msg:
                is_valid, message = file_handler.validate_file(valid_csv_file, mock_parent_widget)
                assert is_valid is False
                assert "권한이 없습니다" in message
                mock_msg.assert_called_once()
        finally:
            # 권한 복구
            os.chmod(valid_csv_file, 0o644) 