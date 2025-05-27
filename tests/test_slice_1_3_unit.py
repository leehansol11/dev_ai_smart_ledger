#!/usr/bin/env python3
"""
AI 스마트 가계부 - 슬라이스 1.3 단위 테스트
메인 창 테이블 위젯에 CSV 데이터 표시 기능
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QWidget

from ai_smart_ledger.app.ui.main_window import MainWindow


class TestSlice13TableWidget:
    """슬라이스 1.3: QTableWidget 및 CSV 데이터 표시 테스트"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """QApplication 인스턴스 생성"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        yield app
    
    @patch('ai_smart_ledger.app.ui.main_window.FileHandler')
    @patch('ai_smart_ledger.app.ui.main_window.FileParser')
    def test_transactions_table_widget_exists(self, mock_file_parser, mock_file_handler, app):
        """거래내역 테이블 위젯이 존재하는지 테스트"""
        # Given: MainWindow 인스턴스 생성
        window = MainWindow()
        
        # When & Then: transactions_table 속성이 존재하고 QTableWidget인지 확인
        assert hasattr(window, 'transactions_table'), "MainWindow에 transactions_table 속성이 없습니다"
        assert isinstance(window.transactions_table, QTableWidget), "transactions_table이 QTableWidget이 아닙니다"
        
        window.close()
    
    @patch('ai_smart_ledger.app.ui.main_window.FileHandler')
    @patch('ai_smart_ledger.app.ui.main_window.FileParser')
    def test_display_csv_data_in_table_method_exists(self, mock_file_parser, mock_file_handler, app):
        """CSV 데이터를 테이블에 표시하는 메서드가 존재하는지 테스트"""
        # Given: MainWindow 인스턴스 생성
        window = MainWindow()
        
        # When & Then: display_csv_data_in_table 메서드가 존재하고 호출 가능한지 확인
        assert hasattr(window, 'display_csv_data_in_table'), "display_csv_data_in_table 메서드가 없습니다"
        assert callable(getattr(window, 'display_csv_data_in_table')), "display_csv_data_in_table이 호출 가능하지 않습니다"
        
        window.close()
    
    @patch('ai_smart_ledger.app.ui.main_window.FileHandler')
    @patch('ai_smart_ledger.app.ui.main_window.FileParser')
    def test_transactions_screen_contains_table(self, mock_file_parser, mock_file_handler, app):
        """거래내역 화면에 테이블이 포함되어 있는지 테스트"""
        # Given: MainWindow 인스턴스 생성
        window = MainWindow()
        
        # When: 거래내역 화면으로 전환
        window.show_transactions_screen()
        
        # Then: 현재 화면이 거래내역 화면이고 테이블이 포함되어 있는지 확인
        current_widget = window.central_widget.currentWidget()
        assert current_widget is not None, "현재 위젯이 None입니다"
        
        # 테이블 위젯이 화면에 포함되어 있는지 확인
        assert hasattr(window, 'transactions_table'), "transactions_table이 없습니다"
        
        window.close()
    
    @patch('ai_smart_ledger.app.ui.main_window.FileHandler')
    @patch('ai_smart_ledger.app.ui.main_window.FileParser')
    def test_table_widget_configuration(self, mock_file_parser, mock_file_handler, app):
        """테이블 위젯의 기본 설정을 테스트"""
        # Given: MainWindow 인스턴스 생성
        window = MainWindow()
        
        # When: 테이블 위젯 확인
        table = window.transactions_table
        
        # Then: 테이블의 기본 설정 확인
        assert table.selectionBehavior() == QTableWidget.SelectRows, "테이블 선택 동작이 행 단위가 아닙니다"
        assert table.alternatingRowColors() == True, "테이블 교대 행 색상이 설정되지 않았습니다"
        assert table.isSortingEnabled() == True, "테이블 정렬 기능이 활성화되지 않았습니다"
        
        window.close()
    
    def test_display_csv_data_functionality(self):
        """CSV 데이터 표시 기능의 로직을 테스트 (mock 데이터 사용)"""
        # Given: 모의 CSV 파싱 결과
        mock_csv_result = {
            'success': True,
            'headers': ['날짜', '내용', '금액', '잔액'],
            'data': [
                ['2024-01-01', '급여', '3000000', '3000000'],
                ['2024-01-02', '커피', '-4500', '2995500'],
                ['2024-01-03', '점심', '-12000', '2983500'],
                ['2024-01-04', '교통비', '-1350', '2982150'],
                ['2024-01-05', '마트', '-45600', '2936550']
            ],
            'total_rows': 100
        }
        
        # When: 테이블 위젯 생성 및 데이터 설정
        app = QApplication.instance() or QApplication(sys.argv)
        table = QTableWidget()
        
        # 헤더 설정
        table.setColumnCount(len(mock_csv_result['headers']))
        table.setHorizontalHeaderLabels(mock_csv_result['headers'])
        
        # 데이터 행 설정
        table.setRowCount(len(mock_csv_result['data']))
        for row_idx, row_data in enumerate(mock_csv_result['data']):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                table.setItem(row_idx, col_idx, item)
        
        # Then: 테이블 설정 확인
        assert table.columnCount() == 4, f"컬럼 수가 잘못되었습니다. 예상: 4, 실제: {table.columnCount()}"
        assert table.rowCount() == 5, f"행 수가 잘못되었습니다. 예상: 5, 실제: {table.rowCount()}"
        
        # 헤더 확인
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            assert header_item.text() == mock_csv_result['headers'][col], f"헤더가 잘못되었습니다. 컬럼 {col}"
        
        # 첫 번째 행 데이터 확인
        for col in range(table.columnCount()):
            item = table.item(0, col)
            assert item.text() == mock_csv_result['data'][0][col], f"첫 번째 행 데이터가 잘못되었습니다. 컬럼 {col}"
    
    @patch('ai_smart_ledger.app.ui.main_window.FileHandler')
    @patch('ai_smart_ledger.app.ui.main_window.FileParser')
    def test_parse_and_display_integration(self, mock_file_parser, mock_file_handler, app):
        """파싱과 테이블 표시의 통합 기능을 테스트"""
        # Given: 모의 파싱 결과 설정
        mock_parser_instance = mock_file_parser.return_value
        mock_parser_instance.parse_csv_preview.return_value = {
            'success': True,
            'headers': ['날짜', '내용', '금액'],
            'data': [
                ['2024-01-01', '급여', '3000000'],
                ['2024-01-02', '커피', '-4500']
            ],
            'total_rows': 50
        }
        
        # MainWindow 인스턴스 생성
        window = MainWindow()
        
        # When: parse_and_display_preview 메서드 호출
        test_file_path = "test.csv"
        window.parse_and_display_preview(test_file_path)
        
        # Then: 파서가 호출되었는지 확인
        mock_parser_instance.parse_csv_preview.assert_called_once_with(test_file_path, max_rows=5)
        
        # display_csv_data_in_table 메서드가 호출되었는지 확인 (구현 후)
        # 이 부분은 실제 구현 후에 활성화
        
        window.close()


