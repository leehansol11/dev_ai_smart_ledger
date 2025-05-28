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
    QTextEdit, QDialogButtonBox, QScrollArea, QComboBox, QListView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont, QPixmap

from ..core.file_handler import FileHandler
from ..core.file_parser import FileParser
from ..db.crud import get_categories_for_dropdown


class MainWindow(QMainWindow):
    """AI 스마트 가계부 메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        
        # 슬라이스 1.1: 파일 핸들러 초기화
        self.file_handler = FileHandler()
        
        # 슬라이스 1.2: 파일 파서 초기화
        self.file_parser = FileParser()
        
        # 현재 선택된 파일 경로 저장
        self.selected_file_path = None
        
        # 슬라이스 1.3: 거래내역 테이블 위젯 초기화
        self.transactions_table = None
        
        self.init_ui()
        
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
        슬라이스 2.2에서 구현 예정: 카테고리 선택 변경 시 호출되는 메서드
        
        Args:
            row (int): 변경된 행 번호
            selected_category (str): 선택된 카테고리명
        """
        # 현재는 로깅만 수행 (슬라이스 2.2에서 실제 구현)
        if selected_category != "카테고리를 선택하세요":
            print(f"📝 행 {row + 1}의 카테고리가 '{selected_category}'로 변경됨")
        else:
            print(f"⚪ 행 {row + 1}의 카테고리 선택이 초기화됨")
    
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
        tools_settings_action.triggered.connect(self.show_settings_screen)  # 화면 전환 연결
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
    
    def parse_and_display_preview(self, file_path: str) -> None:
        """
        슬라이스 1.2 + 1.3 + 1.4: 선택된 파일의 내용을 파싱하여 콘솔에 출력하고 테이블에 표시
        
        Args:
            file_path: 파싱할 파일 경로 (CSV 또는 Excel)
        """
        print(f"\n🔍 파일 파싱 시작: {file_path}")
        
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