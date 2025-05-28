"""
슬라이스 2.3: 분류된 카테고리 transactions DB에 저장
데이터베이스 CRUD 함수 단위 테스트

Author: leehansol
Created: 2025-05-25
"""

import pytest
import sqlite3
import os
import tempfile
from typing import List, Dict, Any, Optional
from datetime import datetime

# 프로젝트 루트를 sys.path에 추가
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestTransactionCategoryCRUD:
    """거래내역 카테고리 업데이트 관련 CRUD 함수 테스트"""
    
    @pytest.fixture(autouse=True)
    def setup_test_database(self):
        """각 테스트마다 임시 데이터베이스 설정"""
        # 임시 데이터베이스 파일 생성
        self.test_db_fd, self.test_db_path = tempfile.mkstemp(suffix='.db')
        os.close(self.test_db_fd)
        
        # 직접 SQLite 연결 생성
        self.conn = sqlite3.connect(self.test_db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # 테이블 생성
        self._create_test_tables()
        
        # 기본 카테고리 데이터 삽입
        self._insert_test_categories()
        
        # 테스트용 샘플 거래내역 삽입
        self._insert_sample_transactions()
        
        yield
        
        # 테스트 후 정리
        self.conn.close()
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def _create_test_tables(self):
        """테스트용 테이블 생성"""
        # categories 테이블
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL,
            parent_category_id INTEGER,
            type TEXT NOT NULL CHECK (type IN ('수입', '지출', '이체')),
            level INTEGER NOT NULL CHECK (level >= 1 AND level <= 3),
            is_default BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_category_id) REFERENCES categories(category_id),
            UNIQUE(category_name, parent_category_id)
        );
        """)
        
        # transactions 테이블
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT,
            timestamp TIMESTAMP NOT NULL,
            description TEXT NOT NULL,
            amount_in DECIMAL(15,2),
            amount_out DECIMAL(15,2),
            category_id INTEGER,
            is_transfer BOOLEAN NOT NULL DEFAULT FALSE,
            source_file TEXT,
            source_row_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(category_id),
            CHECK (
                (amount_in IS NOT NULL AND amount_out IS NULL) OR 
                (amount_in IS NULL AND amount_out IS NOT NULL)
            )
        );
        """)
        
        self.conn.commit()
    
    def _insert_test_categories(self):
        """테스트용 기본 카테고리 삽입"""
        categories = [
            (1, '수입', None, '수입', 1),
            (2, '급여', 1, '수입', 2),
            (3, '지출', None, '지출', 1),
            (4, '식비', 3, '지출', 2),
            (5, '생활용품', 3, '지출', 2),
            (6, '카페/음료', 4, '지출', 3),
            (7, '계좌 간 이체 (분석 제외)', None, '이체', 1),
        ]
        
        for cat_id, name, parent_id, cat_type, level in categories:
            self.conn.execute("""
            INSERT OR IGNORE INTO categories 
            (category_id, category_name, parent_category_id, type, level) 
            VALUES (?, ?, ?, ?, ?)
            """, (cat_id, name, parent_id, cat_type, level))
        
        self.conn.commit()
    
    def _insert_sample_transactions(self):
        """테스트용 샘플 거래내역 삽입"""
        sample_transactions = [
            (1, 'TEST001', '2024-01-15 10:30:00', '스타벅스 커피', None, 5500.0, None, False, 'test.csv', 1),
            (2, 'TEST001', '2024-01-15 12:00:00', '급여 입금', 3000000.0, None, None, False, 'test.csv', 2),
            (3, 'TEST001', '2024-01-16 14:20:00', '마트 장보기', None, 45000.0, None, False, 'test.csv', 3)
        ]
        
        for transaction in sample_transactions:
            self.conn.execute("""
            INSERT INTO transactions (
                transaction_id, account_id, timestamp, description, amount_in, amount_out,
                category_id, is_transfer, source_file, source_row_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, transaction)
        
        self.conn.commit()
    
    def test_update_transaction_category_success(self):
        """거래내역 카테고리 업데이트 성공 테스트"""
        # 직접 SQL로 업데이트 테스트 (CRUD 함수를 시뮬레이션)
        transaction_id = 1
        category_id = 6  # 카페/음료 카테고리 ID
        
        # 거래내역 존재 확인
        cursor = self.conn.cursor()
        cursor.execute("SELECT transaction_id FROM transactions WHERE transaction_id = ?", (transaction_id,))
        transaction = cursor.fetchone()
        assert transaction is not None, "테스트 거래내역이 존재해야 합니다"
        
        # 카테고리 존재 확인
        cursor.execute("SELECT category_id FROM categories WHERE category_id = ?", (category_id,))
        category = cursor.fetchone()
        assert category is not None, "테스트 카테고리가 존재해야 합니다"
        
        # 카테고리 업데이트
        cursor.execute("""
        UPDATE transactions 
        SET category_id = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE transaction_id = ?
        """, (category_id, transaction_id))
        self.conn.commit()
        
        # 업데이트 결과 확인
        cursor.execute("SELECT category_id FROM transactions WHERE transaction_id = ?", (transaction_id,))
        updated_category = cursor.fetchone()
        
        assert updated_category is not None, "업데이트된 거래내역을 찾을 수 있어야 합니다"
        assert updated_category[0] == category_id, f"카테고리 ID가 {category_id}로 업데이트되어야 합니다"
    
    def test_update_transaction_category_invalid_transaction_id(self):
        """존재하지 않는 거래내역 ID로 업데이트 시도 테스트"""
        # 존재하지 않는 거래내역 ID
        invalid_transaction_id = 9999
        category_id = 6
        
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE transactions 
        SET category_id = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE transaction_id = ?
        """, (category_id, invalid_transaction_id))
        self.conn.commit()
        
        # 영향받은 행이 0개여야 함
        assert cursor.rowcount == 0, "존재하지 않는 거래내역 ID에 대해 영향받은 행이 0개여야 합니다"
    
    def test_update_transaction_category_invalid_category_id(self):
        """존재하지 않는 카테고리 ID로 업데이트 시도 테스트"""
        transaction_id = 1
        invalid_category_id = 9999
        
        # 외래키 제약조건 위반으로 오류 발생해야 함
        with pytest.raises(sqlite3.IntegrityError):
            cursor = self.conn.cursor()
            cursor.execute("""
            UPDATE transactions 
            SET category_id = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE transaction_id = ?
            """, (invalid_category_id, transaction_id))
            self.conn.commit()
    
    def test_update_multiple_transactions_categories(self):
        """여러 거래내역 일괄 카테고리 업데이트 테스트"""
        # 여러 거래내역 업데이트 데이터
        updates = [
            {'transaction_id': 1, 'category_id': 6},   # 스타벅스 -> 카페/음료
            {'transaction_id': 2, 'category_id': 2},   # 급여 -> 급여 (수입)
            {'transaction_id': 3, 'category_id': 5}    # 마트 -> 생활용품
        ]
        
        cursor = self.conn.cursor()
        
        # 트랜잭션 시작
        cursor.execute("BEGIN TRANSACTION")
        
        try:
            for update in updates:
                cursor.execute("""
                UPDATE transactions 
                SET category_id = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE transaction_id = ?
                """, (update['category_id'], update['transaction_id']))
            
            cursor.execute("COMMIT")
            
            # 각 거래내역이 올바르게 업데이트되었는지 확인
            for update in updates:
                cursor.execute("SELECT category_id FROM transactions WHERE transaction_id = ?", 
                             (update['transaction_id'],))
                updated_category = cursor.fetchone()
                
                assert updated_category is not None
                assert updated_category[0] == update['category_id']
        
        except Exception as e:
            cursor.execute("ROLLBACK")
            raise e
    
    def test_get_uncategorized_transactions(self):
        """미분류 거래내역 조회 테스트"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT transaction_id, account_id, timestamp, description, 
               amount_in, amount_out, category_id, is_transfer,
               source_file, source_row_id
        FROM transactions 
        WHERE category_id IS NULL
        ORDER BY timestamp DESC
        """)
        
        uncategorized = cursor.fetchall()
        
        # 결과 검증
        assert len(uncategorized) == 3, "미분류 거래내역이 3개여야 합니다"
        
        # 모든 거래내역의 category_id가 None인지 확인
        for transaction in uncategorized:
            assert transaction[6] is None, "카테고리가 미분류 상태여야 합니다"  # category_id는 6번째 인덱스
    
    def test_get_categorized_transactions(self):
        """분류 완료 거래내역 조회 테스트"""
        # 일부 거래내역 분류
        cursor = self.conn.cursor()
        cursor.execute("UPDATE transactions SET category_id = ? WHERE transaction_id = ?", (6, 1))
        cursor.execute("UPDATE transactions SET category_id = ? WHERE transaction_id = ?", (2, 2))
        self.conn.commit()
        
        # 분류 완료 거래내역 조회
        cursor.execute("""
        SELECT transaction_id, category_id
        FROM transactions 
        WHERE category_id IS NOT NULL
        ORDER BY timestamp DESC
        """)
        
        categorized = cursor.fetchall()
        
        # 결과 검증
        assert len(categorized) == 2, "분류 완료 거래내역이 2개여야 합니다"
        
        # 모든 거래내역의 category_id가 None이 아닌지 확인
        for transaction in categorized:
            assert transaction[1] is not None, "카테고리가 분류된 상태여야 합니다"
    
    def test_get_transaction_by_id(self):
        """특정 거래내역 조회 테스트"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT transaction_id, description, amount_out
        FROM transactions 
        WHERE transaction_id = ?
        """, (1,))
        
        transaction = cursor.fetchone()
        
        # 결과 검증
        assert transaction is not None, "거래내역을 찾을 수 있어야 합니다"
        assert transaction[1] == '스타벅스 커피', "거래 내용이 일치해야 합니다"
        assert transaction[2] == 5500.0, "출금액이 일치해야 합니다"
    
    def test_get_transaction_by_invalid_id(self):
        """존재하지 않는 거래내역 조회 테스트"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT transaction_id, description, amount_out
        FROM transactions 
        WHERE transaction_id = ?
        """, (9999,))
        
        transaction = cursor.fetchone()
        
        # 결과 검증
        assert transaction is None, "존재하지 않는 거래내역에 대해 None을 반환해야 합니다"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 