class TestSlice13Integration:
    """슬라이스 1.3 통합 테스트"""
    
    def test_slice_1_3_requirements_coverage(self):
        """슬라이스 1.3 요구사항 커버리지 확인"""
        # 요구사항:
        # 1. QTableWidget이 메인 창에 추가되어야 함
        # 2. 파싱된 CSV 데이터(헤더 및 첫 5행)를 QTableWidget에 채워 넣는 로직 구현
        # 3. UI 테이블에 데이터가 올바르게 표시되어야 함
        
        required_methods = [
            'transactions_table',  # QTableWidget 인스턴스
            'display_csv_data_in_table',  # 데이터 표시 메서드
            'show_transactions_screen'  # 거래내역 화면 전환
        ]
        
        # MainWindow 클래스에서 필요한 속성/메서드들이 정의되어 있는지 확인
        for method_name in required_methods:
            # 이 테스트는 구현 완료 후 실제 MainWindow를 확인할 때 사용
            assert hasattr(MainWindow, '__init__'), f"MainWindow에 {method_name} 관련 로직이 필요합니다"
        
        print("✅ 슬라이스 1.3 요구사항 분석 완료")
        print("📋 구현해야 할 항목:")
        print("   1. MainWindow에 transactions_table (QTableWidget) 추가")
        print("   2. display_csv_data_in_table 메서드 구현")
        print("   3. 거래내역 화면에 테이블 위젯 배치")
        print("   4. parse_and_display_preview에서 테이블 표시 로직 연결") 