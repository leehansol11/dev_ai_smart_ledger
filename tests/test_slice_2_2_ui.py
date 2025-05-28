"""
슬라이스 2.2 UI 테스트: 카테고리 선택 시 내부 데이터 저장 및 UI 반영

테스트 범위:
1. QComboBox 선택 변경 시 시그널 감지 및 처리
2. 선택된 카테고리 정보의 내부 데이터 구조 저장 (DB 저장 전)
3. UI에 선택된 카테고리 반영 확인
4. 카테고리 변경 시 내부 데이터 업데이트 확인

TDD 방식으로 QComboBox의 선택 변경을 감지하고 내부적으로 저장하는 기능을 테스트합니다.
"""

import pytest
import sys
from PySide6.QtWidgets import QApplication, QComboBox, QTableWidget, QTableWidgetItem
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
from unittest.mock import Mock, patch

sys.path.append(".")
from ai_smart_ledger.app.ui.main_window import MainWindow
from ai_smart_ledger.app.db.crud import get_categories_for_dropdown


class TestSlice22UI:
    """슬라이스 2.2 UI 기능 테스트 클래스"""
    
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
        
        # 카테고리 ComboBox 추가 (슬라이스 2.1 기능)
        self.main_window.add_category_comboboxes_to_table()
        
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
    
    def test_category_selection_triggers_callback(self):
        """테스트 1: QComboBox 카테고리 선택 변경 시 콜백 함수가 호출되는지 확인"""
        # Given: 테이블에 카테고리 ComboBox가 추가된 상태
        table = self.main_window.transactions_table
        category_column_index = 4
        combobox = table.cellWidget(0, category_column_index)
        assert isinstance(combobox, QComboBox)
        
        # on_category_selection_changed 메서드가 호출되는지 확인하기 위한 mock
        with patch.object(self.main_window, 'on_category_selection_changed') as mock_callback:
            # When: ComboBox에서 카테고리 선택
            if combobox.count() > 1:
                test_category = combobox.itemText(1)  # 첫 번째 실제 카테고리
                combobox.setCurrentIndex(1)
                QTest.qWait(100)  # 시그널 처리 대기
                
                # Then: 콜백 함수가 호출되어야 함
                mock_callback.assert_called_once_with(0, test_category)
    
    def test_internal_data_structure_exists(self):
        """테스트 2: 카테고리 선택 정보를 저장할 내부 데이터 구조가 존재하는지 확인"""
        # Given: MainWindow 인스턴스
        main_window = self.main_window
        
        # When & Then: 내부 데이터 구조가 존재해야 함
        assert hasattr(main_window, 'transaction_categories'), \
            "MainWindow에 transaction_categories 속성이 없습니다"
        
        # 초기에는 빈 딕셔너리여야 함
        assert isinstance(main_window.transaction_categories, dict), \
            "transaction_categories가 딕셔너리가 아닙니다"
    
    def test_category_selection_stores_in_internal_data(self):
        """테스트 3: 카테고리 선택 시 내부 데이터 구조에 올바르게 저장되는지 확인"""
        # Given: 테이블에 카테고리 ComboBox가 추가된 상태
        table = self.main_window.transactions_table
        category_column_index = 4
        combobox = table.cellWidget(0, category_column_index)
        assert isinstance(combobox, QComboBox)
        
        # When: ComboBox에서 카테고리 선택
        if combobox.count() > 1:
            test_category = combobox.itemText(1)  # 첫 번째 실제 카테고리
            combobox.setCurrentIndex(1)
            QTest.qWait(100)  # 시그널 처리 대기
            
            # Then: 내부 데이터 구조에 저장되어야 함
            assert 0 in self.main_window.transaction_categories, \
                "선택된 카테고리가 내부 데이터에 저장되지 않았습니다"
            assert self.main_window.transaction_categories[0] == test_category, \
                f"저장된 카테고리가 일치하지 않습니다. 예상: {test_category}, 실제: {self.main_window.transaction_categories[0]}"
    
    def test_ui_reflects_selected_category(self):
        """테스트 4: 카테고리 선택 시 UI에 올바르게 반영되는지 확인"""
        # Given: 테이블에 카테고리 ComboBox가 추가된 상태
        table = self.main_window.transactions_table
        category_column_index = 4
        combobox = table.cellWidget(0, category_column_index)
        assert isinstance(combobox, QComboBox)
        
        # When: ComboBox에서 카테고리 선택
        if combobox.count() > 1:
            test_category = combobox.itemText(1)  # 첫 번째 실제 카테고리
            combobox.setCurrentIndex(1)
            QTest.qWait(100)  # 시그널 처리 대기
            
            # Then: UI에 선택된 카테고리가 표시되어야 함
            current_text = combobox.currentText()
            assert current_text == test_category, \
                f"UI에 표시된 카테고리가 일치하지 않습니다. 예상: {test_category}, 실제: {current_text}"
    
    def test_multiple_categories_selection_independent(self):
        """테스트 5: 여러 행의 카테고리 선택이 독립적으로 작동하는지 확인"""
        # Given: 테이블에 여러 행의 카테고리 ComboBox가 추가된 상태
        table = self.main_window.transactions_table
        category_column_index = 4
        
        # 첫 번째 행과 두 번째 행의 ComboBox 가져오기
        combobox1 = table.cellWidget(0, category_column_index)
        combobox2 = table.cellWidget(1, category_column_index)
        assert isinstance(combobox1, QComboBox)
        assert isinstance(combobox2, QComboBox)
        
        # When: 각각 다른 카테고리 선택
        if combobox1.count() > 2 and combobox2.count() > 2:
            test_category1 = combobox1.itemText(1)  # 첫 번째 카테고리
            test_category2 = combobox2.itemText(2)  # 두 번째 카테고리
            
            combobox1.setCurrentIndex(1)
            QTest.qWait(50)
            combobox2.setCurrentIndex(2)
            QTest.qWait(50)
            
            # Then: 각 행의 카테고리가 독립적으로 저장되어야 함
            assert 0 in self.main_window.transaction_categories
            assert 1 in self.main_window.transaction_categories
            assert self.main_window.transaction_categories[0] == test_category1
            assert self.main_window.transaction_categories[1] == test_category2
    
    def test_category_change_updates_internal_data(self):
        """테스트 6: 카테고리 재선택 시 내부 데이터가 업데이트되는지 확인"""
        # Given: 테이블에 카테고리 ComboBox가 추가되고 이미 선택된 상태
        table = self.main_window.transactions_table
        category_column_index = 4
        combobox = table.cellWidget(0, category_column_index)
        assert isinstance(combobox, QComboBox)
        
        # 첫 번째 카테고리 선택
        if combobox.count() > 2:
            first_category = combobox.itemText(1)
            combobox.setCurrentIndex(1)
            QTest.qWait(50)
            
            # When: 다른 카테고리로 변경
            second_category = combobox.itemText(2)
            combobox.setCurrentIndex(2)
            QTest.qWait(50)
            
            # Then: 내부 데이터가 업데이트되어야 함
            assert self.main_window.transaction_categories[0] == second_category, \
                f"카테고리 변경이 내부 데이터에 반영되지 않았습니다. 예상: {second_category}, 실제: {self.main_window.transaction_categories[0]}"
    
    def test_default_selection_handling(self):
        """테스트 7: 기본 선택 항목("카테고리를 선택하세요") 처리 확인"""
        # Given: 테이블에 카테고리 ComboBox가 추가된 상태
        table = self.main_window.transactions_table
        category_column_index = 4
        combobox = table.cellWidget(0, category_column_index)
        assert isinstance(combobox, QComboBox)
        
        # When: 기본 선택 항목을 선택
        combobox.setCurrentIndex(0)  # "카테고리를 선택하세요"
        QTest.qWait(100)
        
        # Then: 내부 데이터에서 해당 행이 제거되거나 빈 값으로 처리되어야 함
        # (또는 기본 선택 항목이 내부 데이터에 저장되지 않아야 함)
        current_text = combobox.currentText()
        if current_text == "카테고리를 선택하세요":
            # 기본 선택 항목의 경우 내부 데이터에 저장하지 않거나 특별 처리
            assert 0 not in self.main_window.transaction_categories or \
                   self.main_window.transaction_categories[0] is None or \
                   self.main_window.transaction_categories[0] == "", \
                   "기본 선택 항목이 내부 데이터에 잘못 저장되었습니다"
    
    def test_category_selection_logging(self):
        """테스트 8: 카테고리 선택 변경 시 로깅이 올바르게 수행되는지 확인"""
        # Given: 테이블에 카테고리 ComboBox가 추가된 상태
        table = self.main_window.transactions_table
        category_column_index = 4
        combobox = table.cellWidget(0, category_column_index)
        assert isinstance(combobox, QComboBox)
        
        # print 출력을 캡처하기 위한 mock
        with patch('builtins.print') as mock_print:
            # When: ComboBox에서 카테고리 선택
            if combobox.count() > 1:
                test_category = combobox.itemText(1)
                combobox.setCurrentIndex(1)
                QTest.qWait(100)
                
                # Then: 적절한 로그 메시지가 출력되어야 함
                # print 호출이 있었는지 확인
                mock_print.assert_called()
                
                # 마지막 print 호출의 인자 확인
                last_call_args = mock_print.call_args_list[-1][0]
                assert any(test_category in str(arg) for arg in last_call_args), \
                    f"선택된 카테고리 '{test_category}'가 로그에 포함되지 않았습니다"


if __name__ == "__main__":
    pytest.main([__file__]) 