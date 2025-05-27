#!/usr/bin/env python3
"""
슬라이스 1.3 테스트: CSV 데이터를 메인 창 테이블 위젯에 표시
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QTableWidget
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

# 데이터베이스 초기화 함수 import
from ai_smart_ledger.app.db.database import init_database, close_db_connection

# 메인 윈도우 import
from ai_smart_ledger.app.ui.main_window import MainWindow

def test_slice_1_3():
    """슬라이스 1.3 대화형 테스트 함수"""
    print("=" * 60)
    print("🧪 슬라이스 1.3 테스트: CSV 데이터를 메인 창 테이블에 표시")
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
    
    # 3. GUI 애플리케이션 시작
    print("3️⃣ GUI 애플리케이션 시작...")
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # 4. 슬라이스 1.3 구현 요소 확인
    print("4️⃣ 슬라이스 1.3 구현 요소 확인:")
    
    # 거래내역 화면으로 전환
    window.show_transactions_screen()
    
    # 현재 화면의 위젯 가져오기
    current_widget = window.central_widget.currentWidget()
    
    # QTableWidget 존재 확인
    table_widget = None
    if hasattr(window, 'transactions_table'):
        table_widget = window.transactions_table
        print(f"   📊 거래내역 테이블 위젯: ✅")
    else:
        print(f"   📊 거래내역 테이블 위젯: ❌")
    
    # 테이블에 데이터 표시 메서드 확인
    display_method_exists = hasattr(window, 'display_csv_data_in_table')
    print(f"   🔧 테이블 데이터 표시 메서드: {'✅' if display_method_exists else '❌'}")
    
    # 5. 샘플 데이터 처리 및 테이블 표시 테스트
    print("5️⃣ 샘플 데이터 처리 및 테이블 표시 테스트:")
    
    try:
        # 파일 검증
        is_valid, message = window.file_handler.validate_file(sample_file, None)
        print(f"   📁 파일 검증: {'✅' if is_valid else '❌'} - {message}")
        
        if is_valid:
            # 파일 선택 시뮬레이션
            window.selected_file_path = sample_file
            window.file_path_label.setText(f"📁 선택된 파일: {sample_file}")
            
            # 파싱 실행
            print("   🔍 파싱 실행 중...")
            window.parse_and_display_preview(sample_file)
            
            # 테이블에 데이터가 표시되었는지 확인
            if table_widget and table_widget.rowCount() > 0:
                print(f"   📊 테이블 데이터 표시: ✅ ({table_widget.rowCount()}행, {table_widget.columnCount()}열)")
                
                # 헤더 확인
                headers = []
                for col in range(table_widget.columnCount()):
                    header_item = table_widget.horizontalHeaderItem(col)
                    if header_item:
                        headers.append(header_item.text())
                print(f"   📋 테이블 헤더: {headers}")
                
                # 첫 번째 행 데이터 확인
                if table_widget.rowCount() > 0:
                    first_row = []
                    for col in range(table_widget.columnCount()):
                        item = table_widget.item(0, col)
                        if item:
                            first_row.append(item.text())
                    print(f"   📝 첫 번째 행: {first_row}")
                    
            else:
                print("   📊 테이블 데이터 표시: ❌")
        
    except Exception as e:
        print(f"   ❌ 테스트 중 오류: {e}")
        return False
    
    # 6. 윈도우 표시
    window.show()
    print("6️⃣ 윈도우 표시 완료")
    
    print("\n💡 테스트 완료! 다음을 확인해보세요:")
    print("   - 거래내역 화면에 QTableWidget이 추가되었는지")
    print("   - CSV 파일 선택 시 테이블에 데이터가 표시되는지")
    print("   - 헤더와 첫 5행이 올바르게 표시되는지")
    print("   - 테이블 위젯이 적절한 크기와 레이아웃을 갖는지")
    
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
    test_slice_1_3() 