#!/usr/bin/env python3
"""
AI 스마트 가계부 - 메인 윈도우
Author: leehansol
Created: 2025-05-25
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget, 
    QMenuBar, QMenu, QLabel, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from ..core.file_handler import FileHandler


class MainWindow(QMainWindow):
    """AI 스마트 가계부 메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        
        # 슬라이스 1.1: 파일 핸들러 초기화
        self.file_handler = FileHandler()
        
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
        # self.transactions_widget = self.create_transactions_screen()  # 나중에 구현
        # self.dashboard_widget = self.create_dashboard_screen()        # 나중에 구현
        # self.settings_widget = self.create_settings_screen()          # 나중에 구현
        
        # 스택에 화면들 추가
        self.central_widget.addWidget(self.welcome_widget)  # 인덱스 0
        # self.central_widget.addWidget(self.transactions_widget)  # 인덱스 1 (나중에)
        # self.central_widget.addWidget(self.dashboard_widget)     # 인덱스 2 (나중에)
        # self.central_widget.addWidget(self.settings_widget)      # 인덱스 3 (나중에)
        
        print("✅ 중앙 위젯 레이아웃 설정 완료 - QStackedWidget 기반 화면 전환 시스템 준비됨")
    
    def show_welcome_screen(self):
        """환영 화면으로 전환"""
        self.central_widget.setCurrentIndex(self.SCREEN_WELCOME)
        print("🏠 환영 화면으로 전환")
    
    def show_transactions_screen(self):
        """거래내역 화면으로 전환 (향후 구현)"""
        # self.central_widget.setCurrentIndex(self.SCREEN_TRANSACTIONS)
        print("📊 거래내역 화면 (아직 구현되지 않음)")
    
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
        help_menu.addAction(help_guide_action)
        
        help_menu.addSeparator()
        
        help_about_action = QAction('AI 스마트 가계부 정보...', self)
        help_about_action.setStatusTip('프로그램 정보를 표시합니다')
        help_menu.addAction(help_about_action)
    
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