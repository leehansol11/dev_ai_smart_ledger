#!/usr/bin/env python3
"""
슬라이스 1.2 테스트: CSV 파일 내용 파싱 및 콘솔 출력
"""

import sys
import os
from PySide6.QtWidgets import QApplication

# 데이터베이스 초기화 함수 import
from ai_smart_ledger.app.db.database import init_database, close_db_connection

# 메인 윈도우 및 파서 import
from ai_smart_ledger.app.ui.main_window import MainWindow
from ai_smart_ledger.app.core.file_parser import FileParser

def test_slice_1_2():
    """슬라이스 1.2 테스트 함수"""
    print("=" * 60)
    print("🧪 슬라이스 1.2 테스트: CSV 파일 내용 파싱 및 콘솔 출력")
    print("=" * 60)
    
    # 1. 데이터베이스 초기화
    print("1️⃣ 데이터베이스 초기화 중...")
    if not init_database():
        print("❌ 데이터베이스 초기화 실패")
        return False
    print("✅ 데이터베이스 초기화 완료")
    
    # 2. 샘플 CSV 파일 확인
    sample_file = "sample_transactions.csv"
    if not os.path.exists(sample_file):
        print(f"❌ 샘플 파일이 없습니다: {sample_file}")
        return False
    
    print(f"2️⃣ 샘플 CSV 파일 확인: {sample_file} ✅")
    
    # 3. 파일 파서 직접 테스트
    print("3️⃣ 파일 파서 직접 테스트:")
    parser = FileParser()
    
    # 샘플 파일 파싱
    result = parser.parse_csv_preview(sample_file, max_rows=5)
    
    if result['success']:
        print("✅ 파싱 성공!")
        parser.print_csv_preview(result)
    else:
        print(f"❌ 파싱 실패: {result['error']}")
        return False
    
    # 4. GUI 애플리케이션 테스트
    print("4️⃣ GUI 애플리케이션 통합 테스트:")
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # 파일 파서가 연결되었는지 확인
    print(f"   📄 파일 파서 연결: {'✅' if hasattr(window, 'file_parser') else '❌'}")
    print(f"   🔍 파싱 함수 존재: {'✅' if hasattr(window, 'parse_and_display_preview') else '❌'}")
    
    # 5. 샘플 파일을 직접 처리해보기
    print("5️⃣ 샘플 파일 직접 처리 테스트:")
    try:
        # 파일 검증
        is_valid, message = window.file_handler.validate_file(sample_file, None)
        print(f"   📁 파일 검증: {'✅' if is_valid else '❌'} - {message}")
        
        if is_valid:
            # 파일 경로 설정
            window.selected_file_path = sample_file
            
            # 파싱 및 미리보기 실행
            print("   🔍 파싱 실행 중...")
            window.parse_and_display_preview(sample_file)
            print("   ✅ 파싱 완료!")
        
    except Exception as e:
        print(f"   ❌ 테스트 중 오류: {e}")
        return False
    
    # 6. 윈도우 표시 (선택사항)
    print("6️⃣ 윈도우 표시 (파일 선택 테스트 가능):")
    window.show_transactions_screen()  # 거래내역 화면으로 전환
    window.show()
    
    print("\n💡 테스트 완료! 다음을 확인해보세요:")
    print("   - 콘솔에 출력된 CSV 파싱 결과")
    print("   - GUI에서 파일 선택 시 콘솔 출력")
    print("   - 파일 선택 후 파싱 자동 실행")
    
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
    success = test_slice_1_2()
    sys.exit(0 if success else 1) 