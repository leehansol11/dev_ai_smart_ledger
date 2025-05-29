import sys
from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout, 
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QMessageBox)
from PySide6.QtCore import Qt

# 프로젝트 루트 디렉토리를 기준으로 app 디렉토리를 sys.path에 추가
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.crud import save_setting, get_setting

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("설정")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)

        # API 키 입력 섹션
        api_key_layout = QHBoxLayout()
        self.api_key_label = QLabel("ChatGPT API 키:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("여기에 API 키를 입력하세요")
        api_key_layout.addWidget(self.api_key_label)
        api_key_layout.addWidget(self.api_key_input)

        self.layout.addLayout(api_key_layout)

        # 저장 버튼
        self.save_button = QPushButton("저장")
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)

        # 현재 API 키 불러오기
        self.load_settings()

    def load_settings(self):
        """
        저장된 설정 값을 불러와 UI에 표시합니다.
        """
        api_key = get_setting("chatgpt_api_key")
        if api_key:
            self.api_key_input.setText(api_key)

    def save_settings(self):
        """
        UI에 입력된 설정 값을 저장합니다.
        """
        api_key = self.api_key_input.text()
        
        if save_setting("chatgpt_api_key", api_key):
            QMessageBox.information(self, "성공", "설정 값이 저장되었습니다.")
        else:
            QMessageBox.critical(self, "오류", "설정 값 저장 중 오류가 발생했습니다.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.exec()
    sys.exit(app.exec()) 