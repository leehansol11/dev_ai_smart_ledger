"""
진행 상태 저장 모듈 (Progress Saver)

분류 작업의 진행 상태를 저장하고 복원하는 기능을 제공합니다.
- JSON 파일을 통한 진행 상태 저장/로드
- 파일 해시를 통한 일관성 검증
- 백업 및 복원 기능
- 진행 상태 데이터 유효성 검증
"""

import json
import os
import hashlib
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class ProgressSaver:
    """분류 진행 상태 저장 및 관리 클래스"""
    
    def __init__(self, database, progress_file_path: str):
        """
        ProgressSaver 초기화
        
        Args:
            database: 데이터베이스 인스턴스
            progress_file_path: 진행 상태를 저장할 JSON 파일 경로
        """
        self.database = database
        self.progress_file_path = progress_file_path
        self.required_fields = [
            'file_path', 'file_hash', 'total_rows', 'processed_rows', 
            'current_row_index', 'timestamp', 'transactions'
        ]
    
    def save_progress(self, progress_data: Dict[str, Any]) -> bool:
        """
        현재 분류 진행 상태를 JSON 파일에 저장
        
        Args:
            progress_data: 저장할 진행 상태 데이터
            
        Returns:
            bool: 저장 성공 여부
            
        Raises:
            TypeError: progress_data가 None인 경우
            ValueError: 필수 필드가 누락된 경우
        """
        if progress_data is None:
            raise TypeError("progress_data는 None일 수 없습니다")
        
        # 데이터 유효성 검증
        self.validate_progress_data(progress_data)
        
        try:
            # 진행 상태 파일의 디렉토리가 없으면 생성
            os.makedirs(os.path.dirname(self.progress_file_path), exist_ok=True)
            
            # JSON 파일로 저장
            with open(self.progress_file_path, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"진행 상태 저장 중 오류 발생: {e}")
            return False
    
    def load_progress(self) -> Optional[Dict[str, Any]]:
        """
        저장된 분류 진행 상태를 JSON 파일에서 로드
        
        Returns:
            Optional[Dict]: 로드된 진행 상태 데이터, 파일이 없으면 None
        """
        if not os.path.exists(self.progress_file_path):
            return None
        
        try:
            with open(self.progress_file_path, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
            
            return progress_data
            
        except Exception as e:
            print(f"진행 상태 로드 중 오류 발생: {e}")
            return None
    
    def clear_progress(self) -> bool:
        """
        저장된 진행 상태 파일을 삭제
        
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if os.path.exists(self.progress_file_path):
                os.unlink(self.progress_file_path)
            return True
            
        except Exception as e:
            print(f"진행 상태 파일 삭제 중 오류 발생: {e}")
            return False
    
    def validate_progress_data(self, progress_data: Dict[str, Any]) -> None:
        """
        진행 상태 데이터의 유효성을 검증
        
        Args:
            progress_data: 검증할 진행 상태 데이터
            
        Raises:
            ValueError: 필수 필드가 누락된 경우
        """
        missing_fields = []
        for field in self.required_fields:
            if field not in progress_data:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}")
    
    def check_file_consistency(self, file_path: str, current_file_hash: str) -> bool:
        """
        저장된 진행 상태와 현재 파일의 일관성을 검사
        
        Args:
            file_path: 현재 파일 경로
            current_file_hash: 현재 파일의 해시값
            
        Returns:
            bool: 일관성 여부 (True: 일관성 있음, False: 일관성 없음)
        """
        progress_data = self.load_progress()
        
        if not progress_data:
            return False
        
        return (progress_data.get('file_path') == file_path and 
                progress_data.get('file_hash') == current_file_hash)
    
    def create_backup(self) -> Optional[str]:
        """
        현재 진행 상태 파일의 백업을 생성
        
        Returns:
            Optional[str]: 백업 파일 경로, 실패 시 None
        """
        if not os.path.exists(self.progress_file_path):
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.progress_file_path}.backup_{timestamp}"
            shutil.copy2(self.progress_file_path, backup_path)
            return backup_path
            
        except Exception as e:
            print(f"백업 생성 중 오류 발생: {e}")
            return None
    
    def restore_from_backup(self, backup_path: str) -> Optional[Dict[str, Any]]:
        """
        백업 파일에서 진행 상태를 복원
        
        Args:
            backup_path: 백업 파일 경로
            
        Returns:
            Optional[Dict]: 복원된 진행 상태 데이터, 실패 시 None
        """
        if not os.path.exists(backup_path):
            return None
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            return backup_data
            
        except Exception as e:
            print(f"백업 복원 중 오류 발생: {e}")
            return None
    
    def get_progress_summary(self) -> Optional[Dict[str, Any]]:
        """
        현재 진행 상태의 요약 정보를 반환
        
        Returns:
            Optional[Dict]: 진행 상태 요약 정보, 데이터가 없으면 None
        """
        progress_data = self.load_progress()
        
        if not progress_data:
            return None
        
        file_path = progress_data.get('file_path', '')
        file_name = os.path.basename(file_path)
        total_rows = progress_data.get('total_rows', 0)
        processed_rows = progress_data.get('processed_rows', 0)
        
        progress_percentage = (processed_rows / total_rows * 100) if total_rows > 0 else 0
        remaining_rows = max(0, total_rows - processed_rows)
        
        summary = {
            'file_name': file_name,
            'progress_percentage': progress_percentage,
            'remaining_rows': remaining_rows,
            'total_rows': total_rows,
            'processed_rows': processed_rows,
            'last_saved_time': progress_data.get('timestamp', '')
        }
        
        return summary
    
    def merge_progress_data(self, existing_progress: Dict[str, Any], 
                          new_progress: Dict[str, Any]) -> Dict[str, Any]:
        """
        기존 진행 상태와 새로운 진행 상태를 병합
        
        Args:
            existing_progress: 기존 진행 상태 데이터
            new_progress: 새로운 진행 상태 데이터
            
        Returns:
            Dict: 병합된 진행 상태 데이터
        """
        merged = existing_progress.copy()
        
        # 기본 필드 업데이트
        for key, value in new_progress.items():
            if key != 'transactions':
                merged[key] = value
        
        # transactions 데이터 병합 (row_index 기준)
        if 'transactions' in new_progress:
            existing_transactions = {
                t['row_index']: t for t in merged.get('transactions', [])
            }
            
            # 새로운 거래 데이터로 업데이트/추가
            for new_transaction in new_progress['transactions']:
                row_index = new_transaction['row_index']
                existing_transactions[row_index] = new_transaction
            
            # 정렬된 리스트로 변환
            merged['transactions'] = sorted(
                existing_transactions.values(), 
                key=lambda x: x['row_index']
            )
        
        return merged 