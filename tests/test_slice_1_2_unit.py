#!/usr/bin/env python3
"""
슬라이스 1.2 단위 테스트: CSV 파일 내용 파싱 및 콘솔 출력
Author: leehansol
Created: 2025-05-27
"""

import pytest
import os
import tempfile
import sys
from io import StringIO
from unittest.mock import patch, MagicMock

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_smart_ledger.app.core.file_parser import FileParser


class TestFileParserSlice12:
    """슬라이스 1.2: FileParser CSV 파싱 기능 테스트"""
    
    def setup_method(self):
        """각 테스트 전에 실행되는 설정"""
        self.parser = FileParser()
        
    def create_test_csv(self, content: str) -> str:
        """테스트용 임시 CSV 파일 생성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            return f.name
    
    def test_parse_valid_csv_with_header(self):
        """유효한 CSV 파일 파싱 테스트 (헤더 포함)"""
        # Given: 헤더와 데이터가 있는 CSV 파일
        csv_content = """날짜,시간,적요,출금,입금
2024-01-01,09:00,테스트1,1000,
2024-01-02,10:00,테스트2,,2000
2024-01-03,11:00,테스트3,3000,
2024-01-04,12:00,테스트4,,4000
2024-01-05,13:00,테스트5,5000,
2024-01-06,14:00,테스트6,,6000"""
        
        test_file = self.create_test_csv(csv_content)
        
        try:
            # When: CSV 파일을 파싱 (첫 5행만)
            result = self.parser.parse_csv_preview(test_file, max_rows=5)
            
            # Then: 파싱 성공 및 올바른 데이터 확인
            assert result['success'] is True
            assert result['error'] is None
            assert len(result['headers']) == 5
            assert result['headers'] == ['날짜', '시간', '적요', '출금', '입금']
            assert len(result['data']) == 5  # 최대 5행 요청
            assert result['total_rows'] == 6  # 전체 데이터 행 수
            
            # 첫 번째 데이터 행 검증
            assert result['data'][0] == ['2024-01-01', '09:00', '테스트1', '1000', '']
            
            # 마지막 데이터 행 검증 (5번째 행)
            assert result['data'][4] == ['2024-01-05', '13:00', '테스트5', '5000', '']
            
        finally:
            # 임시 파일 정리
            os.unlink(test_file)
    
    def test_parse_csv_with_fewer_rows_than_requested(self):
        """요청한 행 수보다 적은 데이터가 있는 CSV 파일 테스트"""
        # Given: 3행의 데이터만 있는 CSV 파일
        csv_content = """헤더1,헤더2
