#!/usr/bin/env python3
"""
슬라이스 1.1 테스트: 파일 선택 및 경로 표시 기능
"""

import sys
from PySide6.QtWidgets import QApplication

# 데이터베이스 초기화 함수 import
from ai_smart_ledger.app.db.database import init_database, close_db_connection

# 메인 윈도우 import
from ai_smart_ledger.app.ui.main_window import MainWindow

def test_slice_1_1():
    """슬라이스 1.1 테스트 함수"""
    print("=" * 60)
    print("🧪 슬라이스 1.1 테스트: CSV 파일 선택 및 경로 표시")
    print("=" * 60)
    
    # 1. 데이터베이스 초기화
    print("1️⃣ 데이터베이스 초기화 중...")
    if not init_database():
        print("❌ 데이터베이스 초기화 실패")
        return False
    print("✅ 데이터베이스 초기화 완료")
    
    # 2. GUI 애플리케이션 시작
    print("2️⃣ GUI 애플리케이션 시작...")
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # 3. 테스트 포인트 확인
    print("3️⃣ 슬라이스 1.1 구현 요소 확인:")
    
    # 파일 핸들러 존재 확인
    print(f"   📁 파일 핸들러 초기화: {'✅' if hasattr(window, 'file_handler') else '❌'}")
    
    # 거래내역 화면 위젯 존재 확인
    print(f"   📊 거래내역 화면 위젯: {'✅' if hasattr(window, 'transactions_widget') else '❌'}")
    
    # 파일 불러오기 버튼 존재 확인
    print(f"   🔘 파일 불러오기 버튼: {'✅' if hasattr(window, 'load_file_button') else '❌'}")
    
    # 파일 경로 표시 레이블 존재 확인
    print(f"   🏷️ 파일 경로 표시 레이블: {'✅' if hasattr(window, 'file_path_label') else '❌'}")
    
    # 메뉴에서 파일 열기 기능 연결 확인
    print(f"   📋 메뉴 파일 열기 기능: {'✅' if hasattr(window, 'open_file_via_menu') else '❌'}")
    
    print("\n4️⃣ 화면 전환 테스트:")
    # 거래내역 화면으로 전환
    window.show_transactions_screen()
    current_index = window.central_widget.currentIndex()
    print(f"   📊 거래내역 화면 전환: {'✅' if current_index == window.SCREEN_TRANSACTIONS else '❌'}")
    
    # 5. 윈도우 표시
    window.show()
    print("\n5️⃣ 윈도우 표시 완료")
    print("\n💡 테스트 완료! 다음을 확인해보세요:")
    print("   - 메뉴 > 파일 > 거래내역 파일 열기... (Ctrl+O)")
    print("   - 메뉴 > 보기 > 거래내역")
    print("   - 거래내역 화면의 '📂 거래내역 파일 불러오기' 버튼")
    print("   - 파일 선택 시 경로 표시 레이블 업데이트")
    
    print("\n🚪 창을 닫으면 테스트가 종료됩니다.")
    
    try:
        # 애플리케이션 실행
        result = app.exec()
    finally:
        # 데이터베이스 연결 정리
        close_db_connection()
        print("\n🔚 테스트 종료")
    
    return True

if __name__ == "__main__":
    success = test_slice_1_1()
    sys.exit(0 if success else 1) 