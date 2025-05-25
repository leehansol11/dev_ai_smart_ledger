#!/usr/bin/env python3
"""
AI 스마트 가계부 - 메인 실행 파일
Author: leehansol
Created: 2025-05-25
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt

class AISmartLedgerMainWindow(QMainWindow):
    """AI 스마트 가계부 메인 창"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI 스마트 가계부 v1.0.0")
        self.setGeometry(100, 100, 800, 600)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 레이아웃 설정
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 환영 메시지
        welcome_label = QLabel("🏦 AI 스마트 가계부에 오신 것을 환영합니다!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(welcome_label)
        
        # 환경 정보 표시
        env_info_label = QLabel(f"""
        📍 개발 환경 설정 완료!
        
        🐍 Python: {sys.version.split()[0]}
        🖥️ PySide6: 설치 완료
        📊 openpyxl: 설치 완료  
        🌐 requests: 설치 완료
        📈 matplotlib: 설치 완료
        🐼 pandas: 설치 완료
        
        이제 개발을 시작할 준비가 되었습니다!
        """)
        env_info_label.setAlignment(Qt.AlignCenter)
        env_info_label.setStyleSheet("font-size: 14px; margin: 20px;")
        layout.addWidget(env_info_label)
        
        # 테스트 버튼
        test_button = QPushButton("환경 테스트 완료!")
        test_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;")
        test_button.clicked.connect(self.show_success_message)
        layout.addWidget(test_button)
        
    def show_success_message(self):
        """성공 메시지 표시"""
        QMessageBox.information(
            self, 
            "환경 설정 완료", 
            "🎉 AI 스마트 가계부 개발 환경이 성공적으로 설정되었습니다!\n\n이제 본격적인 개발을 시작할 수 있습니다."
        )

def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    window = AISmartLedgerMainWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
