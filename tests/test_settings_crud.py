import unittest
import os
from dotenv import load_dotenv
import sqlite3

# 프로젝트 루트 디렉토리를 기준으로 경로 설정
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from ai_smart_ledger.app.db.database import init_database, close_db_connection
from ai_smart_ledger.app.db.crud import save_setting, get_setting # save_setting, get_setting 함수는 이제 구현될 예정

class TestSettingsCRUD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # 테스트 시작 전, 테스트용 DB 파일 설정 및 초기화
        # load_dotenv() # .env 파일 로드는 실제 환경에서, 테스트에서는 직접 경로 설정
        cls.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_AISmartLedger.db'))
        # 테스트 환경 변수 설정
        os.environ['DATABASE_URL'] = cls.db_path
        init_database() # init_database 함수는 환경 변수에서 DB 경로를 읽도록 수정

    @classmethod
    def tearDownClass(cls):
        # 테스트 완료 후, 테스트용 DB 파일 삭제
        close_db_connection() # 커넥션 닫기
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def setUp(self): # 각 테스트 함수 실행 전 호출
        # 매 테스트 시작 전 settings 테이블 비우기 (선택 사항, 테스트 독립성을 위해)
        # conn = get_db_connection()
        # cursor = conn.cursor()
        # cursor.execute("DELETE FROM settings")
        # conn.commit()
        # close_db_connection(conn) # 커넥션 닫기
        pass

    def tearDown(self):
        # 각 테스트 함수 실행 후 호출
        pass

    def test_save_and_get_api_key(self):
        # API 키 저장 및 조회 테스트
        api_key = "test_api_key_12345"
        setting_key = "chatgpt_api_key"

        # 1. API 키 저장 시도
        # save_setting 함수는 아직 구현되지 않았으므로, mock 또는 예상 동작 기반으로 테스트 작성
        print(f"\n테스트: {setting_key} 저장 시도")
        success = save_setting(setting_key, api_key)
        self.assertTrue(success, "API 키 저장 실패")

        # 2. 저장된 API 키 조회 시도
        print(f"테스트: {setting_key} 조회 시도")
        retrieved_key = get_setting(setting_key)
        print(f"조회 결과: {retrieved_key}")
        self.assertEqual(retrieved_key, api_key, "저장된 API 키와 조회된 키가 다름")

        # 3. API 키 업데이트 시도
        print(f"테스트: {setting_key} 업데이트 시도")
        new_api_key = "new_test_api_key_67890"
        success_update = save_setting(setting_key, new_api_key)
        self.assertTrue(success_update, "API 키 업데이트 실패")

        # 4. 업데이트된 API 키 조회 시도
        print(f"테스트: 업데이트된 {setting_key} 조회 시도")
        retrieved_new_key = get_setting(setting_key)
        print(f"조회 결과: {retrieved_new_key}")
        self.assertEqual(retrieved_new_key, new_api_key, "업데이트된 API 키와 조회된 키가 다름")

        # 5. 존재하지 않는 설정 키 조회 시도
        print("테스트: 존재하지 않는 키 조회 시도")
        non_existent_key = get_setting("non_existent_key")
        print(f"조회 결과: {non_existent_key}")
        self.assertIsNone(non_existent_key, "존재하지 않는 키 조회 시 None이 아님")

    def test_save_different_setting_type(self):
        # 다른 타입의 설정 값 저장 테스트 (예: 정수)
        setting_key = "transfer_time_window"
        setting_value = 10 # 정수 값

        print(f"\n테스트: 다른 타입 설정 ({setting_key}: {setting_value}) 저장 시도")
        success = save_setting(setting_key, setting_value)
        self.assertTrue(success, "정수 설정 값 저장 실패")

        print(f"테스트: 저장된 {setting_key} 조회 시도")
        retrieved_value = get_setting(setting_key)
        print(f"조회 결과: {retrieved_value} (타입: {type(retrieved_value)})")
        # SQLite는 기본적으로 숫자를 TEXT로 저장할 수 있으므로, 조회 시 타입 변환 필요
        # 현재 get_setting은 TEXT를 반환할 것으로 예상
        self.assertEqual(retrieved_value, str(setting_value), "저장된 정수 설정 값과 조회된 값이 다름")
        # 실제 애플리케이션에서는 조회 후 적절한 타입으로 변환해야 함

        print("테스트: 존재하지 않는 다른 타입 키 조회 시도")
        non_existent_key = get_setting("another_non_existent_key")
        print(f"조회 결과: {non_existent_key}")
        self.assertIsNone(non_existent_key, "존재하지 않는 키 조회 시 None이 아님")

if __name__ == '__main__':
    unittest.main() 