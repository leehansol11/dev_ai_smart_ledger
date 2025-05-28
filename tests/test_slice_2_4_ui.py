"""
슬라이스 2.4 UI 테스트: "실행 취소(Undo)" 기능

테스트 범위:
1. "실행 취소" 버튼이 UI에 존재하는지 확인
2. 카테고리 변경 시 이전 상태가 스택에 저장되는지 확인
3. "실행 취소" 버튼 클릭 시 이전 카테고리로 복원되는지 확인
4. 실행 취소 후 UI 상태가 올바르게 업데이트되는지 확인
5. 실행 취소 가능한 상태인지 버튼 활성화/비활성화 확인

TDD 방식으로 실행 취소 기능을 테스트합니다.
"""

import pytest
import sys
import os
from PySide6.QtWidgets import QApplication, QComboBox, QTableWidget, QTableWidgetItem, QPushButton
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
from unittest.mock import Mock, patch

sys.path.append(".")
from ai_smart_ledger.app.ui.main_window import MainWindow
from ai_smart_ledger.app.db.crud import get_categories_for_dropdown


class TestSlice24UI:
    """슬라이스 2.4 UI 기능 테스트 클래스"""
    
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
        
        # 카테고리 ComboBox 추가
        self.main_window.add_category_comboboxes_to_table()
    
    def test_undo_button_exists_in_ui(self):
        """테스트 1: "실행 취소" 버튼이 UI에 존재하는지 확인"""
        # Given: MainWindow가 초기화된 상태
        main_window = self.main_window
        
        # When: UI에서 "실행 취소" 버튼을 찾기
        undo_button = None
        for child in main_window.findChildren(QPushButton):
            if "실행 취소" in child.text() or "Undo" in child.text():
                undo_button = child
                break
        
        # Then: "실행 취소" 버튼이 존재해야 함
        assert undo_button is not None, "UI에 '실행 취소' 버튼이 없습니다"
        assert isinstance(undo_button, QPushButton), "'실행 취소' 버튼이 QPushButton이 아닙니다"
    
    def test_undo_stack_exists_for_category_history(self):
        """테스트 2: 카테고리 변경 히스토리를 저장할 스택이 존재하는지 확인"""
        # Given: MainWindow가 초기화된 상태
        main_window = self.main_window
        
        # When & Then: 카테고리 변경 히스토리를 저장할 스택이 존재해야 함
        assert hasattr(main_window, 'category_change_history'), \
            "MainWindow에 category_change_history 속성이 없습니다"
        
        # 스택이 리스트 형태로 구현되어야 함
        assert isinstance(main_window.category_change_history, list), \
            "category_change_history가 리스트가 아닙니다"
    
    def test_category_change_saves_to_history_stack(self):
        """테스트 3: 카테고리 변경 시 이전 상태가 히스토리 스택에 저장되는지 확인"""
        # Given: 테이블에 카테고리 ComboBox가 추가된 상태
        table = self.main_window.transactions_table
        category_column_index = 4  # "사용자 확정 카테고리" 열
        combobox = table.cellWidget(0, category_column_index)
        assert isinstance(combobox, QComboBox)
        
        # When: 카테고리 선택 변경
        if combobox.count() > 1:
            # 초기 상태 확인
            initial_history_length = len(self.main_window.category_change_history)
            
            # 카테고리 선택
            test_category = combobox.itemText(1)
            combobox.setCurrentIndex(1)
            QTest.qWait(100)  # 시그널 처리 대기
            
            # Then: 히스토리 스택에 변경 사항이 저장되어야 함
            assert len(self.main_window.category_change_history) > initial_history_length, \
                "카테고리 변경 시 히스토리가 저장되지 않았습니다"
            
            # 저장된 히스토리 확인
            latest_history = self.main_window.category_change_history[-1]
            assert 'row' in latest_history, "히스토리에 행 정보가 없습니다"
            assert 'previous_category' in latest_history, "히스토리에 이전 카테고리 정보가 없습니다"
            assert 'current_category' in latest_history, "히스토리에 현재 카테고리 정보가 없습니다"
    
    def test_undo_button_restores_previous_category(self):
        """테스트 4: "실행 취소" 버튼 클릭 시 이전 카테고리로 복원되는지 확인"""
        # Given: 카테고리가 변경된 상태
        table = self.main_window.transactions_table
        category_column_index = 4
        combobox = table.cellWidget(0, category_column_index)
        assert isinstance(combobox, QComboBox)
        
        # 초기 카테고리 (기본 선택)
        initial_category = combobox.currentText()
        
        # 카테고리 변경
        if combobox.count() > 1:
            new_category = combobox.itemText(1)
            combobox.setCurrentIndex(1)
            QTest.qWait(100)
            
            # 변경 확인
            assert combobox.currentText() == new_category
            
            # When: "실행 취소" 버튼 클릭
            undo_button = None
            for child in self.main_window.findChildren(QPushButton):
                if "실행 취소" in child.text() or "Undo" in child.text():
                    undo_button = child
                    break
            
            assert undo_button is not None, "실행 취소 버튼을 찾을 수 없습니다"
            
            undo_button.click()
            QTest.qWait(100)
            
            # Then: 이전 카테고리로 복원되어야 함
            assert combobox.currentText() == initial_category, \
                f"실행 취소 후 카테고리가 복원되지 않았습니다. 예상: {initial_category}, 실제: {combobox.currentText()}"
    
    def test_undo_button_enabled_disabled_state(self):
        """테스트 5: 실행 취소 가능 여부에 따른 버튼 활성화/비활성화 확인"""
        # Given: "실행 취소" 버튼 찾기
        undo_button = None
        for child in self.main_window.findChildren(QPushButton):
            if "실행 취소" in child.text() or "Undo" in child.text():
                undo_button = child
                break
        
        assert undo_button is not None, "실행 취소 버튼을 찾을 수 없습니다"
        
        # When: 초기 상태 (변경 사항이 없을 때)
        # Then: 버튼이 비활성화되어야 함
        assert not undo_button.isEnabled(), "초기 상태에서 실행 취소 버튼이 활성화되어 있습니다"
        
        # When: 카테고리 변경 후
        table = self.main_window.transactions_table
        category_column_index = 4
        combobox = table.cellWidget(0, category_column_index)
        
        if combobox.count() > 1:
            combobox.setCurrentIndex(1)
            QTest.qWait(100)
            
            # Then: 버튼이 활성화되어야 함
            assert undo_button.isEnabled(), "카테고리 변경 후 실행 취소 버튼이 활성화되지 않았습니다"
    
    def test_undo_updates_internal_data_structure(self):
        """테스트 6: 실행 취소 시 내부 데이터 구조가 올바르게 업데이트되는지 확인"""
        # Given: 카테고리가 변경된 상태
        table = self.main_window.transactions_table
        category_column_index = 4
        combobox = table.cellWidget(0, category_column_index)
        
        # 초기 내부 데이터 상태
        initial_data = self.main_window.transaction_categories.copy()
        
        if combobox.count() > 1:
            # 카테고리 변경
            new_category = combobox.itemText(1)
            combobox.setCurrentIndex(1)
            QTest.qWait(100)
            
            # 변경된 내부 데이터 확인
            assert 0 in self.main_window.transaction_categories
            assert self.main_window.transaction_categories[0] == new_category
            
            # When: 실행 취소
            undo_button = None
            for child in self.main_window.findChildren(QPushButton):
                if "실행 취소" in child.text() or "Undo" in child.text():
                    undo_button = child
                    break
            
            undo_button.click()
            QTest.qWait(100)
            
            # Then: 내부 데이터가 이전 상태로 복원되어야 함
            assert self.main_window.transaction_categories == initial_data, \
                "실행 취소 후 내부 데이터가 복원되지 않았습니다"
    
    def test_multiple_changes_undo_restores_last_change_only(self):
        """테스트 7: 여러 번 변경 후 실행 취소 시 가장 최근 변경만 되돌리는지 확인"""
        # Given: 여러 번의 카테고리 변경
        table = self.main_window.transactions_table
        category_column_index = 4
        combobox = table.cellWidget(0, category_column_index)
        
        if combobox.count() > 2:
            # 첫 번째 변경
            first_category = combobox.itemText(1)
            combobox.setCurrentIndex(1)
            QTest.qWait(50)
            
            # 두 번째 변경
            second_category = combobox.itemText(2)
            combobox.setCurrentIndex(2)
            QTest.qWait(50)
            
            # When: 실행 취소
            undo_button = None
            for child in self.main_window.findChildren(QPushButton):
                if "실행 취소" in child.text() or "Undo" in child.text():
                    undo_button = child
                    break
            
            undo_button.click()
            QTest.qWait(100)
            
            # Then: 가장 최근의 변경(두 번째 변경)만 되돌려서 첫 번째 카테고리로 복원되어야 함
            assert combobox.currentText() == first_category, \
                f"실행 취소가 가장 최근 변경만 되돌리지 않았습니다. 예상: {first_category}, 실제: {combobox.currentText()}" 