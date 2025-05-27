#%%
#!/usr/bin/env python3
"""
AI 스마트 가계부 - 메인 실행 파일
Author: leehansol
Created: 2025-05-25
"""

import sys
from PySide6.QtWidgets import QApplication

# 데이터베이스 초기화 함수 import
from ai_smart_ledger.app.db.database import init_database, close_db_connection

# 메인 윈도우 import
from ai_smart_ledger.app.ui.main_window import MainWindow

def main():
    """메인 함수"""
    # 1. 데이터베이스 초기화
    print("=" * 50)
    print("🏦 AI 스마트 가계부를 시작합니다...")
    print("=" * 50)
    
    if not init_database():
        print("❌ 데이터베이스 초기화에 실패했습니다. 프로그램을 종료합니다.")
        return 1
    
    # 2. GUI 애플리케이션 시작
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    try:
        # 3. 애플리케이션 실행
        result = app.exec()
    finally:
        # 4. 프로그램 종료 시 데이터베이스 연결 정리
        print("\n" + "=" * 50)
        print("🔚 프로그램을 종료합니다...")
        close_db_connection()
        print("=" * 50)
    
    return result

if __name__ == "__main__":
    sys.exit(main())

# %%
