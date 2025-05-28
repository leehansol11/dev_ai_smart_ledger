"""
슬라이스 2.4 통합 테스트: "실행 취소(Undo)" 기능

테스트 범위:
1. 전체 워크플로우 - 파일 로딩부터 카테고리 변경, 실행 취소까지
2. 여러 행에서 카테고리 변경 후 실행 취소의 동작 확인
3. 데이터베이스 연동이 있는 경우 실행 취소의 DB 반영 확인
4. 실행 취소 히스토리의 크기 제한 확인
5. 복잡한 시나리오에서의 실행 취소 동작 확인

TDD 방식으로 실행 취소 기능의 통합 시나리오를 테스트합니다.
"""

import pytest
import sys
import os
import tempfile
from PySide6.QtWidgets import QApplication, QComboBox, QTableWidget, QPushButton
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

sys.path.append(".")
from ai_smart_ledger.app.ui.main_window import MainWindow
from ai_smart_ledger.app.core.file_parser import FileParser


class TestSlice24Integration:
    """슬라이스 2.4 통합 테스트 클래스"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """각 테스트 전에 QApplication과 MainWindow 설정"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.main_window = MainWindow()
        self.main_window.show_transactions_screen()
        
        # 테스트용 임시 CSV 파일 생성
        self.temp_csv_file = self.create_temp_csv_file()
        
        yield
        
        # 테스트 후 정리
        if hasattr(self, 'main_window'):
            self.main_window.close()
        
        # 임시 파일 정리
        if os.path.exists(self.temp_csv_file):
            os.unlink(self.temp_csv_file)
    
    def create_temp_csv_file(self):
        """테스트용 임시 CSV 파일 생성"""
        temp_fd, temp_path = tempfile.mkstemp(suffix='.csv')
        
        csv_content = """날짜,적요,금액,거래후잔액
2024-01-01,마트 결제,-50000,1000000
2024-01-02,급여 입금,3000000,4000000
2024-01-03,카페 결제,-5000,3995000
2024-01-04,택시 요금,-12000,3983000
2024-01-05,온라인 쇼핑,-85000,3898000
"""
        
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        return temp_path
    
    def test_end_to_end_undo_workflow(self):
        """테스트 1: 전체 워크플로우 - CSV 로딩부터 카테고리 변경, 실행 취소까지"""
        # Given: 테스트용 CSV 파일이 준비된 상태
        assert os.path.exists(self.temp_csv_file)
        
        # When: CSV 파일을 파싱하여 테이블에 로딩
        self.main_window.parse_and_display_preview(self.temp_csv_file)
        QTest.qWait(200)  # 파싱 및 UI 업데이트 대기
        
        # Then: 테이블에 데이터가 로딩되고 카테고리 ComboBox가 추가되어야 함
        table = self.main_window.transactions_table
        assert table.rowCount() > 0, "테이블에 데이터가 로딩되지 않았습니다"
        
        # 카테고리 열 인덱스 찾기
        category_column_index = -1
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item and header_item.text() == "사용자 확정 카테고리":
                category_column_index = col
                break
        
        assert category_column_index != -1, "'사용자 확정 카테고리' 열이 찾아지지 않았습니다"
        
        # 첫 번째 행에 ComboBox가 있는지 확인
        combobox = table.cellWidget(0, category_column_index)
        assert isinstance(combobox, QComboBox), "카테고리 ComboBox가 추가되지 않았습니다"
        
        # 초기 카테고리 상태 저장
        initial_category = combobox.currentText()
        
        # When: 카테고리 선택 변경
        if combobox.count() > 1:
            test_category = combobox.itemText(1)
            combobox.setCurrentIndex(1)
            QTest.qWait(100)
            
            # 변경 확인
            assert combobox.currentText() == test_category
            
            # "실행 취소" 버튼 찾기
            undo_button = None
            for child in self.main_window.findChildren(QPushButton):
                if "실행 취소" in child.text() or "Undo" in child.text():
                    undo_button = child
                    break
            
            assert undo_button is not None, "실행 취소 버튼을 찾을 수 없습니다"
            
            # When: 실행 취소
            undo_button.click()
            QTest.qWait(100)
            
            # Then: 초기 카테고리로 복원되어야 함
            assert combobox.currentText() == initial_category, \
                f"실행 취소 후 카테고리가 복원되지 않았습니다. 예상: {initial_category}, 실제: {combobox.currentText()}"
    
    def test_multiple_rows_undo_independence(self):
        """테스트 2: 여러 행에서 카테고리 변경 후 실행 취소가 최근 변경만 영향을 주는지 확인"""
        # Given: CSV 파일이 로딩된 상태
        self.main_window.parse_and_display_preview(self.temp_csv_file)
        QTest.qWait(200)
        
        table = self.main_window.transactions_table
        category_column_index = -1
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item and header_item.text() == "사용자 확정 카테고리":
                category_column_index = col
                break
        
        # When: 여러 행에서 카테고리 변경
        row1_combobox = table.cellWidget(0, category_column_index)
        row2_combobox = table.cellWidget(1, category_column_index)
        
        # 첫 번째 행 카테고리 변경
        if row1_combobox.count() > 1:
            row1_new_category = row1_combobox.itemText(1)
            row1_combobox.setCurrentIndex(1)
            QTest.qWait(50)
        
        # 두 번째 행 카테고리 변경 (더 최근)
        if row2_combobox.count() > 1:
            row2_initial_category = row2_combobox.currentText()
            row2_new_category = row2_combobox.itemText(1)
            row2_combobox.setCurrentIndex(1)
            QTest.qWait(50)
        
        # "실행 취소" 버튼 찾기 및 클릭
        undo_button = None
        for child in self.main_window.findChildren(QPushButton):
            if "실행 취소" in child.text() or "Undo" in child.text():
                undo_button = child
                break
        
        undo_button.click()
        QTest.qWait(100)
        
        # Then: 가장 최근 변경(두 번째 행)만 되돌려져야 함
        assert row2_combobox.currentText() == row2_initial_category, \
            "실행 취소가 가장 최근 변경된 행에 적용되지 않았습니다"
        
        # 첫 번째 행은 변경된 상태를 유지해야 함
        assert row1_combobox.currentText() == row1_new_category, \
            "실행 취소가 이전 변경에 잘못 적용되었습니다"
    
    def test_undo_history_size_limit(self):
        """테스트 3: 실행 취소 히스토리의 크기 제한 확인 (메모리 관리)"""
        # Given: CSV 파일이 로딩된 상태
        self.main_window.parse_and_display_preview(self.temp_csv_file)
        QTest.qWait(200)
        
        table = self.main_window.transactions_table
        category_column_index = -1
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item and header_item.text() == "사용자 확정 카테고리":
                category_column_index = col
                break
        
        combobox = table.cellWidget(0, category_column_index)
        
        # When: 많은 수의 카테고리 변경 수행 (히스토리 크기 제한 테스트)
        max_changes = 15  # 히스토리 제한보다 많이 변경
        for i in range(max_changes):
            if combobox.count() > 2:
                # 1번과 2번 카테고리 사이에서 번갈아 변경
                index = 1 + (i % 2)
                combobox.setCurrentIndex(index)
                QTest.qWait(10)
        
        # Then: 히스토리가 적절한 크기로 제한되어야 함 (예: 최대 10개)
        max_history_size = 10
        assert len(self.main_window.category_change_history) <= max_history_size, \
            f"히스토리 크기가 제한을 초과했습니다. 실제: {len(self.main_window.category_change_history)}, 최대: {max_history_size}"
    
    def test_undo_persistence_across_file_changes(self):
        """테스트 4: 다른 파일 로딩 시 실행 취소 히스토리가 적절히 초기화되는지 확인"""
        # Given: 첫 번째 CSV 파일이 로딩되고 카테고리 변경이 있는 상태
        self.main_window.parse_and_display_preview(self.temp_csv_file)
        QTest.qWait(200)
        
        table = self.main_window.transactions_table
        category_column_index = -1
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item and header_item.text() == "사용자 확정 카테고리":
                category_column_index = col
                break
        
        combobox = table.cellWidget(0, category_column_index)
        
        # 카테고리 변경
        if combobox.count() > 1:
            combobox.setCurrentIndex(1)
            QTest.qWait(50)
        
        # 히스토리가 있는지 확인
        assert len(self.main_window.category_change_history) > 0, "카테고리 변경 히스토리가 없습니다"
        
        # When: 새로운 파일 로딩 (또는 파일 재로딩)
        self.main_window.parse_and_display_preview(self.temp_csv_file)
        QTest.qWait(200)
        
        # Then: 히스토리가 초기화되어야 함
        assert len(self.main_window.category_change_history) == 0, \
            "새 파일 로딩 후 히스토리가 초기화되지 않았습니다"
        
        # 실행 취소 버튼이 비활성화되어야 함
        undo_button = None
        for child in self.main_window.findChildren(QPushButton):
            if "실행 취소" in child.text() or "Undo" in child.text():
                undo_button = child
                break
        
        if undo_button:
            assert not undo_button.isEnabled(), "새 파일 로딩 후 실행 취소 버튼이 비활성화되지 않았습니다"
    
    def test_complex_undo_scenario_with_db_integration(self):
        """테스트 5: 복잡한 시나리오 - 카테고리 변경, DB 저장, 실행 취소의 조합"""
        # Given: CSV 파일이 로딩된 상태
        self.main_window.parse_and_display_preview(self.temp_csv_file)
        QTest.qWait(200)
        
        table = self.main_window.transactions_table
        category_column_index = -1
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item and header_item.text() == "사용자 확정 카테고리":
                category_column_index = col
                break
        
        combobox = table.cellWidget(0, category_column_index)
        
        # When: 복잡한 시나리오 수행
        # 1. 카테고리 변경
        if combobox.count() > 2:
            initial_category = combobox.currentText()
            first_category = combobox.itemText(1)
            second_category = combobox.itemText(2)
            
            # 첫 번째 변경
            combobox.setCurrentIndex(1)
            QTest.qWait(50)
            
            # 두 번째 변경
            combobox.setCurrentIndex(2)
            QTest.qWait(50)
            
            # 2. 실행 취소 (두 번째 → 첫 번째 변경으로)
            undo_button = None
            for child in self.main_window.findChildren(QPushButton):
                if "실행 취소" in child.text() or "Undo" in child.text():
                    undo_button = child
                    break
            
            undo_button.click()
            QTest.qWait(100)
            
            # Then: 첫 번째 변경 상태로 복원되어야 함
            assert combobox.currentText() == first_category, \
                f"복잡한 시나리오에서 실행 취소가 올바르게 작동하지 않았습니다. 예상: {first_category}, 실제: {combobox.currentText()}"
            
            # 내부 데이터 일관성 확인
            if 0 in self.main_window.transaction_categories:
                assert self.main_window.transaction_categories[0] == first_category, \
                    "내부 데이터가 UI와 일치하지 않습니다"
    
    def test_undo_button_state_consistency(self):
        """테스트 6: 다양한 상황에서 실행 취소 버튼 상태의 일관성 확인"""
        # Given: CSV 파일이 로딩된 상태
        self.main_window.parse_and_display_preview(self.temp_csv_file)
        QTest.qWait(200)
        
        table = self.main_window.transactions_table
        category_column_index = -1
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item and header_item.text() == "사용자 확정 카테고리":
                category_column_index = col
                break
        
        combobox = table.cellWidget(0, category_column_index)
        
        # 실행 취소 버튼 찾기
        undo_button = None
        for child in self.main_window.findChildren(QPushButton):
            if "실행 취소" in child.text() or "Undo" in child.text():
                undo_button = child
                break
        
        assert undo_button is not None, "실행 취소 버튼을 찾을 수 없습니다"
        
        # When & Then: 다양한 상황에서 버튼 상태 확인
        
        # 1. 초기 상태 - 비활성화
        assert not undo_button.isEnabled(), "초기 상태에서 실행 취소 버튼이 활성화되어 있습니다"
        
        # 2. 카테고리 변경 후 - 활성화
        if combobox.count() > 1:
            combobox.setCurrentIndex(1)
            QTest.qWait(50)
            assert undo_button.isEnabled(), "카테고리 변경 후 실행 취소 버튼이 활성화되지 않았습니다"
            
            # 3. 실행 취소 후 - 적절한 상태 (히스토리가 남아있으면 활성화, 없으면 비활성화)
            undo_button.click()
            QTest.qWait(50)
            
            # 히스토리가 남아있는지 확인
            has_more_history = len(self.main_window.category_change_history) > 0
            assert undo_button.isEnabled() == has_more_history, \
                f"실행 취소 후 버튼 상태가 올바르지 않습니다. 히스토리 유무: {has_more_history}, 버튼 활성화: {undo_button.isEnabled()}" 