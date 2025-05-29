#!/usr/bin/env python3
"""
AI 스마트 가계부 - 메인 윈도우
Author: leehansol
Created: 2025-05-25
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget, 
    QMenuBar, QMenu, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QHeaderView, QDialog,
    QTextEdit, QDialogButtonBox, QScrollArea, QComboBox, QListView,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont, QPixmap
import os
import hashlib
from datetime import datetime

from ..core.file_handler import FileHandler
from ..core.file_parser import FileParser
from ..core.progress_saver import ProgressSaver
from ..db.crud import get_categories_for_dropdown, get_setting
from ..db.database import DatabaseManager
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """AI 스마트 가계부 메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        
        # 슬라이스 1.1: 파일 핸들러 초기화
        self.file_handler = FileHandler()
        
        # 슬라이스 1.2: 파일 파서 초기화
        self.file_parser = FileParser()
        
        # 슬라이스 2.5: 중간 저장 기능 초기화
        self.database_manager = DatabaseManager()
        progress_file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'progress.json')
        self.progress_saver = ProgressSaver(self.database_manager, progress_file_path)
        
        # 현재 선택된 파일 경로 저장
        self.selected_file_path = None
        
        # 슬라이스 2.5: 현재 파일 해시 저장 (파일 일관성 검증용)
        self.current_file_hash = None
        
        # 슬라이스 1.3: 거래내역 테이블 위젯 초기화
        self.transactions_table = None
        
        # 슬라이스 2.2: 카테고리 선택 정보 저장용 딕셔너리 (행 번호 -> 카테고리명)
        self.transaction_categories = {}
        
        # 슬라이스 2.4: 실행 취소 기능을 위한 카테고리 변경 히스토리 스택
        self.category_change_history = []
        self.max_history_size = 10  # 메모리 관리를 위한 히스토리 크기 제한
        
        # 슬라이스 2.4: 실행 취소 버튼 (나중에 초기화됨)
        self.undo_button = None
        
        # 슬라이스 2.5: 중간 저장 버튼 (나중에 초기화됨)
        self.save_progress_button = None

        # 슬라이스 3.1: 프로그램 시작 시 저장된 API 키 로드
        self.api_key = get_setting("chatgpt_api_key")
        if self.api_key:
            print("✅ 프로그램 시작 시 API 키 로드 완료")
        else:
            print("⚠️ 저장된 API 키가 없습니다. 설정에서 입력해주세요.")
        
        self.init_ui()
        
        # 슬라이스 2.5: 프로그램 시작 시 저장된 진행 상태가 있는지 확인
        self.check_and_restore_progress_on_startup()
        
    def init_ui(self):
        """UI 초기화"""
        # 59번: 프로그램 제목 설정 ("AI 스마트 가계부")
        self.setWindowTitle("AI 스마트 가계부")
        
        # 기본 윈도우 크기 및 위치 설정
        self.setGeometry(100, 100, 1200, 800)
        
        # 60번: 기본 메뉴 바 구조 생성 (파일, 보기, 도구, 도움말)
        self.create_menu_bar()
        
        # 61번: 주요 화면 영역을 위한 중앙 위젯 레이아웃 설정
        self.setup_central_layout()
        
        # 초기 화면 설정
        self.show_welcome_screen()
        
    def setup_central_layout(self):
        """61번: 주요 화면 영역을 위한 중앙 위젯 레이아웃 설정"""
        # QStackedWidget을 중앙 위젯으로 설정 (화면 전환 준비)
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        # 화면 식별자 상수 정의
        self.SCREEN_WELCOME = 0
        self.SCREEN_TRANSACTIONS = 1
        self.SCREEN_DASHBOARD = 2
        self.SCREEN_SETTINGS = 3
        
        # 각 화면 위젯들을 미리 생성
        self.welcome_widget = self.create_welcome_screen()
        self.transactions_widget = self.create_transactions_screen()  # 슬라이스 1.3: 거래내역 화면 구현
        # self.dashboard_widget = self.create_dashboard_screen()        # 나중에 구현
        # self.settings_widget = self.create_settings_screen()          # 나중에 구현
        
        # 스택에 화면들 추가
        self.central_widget.addWidget(self.welcome_widget)  # 인덱스 0
        self.central_widget.addWidget(self.transactions_widget)  # 인덱스 1: 슬라이스 1.3
        # self.central_widget.addWidget(self.dashboard_widget)     # 인덱스 2 (나중에)
        # self.central_widget.addWidget(self.settings_widget)      # 인덱스 3 (나중에)
        
        print("✅ 중앙 위젯 레이아웃 설정 완료 - QStackedWidget 기반 화면 전환 시스템 준비됨")
    
    def show_welcome_screen(self):
        """환영 화면으로 전환"""
        self.central_widget.setCurrentIndex(self.SCREEN_WELCOME)
        print("🏠 환영 화면으로 전환")
    
    def show_transactions_screen(self):
        """거래내역 화면으로 전환"""
        self.central_widget.setCurrentIndex(self.SCREEN_TRANSACTIONS)
        print("📊 거래내역 화면으로 전환")
    
    def show_dashboard_screen(self):
        """대시보드 화면으로 전환 (향후 구현)"""
        # self.central_widget.setCurrentIndex(self.SCREEN_DASHBOARD)
        print("📈 대시보드 화면 (아직 구현되지 않음)")
    
    def show_settings_screen(self):
        """설정 화면으로 전환 (향후 구현)"""
        # self.central_widget.setCurrentIndex(self.SCREEN_SETTINGS)
        print("⚙️ 설정 화면 (아직 구현되지 않음)")
        
    def create_welcome_screen(self):
        """환영 화면 위젯 생성 및 반환"""
        welcome_widget = QWidget()
        layout = QVBoxLayout()
        welcome_widget.setLayout(layout)
        
        # 환영 메시지
        welcome_label = QLabel("🏦 AI 스마트 가계부")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            margin: 50px;
            color: #2c3e50;
        """)
        layout.addWidget(welcome_label)
        
        # 설명 텍스트
        description_label = QLabel("지능형 가계부 관리 시스템")
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setStyleSheet("""
            font-size: 16px; 
            color: #7f8c8d;
            margin-bottom: 30px;
        """)
        layout.addWidget(description_label)
        
        # 화면 전환 테스트 정보 추가
        info_label = QLabel("💡 화면 전환 시스템이 준비되었습니다!\n메뉴를 통해 다른 화면으로 이동할 수 있습니다.")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            font-size: 14px; 
            color: #95a5a6;
            margin-top: 20px;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 8px;
        """)
        layout.addWidget(info_label)
        
        # 슬라이스 1.1: "거래내역 파일 불러오기" 버튼 추가
        self.load_file_button = QPushButton("📁 거래내역 파일 불러오기")
        self.load_file_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 15px 30px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                margin: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        layout.addWidget(self.load_file_button)
        
        # 슬라이스 1.1: 버튼 클릭 이벤트 연결
        self.load_file_button.clicked.connect(self.on_load_file_clicked)
        
        # 슬라이스 1.1: 선택된 파일 경로를 표시할 레이블 추가
        self.file_path_label = QLabel("파일을 선택해주세요.")
        self.file_path_label.setAlignment(Qt.AlignCenter)
        self.file_path_label.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            padding: 10px;
            margin: 10px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
        """)
        layout.addWidget(self.file_path_label)
        
        return welcome_widget
    
    def create_transactions_screen(self):
        """슬라이스 1.3: 거래내역 화면 위젯 생성 및 반환"""
        transactions_widget = QWidget()
        layout = QVBoxLayout()
        transactions_widget.setLayout(layout)
        
        # 제목
        title_label = QLabel("📊 거래내역 관리")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            margin: 20px;
            color: #2c3e50;
        """)
        layout.addWidget(title_label)
        
        # 파일 정보 영역
        file_info_layout = QHBoxLayout()
        
        # 파일 불러오기 버튼
        self.transactions_load_button = QPushButton("📁 거래내역 파일 불러오기")
        self.transactions_load_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.transactions_load_button.clicked.connect(self.on_load_file_clicked)
        file_info_layout.addWidget(self.transactions_load_button)
        
        # 슬라이스 2.4: 실행 취소 버튼 추가
        self.undo_button = QPushButton("⏪ 실행 취소")
        self.undo_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.undo_button.clicked.connect(self.on_undo_button_clicked)
        self.undo_button.setEnabled(False)  # 초기에는 비활성화
        file_info_layout.addWidget(self.undo_button)
        
        # 슬라이스 2.5: 중간 저장 버튼 추가
        self.save_progress_button = QPushButton("💾 중간 저장")
        self.save_progress_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.save_progress_button.clicked.connect(self.on_save_progress_clicked)
        self.save_progress_button.setEnabled(False)  # 파일이 로드되기 전까지는 비활성화
        file_info_layout.addWidget(self.save_progress_button)
        
        # 파일 경로 레이블 (거래내역 화면용)
        self.transactions_file_label = QLabel("파일을 선택해주세요.")
        self.transactions_file_label.setStyleSheet("""
            font-size: 12px;
            color: #7f8c8d;
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            margin: 10px;
        """)
        file_info_layout.addWidget(self.transactions_file_label)
        
        layout.addLayout(file_info_layout)
        
        # 거래내역 테이블 위젯 생성
        self.transactions_table = QTableWidget()
        self.setup_transactions_table()
        
        layout.addWidget(self.transactions_table)
        
        return transactions_widget
    
    def setup_transactions_table(self):
        """거래내역 테이블 위젯 설정"""
        # 기본 테이블 설정
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transactions_table.setSortingEnabled(True)
        
        # 헤더 설정
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.transactions_table.verticalHeader().setVisible(False)
        
        # 스타일 설정
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e1e8ed;
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e1e8ed;
                color: #2c3e50;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        print("✅ 거래내역 테이블 위젯 설정 완료")
    
    def display_csv_data_in_table(self, csv_result: dict):
        """
        슬라이스 1.3: CSV 파싱 결과를 테이블에 표시
        
        Args:
            csv_result: 파일 파서에서 반환된 CSV 파싱 결과
        """
        if not csv_result.get('success', False):
            print(f"❌ CSV 데이터 표시 실패: {csv_result.get('error', '알 수 없는 오류')}")
            return
        
        headers = csv_result.get('headers', [])
        data = csv_result.get('data', [])
        
        print(f"🔄 테이블에 CSV 데이터 표시 중... (헤더: {len(headers)}개, 데이터: {len(data)}행)")
        
        try:
            # 테이블 크기 설정
            self.transactions_table.setColumnCount(len(headers))
            self.transactions_table.setRowCount(len(data))
            
            # 헤더 설정
            self.transactions_table.setHorizontalHeaderLabels(headers)
            
            # 데이터 입력
            for row_idx, row_data in enumerate(data):
                for col_idx, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    self.transactions_table.setItem(row_idx, col_idx, item)
            
            # 컬럼 크기 자동 조정
            self.transactions_table.resizeColumnsToContents()
            
            # 파일 경로 레이블 업데이트
            if hasattr(self, 'transactions_file_label') and self.selected_file_path:
                file_name = self.selected_file_path.split('/')[-1]
                self.transactions_file_label.setText(f"📁 로드된 파일: {file_name} ({len(data)}행)")
                self.transactions_file_label.setStyleSheet("""
                    font-size: 12px;
                    color: #27ae60;
                    padding: 10px;
                    background-color: #d5f4e6;
                    border: 1px solid #27ae60;
                    border-radius: 4px;
                    margin: 10px;
                """)
            
            print(f"✅ 테이블 데이터 표시 완료: {len(data)}행 x {len(headers)}열")
            
            self.add_category_comboboxes_to_table()
            
            # 슬라이스 2.5: 파일 로드 완료 후 중간 저장 버튼 활성화
            self.enable_save_progress_button()
            
        except Exception as e:
            print(f"❌ 테이블 데이터 표시 중 오류: {e}")
    
    def add_category_comboboxes_to_table(self):
        """
        슬라이스 2.1: QTableWidget의 "사용자 확정 카테고리" 열에 각 행마다 QComboBox 추가
        
        데이터베이스에서 카테고리 목록을 가져와서 각 거래 행에 드롭다운 메뉴를 생성합니다.
        "사용자 확정 카테고리" 열이 없으면 자동으로 추가합니다.
        """
        try:
            table = self.transactions_table
            
            # 테이블에 데이터가 없으면 종료
            if table.rowCount() == 0:
                print("⚠️ 테이블에 데이터가 없어서 ComboBox를 추가할 수 없습니다")
                return
            
            # "사용자 확정 카테고리" 열 인덱스 찾기
            category_column_index = -1
            for col in range(table.columnCount()):
                header_item = table.horizontalHeaderItem(col)
                if header_item and header_item.text() == "사용자 확정 카테고리":
                    category_column_index = col
                    break
            
            # "사용자 확정 카테고리" 열이 없으면 추가
            if category_column_index == -1:
                print("📝 '사용자 확정 카테고리' 열이 없어서 새로 추가합니다")
                
                # 새 열 추가
                category_column_index = table.columnCount()
                table.setColumnCount(category_column_index + 1)
                
                # 헤더 설정
                header_item = QTableWidgetItem("사용자 확정 카테고리")
                table.setHorizontalHeaderItem(category_column_index, header_item)
                
                # 기존 행들에 빈 셀 추가
                for row in range(table.rowCount()):
                    item = QTableWidgetItem("")
                    table.setItem(row, category_column_index, item)
                
                print(f"✅ '사용자 확정 카테고리' 열을 {category_column_index}번 위치에 추가했습니다")
            
            # 데이터베이스에서 카테고리 목록 가져오기
            print("🔄 데이터베이스에서 카테고리 목록을 가져오는 중...")
            categories = get_categories_for_dropdown()
            
            if not categories:
                print("⚠️ 데이터베이스에서 카테고리를 가져올 수 없습니다")
                return
            
            print(f"✅ {len(categories)}개의 카테고리를 가져왔습니다")
            
            # 각 행에 ComboBox 추가
            for row in range(table.rowCount()):
                # ComboBox 생성
                combobox = QComboBox()
                
                # 드롭다운에 사용할 QListView를 따로 만들어 설정 (마우스 오버 효과용)
                view = QListView()
                view.setMouseTracking(True)  # 마우스 오버 감지 활성화
                combobox.setView(view)
                
                # 기본 선택 항목 추가
                combobox.addItem("카테고리를 선택하세요")
                
                # 카테고리 목록 추가
                for category in categories:
                    combobox.addItem(category)
                
                # 가장 긴 카테고리 문자열에 맞춰 최적 너비 계산 (대략 글자당 8px + 여백)
                max_category_length = max(len(cat) for cat in categories + ["카테고리를 선택하세요"])
                optimal_width = max_category_length * 8 + 30  # 글자당 8px + 드롭다운 버튼 여백
                combobox.setFixedWidth(optimal_width)
                combobox.setFixedHeight(20)  # 높이를 20px로 고정 (10px < 20px < 28px)
                
                # ComboBox 스타일링 (크기 최적화 + 마우스 오버 효과)
                combobox.setStyleSheet(f"""
                    QComboBox {{
                        font-size: 10px;
                        padding: 1px 4px;
                        border: 1px solid #bdc3c7;
                        border-radius: 3px;
                        background-color: white;
                        color: #2c3e50;
                        min-width: {optimal_width}px;
                        max-width: {optimal_width}px;
                        height: 20px;
                        max-height: 20px;
                    }}
                    QComboBox:hover {{
                        border-color: #3498db;
                        background-color: #f8f9fa;
                    }}
                    QComboBox:focus {{
                        border-color: #3498db;
                        outline: none;
                    }}
                    QComboBox::drop-down {{
                        subcontrol-origin: padding;
                        subcontrol-position: top right;
                        width: 16px;
                        border-left-width: 1px;
                        border-left-color: #bdc3c7;
                        border-left-style: solid;
                        border-top-right-radius: 3px;
                        border-bottom-right-radius: 3px;
                        background-color: #ecf0f1;
                    }}
                    QComboBox::down-arrow {{
                        width: 6px;
                        height: 6px;
                    }}
                    /* 드롭다운 리스트 전체 */
                    QComboBox QAbstractItemView {{
                        border: 1px solid #bdc3c7;
                        selection-background-color: #2980b9;
                        selection-color: white;
                        background-color: white;
                        color: #2c3e50;
                        font-size: 10px;
                        outline: 0;
                    }}
                    /* 각 항목 공통 패딩 */
                    QComboBox QAbstractItemView::item {{
                        padding: 4px 6px;
                        color: #2c3e50;
                        background-color: white;
                    }}
                    /* 마우스 오버(hover) 상태용 배경 - 대비 개선 */
                    QComboBox QAbstractItemView::item:hover {{
                        background-color: #e8f4fd;
                        color: #1a365d;
                        border: none;
                    }}
                    /* 선택된 항목 스타일 - 대비 개선 */
                    QComboBox QAbstractItemView::item:selected {{
                        background-color: #2980b9;
                        color: white;
                        border: none;
                    }}
                """)
                
                # 선택 변경 시그널 연결 (슬라이스 2.2에서 사용)
                combobox.currentTextChanged.connect(
                    lambda text, r=row: self.on_category_selection_changed(r, text)
                )
                
                # 테이블 셀에 ComboBox 설정
                table.setCellWidget(row, category_column_index, combobox)
                
                print(f"✅ 행 {row + 1}에 카테고리 ComboBox 추가 완료 (너비: {optimal_width}px)")
            
            # 카테고리 열 너비 최적화
            table.setColumnWidth(category_column_index, optimal_width + 10)
            
            print(f"🎉 모든 {table.rowCount()}개 행에 카테고리 ComboBox 추가 완료! (최적 너비: {optimal_width}px)")
            
        except Exception as e:
            print(f"❌ 카테고리 ComboBox 추가 중 오류 발생: {e}")
            raise
    
    def on_category_selection_changed(self, row: int, selected_category: str):
        """
        슬라이스 2.2: 카테고리 선택 변경 시 호출되는 메서드
        슬라이스 2.4: 실행 취소를 위한 히스토리 저장 기능 추가
        
        Args:
            row (int): 변경된 행 번호
            selected_category (str): 선택된 카테고리명
        """
        # 슬라이스 2.4: 이전 카테고리 값 저장 (실행 취소용)
        previous_category = self.transaction_categories.get(row, "카테고리를 선택하세요")
        
        # 기본 선택 항목이 아닌 경우에만 내부 데이터에 저장
        if selected_category != "카테고리를 선택하세요":
            # 슬라이스 2.4: 히스토리에 변경 사항 저장 (변경이 있는 경우에만)
            if previous_category != selected_category:
                self.save_category_change_to_history(row, previous_category, selected_category)
            
            # 선택된 카테고리를 내부 데이터 구조에 저장
            self.transaction_categories[row] = selected_category
            print(f"📝 행 {row + 1}의 카테고리가 '{selected_category}'로 변경됨")
            print(f"🔄 내부 데이터 업데이트: 행 {row} -> '{selected_category}'")
        else:
            # 기본 선택 항목으로 되돌린 경우 내부 데이터에서 제거
            if row in self.transaction_categories:
                # 슬라이스 2.4: 히스토리에 변경 사항 저장 (삭제도 변경으로 취급)
                self.save_category_change_to_history(row, previous_category, selected_category)
                
                del self.transaction_categories[row]
            print(f"⚪ 행 {row + 1}의 카테고리 선택이 초기화됨")
            print(f"🔄 내부 데이터에서 행 {row} 제거됨")
        
        # 슬라이스 2.4: 실행 취소 버튼 상태 업데이트
        self.update_undo_button_state()
        
        # 현재 내부 데이터 상태 출력 (디버깅용)
        print(f"📊 현재 저장된 카테고리: {self.transaction_categories}")
    
    def save_category_change_to_history(self, row: int, previous_category: str, current_category: str):
        """
        슬라이스 2.4: 카테고리 변경 사항을 히스토리 스택에 저장
        
        Args:
            row (int): 변경된 행 번호
            previous_category (str): 이전 카테고리명
            current_category (str): 현재 카테고리명
        """
        history_entry = {
            'row': row,
            'previous_category': previous_category,
            'current_category': current_category
        }
        
        # 히스토리에 추가
        self.category_change_history.append(history_entry)
        
        # 히스토리 크기 제한 (메모리 관리)
        if len(self.category_change_history) > self.max_history_size:
            self.category_change_history.pop(0)  # 가장 오래된 항목 제거
        
        print(f"💾 히스토리 저장: 행 {row + 1}, '{previous_category}' → '{current_category}'")
        print(f"📝 현재 히스토리 크기: {len(self.category_change_history)}")
    
    def on_undo_button_clicked(self):
        """
        슬라이스 2.4: 실행 취소 버튼 클릭 이벤트 처리
        """
        if not self.category_change_history:
            print("⚠️ 실행 취소할 변경 사항이 없습니다")
            return
        
        # 가장 최근 변경 사항 가져오기
        last_change = self.category_change_history.pop()
        row = last_change['row']
        previous_category = last_change['previous_category']
        current_category = last_change['current_category']
        
        print(f"⏪ 실행 취소: 행 {row + 1}, '{current_category}' → '{previous_category}'")
        
        # UI에서 ComboBox 찾기
        table = self.transactions_table
        category_column_index = -1
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item and header_item.text() == "사용자 확정 카테고리":
                category_column_index = col
                break
        
        if category_column_index != -1 and row < table.rowCount():
            combobox = table.cellWidget(row, category_column_index)
            if isinstance(combobox, QComboBox):
                # 시그널 연결을 일시적으로 해제하여 무한 루프 방지
                combobox.currentTextChanged.disconnect()
                
                # ComboBox를 이전 카테고리로 변경
                for i in range(combobox.count()):
                    if combobox.itemText(i) == previous_category:
                        combobox.setCurrentIndex(i)
                        break
                
                # 내부 데이터 업데이트
                if previous_category != "카테고리를 선택하세요":
                    self.transaction_categories[row] = previous_category
                else:
                    if row in self.transaction_categories:
                        del self.transaction_categories[row]
                
                # 시그널 다시 연결
                combobox.currentTextChanged.connect(
                    lambda text, r=row: self.on_category_selection_changed(r, text)
                )
                
                print(f"✅ 실행 취소 완료: 행 {row + 1}이 '{previous_category}'로 복원됨")
        
        # 실행 취소 버튼 상태 업데이트
        self.update_undo_button_state()
        
        # 현재 내부 데이터 상태 출력
        print(f"📊 실행 취소 후 저장된 카테고리: {self.transaction_categories}")
    
    def update_undo_button_state(self):
        """
        슬라이스 2.4: 실행 취소 버튼의 활성화/비활성화 상태 업데이트
        """
        if self.undo_button:
            has_history = len(self.category_change_history) > 0
            self.undo_button.setEnabled(has_history)
            
            if has_history:
                # 가장 최근 변경 사항 정보를 툴팁으로 표시
                last_change = self.category_change_history[-1]
                tooltip = f"실행 취소: 행 {last_change['row'] + 1} '{last_change['current_category']}' → '{last_change['previous_category']}'"
                self.undo_button.setToolTip(tooltip)
            else:
                self.undo_button.setToolTip("실행 취소할 변경 사항이 없습니다")
    
    def clear_category_change_history(self):
        """
        슬라이스 2.4: 카테고리 변경 히스토리 초기화 (새 파일 로딩 시 사용)
        """
        self.category_change_history.clear()
        self.update_undo_button_state()
        print("🧹 카테고리 변경 히스토리가 초기화되었습니다")
    
    def create_menu_bar(self):
        """60번: 기본 메뉴 바 구조 생성"""
        # 메뉴 바 생성
        menubar = self.menuBar()
        
        # 1. 파일 메뉴
        file_menu = menubar.addMenu('파일(&F)')
        
        # 파일 메뉴 항목들 (실제 기능은 나중에 연결)
        file_open_action = QAction('거래내역 파일 열기...', self)
        file_open_action.setShortcut('Ctrl+O')
        file_open_action.setStatusTip('CSV 또는 Excel 파일을 불러옵니다')
        file_menu.addAction(file_open_action)
        
        file_menu.addSeparator()
        
        file_export_action = QAction('내보내기...', self)
        file_export_action.setShortcut('Ctrl+E')
        file_export_action.setStatusTip('데이터를 CSV 파일로 내보냅니다')
        file_menu.addAction(file_export_action)
        
        file_menu.addSeparator()
        
        file_exit_action = QAction('종료(&X)', self)
        file_exit_action.setShortcut('Ctrl+Q')
        file_exit_action.setStatusTip('프로그램을 종료합니다')
        file_exit_action.triggered.connect(self.close)  # 종료 기능은 바로 연결
        file_menu.addAction(file_exit_action)
        
        # 2. 보기 메뉴
        view_menu = menubar.addMenu('보기(&V)')
        
        view_dashboard_action = QAction('대시보드', self)
        view_dashboard_action.setStatusTip('데이터 시각화 대시보드를 표시합니다')
        view_dashboard_action.triggered.connect(self.show_dashboard_screen)  # 화면 전환 연결
        view_menu.addAction(view_dashboard_action)
        
        view_transactions_action = QAction('거래내역', self)
        view_transactions_action.setStatusTip('거래내역 분류 화면을 표시합니다')
        view_transactions_action.triggered.connect(self.show_transactions_screen)  # 화면 전환 연결
        view_menu.addAction(view_transactions_action)
        
        view_menu.addSeparator()
        
        view_refresh_action = QAction('새로고침', self)
        view_refresh_action.setShortcut('F5')
        view_refresh_action.setStatusTip('현재 화면을 새로고침합니다')
        view_menu.addAction(view_refresh_action)
        
        # 3. 도구 메뉴
        tools_menu = menubar.addMenu('도구(&T)')
        
        tools_transfer_action = QAction('계좌 간 이체 자동 찾기', self)
        tools_transfer_action.setStatusTip('계좌 간 이체 거래를 자동으로 찾아 분류합니다')
        tools_menu.addAction(tools_transfer_action)
        
        tools_menu.addSeparator()
        
        tools_backup_action = QAction('데이터 백업', self)
        tools_backup_action.setStatusTip('현재 데이터를 백업합니다')
        tools_menu.addAction(tools_backup_action)
        
        tools_restore_action = QAction('데이터 복원', self)
        tools_restore_action.setStatusTip('백업된 데이터를 복원합니다')
        tools_menu.addAction(tools_restore_action)
        
        tools_menu.addSeparator()
        
        tools_settings_action = QAction('설정...', self)
        tools_settings_action.setShortcut('Ctrl+,')
        tools_settings_action.setStatusTip('프로그램 설정을 변경합니다')
        tools_settings_action.triggered.connect(self.open_settings_dialog)  # 설정 대화 상자 열기
        tools_menu.addAction(tools_settings_action)
        
        # 4. 도움말 메뉴
        help_menu = menubar.addMenu('도움말(&H)')
        
        help_guide_action = QAction('파일 형식 안내', self)
        help_guide_action.setStatusTip('지원되는 파일 형식에 대한 안내를 표시합니다')
        help_guide_action.triggered.connect(self.show_file_format_guide)  # 슬라이스 1.6: 파일 형식 안내 액션 연결
        help_menu.addAction(help_guide_action)
        
        help_menu.addSeparator()
        
        help_about_action = QAction('AI 스마트 가계부 정보...', self)
        help_about_action.setStatusTip('프로그램 정보를 표시합니다')
        help_menu.addAction(help_about_action)
    
    def open_settings_dialog(self):
        """
        설정 대화 상자를 엽니다.
        """
        print("⚙️ 설정 대화 상자 열기 요청")
        dialog = SettingsDialog(self) # 메인 윈도우를 부모로 설정
        dialog.exec() # 모달 방식으로 실행

    def parse_and_display_preview(self, file_path: str) -> None:
        """
        슬라이스 1.2 + 1.3 + 1.4: 선택된 파일의 내용을 파싱하여 콘솔에 출력하고 테이블에 표시
        
        Args:
            file_path: 파싱할 파일 경로 (CSV 또는 Excel)
        """
        print(f"\n🔍 파일 파싱 시작: {file_path}")
        
        # 슬라이스 2.4: 새 파일 로딩 시 카테고리 변경 히스토리 초기화
        self.clear_category_change_history()
        
        try:
            # 파일 확장자 확인
            import os
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # 파일 확장자에 따라 적절한 파싱 함수 호출
            if file_ext == '.csv':
                print("📄 CSV 파일 파싱 중...")
                result = self.file_parser.parse_csv_preview(file_path, max_rows=5)
                file_type = "CSV"
            elif file_ext in ['.xls', '.xlsx']:
                print("📊 Excel 파일 파싱 중...")
                result = self.file_parser.parse_excel_preview(file_path, max_rows=5)
                file_type = "Excel"
            else:
                print(f"❌ 지원하지 않는 파일 형식: {file_ext}")
                return
            
            if result['success']:
                print(f"✅ {file_type} 파싱 성공!")
                
                # 슬라이스 1.2: 콘솔에 파싱 결과 출력
                self.file_parser.print_csv_preview(result)
                
                # 현재 선택된 파일 경로 저장
                self.selected_file_path = file_path
                
                print(f"📝 총 {result['total_rows']}개의 데이터 행 발견")
                print(f"📊 {len(result['headers'])}개의 컬럼 발견: {', '.join(result['headers'])}")
                
                # 슬라이스 1.3: 테이블에 데이터 표시
                if self.transactions_table is not None:
                    self.display_csv_data_in_table(result)
                    print("🔄 거래내역 화면으로 자동 전환")
                    self.show_transactions_screen()
                
            else:
                print(f"❌ {file_type} 파싱 실패: {result['error']}")
                
        except Exception as e:
            print(f"❌ 파싱 중 예외 발생: {e}")

    def on_load_file_clicked(self):
        """슬라이스 1.1: 거래내역 파일 불러오기 버튼 클릭 이벤트 처리"""
        print("🔄 파일 선택 시작...")
        
        # 파일 선택 대화상자 열기
        file_path = self.file_handler.select_file(self)
        
        if file_path:
            # 파일 유효성 검증
            is_valid, message = self.file_handler.validate_file(file_path, self)
            
            if is_valid:
                # 파일 경로를 레이블에 표시
                self.file_path_label.setText(f"📁 선택된 파일: {file_path}")
                self.file_path_label.setStyleSheet("""
                    font-size: 14px;
                    color: #27ae60;
                    padding: 10px;
                    margin: 10px;
                    background-color: #d5f4e6;
                    border: 1px solid #27ae60;
                    border-radius: 4px;
                """)
                print(f"✅ 파일 선택 완료: {file_path}")
                
                # 슬라이스 1.2: 파일 선택 완료 후 자동으로 파싱 및 콘솔 출력 실행
                self.parse_and_display_preview(file_path)
                
            else:
                # 오류 시 기본 상태로 되돌리기
                self.file_path_label.setText("파일을 선택해주세요.")
                self.file_path_label.setStyleSheet("""
                    font-size: 14px;
                    color: #7f8c8d;
                    padding: 10px;
                    margin: 10px;
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                """)
                print(f"❌ 파일 검증 실패: {message}")
        else:
            print("📂 파일 선택 취소됨")
    
    # 슬라이스 1.6: 파일 형식 안내 팝업 기능
    def show_file_format_guide(self):
        """슬라이스 1.6: 파일 형식 안내 대화상자를 표시합니다"""
        print("📖 파일 형식 안내 팝업 표시")
        
        try:
            # 파일 형식 안내 대화상자 생성
            dialog = self.create_file_format_dialog()
            
            # 대화상자 표시 (모달)
            dialog.exec()
            
            print("✅ 파일 형식 안내 팝업 표시 완료")
            
        except Exception as e:
            print(f"❌ 파일 형식 안내 팝업 표시 중 오류: {e}")
    
    def create_file_format_dialog(self):
        """슬라이스 1.6: 파일 형식 안내 대화상자를 생성합니다"""
        # 대화상자 생성
        dialog = QDialog(self)
        dialog.setWindowTitle("파일 형식 안내")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        # 레이아웃 설정
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # 제목 레이블
        title_label = QLabel("📁 지원되는 파일 형식 안내")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            color: #2c3e50;
            margin: 20px;
            padding: 10px;
        """)
        layout.addWidget(title_label)
        
        # 스크롤 영역 생성
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 내용 위젯 생성
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)
        
        # 안내 내용 생성
        guide_text = self._create_file_format_guide_content()
        
        guide_label = QTextEdit()
        guide_label.setHtml(guide_text)
        guide_label.setReadOnly(True)
        guide_label.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                font-size: 13px;
                line-height: 1.5;
                color: #2c3e50;
            }
        """)
        content_layout.addWidget(guide_label)
        
        # 스크롤 영역에 내용 위젯 설정
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # 확인 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        button_box.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 8px 20px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        layout.addWidget(button_box)
        
        return dialog
    
    def _create_file_format_guide_content(self):
        """슬라이스 1.6: 파일 형식 안내 대화상자의 HTML 내용을 생성합니다"""
        return """
        <div style="color: #2c3e50;">
        <h3 style="color: #2c3e50; margin-bottom: 15px;">🎯 지원되는 파일 형식</h3>
        
        <div style="margin-bottom: 20px;">
            <h4 style="color: #e74c3c; margin-bottom: 10px;">📄 CSV 파일 (권장)</h4>
            <ul style="margin-left: 20px; line-height: 1.6;">
                <li><strong>확장자:</strong> .csv</li>
                <li><strong>인코딩:</strong> UTF-8 (권장)</li>
                <li><strong>구분자:</strong> 쉼표(,)</li>
                <li><strong>헤더:</strong> 첫 번째 행에 컬럼명 포함</li>
                <li><strong>예시:</strong> 날짜,내용,금액,카테고리</li>
            </ul>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h4 style="color: #27ae60; margin-bottom: 10px;">📊 Excel 파일</h4>
            <ul style="margin-left: 20px; line-height: 1.6;">
                <li><strong>확장자:</strong> .xls, .xlsx</li>
                <li><strong>시트:</strong> 첫 번째 시트만 읽기</li>
                <li><strong>헤더:</strong> 첫 번째 행에 컬럼명 포함</li>
                <li><strong>데이터:</strong> 두 번째 행부터 거래내역</li>
            </ul>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h4 style="color: #f39c12; margin-bottom: 10px;">⚠️ 파일 제한사항</h4>
            <ul style="margin-left: 20px; line-height: 1.6;">
                <li><strong>최대 크기:</strong> 50MB</li>
                <li><strong>지원하지 않는 형식:</strong> .txt, .doc, .pdf 등</li>
                <li><strong>특수문자:</strong> 파일명에 특수문자 주의</li>
            </ul>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h4 style="color: #8e44ad; margin-bottom: 10px;">💡 권장 컬럼 구성</h4>
            <ul style="margin-left: 20px; line-height: 1.6;">
                <li><strong>날짜:</strong> YYYY-MM-DD 형식 (예: 2023-12-25)</li>
                <li><strong>내용/적요:</strong> 거래 설명 (AI 분류에 중요)</li>
                <li><strong>금액:</strong> 숫자만 입력 (양수: 수입, 음수: 지출)</li>
                <li><strong>카테고리:</strong> 기존 분류가 있다면 포함</li>
            </ul>
        </div>
        
        <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <h4 style="color: #27ae60; margin-bottom: 10px;">✅ 올바른 파일 예시</h4>
            <code style="display: block; background-color: white; padding: 10px; border-radius: 4px; font-family: monospace;">
날짜,내용,금액,카테고리<br>
2023-12-01,스타벅스 아메리카노,4500,식비<br>
2023-12-01,지하철 요금,-1350,교통비<br>
2023-12-02,월급,2500000,급여
            </code>
        </div>
        
        <div style="background-color: #fdf2f2; padding: 15px; border-radius: 8px; border-left: 4px solid #e74c3c;">
            <h4 style="color: #e74c3c; margin-bottom: 10px;">🚨 문제 해결</h4>
            <p style="margin-bottom: 8px;"><strong>파일이 열리지 않는 경우:</strong></p>
            <ul style="margin-left: 20px; margin-bottom: 15px;">
                <li>파일 크기가 50MB 이하인지 확인</li>
                <li>확장자가 .csv, .xls, .xlsx인지 확인</li>
                <li>Excel 파일이 열려있지 않은지 확인</li>
            </ul>
            <p style="margin-bottom: 8px;"><strong>데이터가 이상하게 표시되는 경우:</strong></p>
            <ul style="margin-left: 20px;">
                <li>CSV 파일의 인코딩을 UTF-8로 저장</li>
                <li>첫 번째 행에 헤더가 있는지 확인</li>
                <li>금액 컬럼에 숫자만 입력되었는지 확인</li>
            </ul>
        </div>
        </div>
        """ 

    def check_and_restore_progress_on_startup(self):
        """
        슬라이스 2.5: 프로그램 시작 시 저장된 진행 상태가 있는지 확인
        """
        try:
            # 저장된 진행 상태 로드
            progress_data = self.progress_saver.load_progress()
            
            if progress_data:
                print("📂 저장된 진행 상태를 발견했습니다!")
                
                # 진행 상태 요약 정보 표시
                summary = self.progress_saver.get_progress_summary()
                if summary:
                    print(f"📊 파일: {summary['file_name']}")
                    print(f"📈 진행률: {summary['progress_percentage']:.1f}% ({summary['processed_rows']}/{summary['total_rows']})")
                    print(f"⏰ 마지막 저장: {summary['last_saved_time']}")
                
                # 사용자에게 복원 여부 확인
                reply = QMessageBox.question(
                    self, 
                    "진행 상태 복원", 
                    f"이전 작업 진행 상태가 있습니다.\n\n"
                    f"파일: {summary['file_name'] if summary else '알 수 없음'}\n"
                    f"진행률: {summary['progress_percentage']:.1f}% ({summary['processed_rows']}/{summary['total_rows']})\n"
                    f"마지막 저장: {summary['last_saved_time'] if summary else '알 수 없음'}\n\n"
                    f"이전 작업을 이어서 하시겠습니까?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    self.restore_progress_from_data(progress_data)
                else:
                    # 사용자가 거부한 경우 진행 상태 삭제
                    self.progress_saver.clear_progress()
                    print("🗑️ 이전 진행 상태를 삭제했습니다")
            else:
                print("📝 저장된 진행 상태가 없습니다")
                
        except Exception as e:
            print(f"❌ 진행 상태 복원 중 오류 발생: {e}")

    def on_save_progress_clicked(self):
        """
        슬라이스 2.5: 중간 저장 버튼 클릭 이벤트 처리
        """
        try:
            if not self.selected_file_path:
                QMessageBox.warning(self, "경고", "저장할 파일이 선택되지 않았습니다.")
                return
            
            # 현재 진행 상태 데이터 수집
            progress_data = self.collect_current_progress_data()
            
            if not progress_data:
                QMessageBox.warning(self, "경고", "저장할 진행 상태 데이터가 없습니다.")
                return
            
            # 진행 상태 저장
            success = self.progress_saver.save_progress(progress_data)
            
            if success:
                # 백업 생성 로직 제거 - 사용자가 필요할 때만 수동으로 백업
                # backup_path = self.progress_saver.create_backup()
                
                # 백업 파일 정보를 별도로 구성 (f-string 내 백슬래시 문제 해결) - 제거
                # backup_info = f"\n백업 파일: {backup_path}" if backup_path else ""
                
                QMessageBox.information(
                    self, 
                    "저장 완료", 
                    f"진행 상태가 성공적으로 저장되었습니다!\n\n"
                    f"처리된 행: {progress_data['processed_rows']}/{progress_data['total_rows']}\n"
                    f"진행률: {(progress_data['processed_rows']/progress_data['total_rows']*100):.1f}%"
                )
                print(f"✅ 진행 상태 저장 완료: {progress_data['processed_rows']}/{progress_data['total_rows']} 행")
            else:
                QMessageBox.critical(self, "오류", "진행 상태 저장에 실패했습니다.")
                
        except Exception as e:
            print(f"❌ 진행 상태 저장 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"진행 상태 저장 중 오류가 발생했습니다:\n{str(e)}")

    def collect_current_progress_data(self):
        """
        슬라이스 2.5: 현재 진행 상태 데이터를 수집
        
        Returns:
            Dict: 진행 상태 데이터
        """
        try:
            if not self.selected_file_path or not self.transactions_table:
                return None
            
            # 파일 해시 계산
            file_hash = self.calculate_file_hash(self.selected_file_path)
            
            # 테이블에서 거래 데이터 수집
            transactions = []
            total_rows = self.transactions_table.rowCount()
            processed_rows = 0
            
            for row in range(total_rows):
                transaction_data = {
                    'row_index': row,
                    'transaction_id': f'txn_{row:04d}',  # 임시 ID
                    'is_confirmed': row in self.transaction_categories
                }
                
                # 테이블에서 거래 정보 추출
                for col in range(self.transactions_table.columnCount()):
                    header_item = self.transactions_table.horizontalHeaderItem(col)
                    if header_item:
                        header_name = header_item.text()
                        item = self.transactions_table.item(row, col)
                        if item:
                            transaction_data[header_name] = item.text()
                
                # 사용자 확정 카테고리 추가
                if row in self.transaction_categories:
                    transaction_data['user_confirmed_category'] = self.transaction_categories[row]
                    processed_rows += 1
                else:
                    transaction_data['user_confirmed_category'] = None
                
                transactions.append(transaction_data)
            
            # 현재 작업 위치 (마지막으로 분류된 행)
            current_row_index = max(self.transaction_categories.keys()) if self.transaction_categories else -1
            
            progress_data = {
                'file_path': self.selected_file_path,
                'file_hash': file_hash,
                'total_rows': total_rows,
                'processed_rows': processed_rows,
                'current_row_index': current_row_index,
                'timestamp': datetime.now().isoformat(),
                'transactions': transactions
            }
            
            return progress_data
            
        except Exception as e:
            print(f"❌ 진행 상태 데이터 수집 중 오류: {e}")
            return None

    def calculate_file_hash(self, file_path: str) -> str:
        """
        슬라이스 2.5: 파일의 해시값을 계산하여 일관성 검증에 사용
        
        Args:
            file_path: 해시를 계산할 파일 경로
            
        Returns:
            str: 파일의 MD5 해시값
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"❌ 파일 해시 계산 중 오류: {e}")
            return ""

    def restore_progress_from_data(self, progress_data: dict):
        """
        슬라이스 2.5: 저장된 진행 상태 데이터로부터 UI 복원
        
        Args:
            progress_data: 복원할 진행 상태 데이터
        """
        try:
            file_path = progress_data.get('file_path')
            file_hash = progress_data.get('file_hash')
            
            # 파일 존재 여부 확인
            if not os.path.exists(file_path):
                QMessageBox.warning(
                    self, 
                    "파일 없음", 
                    f"저장된 파일을 찾을 수 없습니다:\n{file_path}\n\n"
                    f"파일 경로가 변경되었거나 파일이 삭제되었을 수 있습니다."
                )
                return
            
            # 파일 일관성 검증
            current_hash = self.calculate_file_hash(file_path)
            if current_hash != file_hash:
                reply = QMessageBox.question(
                    self,
                    "파일 변경 감지",
                    f"파일이 마지막 저장 이후 변경된 것 같습니다.\n\n"
                    f"그래도 진행 상태를 복원하시겠습니까?\n"
                    f"(데이터 불일치가 발생할 수 있습니다)",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
            
            # 파일 로드 및 UI 복원
            self.selected_file_path = file_path
            self.current_file_hash = current_hash
            
            # 파일 파싱 및 테이블 표시
            self.parse_and_display_preview(file_path)
            
            # 카테고리 선택 상태 복원
            transactions = progress_data.get('transactions', [])
            for transaction in transactions:
                row_index = transaction.get('row_index')
                user_category = transaction.get('user_confirmed_category')
                
                if row_index is not None and user_category:
                    self.transaction_categories[row_index] = user_category
                    
                    # UI에서 해당 ComboBox 찾아서 설정
                    self.restore_combobox_selection(row_index, user_category)
            
            # 중간 저장 버튼 활성화
            if self.save_progress_button:
                self.save_progress_button.setEnabled(True)
            
            # 거래내역 화면으로 전환
            self.show_transactions_screen()
            
            print(f"✅ 진행 상태 복원 완료: {len(self.transaction_categories)}개 카테고리 복원됨")
            
        except Exception as e:
            print(f"❌ 진행 상태 복원 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"진행 상태 복원 중 오류가 발생했습니다:\n{str(e)}")

    def restore_combobox_selection(self, row_index: int, category: str):
        """
        슬라이스 2.5: 특정 행의 ComboBox 선택 상태를 복원
        
        Args:
            row_index: 행 번호
            category: 선택할 카테고리명
        """
        try:
            table = self.transactions_table
            if not table or row_index >= table.rowCount():
                return
            
            # "사용자 확정 카테고리" 열 찾기
            category_column_index = -1
            for col in range(table.columnCount()):
                header_item = table.horizontalHeaderItem(col)
                if header_item and header_item.text() == "사용자 확정 카테고리":
                    category_column_index = col
                    break
            
            if category_column_index == -1:
                return
            
            # ComboBox 찾기 및 선택 상태 설정
            combobox = table.cellWidget(row_index, category_column_index)
            if isinstance(combobox, QComboBox):
                # 시그널 연결을 일시적으로 해제
                combobox.currentTextChanged.disconnect()
                
                # 카테고리 선택
                for i in range(combobox.count()):
                    if combobox.itemText(i) == category:
                        combobox.setCurrentIndex(i)
                        break
                
                # 시그널 다시 연결
                combobox.currentTextChanged.connect(
                    lambda text, r=row_index: self.on_category_selection_changed(r, text)
                )
                
                print(f"✅ 행 {row_index + 1} 카테고리 복원: {category}")
                
        except Exception as e:
            print(f"❌ ComboBox 선택 상태 복원 중 오류 (행 {row_index}): {e}")

    def enable_save_progress_button(self):
        """
        슬라이스 2.5: 중간 저장 버튼 활성화 (파일 로드 후 호출)
        """
        if self.save_progress_button:
            self.save_progress_button.setEnabled(True)
            print("✅ 중간 저장 버튼이 활성화되었습니다") 