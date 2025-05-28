"""
슬라이스 2.1 통합 테스트: 파일 로딩부터 ComboBox 추가까지 전체 워크플로우 테스트
Author: leehansol
Created: 2025-05-25

실제 CSV 파일을 로딩하고 테이블에 표시한 후 ComboBox가 추가되는 전체 과정을 테스트합니다.
"""

import pytest
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from ai_smart_ledger.app.ui.main_window import MainWindow
from ai_smart_ledger.app.core.file_parser import FileParser


class TestSlice21Integration:
    """슬라이스 2.1 통합 테스트 클래스"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """각 테스트 전에 QApplication과 MainWindow 설정"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.main_window = MainWindow()
        self.main_window.show_transactions_screen()
        
        # 테스트 파일 경로
        self.test_csv_path = "sample_transactions_with_category.csv"
        
        yield
        
        # 테스트 후 정리
        if hasattr(self, 'main_window'):
            self.main_window.close()
    
    def test_full_workflow_file_loading_to_combobox(self):
        """통합 테스트: 파일 로딩부터 ComboBox 추가까지 전체 워크플로우"""
        # Given: CSV 파일이 존재함
        assert os.path.exists(self.test_csv_path), f"테스트 파일 {self.test_csv_path}이 존재하지 않습니다"
        
        # When: 파일을 파싱하여 테이블에 표시
        file_parser = FileParser()
        
        # CSV 파일 파싱
        parse_result = file_parser.parse_csv_preview(self.test_csv_path)
        
        # 파싱 결과 확인
        assert parse_result['success'], f"CSV 파싱 실패: {parse_result.get('error', '알 수 없는 오류')}"
        
        # 테이블에 데이터 표시 (이 과정에서 자동으로 ComboBox도 추가됨)
        self.main_window.display_csv_data_in_table(parse_result)
        
        # Then: 테이블에 데이터가 올바르게 표시되어야 함
        table = self.main_window.transactions_table
        
        # 헤더 확인
        headers = []
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item:
                headers.append(header_item.text())
        
        assert "사용자 확정 카테고리" in headers, "테이블에 '사용자 확정 카테고리' 열이 없습니다"
        
        # 데이터 행 확인
        assert table.rowCount() > 0, "테이블에 데이터가 없습니다"
        
        # 카테고리 열 인덱스 찾기
        category_column_index = headers.index("사용자 확정 카테고리")
        
        # 모든 행에 ComboBox가 추가되었는지 확인
        for row in range(table.rowCount()):
            cell_widget = table.cellWidget(row, category_column_index)
            assert cell_widget is not None, f"행 {row}의 카테고리 열에 위젯이 없습니다"
            assert isinstance(cell_widget, QComboBox), f"행 {row}의 카테고리 열 위젯이 QComboBox가 아닙니다"
            
            # ComboBox에 카테고리 목록이 있는지 확인
            assert cell_widget.count() > 1, f"행 {row}의 ComboBox에 카테고리가 없습니다"
            
            # 기본 선택 확인
            assert cell_widget.currentText() == "카테고리를 선택하세요", f"행 {row}의 ComboBox 기본 선택이 올바르지 않습니다"
    
    def test_combobox_interaction_after_file_loading(self):
        """통합 테스트: 파일 로딩 후 ComboBox 상호작용 테스트"""
        # Given: 파일이 로딩되고 ComboBox가 추가된 상태
        file_parser = FileParser()
        parse_result = file_parser.parse_csv_preview(self.test_csv_path)
        self.main_window.display_csv_data_in_table(parse_result)
        
        table = self.main_window.transactions_table
        
        # 카테고리 열 인덱스 찾기
        category_column_index = -1
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item and header_item.text() == "사용자 확정 카테고리":
                category_column_index = col
                break
        
        assert category_column_index != -1, "카테고리 열을 찾을 수 없습니다"
        
        # When: 첫 번째 행의 ComboBox에서 카테고리 선택
        first_row_combobox = table.cellWidget(0, category_column_index)
        assert isinstance(first_row_combobox, QComboBox)
        
        # 사용 가능한 카테고리 확인
        available_categories = []
        for i in range(first_row_combobox.count()):
            available_categories.append(first_row_combobox.itemText(i))
        
        # "카테고리를 선택하세요" 외의 실제 카테고리가 있는지 확인
        actual_categories = [cat for cat in available_categories if cat != "카테고리를 선택하세요"]
        assert len(actual_categories) > 0, "실제 카테고리가 없습니다"
        
        # 첫 번째 실제 카테고리 선택
        first_category = actual_categories[0]
        category_index = available_categories.index(first_category)
        
        # Then: 카테고리 선택 변경
        first_row_combobox.setCurrentIndex(category_index)
        QTest.qWait(100)  # 시그널 처리 대기
        
        # 선택된 카테고리 확인
        assert first_row_combobox.currentText() == first_category, "카테고리 선택이 반영되지 않았습니다"
    
    def test_multiple_file_loading_combobox_reset(self):
        """통합 테스트: 여러 파일 로딩 시 ComboBox 재설정 테스트"""
        # Given: 첫 번째 파일 로딩
        file_parser = FileParser()
        parse_result = file_parser.parse_csv_preview(self.test_csv_path)
        self.main_window.display_csv_data_in_table(parse_result)
        
        table = self.main_window.transactions_table
        initial_row_count = table.rowCount()
        
        # When: 같은 파일을 다시 로딩 (실제 사용 시나리오)
        parse_result2 = file_parser.parse_csv_preview(self.test_csv_path)
        self.main_window.display_csv_data_in_table(parse_result2)
        
        # Then: 테이블이 새로 설정되고 ComboBox도 다시 추가되어야 함
        assert table.rowCount() == initial_row_count, "파일 재로딩 후 행 수가 다릅니다"
        
        # 카테고리 열에 여전히 ComboBox가 있는지 확인
        category_column_index = -1
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item and header_item.text() == "사용자 확정 카테고리":
                category_column_index = col
                break
        
        assert category_column_index != -1, "재로딩 후 카테고리 열을 찾을 수 없습니다"
        
        # 모든 행에 ComboBox가 있는지 확인
        for row in range(table.rowCount()):
            cell_widget = table.cellWidget(row, category_column_index)
            assert isinstance(cell_widget, QComboBox), f"재로딩 후 행 {row}에 ComboBox가 없습니다"
    
    def test_error_handling_invalid_file(self):
        """통합 테스트: 잘못된 파일 처리 시 오류 핸들링"""
        # Given: 존재하지 않는 파일
        invalid_file_path = "non_existent_file.csv"
        
        # When: 잘못된 파일을 파싱 시도
        file_parser = FileParser()
        parse_result = file_parser.parse_csv_preview(invalid_file_path)
        
        # Then: 파싱이 실패해야 하고, 테이블은 변경되지 않아야 함
        assert not parse_result['success'], "존재하지 않는 파일에 대해 파싱이 성공했습니다"
        
        # display_csv_data_in_table 호출 시 오류 처리되어야 함
        table = self.main_window.transactions_table
        initial_row_count = table.rowCount()
        
        # 오류가 있는 결과로 테이블 업데이트 시도
        self.main_window.display_csv_data_in_table(parse_result)
        
        # 테이블이 변경되지 않았는지 확인
        assert table.rowCount() == initial_row_count, "오류 상황에서 테이블이 변경되었습니다"


if __name__ == "__main__":
    pytest.main([__file__]) 