#!/usr/bin/env python3
"""
AI 스마트 가계부 - 파일 처리 핸들러
Author: leehansol
Created: 2025-05-25

PRD 2.1 파일 입력 기능 구현
- CSV/Excel 파일 선택
- 파일 크기 및 형식 검증
"""

import os
from typing import Optional, Tuple
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget


class FileHandler:
    """파일 처리를 담당하는 클래스"""
    
    # 지원하는 파일 확장자
    SUPPORTED_EXTENSIONS = ['.csv', '.xls', '.xlsx']
    
    # 최대 파일 크기 (50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes
    
    def __init__(self):
        """초기화"""
        pass
    
    def select_file(self, parent: Optional[QWidget] = None) -> Optional[str]:
        """
        파일 선택 대화상자를 열어 CSV/Excel 파일 경로를 반환합니다.
        
        Args:
            parent: 부모 위젯 (선택적)
            
        Returns:
            선택된 파일 경로 (취소 시 None)
        """
        try:
            # 파일 필터 설정
            file_filter = "거래내역 파일 (*.csv *.xls *.xlsx);;CSV 파일 (*.csv);;Excel 파일 (*.xls *.xlsx);;모든 파일 (*.*)"
            
            # 파일 선택 대화상자 열기
            file_path, _ = QFileDialog.getOpenFileName(
                parent,
                "거래내역 파일 불러오기",
                "",  # 기본 디렉토리 (빈 문자열 = 현재 디렉토리)
                file_filter
            )
            
            # 사용자가 취소를 누른 경우
            if not file_path:
                print("📂 파일 선택이 취소되었습니다.")
                return None
            
            # 선택된 파일 경로 반환
            print(f"📂 파일 선택됨: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"❌ 파일 선택 중 오류 발생: {e}")
            if parent:
                QMessageBox.critical(
                    parent,
                    "파일 선택 오류",
                    f"파일 선택 중 오류가 발생했습니다:\n{str(e)}"
                )
            return None
    
    def validate_file(self, file_path: str, parent: Optional[QWidget] = None) -> Tuple[bool, str]:
        """
        선택된 파일의 유효성을 검증합니다.
        
        Args:
            file_path: 검증할 파일 경로
            parent: 부모 위젯 (오류 메시지 표시용)
            
        Returns:
            Tuple[bool, str]: (유효성 여부, 오류 메시지)
        """
        try:
            # 1. 파일 존재 여부 확인
            if not os.path.exists(file_path):
                error_msg = "선택한 파일이 존재하지 않습니다."
                self._show_error_message(parent, "파일 오류", error_msg)
                return False, error_msg
            
            # 2. 파일 확장자 확인
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.SUPPORTED_EXTENSIONS:
                error_msg = f"지원하지 않는 파일 형식입니다.\n지원 형식: {', '.join(self.SUPPORTED_EXTENSIONS)}"
                self._show_error_message(parent, "파일 형식 오류", error_msg)
                return False, error_msg
            
            # 3. 파일 크기 확인
            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_FILE_SIZE:
                size_mb = file_size / (1024 * 1024)
                max_mb = self.MAX_FILE_SIZE / (1024 * 1024)
                error_msg = f"파일 크기가 너무 큽니다.\n현재 크기: {size_mb:.1f}MB\n최대 허용 크기: {max_mb}MB"
                self._show_error_message(parent, "파일 크기 오류", error_msg)
                return False, error_msg
            
            # 4. 파일 읽기 권한 확인
            if not os.access(file_path, os.R_OK):
                error_msg = "파일을 읽을 수 있는 권한이 없습니다."
                self._show_error_message(parent, "파일 권한 오류", error_msg)
                return False, error_msg
            
            print(f"✅ 파일 검증 완료: {file_path}")
            return True, "파일이 유효합니다."
            
        except Exception as e:
            error_msg = f"파일 검증 중 오류가 발생했습니다: {str(e)}"
            self._show_error_message(parent, "검증 오류", error_msg)
            return False, error_msg
    
    def _show_error_message(self, parent: Optional[QWidget], title: str, message: str):
        """오류 메시지를 표시합니다."""
        print(f"❌ {title}: {message}")
        if parent:
            QMessageBox.critical(parent, title, message)
    
    def get_file_info(self, file_path: str) -> dict:
        """
        파일 정보를 반환합니다.
        
        Args:
            file_path: 파일 경로
            
        Returns:
            파일 정보 딕셔너리
        """
        try:
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_path)[1].lower()
            
            return {
                'path': file_path,
                'name': file_name,
                'extension': file_ext,
                'size_bytes': file_size,
                'size_mb': file_size / (1024 * 1024),
                'is_valid': file_ext in self.SUPPORTED_EXTENSIONS and file_size <= self.MAX_FILE_SIZE
            }
        except Exception as e:
            print(f"❌ 파일 정보 가져오기 실패: {e}")
            return {} 