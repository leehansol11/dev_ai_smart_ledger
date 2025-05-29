import pytest
from PySide6.QtWidgets import QApplication, QTableWidgetItem, QPushButton
from PySide6.QtGui import QColor
from PySide6.QtTest import QTest
from unittest.mock import patch

from ai_smart_ledger.app.ui.main_window import MainWindow

class TestSlice33UI:
    @pytest.fixture(autouse=True)
    def setup(self):
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        self.main_window = MainWindow()
        self.main_window.show_transactions_screen()
        self.setup_sample_data()
        yield
        self.main_window.close()

    def setup_sample_data(self):
        headers = ["날짜", "적요", "금액", "잔액"]
        data = [
            ["2024-01-01", "스타벅스 결제", "-5500", "1000000"],
            ["2024-01-02", "급여 입금", "3000000", "4000000"],
            ["2024-01-03", "편의점", "-2000", "3998000"],
        ]
        table = self.main_window.transactions_table
        table.setColumnCount(len(headers))
        table.setRowCount(len(data))
        table.setHorizontalHeaderLabels(headers)
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                table.setItem(row_idx, col_idx, item)

    @patch("ai_smart_ledger.app.ui.main_window.suggest_category_for_transaction")
    def test_ai_suggestion_column_display(self, mock_suggest):
        # Given: AI 추천값 모킹
        mock_suggest.side_effect = ["식비 > 카페/음료", "수입 > 급여"]
        # When: 추천값을 UI에 반영하는 메서드 호출
        self.main_window.add_ai_suggestion_column_to_table()
        table = self.main_window.transactions_table
        ai_col_idx = None
        for col in range(table.columnCount()):
            if table.horizontalHeaderItem(col).text() == "AI 추천 카테고리":
                ai_col_idx = col
                break
        assert ai_col_idx is not None, "'AI 추천 카테고리' 열이 없음"
        assert table.item(0, ai_col_idx).text() == "식비 > 카페/음료"
        assert table.item(1, ai_col_idx).text() == "수입 > 급여"

    @patch("ai_smart_ledger.app.ui.main_window.suggest_category_for_transaction")
    def test_ai_suggestion_confidence_coloring(self, mock_suggest):
        # Given: (추천값, 신뢰도) 튜플을 반환하도록 mock
        mock_suggest.side_effect = [
            ("식비 > 카페/음료", "HIGH"),
            ("수입 > 급여", "MEDIUM"),
            ("생활비 > 편의점", "LOW"),
        ]
        # When: 추천값+신뢰도를 UI에 반영하는 메서드 호출 (구현 필요)
        self.main_window.add_ai_suggestion_column_to_table(confidence_mode=True)
        table = self.main_window.transactions_table
        ai_col_idx = None
        for col in range(table.columnCount()):
            if table.horizontalHeaderItem(col).text() == "AI 추천 카테고리":
                ai_col_idx = col
                break
        assert ai_col_idx is not None, "'AI 추천 카테고리' 열이 없음"
        # Then: 각 행의 배경색이 신뢰도에 따라 맞는지 확인
        expected_colors = [QColor(200,255,200), QColor(255,255,180), QColor(255,200,200)]
        for row, expected_color in enumerate(expected_colors):
            item = table.item(row, ai_col_idx)
            assert item is not None
            bg = item.background().color()
            assert bg == expected_color, f"row {row} 배경색 불일치: {bg.getRgb()} vs {expected_color.getRgb()}"

    @patch.object(MainWindow, "_update_transaction_category")
    @patch.object(MainWindow, "_get_all_categories")
    def test_category_change_triggers_db_update(self, mock_get_all, mock_update):
        # Given: 카테고리 계층 및 row_to_transaction_id 세팅
        mock_get_all.return_value = [
            (6, '카페/음료', 4, '지출', 3),
            (4, '식비', 3, '지출', 2),
            (3, '지출', None, '지출', 1),
        ]
        self.main_window.row_to_transaction_id = {0: 123}
        # When: 카테고리 변경 시그널 발생
        self.main_window.on_category_selection_changed(0, '지출 > 식비 > 카페/음료')
        # Then: update_transaction_category가 올바른 인자로 호출되는지 확인
        mock_update.assert_called_once_with(123, 6)

    @patch("ai_smart_ledger.app.ui.main_window.suggest_category_for_transaction")
    def test_ai_suggestion_confirm_buttons(self, mock_suggest):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QPushButton
        from PySide6.QtTest import QTest
        # Given: (추천값, 신뢰도) 튜플을 반환하도록 mock
        expected_values = [
            ("식비 > 카페/음료", "HIGH"),
            ("수입 > 급여", "MEDIUM"),
            ("생활비 > 편의점", "LOW"),
        ]
        mock_suggest.side_effect = expected_values.copy()
        self.main_window.add_ai_suggestion_column_to_table(with_confirm_buttons=True)
        table = self.main_window.transactions_table
        ai_col_idx = None
        user_col_idx = None
        for col in range(table.columnCount()):
            if table.horizontalHeaderItem(col).text() == "AI 추천 카테고리":
                ai_col_idx = col
            if table.horizontalHeaderItem(col).text() == "사용자 확정 카테고리":
                user_col_idx = col
        assert ai_col_idx is not None and user_col_idx is not None
        # 각 행에 Y/N 버튼이 있는지 확인
        for row in range(table.rowCount()):
            yn_widget = table.cellWidget(row, ai_col_idx+1)
            assert yn_widget is not None
            btn_yes = yn_widget.findChildren(QPushButton)[0]
            btn_no = yn_widget.findChildren(QPushButton)[1]
            # '예' 클릭 시 추천값 복사
            QTest.mouseClick(btn_yes, Qt.LeftButton)
            assert table.item(row, user_col_idx).text() == expected_values[row][0]
            # '아니요' 클릭 시 값이 비워지거나 기본값이면 통과
            QTest.mouseClick(btn_no, Qt.LeftButton)
            cell_val = table.item(row, user_col_idx).text()
            assert cell_val in ("", "카테고리를 선택하세요") 