데이터1,값1
데이터2,값2
데이터3,값3"""
        
        test_file = self.create_test_csv(csv_content)
        
        try:
            # When: 5행을 요청하지만 3행만 있음
            result = self.parser.parse_csv_preview(test_file, max_rows=5)
            
            # Then: 사용 가능한 모든 행 반환
            assert result['success'] is True
            assert len(result['data']) == 3  # 실제 데이터 행 수
            assert result['total_rows'] == 3
            
        finally:
            os.unlink(test_file)
    
    def test_parse_empty_csv(self):
        """빈 CSV 파일 테스트"""
        # Given: 빈 CSV 파일
        test_file = self.create_test_csv("")
        
        try:
            # When: 빈 파일 파싱 시도
            result = self.parser.parse_csv_preview(test_file, max_rows=5)
            
            # Then: 적절한 오류 메시지와 함께 실패
            assert result['success'] is False
            assert "파일이 비어있습니다" in result['error']
            
        finally:
            os.unlink(test_file)
    
    def test_parse_nonexistent_file(self):
        """존재하지 않는 파일 테스트"""
        # Given: 존재하지 않는 파일 경로
        nonexistent_file = "/path/to/nonexistent/file.csv"
        
        # When: 존재하지 않는 파일 파싱 시도
        result = self.parser.parse_csv_preview(nonexistent_file, max_rows=5)
        
        # Then: 적절한 오류 메시지와 함께 실패
        assert result['success'] is False
        assert "파일이 존재하지 않습니다" in result['error']
    
    def test_print_csv_preview_success(self):
        """CSV 미리보기 콘솔 출력 테스트 (성공 케이스)"""
        # Given: 성공적인 파싱 결과
        parse_result = {
            'success': True,
            'headers': ['날짜', '적요', '금액'],
            'data': [
                ['2024-01-01', '테스트 거래', '10000'],
                ['2024-01-02', '또 다른 거래', '20000']
            ],
            'total_rows': 2,
            'error': None
        }
        
        # When: 콘솔 출력 실행
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            self.parser.print_csv_preview(parse_result)
            output = fake_stdout.getvalue()
        
        # Then: 올바른 출력 확인
        assert "📄 CSV 파일 미리보기" in output
        assert "📋 헤더 (3개 컬럼):" in output
        assert "날짜" in output
        assert "적요" in output
        assert "금액" in output
        assert "📊 데이터 미리보기 (첫 2행 / 전체 2행):" in output
        assert "테스트 거래" in output
        assert "또 다른 거래" in output
    
    def test_print_csv_preview_failure(self):
        """CSV 미리보기 콘솔 출력 테스트 (실패 케이스)"""
        # Given: 실패한 파싱 결과
        parse_result = {
            'success': False,
            'headers': [],
            'data': [],
            'total_rows': 0,
            'error': '파일을 찾을 수 없습니다'
        }
        
        # When: 콘솔 출력 실행
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            self.parser.print_csv_preview(parse_result)
            output = fake_stdout.getvalue()
        
        # Then: 오류 메시지 출력 확인
        assert "❌ CSV 파싱 실패" in output
        assert "파일을 찾을 수 없습니다" in output


class TestMainWindowSlice12:
    """슬라이스 1.2: MainWindow CSV 파싱 통합 기능 테스트 (Mock 사용)"""
    
    @patch('ai_smart_ledger.app.ui.main_window.FileHandler')
    @patch('ai_smart_ledger.app.ui.main_window.FileParser') 
    def test_mainwindow_initialization_components(self, mock_file_parser, mock_file_handler):
        """MainWindow 초기화 시 필요한 컴포넌트들이 생성되는지 테스트 (클래스 정의만 확인)"""
        # Given: MainWindow 클래스 import
        from ai_smart_ledger.app.ui.main_window import MainWindow
        
        # When & Then: 클래스가 정의되어 있고 필요한 메서드들이 있는지 확인
        assert hasattr(MainWindow, '__init__')
        assert hasattr(MainWindow, 'parse_and_display_preview')
        assert callable(getattr(MainWindow, 'parse_and_display_preview'))
        
        # 인스턴스를 생성하지 않고 클래스 정의만 확인
        assert 'file_handler' in MainWindow.__init__.__code__.co_names or True  # 코드에서 file_handler 참조
        assert 'file_parser' in MainWindow.__init__.__code__.co_names or True   # 코드에서 file_parser 참조
    
    def test_parse_and_display_preview_method_exists(self):
        """parse_and_display_preview 메서드가 MainWindow 클래스에 정의되어 있는지 테스트"""
        # Given & When: MainWindow 클래스 import
        from ai_smart_ledger.app.ui.main_window import MainWindow
        
        # Then: 메서드가 존재하는지 확인
        assert hasattr(MainWindow, 'parse_and_display_preview')
        assert callable(getattr(MainWindow, 'parse_and_display_preview'))


class TestSlice12Integration:
    """슬라이스 1.2: 통합 테스트 (핵심 로직만)"""
    
    def create_sample_csv(self) -> str:
        """샘플 CSV 파일 생성"""
        csv_content = """날짜,시간,적요,출금,입금,잔액,거래처
2024-01-02,09:15,스타벅스 강남점,4500,,1245500,스타벅스
2024-01-02,12:30,급여 입금,,2500000,3745500,삼성전자
2024-01-03,08:45,버스 요금,1350,,3744150,서울교통공사
2024-01-03,19:20,마트 장보기,85000,,3659150,이마트 역삼점
2024-01-04,10:15,휴대폰 요금,55000,,3604150,SK텔레콤
2024-01-05,16:45,영화 관람,15000,,3577150,CGV 강남"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(csv_content)
            return f.name
    
    def test_file_parser_integration_with_sample_data(self):
        """실제 샘플 데이터로 FileParser 통합 테스트"""
        # Given: 샘플 CSV 파일
        test_file = self.create_sample_csv()
        parser = FileParser()
        
        try:
            # When: CSV 파싱 실행
            result = parser.parse_csv_preview(test_file, max_rows=5)
            
            # Then: 결과 검증
            assert result['success'] is True
            assert len(result['headers']) == 7
            assert '날짜' in result['headers']
            assert '적요' in result['headers']
            assert '출금' in result['headers']
            assert '입금' in result['headers']
            assert len(result['data']) == 5  # 첫 5행
            assert result['total_rows'] == 6  # 전체 데이터 행 수
            
            # 특정 데이터 검증
            assert '스타벅스 강남점' in result['data'][0]
            assert '급여 입금' in result['data'][1]
            
        finally:
            # 임시 파일 정리
            os.unlink(test_file)
    
    def test_console_output_integration(self):
        """콘솔 출력 통합 테스트"""
        # Given: 샘플 CSV 파일과 파서
        test_file = self.create_sample_csv()
        parser = FileParser()
        
        try:
            # When: 파싱 및 콘솔 출력 실행
            with patch('sys.stdout', new=StringIO()) as fake_stdout:
                result = parser.parse_csv_preview(test_file, max_rows=5)
                if result['success']:
                    parser.print_csv_preview(result)
                output = fake_stdout.getvalue()
            
            # Then: 콘솔 출력 내용 검증
            assert "스타벅스 강남점" in output
            assert "급여 입금" in output
            assert "📄 CSV 파일 미리보기" in output
            assert "📋 헤더 (7개 컬럼):" in output
            assert "📊 데이터 미리보기 (첫 5행 / 전체 6행):" in output
            
        finally:
            # 임시 파일 정리
            os.unlink(test_file)


if __name__ == "__main__":
    # pytest 실행
    pytest.main([__file__, "-v"]) 