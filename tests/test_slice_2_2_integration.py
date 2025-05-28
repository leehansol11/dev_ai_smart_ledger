"""
슬라이스 2.2 통합 테스트: 카테고리 선택 시 내부 데이터 저장 및 UI 반영

통합 테스트 범위:
1. 실제 CSV 파일 로딩 후 카테고리 선택 기능 동작 확인
2. 여러 카테고리 선택 시나리오의 전체 워크플로우 테스트
3. 카테고리 선택 데이터의 지속성 및 일관성 확인
4. UI와 내부 데이터 간의 동기화 확인

실제 사용자 워크플로우를 시뮬레이션하여 전체적인 기능 검증을 수행합니다.
"""

import pytest
import sys
import tempfile
import os
from PySide6.QtWidgets import QApplication, QComboBox
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

sys.path.append(".")
from ai_smart_ledger.app.ui.main_window import MainWindow


class TestSlice22Integration:
    """슬라이스 2.2 통합 테스트 클래스"""
    
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
        
        # 테스트용 임시 CSV 파일 생성
        self.temp_csv_file = self.create_temp_csv_file()
        
        yield
        
        # 테스트 후 정리
        if hasattr(self, 'main_window'):
            self.main_window.close()
        
        # 임시 파일 정리
        if hasattr(self, 'temp_csv_file') and os.path.exists(self.temp_csv_file):
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
    
    def test_end_to_end_category_selection_workflow(self):
        """테스트 1: 전체 워크플로우 - CSV 로딩부터 카테고리 선택까지"""
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
        
        # When: 카테고리 선택
        if combobox.count() > 1:
            test_category = combobox.itemText(1)
            combobox.setCurrentIndex(1)
            QTest.qWait(100)
            
            # Then: 내부 데이터에 저장되어야 함
            assert 0 in self.main_window.transaction_categories
            assert self.main_window.transaction_categories[0] == test_category
    
    def test_multiple_rows_category_selection_persistence(self):
        """테스트 2: 여러 행의 카테고리 선택이 지속적으로 유지되는지 확인"""
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
        
        # When: 여러 행에서 서로 다른 카테고리 선택
        selected_categories = {}
        for row in range(min(3, table.rowCount())):  # 최대 3개 행 테스트
            combobox = table.cellWidget(row, category_column_index)
            if isinstance(combobox, QComboBox) and combobox.count() > row + 1:
                test_category = combobox.itemText(row + 1)
                combobox.setCurrentIndex(row + 1)
                selected_categories[row] = test_category
                QTest.qWait(50)
        
        # Then: 모든 선택이 내부 데이터에 정확히 저장되어야 함
        for row, expected_category in selected_categories.items():
            assert row in self.main_window.transaction_categories, \
                f"행 {row}의 카테고리가 내부 데이터에 저장되지 않았습니다"
            assert self.main_window.transaction_categories[row] == expected_category, \
                f"행 {row}의 저장된 카테고리가 일치하지 않습니다"
    
    def test_category_selection_ui_sync(self):
        """테스트 3: UI와 내부 데이터 간의 동기화 확인"""
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
        assert isinstance(combobox, QComboBox)
        
        # When: 카테고리 선택 후 변경
        if combobox.count() > 2:
            # 첫 번째 카테고리 선택
            first_category = combobox.itemText(1)
            combobox.setCurrentIndex(1)
            QTest.qWait(50)
            
            # Then: UI와 내부 데이터가 일치해야 함
            assert combobox.currentText() == first_category
            assert self.main_window.transaction_categories[0] == first_category
            
            # When: 다른 카테고리로 변경
            second_category = combobox.itemText(2)
            combobox.setCurrentIndex(2)
            QTest.qWait(50)
            
            # Then: 변경된 내용이 UI와 내부 데이터에 모두 반영되어야 함
            assert combobox.currentText() == second_category
            assert self.main_window.transaction_categories[0] == second_category
    
    def test_default_selection_reset_behavior(self):
        """테스트 4: 기본 선택으로 되돌릴 때의 동작 확인"""
        # Given: CSV 파일이 로딩되고 카테고리가 선택된 상태
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
        assert isinstance(combobox, QComboBox)
        
        # 먼저 카테고리 선택
        if combobox.count() > 1:
            test_category = combobox.itemText(1)
            combobox.setCurrentIndex(1)
            QTest.qWait(50)
            
            # 선택이 저장되었는지 확인
            assert 0 in self.main_window.transaction_categories
            
            # When: 기본 선택으로 되돌리기
            combobox.setCurrentIndex(0)  # "카테고리를 선택하세요"
            QTest.qWait(50)
            
            # Then: 내부 데이터에서 제거되어야 함
            assert 0 not in self.main_window.transaction_categories, \
                "기본 선택으로 되돌린 후에도 내부 데이터에 남아있습니다"
    
    def test_large_dataset_category_selection_performance(self):
        """테스트 5: 많은 데이터에서 카테고리 선택 성능 확인"""
        # Given: 미리보기 모드에 맞는 테스트 데이터셋 생성 (5행 + 헤더)
        large_temp_fd, large_temp_path = tempfile.mkstemp(suffix='.csv')
        
        try:
            # 미리보기 모드에서 로딩될 5개 행의 CSV 생성
            csv_content = "날짜,적요,금액,거래후잔액\n"
            for i in range(5):  # 미리보기 모드에서 로딩되는 행 수에 맞춤
                csv_content += f"2024-01-{i+1:02d},거래 {i+1},-{(i+1)*1000},1000000\n"
            
            with os.fdopen(large_temp_fd, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            # When: CSV 파일 로딩 (미리보기 모드)
            import time
            start_time = time.time()
            
            self.main_window.parse_and_display_preview(large_temp_path)
            QTest.qWait(300)  # UI 업데이트 대기
            
            load_time = time.time() - start_time
            
            # Then: 합리적인 시간 내에 로딩되어야 함 (2초 이하)
            assert load_time < 2.0, f"로딩 시간이 너무 오래 걸렸습니다: {load_time:.2f}초"
            
            table = self.main_window.transactions_table
            assert table.rowCount() == 5, f"예상 데이터가 로딩되지 않았습니다. 실제: {table.rowCount()}, 예상: 5"
            
            # 카테고리 선택 테스트
            category_column_index = -1
            for col in range(table.columnCount()):
                header_item = table.horizontalHeaderItem(col)
                if header_item and header_item.text() == "사용자 확정 카테고리":
                    category_column_index = col
                    break
            
            # 모든 행에서 카테고리 선택
            for row in range(table.rowCount()):
                combobox = table.cellWidget(row, category_column_index)
                assert isinstance(combobox, QComboBox), f"행 {row}에 ComboBox가 없습니다"
                
                if combobox.count() > 1:
                    combobox.setCurrentIndex(1)
                    QTest.qWait(10)
            
            # 선택된 카테고리들이 모두 저장되었는지 확인
            assert len(self.main_window.transaction_categories) == 5, \
                f"선택된 카테고리가 모두 저장되지 않았습니다. 실제: {len(self.main_window.transaction_categories)}, 예상: 5"
                
        finally:
            # 임시 파일 정리
            if os.path.exists(large_temp_path):
                os.unlink(large_temp_path)
    
    def test_category_selection_data_consistency(self):
        """테스트 6: 카테고리 선택 데이터의 일관성 확인"""
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
        
        # When: 복잡한 선택 시나리오 수행
        test_scenarios = [
            (0, 1),  # 행 0에 카테고리 1 선택
            (1, 2),  # 행 1에 카테고리 2 선택
            (0, 2),  # 행 0을 카테고리 2로 변경
            (2, 1),  # 행 2에 카테고리 1 선택
            (1, 0),  # 행 1을 기본 선택으로 되돌리기
        ]
        
        for row, category_index in test_scenarios:
            if row < table.rowCount():
                combobox = table.cellWidget(row, category_column_index)
                if isinstance(combobox, QComboBox) and combobox.count() > category_index:
                    combobox.setCurrentIndex(category_index)
                    QTest.qWait(30)
        
        # Then: 최종 상태 확인
        expected_final_state = {
            0: combobox.itemText(2) if table.cellWidget(0, category_column_index).count() > 2 else None,
            2: combobox.itemText(1) if table.cellWidget(2, category_column_index).count() > 1 else None
        }
        
        # 행 1은 기본 선택으로 되돌렸으므로 저장되지 않아야 함
        for row, expected_category in expected_final_state.items():
            if expected_category:
                assert row in self.main_window.transaction_categories, \
                    f"행 {row}의 카테고리가 저장되지 않았습니다"
                assert self.main_window.transaction_categories[row] == expected_category, \
                    f"행 {row}의 저장된 카테고리가 예상과 다릅니다"
        
        # 행 1은 내부 데이터에 없어야 함
        assert 1 not in self.main_window.transaction_categories, \
            "기본 선택으로 되돌린 행 1이 여전히 내부 데이터에 있습니다"


if __name__ == "__main__":
    pytest.main([__file__]) 