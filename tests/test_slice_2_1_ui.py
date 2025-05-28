"""
슬라이스 2.1 UI 테스트: QTableWidget의 각 행에 카테고리 선택 QComboBox 추가
Author: leehansol
Created: 2025-05-25

TDD 방식으로 QTableWidget에 QComboBox를 추가하는 기능을 테스트합니다.
"""

import pytest
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication, QComboBox, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from ai_smart_ledger.app.ui.main_window import MainWindow
from ai_smart_ledger.app.db.crud import get_categories_for_dropdown


class TestSlice21UI:
    """슬라이스 2.1 UI 기능 테스트 클래스"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """각 테스트 전에 QApplication과 MainWindow 설정"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.main_window = MainWindow()
        # 거래내역 화면으로 전환
        self.main_window.show_transactions_screen()
        
        # 테스트용 샘플 데이터 설정
        self.setup_sample_data()
        
        yield
        
        # 테스트 후 정리
        if hasattr(self, 'main_window'):
            self.main_window.close()
    
    def setup_sample_data(self):
        """테스트용 샘플 거래 데이터 설정"""
        # 샘플 CSV 데이터
        sample_headers = ["날짜", "적요", "금액", "거래후잔액", "사용자 확정 카테고리"]
        sample_data = [
            ["2024-01-01", "마트 결제", "-50000", "1000000", ""],
            ["2024-01-02", "급여 입금", "3000000", "4000000", ""],
            ["2024-01-03", "카페 결제", "-5000", "3995000", ""]
        ]
        
        # 테이블에 데이터 설정
        self.main_window.transactions_table.setColumnCount(len(sample_headers))
        self.main_window.transactions_table.setRowCount(len(sample_data))
        self.main_window.transactions_table.setHorizontalHeaderLabels(sample_headers)
        
        for row_idx, row_data in enumerate(sample_data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                self.main_window.transactions_table.setItem(row_idx, col_idx, item)
    
    def test_add_category_combobox_to_table_column(self):
        """테스트 1: 테이블의 특정 열에 QComboBox 위젯이 추가되는지 확인"""
        # Given: 거래내역이 로드된 테이블
        table = self.main_window.transactions_table
        category_column_index = 4  # "사용자 확정 카테고리" 열
        row_count = table.rowCount()
        
        # When: 카테고리 ComboBox 추가 메서드 호출
        self.main_window.add_category_comboboxes_to_table()
        
        # Then: 각 행의 카테고리 열에 QComboBox가 추가되어야 함
        for row in range(row_count):
            cell_widget = table.cellWidget(row, category_column_index)
            assert cell_widget is not None, f"행 {row}의 카테고리 열에 위젯이 없습니다"
            assert isinstance(cell_widget, QComboBox), f"행 {row}의 카테고리 열 위젯이 QComboBox가 아닙니다"
    
    def test_combobox_contains_categories_from_database(self):
        """테스트 2: QComboBox에 데이터베이스에서 가져온 카테고리 목록이 포함되는지 확인"""
        # Given: 거래내역이 로드된 테이블
        table = self.main_window.transactions_table
        category_column_index = 4
        
        # 데이터베이스에서 카테고리 목록 가져오기
        expected_categories = get_categories_for_dropdown()
        
        # When: 카테고리 ComboBox 추가
        self.main_window.add_category_comboboxes_to_table()
        
        # Then: 첫 번째 행의 ComboBox에 올바른 카테고리 목록이 있어야 함
        first_row_combobox = table.cellWidget(0, category_column_index)
        assert isinstance(first_row_combobox, QComboBox)
        
        # ComboBox의 항목 수 확인
        combobox_item_count = first_row_combobox.count()
        assert combobox_item_count > 0, "ComboBox에 항목이 없습니다"
        
        # ComboBox의 모든 항목 확인
        combobox_items = []
        for i in range(combobox_item_count):
            combobox_items.append(first_row_combobox.itemText(i))
        
        # 기본 선택 항목("카테고리를 선택하세요") 제외하고 비교
        if combobox_items and combobox_items[0] == "카테고리를 선택하세요":
            actual_categories = combobox_items[1:]
        else:
            actual_categories = combobox_items
        
        # 카테고리 목록이 포함되어 있는지 확인
        for category in expected_categories:
            assert category in combobox_items, f"카테고리 '{category}'가 ComboBox에 없습니다"
    
    def test_combobox_has_default_selection(self):
        """테스트 3: QComboBox에 기본 선택 항목이 있는지 확인"""
        # Given: 거래내역이 로드된 테이블
        table = self.main_window.transactions_table
        category_column_index = 4
        
        # When: 카테고리 ComboBox 추가
        self.main_window.add_category_comboboxes_to_table()
        
        # Then: 각 행의 ComboBox 기본 선택 확인
        for row in range(table.rowCount()):
            combobox = table.cellWidget(row, category_column_index)
            assert isinstance(combobox, QComboBox)
            
            # 기본 선택이 "카테고리를 선택하세요" 또는 첫 번째 항목이어야 함
            current_text = combobox.currentText()
            assert current_text != "", "ComboBox에 선택된 항목이 없습니다"
    
    def test_category_column_exists_in_table(self):
        """테스트 4: 테이블에 "사용자 확정 카테고리" 열이 존재하는지 확인"""
        # Given: 거래내역이 로드된 테이블
        table = self.main_window.transactions_table
        
        # When: 테이블 헤더 확인
        headers = []
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item:
                headers.append(header_item.text())
        
        # Then: "사용자 확정 카테고리" 열이 존재해야 함
        assert "사용자 확정 카테고리" in headers, "테이블에 '사용자 확정 카테고리' 열이 없습니다"
    
    def test_combobox_selection_change_signal(self):
        """테스트 5: QComboBox 선택 변경 시 시그널이 발생하는지 확인"""
        # Given: 거래내역이 로드된 테이블
        table = self.main_window.transactions_table
        category_column_index = 4
        
        # When: 카테고리 ComboBox 추가
        self.main_window.add_category_comboboxes_to_table()
        
        # 첫 번째 행의 ComboBox 가져오기
        combobox = table.cellWidget(0, category_column_index)
        assert isinstance(combobox, QComboBox)
        
        # 시그널 연결 확인을 위한 플래그
        signal_received = False
        
        def on_category_changed():
            nonlocal signal_received
            signal_received = True
        
        # Then: 시그널 연결 및 변경 시 발생 확인
        combobox.currentTextChanged.connect(on_category_changed)
        
        # ComboBox 선택 변경 (두 번째 항목으로)
        if combobox.count() > 1:
            combobox.setCurrentIndex(1)
            QTest.qWait(100)  # 시그널 처리 대기
            
            assert signal_received, "ComboBox 선택 변경 시 시그널이 발생하지 않았습니다"
    
    def test_all_rows_have_comboboxes(self):
        """테스트 6: 모든 거래 행에 ComboBox가 추가되는지 확인"""
        # Given: 거래내역이 로드된 테이블
        table = self.main_window.transactions_table
        category_column_index = 4
        initial_row_count = table.rowCount()
        
        # When: 카테고리 ComboBox 추가
        self.main_window.add_category_comboboxes_to_table()
        
        # Then: 모든 행에 ComboBox가 있어야 함
        combobox_count = 0
        for row in range(initial_row_count):
            cell_widget = table.cellWidget(row, category_column_index)
            if isinstance(cell_widget, QComboBox):
                combobox_count += 1
        
        assert combobox_count == initial_row_count, f"전체 {initial_row_count}행 중 {combobox_count}행에만 ComboBox가 추가되었습니다"
    
    def test_combobox_styling(self):
        """테스트 7: QComboBox 스타일링이 적용되는지 확인"""
        # Given: 거래내역이 로드된 테이블
        table = self.main_window.transactions_table
        category_column_index = 4
        
        # When: 카테고리 ComboBox 추가
        self.main_window.add_category_comboboxes_to_table()
        
        # Then: ComboBox에 스타일이 적용되어야 함
        combobox = table.cellWidget(0, category_column_index)
        assert isinstance(combobox, QComboBox)
        
        # 스타일시트가 설정되어 있는지 확인
        stylesheet = combobox.styleSheet()
        assert stylesheet != "", "ComboBox에 스타일시트가 설정되지 않았습니다"


if __name__ == "__main__":
    pytest.main([__file__]) 