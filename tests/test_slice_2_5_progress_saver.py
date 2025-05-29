"""
테스트 파일: 슬라이스 2.5 - "중간 저장" 기능 (분류 진행 상태)

이 테스트는 현재까지의 분류 작업 상태를 저장하고 나중에 이어할 수 있도록 하는 기능을 검증합니다.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai_smart_ledger.app.core.progress_saver import ProgressSaver
from ai_smart_ledger.app.db.database import DatabaseManager


class TestProgressSaver:
    """중간 저장 기능 테스트 클래스"""

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

    def test_progress_saver_initialization(self, progress_saver):
        """ProgressSaver 초기화 테스트"""
        assert progress_saver is not None
        assert hasattr(progress_saver, 'save_progress')
        assert hasattr(progress_saver, 'load_progress')
        assert hasattr(progress_saver, 'clear_progress')

    def test_save_basic_progress_data(self, progress_saver, temp_progress_file):
        """기본 진행 상태 데이터 저장 테스트"""
        # Given: 분류 진행 상태 데이터
        progress_data = {
            'file_path': '/path/to/transactions.csv',
            'file_hash': 'abc123',
            'total_rows': 10,
            'processed_rows': 5,
            'current_row_index': 4,
            'timestamp': '2024-01-15T10:30:00',
            'transactions': [
                {
                    'row_index': 0,
                    'transaction_id': 'txn_001',
                    'amount': -50000,
                    'description': '카페 결제',
                    'user_confirmed_category': '식비',
                    'ai_suggested_category': '식비',
                    'is_confirmed': True
                },
                {
                    'row_index': 1,
                    'transaction_id': 'txn_002',
                    'amount': -30000,
                    'description': '주유소',
                    'user_confirmed_category': None,
                    'ai_suggested_category': '교통비',
                    'is_confirmed': False
                }
            ]
        }

        # When: 진행 상태 저장
        result = progress_saver.save_progress(progress_data)

        # Then: 저장 성공 확인
        assert result is True
        assert os.path.exists(temp_progress_file)
        
        # 저장된 내용 검증
        with open(temp_progress_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data['file_path'] == progress_data['file_path']
        assert saved_data['total_rows'] == progress_data['total_rows']
        assert saved_data['processed_rows'] == progress_data['processed_rows']
        assert len(saved_data['transactions']) == 2

    def test_load_existing_progress_data(self, progress_saver, temp_progress_file):
        """기존 진행 상태 데이터 로드 테스트"""
        # Given: 미리 저장된 진행 상태 파일
        existing_data = {
            'file_path': '/path/to/saved_transactions.csv',
            'file_hash': 'def456',
            'total_rows': 8,
            'processed_rows': 3,
            'current_row_index': 2,
            'timestamp': '2024-01-15T09:15:00',
            'transactions': [
                {
                    'row_index': 0,
                    'transaction_id': 'txn_003',
                    'amount': 1000000,
                    'description': '급여',
                    'user_confirmed_category': '급여',
                    'ai_suggested_category': '급여',
                    'is_confirmed': True
                }
            ]
        }
        
        with open(temp_progress_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        # When: 진행 상태 로드
        loaded_data = progress_saver.load_progress()

        # Then: 로드된 데이터 검증
        assert loaded_data is not None
        assert loaded_data['file_path'] == existing_data['file_path']
        assert loaded_data['total_rows'] == existing_data['total_rows']
        assert loaded_data['processed_rows'] == existing_data['processed_rows']
        assert len(loaded_data['transactions']) == 1
        assert loaded_data['transactions'][0]['description'] == '급여'

    def test_load_progress_when_file_not_exists(self, progress_saver):
        """진행 상태 파일이 없을 때 로드 테스트"""
        # Given: 진행 상태 파일이 없는 상황
        
        # When: 진행 상태 로드 시도
        loaded_data = progress_saver.load_progress()

        # Then: None 반환 확인
        assert loaded_data is None

    def test_clear_progress_data(self, progress_saver, temp_progress_file):
        """진행 상태 데이터 삭제 테스트"""
        # Given: 저장된 진행 상태 파일
        test_data = {'test': 'data'}
        with open(temp_progress_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        assert os.path.exists(temp_progress_file)

        # When: 진행 상태 삭제
        result = progress_saver.clear_progress()

        # Then: 파일 삭제 확인
        assert result is True
        assert not os.path.exists(temp_progress_file)

    def test_save_progress_with_invalid_data(self, progress_saver):
        """잘못된 데이터로 저장 시도 테스트"""
        # Given: 잘못된 진행 상태 데이터
        invalid_data = None

        # When & Then: 예외 발생 확인
        with pytest.raises((TypeError, ValueError)):
            progress_saver.save_progress(invalid_data)

    def test_progress_data_validation(self, progress_saver):
        """진행 상태 데이터 유효성 검증 테스트"""
        # Given: 필수 필드가 누락된 데이터
        incomplete_data = {
            'file_path': '/path/to/file.csv',
            # 'total_rows' 누락
            'processed_rows': 5
        }

        # When & Then: 유효성 검증 실패 확인
        with pytest.raises(ValueError, match="필수 필드가 누락되었습니다"):
            progress_saver.validate_progress_data(incomplete_data)

    def test_file_hash_consistency_check(self, progress_saver, temp_progress_file):
        """파일 해시 일관성 검사 테스트"""
        # Given: 저장된 진행 상태 (특정 파일 해시)
        original_data = {
            'file_path': '/path/to/file.csv',
            'file_hash': 'original_hash_123',
            'total_rows': 10,
            'processed_rows': 5,
            'current_row_index': 4,
            'timestamp': '2024-01-15T10:30:00',
            'transactions': []
        }
        
        with open(temp_progress_file, 'w', encoding='utf-8') as f:
            json.dump(original_data, f, ensure_ascii=False)

        # When: 다른 파일 해시로 일관성 검사
        current_file_hash = 'different_hash_456'
        is_consistent = progress_saver.check_file_consistency(
            '/path/to/file.csv', current_file_hash
        )

        # Then: 일관성 없음 확인
        assert is_consistent is False

    def test_progress_backup_and_restore(self, progress_saver, temp_progress_file):
        """진행 상태 백업 및 복원 테스트"""
        # Given: 원본 진행 상태 데이터
        original_data = {
            'file_path': '/path/to/file.csv',
            'file_hash': 'hash123',
            'total_rows': 10,
            'processed_rows': 7,
            'current_row_index': 6,
            'timestamp': '2024-01-15T10:30:00',
            'transactions': []
        }
        
        progress_saver.save_progress(original_data)

        # When: 백업 생성
        backup_path = progress_saver.create_backup()
        
        # Then: 백업 파일 생성 확인
        assert backup_path is not None
        assert os.path.exists(backup_path)
        
        # 백업에서 복원
        restored_data = progress_saver.restore_from_backup(backup_path)
        assert restored_data == original_data
        
        # 백업 파일 정리
        if os.path.exists(backup_path):
            os.unlink(backup_path)

    def test_get_progress_summary(self, progress_saver, temp_progress_file):
        """진행 상태 요약 정보 테스트"""
        # Given: 진행 상태 데이터
        progress_data = {
            'file_path': '/path/to/transactions.csv',
            'file_hash': 'abc123',
            'total_rows': 20,
            'processed_rows': 12,
            'current_row_index': 11,
            'timestamp': '2024-01-15T10:30:00',
            'transactions': []
        }
        
        progress_saver.save_progress(progress_data)

        # When: 진행 상태 요약 정보 요청
        summary = progress_saver.get_progress_summary()

        # Then: 요약 정보 검증
        assert summary is not None
        assert summary['file_name'] == 'transactions.csv'
        assert summary['progress_percentage'] == 60.0  # 12/20 * 100
        assert summary['remaining_rows'] == 8  # 20 - 12
        assert 'last_saved_time' in summary

    def test_merge_progress_data(self, progress_saver):
        """진행 상태 데이터 병합 테스트"""
        # Given: 기존 진행 상태와 새로운 진행 상태
        existing_progress = {
            'file_path': '/path/to/file.csv',
            'total_rows': 10,
            'processed_rows': 5,
            'transactions': [
                {'row_index': 0, 'is_confirmed': True},
                {'row_index': 1, 'is_confirmed': False}
            ]
        }
        
        new_progress = {
            'processed_rows': 7,
            'transactions': [
                {'row_index': 1, 'is_confirmed': True},  # 업데이트
                {'row_index': 2, 'is_confirmed': True}   # 새로 추가
            ]
        }

        # When: 진행 상태 병합
        merged = progress_saver.merge_progress_data(existing_progress, new_progress)

        # Then: 병합 결과 검증
        assert merged['processed_rows'] == 7
        assert len(merged['transactions']) == 3
        # row_index 1번 거래의 is_confirmed가 True로 업데이트되었는지 확인
        updated_transaction = next(
            (t for t in merged['transactions'] if t['row_index'] == 1), None
        )
        assert updated_transaction['is_confirmed'] is True 