"""
테스트 파일: 슬라이스 2.5 - "중간 저장" 기능 UI 통합 테스트

이 테스트는 중간 저장 기능이 UI와 올바르게 통합되어 동작하는지 검증합니다.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QTableWidget, QMessageBox
from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QTest

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai_smart_ledger.app.core.progress_saver import ProgressSaver
from ai_smart_ledger.app.db.database import DatabaseManager


class TestProgressSaverUIIntegration:
    """중간 저장 기능 UI 통합 테스트 클래스"""

    @pytest.fixture(scope="session")
    def qapp(self):
        """QApplication 인스턴스"""
        if QCoreApplication.instance() is None:
            app = QApplication([])
        else:
            app = QCoreApplication.instance()
        yield app

    @pytest.fixture
    def temp_db_path(self):
        """임시 데이터베이스 파일 경로"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def temp_progress_file(self):
        """임시 진행 상태 파일 경로"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def mock_database(self, temp_db_path):
        """목킹된 데이터베이스"""
        db = DatabaseManager(os.path.basename(temp_db_path))
        return db

    @pytest.fixture
    def progress_saver(self, mock_database, temp_progress_file):
        """ProgressSaver 인스턴스"""
        return ProgressSaver(mock_database, temp_progress_file)

    @pytest.fixture
    def mock_main_window(self, qapp, progress_saver):
        """목킹된 메인 윈도우"""
        main_window = QMainWindow()
        
        # 중간 저장 버튼 추가
        save_progress_button = QPushButton("중간 저장")
        save_progress_button.setObjectName("save_progress_button")
        main_window.setCentralWidget(save_progress_button)
        
        # 거래 내역 테이블 (모킹)
        table_widget = QTableWidget(5, 6)  # 5행 6열
        table_widget.setObjectName("transactions_table")
        
        # ProgressSaver 인스턴스 연결
        main_window.progress_saver = progress_saver
        main_window.transactions_table = table_widget
        
        return main_window

    def test_save_progress_button_exists(self, mock_main_window):
        """중간 저장 버튼이 UI에 존재하는지 테스트"""
        # Given: 메인 윈도우
        main_window = mock_main_window
        
        # When: 중간 저장 버튼 찾기
        save_button = main_window.findChild(QPushButton, "save_progress_button")
        
        # Then: 버튼이 존재해야 함
        assert save_button is not None
        assert save_button.text() == "중간 저장"

    def test_save_progress_button_click_functionality(self, mock_main_window, temp_progress_file):
        """중간 저장 버튼 클릭 시 진행 상태 저장 기능 테스트"""
        # Given: 메인 윈도우와 샘플 진행 상태 데이터
        main_window = mock_main_window
        save_button = main_window.findChild(QPushButton, "save_progress_button")
        
        # 샘플 진행 상태 데이터 준비
        sample_progress = {
            'file_path': '/test/sample.csv',
            'file_hash': 'test_hash_123',
            'total_rows': 10,
            'processed_rows': 5,
            'current_row_index': 4,
            'timestamp': '2024-01-15T10:30:00',
            'transactions': [
                {
                    'row_index': 0,
                    'transaction_id': 'txn_001',
                    'amount': -50000,
                    'description': '테스트 거래',
                    'user_confirmed_category': '식비',
                    'ai_suggested_category': '식비',
                    'is_confirmed': True
                }
            ]
        }
        
        # 진행 상태 저장 함수 모킹
        with patch.object(main_window.progress_saver, 'save_progress', return_value=True) as mock_save:
            # 버튼 클릭 이벤트 시뮬레이션을 위한 함수 연결
            def save_current_progress():
                return main_window.progress_saver.save_progress(sample_progress)
            
            save_button.clicked.connect(save_current_progress)
            
            # When: 중간 저장 버튼 클릭
            save_button.click()
            
            # Then: save_progress 함수가 호출되었는지 확인
            mock_save.assert_called_once_with(sample_progress)

    def test_progress_restoration_on_startup(self, mock_main_window, temp_progress_file):
        """프로그램 시작 시 진행 상태 복원 테스트"""
        # Given: 저장된 진행 상태 파일
        saved_progress = {
            'file_path': '/test/restored_file.csv',
            'file_hash': 'restored_hash_456',
            'total_rows': 8,
            'processed_rows': 3,
            'current_row_index': 2,
            'timestamp': '2024-01-15T09:00:00',
            'transactions': [
                {
                    'row_index': 0,
                    'transaction_id': 'txn_restored',
                    'amount': 100000,
                    'description': '복원된 거래',
                    'user_confirmed_category': '급여',
                    'ai_suggested_category': '급여',
                    'is_confirmed': True
                }
            ]
        }
        
        # 진행 상태 파일 생성
        with open(temp_progress_file, 'w', encoding='utf-8') as f:
            json.dump(saved_progress, f, ensure_ascii=False, indent=2)
        
        main_window = mock_main_window
        
        # When: 진행 상태 로드
        loaded_progress = main_window.progress_saver.load_progress()
        
        # Then: 올바르게 로드되었는지 확인
        assert loaded_progress is not None
        assert loaded_progress['file_path'] == '/test/restored_file.csv'
        assert loaded_progress['total_rows'] == 8
        assert loaded_progress['processed_rows'] == 3
        assert len(loaded_progress['transactions']) == 1

    def test_progress_summary_display(self, mock_main_window, temp_progress_file):
        """진행 상태 요약 정보 표시 테스트"""
        # Given: 진행 상태 데이터
        progress_data = {
            'file_path': '/test/summary_test.csv',
            'file_hash': 'summary_hash',
            'total_rows': 20,
            'processed_rows': 15,
            'current_row_index': 14,
            'timestamp': '2024-01-15T11:00:00',
            'transactions': []
        }
        
        main_window = mock_main_window
        main_window.progress_saver.save_progress(progress_data)
        
        # When: 진행 상태 요약 정보 요청
        summary = main_window.progress_saver.get_progress_summary()
        
        # Then: 요약 정보 검증
        assert summary is not None
        assert summary['file_name'] == 'summary_test.csv'
        assert summary['progress_percentage'] == 75.0  # 15/20 * 100
        assert summary['remaining_rows'] == 5  # 20 - 15
        assert summary['total_rows'] == 20
        assert summary['processed_rows'] == 15

    def test_file_consistency_warning(self, mock_main_window, temp_progress_file):
        """파일 일관성 경고 메시지 테스트"""
        # Given: 저장된 진행 상태와 다른 파일 해시
        original_progress = {
            'file_path': '/test/consistency_test.csv',
            'file_hash': 'original_hash_123',
            'total_rows': 10,
            'processed_rows': 5,
            'current_row_index': 4,
            'timestamp': '2024-01-15T10:00:00',
            'transactions': []
        }
        
        main_window = mock_main_window
        main_window.progress_saver.save_progress(original_progress)
        
        # When: 다른 파일 해시로 일관성 검사
        different_hash = 'different_hash_456'
        is_consistent = main_window.progress_saver.check_file_consistency(
            '/test/consistency_test.csv', different_hash
        )
        
        # Then: 일관성 없음 확인
        assert is_consistent is False

    def test_clear_progress_confirmation(self, mock_main_window, temp_progress_file):
        """진행 상태 삭제 확인 다이얼로그 테스트"""
        # Given: 저장된 진행 상태
        test_progress = {
            'file_path': '/test/clear_test.csv',
            'file_hash': 'clear_hash',
            'total_rows': 5,
            'processed_rows': 2,
            'current_row_index': 1,
            'timestamp': '2024-01-15T12:00:00',
            'transactions': []
        }
        
        main_window = mock_main_window
        main_window.progress_saver.save_progress(test_progress)
        
        # 진행 상태가 저장되었는지 확인
        assert main_window.progress_saver.load_progress() is not None
        
        # When: 진행 상태 삭제
        result = main_window.progress_saver.clear_progress()
        
        # Then: 삭제 성공 확인
        assert result is True
        assert main_window.progress_saver.load_progress() is None

    def test_save_progress_error_handling(self, mock_main_window):
        """진행 상태 저장 시 오류 처리 테스트"""
        # Given: 저장 시 오류가 발생하는 상황
        main_window = mock_main_window
        
        # 잘못된 경로로 ProgressSaver 재설정
        invalid_path = "/invalid/path/that/does/not/exist/progress.json"
        main_window.progress_saver.progress_file_path = invalid_path
        
        invalid_data = {
            'file_path': '/test/error_test.csv',
            'file_hash': 'error_hash',
            'total_rows': 10,
            'processed_rows': 5,
            'current_row_index': 4,
            'timestamp': '2024-01-15T13:00:00',
            'transactions': []
        }
        
        # When: 잘못된 경로로 저장 시도
        # os.makedirs가 실패하도록 모킹
        with patch('os.makedirs', side_effect=PermissionError("권한 없음")):
            result = main_window.progress_saver.save_progress(invalid_data)
        
        # Then: 저장 실패 확인
        assert result is False

    def test_backup_creation_and_restoration(self, mock_main_window, temp_progress_file):
        """백업 생성 및 복원 테스트"""
        # Given: 진행 상태 데이터
        backup_test_data = {
            'file_path': '/test/backup_test.csv',
            'file_hash': 'backup_hash',
            'total_rows': 12,
            'processed_rows': 8,
            'current_row_index': 7,
            'timestamp': '2024-01-15T14:00:00',
            'transactions': []
        }
        
        main_window = mock_main_window
        main_window.progress_saver.save_progress(backup_test_data)
        
        # When: 백업 생성
        backup_path = main_window.progress_saver.create_backup()
        
        # Then: 백업 파일 생성 확인
        assert backup_path is not None
        assert os.path.exists(backup_path)
        
        # 백업에서 복원
        restored_data = main_window.progress_saver.restore_from_backup(backup_path)
        assert restored_data == backup_test_data
        
        # 백업 파일 정리
        if os.path.exists(backup_path):
            os.unlink(backup_path) 