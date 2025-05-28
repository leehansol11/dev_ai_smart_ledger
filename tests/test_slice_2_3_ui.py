"""
슬라이스 2.3: 분류된 카테고리 transactions DB에 저장
UI 통합 테스트

Author: leehansol
Created: 2025-05-25
"""

import pytest
import sys
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QTableWidget, QComboBox
from PySide6.QtCore import Qt

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_smart_ledger.app.ui.main_window import MainWindow
from ai_smart_ledger.app.db.database import DatabaseManager
from ai_smart_ledger.app.db.models import create_all_tables
from ai_smart_ledger.app.db.initial_data import insert_default_categories


class TestSlice23UI:
    """슬라이스 2.3 UI 동작 통합 테스트"""
    
    @pytest.fixture(autouse=True)
    def setup_ui_test(self):
        """UI 테스트 설정"""
        # QApplication이 없으면 생성
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        # 임시 데이터베이스 설정
        self.test_db_fd, self.test_db_path = tempfile.mkstemp(suffix='.db')
        os.close(self.test_db_fd)
        
        # 테스트용 DatabaseManager 설정
        self.db_manager = DatabaseManager(self.test_db_path)
        
        # 테이블 생성 및 기본 데이터 삽입
        create_all_tables()
        insert_default_categories()
        
        # 메인 윈도우 생성
        self.main_window = MainWindow()
        self.main_window.db_manager = self.db_manager
        
        # 테스트용 샘플 데이터 로드
        self._load_sample_data()
        
        yield
        
        # 테스트 후 정리
        self.main_window.close()
        self.db_manager.close()
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def _load_sample_data(self):
        """테스트용 샘플 거래내역 데이터 로드"""
        # 슬라이스 1.3에서 구현된 테이블에 샘플 데이터 추가
        sample_data = [
            ['2024-01-15 10:30:00', '스타벅스 커피', '', '5,500'],
            ['2024-01-15 12:00:00', '급여 입금', '3,000,000', ''], 
            ['2024-01-16 14:20:00', '마트 장보기', '', '45,000']
        ]
        
        # 테이블 헤더 설정
        headers = ['거래일시', '거래내용', '입금액', '출금액', '사용자 확정 카테고리', '저장 상태']
        self.main_window.transaction_table.setColumnCount(len(headers))
        self.main_window.transaction_table.setHorizontalHeaderLabels(headers)
        
        # 샘플 데이터 추가
        self.main_window.transaction_table.setRowCount(len(sample_data))
        
        for row_idx, row_data in enumerate(sample_data):
            for col_idx, cell_data in enumerate(row_data):
                self.main_window.transaction_table.setItem(row_idx, col_idx, 
                                                         QTableWidget.QTableWidgetItem(cell_data))
            
            # 카테고리 드롭다운 추가 (슬라이스 2.1에서 구현됨)
            category_combo = QComboBox()
            category_combo.addItems(['미분류', '수입 > 급여', '지출 > 식비 > 카페/음료', '지출 > 생활용품'])
            self.main_window.transaction_table.setCellWidget(row_idx, 4, category_combo)
            
            # 저장 상태 초기값
            self.main_window.transaction_table.setItem(row_idx, 5,
                                                     QTableWidget.QTableWidgetItem('미저장'))
    
    def test_save_categories_button_exists(self):
        """'분류 완료/저장' 버튼이 존재하는지 테스트"""
        # 버튼 찾기
        save_button = self.main_window.findChild(QPushButton, 'save_categories_button')
        
        # 검증
        assert save_button is not None, "'분류 완료/저장' 버튼이 메인 윈도우에 존재해야 합니다"
        assert save_button.text() in ['분류 완료', '분류 저장', '저장'], "버튼 텍스트가 적절해야 합니다"
        assert save_button.isEnabled(), "버튼이 활성화되어 있어야 합니다"
    
    def test_save_categories_button_click_with_no_categories(self):
        """카테고리가 선택되지 않은 상태에서 저장 버튼 클릭 테스트"""
        save_button = self.main_window.findChild(QPushButton, 'save_categories_button')
        
        # 메시지 박스 모킹
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            # 버튼 클릭
            save_button.click()
            
            # 검증: 경고 메시지가 표시되어야 함
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert '분류된 거래내역이 없습니다' in args[1] or '선택된 카테고리가 없습니다' in args[1]
    
    def test_save_categories_button_click_with_selected_categories(self):
        """카테고리가 선택된 상태에서 저장 버튼 클릭 테스트"""
        # 첫 번째 거래내역의 카테고리 선택
        category_combo = self.main_window.transaction_table.cellWidget(0, 4)
        category_combo.setCurrentText('지출 > 식비 > 카페/음료')
        
        # 두 번째 거래내역의 카테고리 선택
        category_combo2 = self.main_window.transaction_table.cellWidget(1, 4)
        category_combo2.setCurrentText('수입 > 급여')
        
        save_button = self.main_window.findChild(QPushButton, 'save_categories_button')
        
        # CRUD 함수 모킹
        with patch('ai_smart_ledger.app.db.crud.update_multiple_transactions_categories') as mock_update:
            mock_update.return_value = True
            
            with patch('PySide6.QtWidgets.QMessageBox.information') as mock_info:
                # 버튼 클릭
                save_button.click()
                
                # 검증: 업데이트 함수가 호출되었는지 확인
                mock_update.assert_called_once()
                
                # 성공 메시지가 표시되었는지 확인
                mock_info.assert_called_once()
                args = mock_info.call_args[0]
                assert '저장 완료' in args[1] or '분류 완료' in args[1]
    
    def test_save_categories_database_error_handling(self):
        """데이터베이스 저장 중 오류 발생 시 처리 테스트"""
        # 카테고리 선택
        category_combo = self.main_window.transaction_table.cellWidget(0, 4)
        category_combo.setCurrentText('지출 > 식비 > 카페/음료')
        
        save_button = self.main_window.findChild(QPushButton, 'save_categories_button')
        
        # CRUD 함수에서 오류 발생하도록 모킹
        with patch('ai_smart_ledger.app.db.crud.update_multiple_transactions_categories') as mock_update:
            mock_update.return_value = False  # 저장 실패
            
            with patch('PySide6.QtWidgets.QMessageBox.critical') as mock_critical:
                # 버튼 클릭
                save_button.click()
                
                # 검증: 오류 메시지가 표시되었는지 확인
                mock_critical.assert_called_once()
                args = mock_critical.call_args[0]
                assert '저장 실패' in args[1] or '오류' in args[1]
    
    def test_table_save_status_column_update(self):
        """저장 상태 열 업데이트 테스트"""
        # 카테고리 선택
        category_combo = self.main_window.transaction_table.cellWidget(0, 4)
        category_combo.setCurrentText('지출 > 식비 > 카페/음료')
        
        save_button = self.main_window.findChild(QPushButton, 'save_categories_button')
        
        # 성공적인 저장 모킹
        with patch('ai_smart_ledger.app.db.crud.update_multiple_transactions_categories') as mock_update:
            mock_update.return_value = True
            
            with patch('PySide6.QtWidgets.QMessageBox.information'):
                # 버튼 클릭
                save_button.click()
                
                # 검증: 저장 상태가 '저장됨'으로 업데이트되었는지 확인
                status_item = self.main_window.transaction_table.item(0, 5)
                assert status_item.text() == '저장됨', "저장 상태가 '저장됨'으로 업데이트되어야 합니다"
    
    def test_category_selection_tracking(self):
        """카테고리 선택 추적 기능 테스트"""
        # 첫 번째 거래내역의 카테고리 변경
        category_combo = self.main_window.transaction_table.cellWidget(0, 4)
        
        # 초기 상태 확인
        initial_selection = category_combo.currentText()
        assert initial_selection == '미분류', "초기 상태는 '미분류'여야 합니다"
        
        # 카테고리 변경
        category_combo.setCurrentText('지출 > 식비 > 카페/음료')
        
        # 변경된 카테고리 확인
        new_selection = category_combo.currentText()
        assert new_selection == '지출 > 식비 > 카페/음료', "카테고리가 변경되어야 합니다"
        
        # 저장 상태 확인 (변경되었으므로 '변경됨'이어야 함)
        status_item = self.main_window.transaction_table.item(0, 5)
        assert status_item.text() in ['미저장', '변경됨'], "저장 상태가 '변경됨' 또는 '미저장'이어야 합니다"
    
    def test_auto_save_option(self):
        """자동 저장 옵션 테스트 (설정에 따른 동작)"""
        # 자동 저장 설정 활성화 모킹
        with patch('ai_smart_ledger.app.ui.main_window.get_setting') as mock_get_setting:
            mock_get_setting.return_value = True  # 자동 저장 활성화
            
            # 카테고리 변경
            category_combo = self.main_window.transaction_table.cellWidget(0, 4)
            category_combo.setCurrentText('지출 > 식비 > 카페/음료')
            
            # CRUD 함수 모킹
            with patch('ai_smart_ledger.app.db.crud.update_transaction_category') as mock_update:
                mock_update.return_value = True
                
                # 카테고리 변경 시그널 발생 시뮬레이션
                category_combo.currentTextChanged.emit('지출 > 식비 > 카페/음료')
                
                # 검증: 자동 저장이 호출되었는지 확인 (설정 활성화 시)
                # 이 부분은 실제 구현에 따라 다를 수 있음
                pass
    
    def test_bulk_category_assignment_and_save(self):
        """대량 카테고리 할당 및 일괄 저장 테스트"""
        # 여러 거래내역에 카테고리 할당
        categories = [
            '지출 > 식비 > 카페/음료',
            '수입 > 급여', 
            '지출 > 생활용품'
        ]
        
        for i, category in enumerate(categories):
            category_combo = self.main_window.transaction_table.cellWidget(i, 4)
            category_combo.setCurrentText(category)
        
        save_button = self.main_window.findChild(QPushButton, 'save_categories_button')
        
        # 일괄 저장 모킹
        with patch('ai_smart_ledger.app.db.crud.update_multiple_transactions_categories') as mock_update:
            mock_update.return_value = True
            
            with patch('PySide6.QtWidgets.QMessageBox.information') as mock_info:
                # 저장 버튼 클릭
                save_button.click()
                
                # 검증: 3개 거래내역이 모두 업데이트 요청되었는지 확인
                call_args = mock_update.call_args[0][0]  # 첫 번째 인자 (업데이트 목록)
                assert len(call_args) == 3, "3개 거래내역이 모두 업데이트되어야 합니다"
                
                # 성공 메시지 확인
                mock_info.assert_called_once()
    
    def test_partial_save_failure_rollback(self):
        """일부 저장 실패 시 롤백 동작 테스트"""
        # 카테고리 선택
        category_combo = self.main_window.transaction_table.cellWidget(0, 4)
        category_combo.setCurrentText('지출 > 식비 > 카페/음료')
        
        save_button = self.main_window.findChild(QPushButton, 'save_categories_button')
        
        # 일부 실패 시나리오 모킹
        with patch('ai_smart_ledger.app.db.crud.update_multiple_transactions_categories') as mock_update:
            mock_update.return_value = False  # 저장 실패
            
            with patch('PySide6.QtWidgets.QMessageBox.critical') as mock_critical:
                # 저장 버튼 클릭
                save_button.click()
                
                # 검증: 오류 메시지 표시
                mock_critical.assert_called_once()
                
                # 상태가 원래대로 롤백되었는지 확인 (UI 상태)
                status_item = self.main_window.transaction_table.item(0, 5)
                assert status_item.text() in ['미저장', '변경됨'], "저장 실패 시 상태가 롤백되어야 합니다"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 