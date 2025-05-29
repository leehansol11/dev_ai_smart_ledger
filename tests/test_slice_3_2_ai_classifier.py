"""
슬라이스 3.2: OpenAI API 연동 및 카테고리 추천 기능 테스트
Author: leehansol
Created: 2025-05-25

TDD 방식으로 구현:
1. OpenAI API와 통신하는 기본 모듈 테스트
2. 거래 내역과 카테고리 목록을 포함하는 프롬프트 구성 테스트
3. API 호출 및 응답 처리 테스트
4. 콘솔 출력 테스트
"""

import pytest
import unittest.mock as mock
from unittest.mock import patch, MagicMock
import json
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_smart_ledger.app.core.ai_classifier import (
    AIClassifier,
    build_category_suggestion_prompt,
    call_openai_api,
    suggest_category_for_transaction
)
from ai_smart_ledger.app.db.crud import save_setting, get_setting


class TestAIClassifier:
    """AI 분류기 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.test_api_key = "test-api-key-12345"
        self.test_transaction = {
            'transaction_id': 1,
            'description': '스타벅스 강남점',
            'amount_out': 5500,
            'amount_in': 0,
            'timestamp': '2025-01-15 14:30:00'
        }
        self.test_categories = [
            "식비 > 카페/음료",
            "식비 > 식당/외식",
            "교통비 > 대중교통",
            "생활비 > 마트/편의점",
            "계좌 간 이체 (분석 제외)"
        ]
    
    def test_ai_classifier_initialization(self):
        """AI 분류기 초기화 테스트"""
        classifier = AIClassifier(self.test_api_key)
        assert classifier.api_key == self.test_api_key
        assert classifier.base_url == "https://api.openai.com/v1/chat/completions"
        assert classifier.model == "gpt-3.5-turbo"
    
    def test_ai_classifier_initialization_without_api_key(self):
        """API 키 없이 초기화 시 예외 발생 테스트"""
        with pytest.raises(ValueError, match="API 키가 필요합니다"):
            AIClassifier(None)
        
        with pytest.raises(ValueError, match="API 키가 필요합니다"):
            AIClassifier("")


class TestPromptBuilder:
    """프롬프트 구성 함수 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.test_transaction = {
            'description': '스타벅스 강남점',
            'amount_out': 5500,
            'amount_in': 0,
            'timestamp': '2025-01-15 14:30:00'
        }
        self.test_categories = [
            "식비 > 카페/음료",
            "식비 > 식당/외식",
            "교통비 > 대중교통",
            "생활비 > 마트/편의점",
            "계좌 간 이체 (분석 제외)"
        ]
    
    def test_build_category_suggestion_prompt_basic(self):
        """기본 프롬프트 구성 테스트"""
        prompt = build_category_suggestion_prompt(self.test_transaction, self.test_categories)
        
        # 프롬프트에 필수 요소들이 포함되어 있는지 확인
        assert "스타벅스 강남점" in prompt
        assert "5,500" in prompt  # 콤마 포맷팅된 숫자 확인
        assert "식비 > 카페/음료" in prompt
        assert "카테고리를 추천해주세요" in prompt or "분류해주세요" in prompt
    
    def test_build_category_suggestion_prompt_with_income(self):
        """수입 거래에 대한 프롬프트 구성 테스트"""
        income_transaction = {
            'description': '급여',
            'amount_out': 0,
            'amount_in': 3000000,
            'timestamp': '2025-01-25 09:00:00'
        }
        
        prompt = build_category_suggestion_prompt(income_transaction, self.test_categories)
        
        assert "급여" in prompt
        assert "3,000,000" in prompt  # 콤마 포맷팅된 숫자 확인
        assert "수입" in prompt or "입금" in prompt
    
    def test_build_category_suggestion_prompt_empty_categories(self):
        """빈 카테고리 목록에 대한 처리 테스트"""
        with pytest.raises(ValueError, match="카테고리 목록이 비어있습니다"):
            build_category_suggestion_prompt(self.test_transaction, [])
    
    def test_build_category_suggestion_prompt_missing_description(self):
        """거래 설명이 없는 경우 처리 테스트"""
        transaction_without_desc = {
            'description': '',
            'amount_out': 5500,
            'amount_in': 0,
            'timestamp': '2025-01-15 14:30:00'
        }
        
        with pytest.raises(ValueError, match="거래 설명이 필요합니다"):
            build_category_suggestion_prompt(transaction_without_desc, self.test_categories)


class TestOpenAIAPICall:
    """OpenAI API 호출 함수 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.test_api_key = "test-api-key-12345"
        self.test_prompt = "스타벅스 강남점에서 5500원을 지출했습니다. 다음 카테고리 중 가장 적절한 것을 추천해주세요: 식비 > 카페/음료, 식비 > 식당/외식"
    
    @patch('requests.post')
    def test_call_openai_api_success(self, mock_post):
        """OpenAI API 호출 성공 테스트"""
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "식비 > 카페/음료"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # API 호출 테스트
        result = call_openai_api(self.test_api_key, self.test_prompt)
        
        # 결과 검증
        assert result == "식비 > 카페/음료"
        
        # API 호출이 올바른 파라미터로 이루어졌는지 확인
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        assert call_args[1]['headers']['Authorization'] == f"Bearer {self.test_api_key}"
        assert call_args[1]['headers']['Content-Type'] == "application/json"
        
        request_data = json.loads(call_args[1]['data'])
        assert request_data['model'] == "gpt-3.5-turbo"
        assert request_data['messages'][0]['content'] == self.test_prompt
    
    @patch('requests.post')
    def test_call_openai_api_http_error(self, mock_post):
        """OpenAI API HTTP 오류 테스트"""
        # Mock 응답 설정 (HTTP 오류)
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        # API 호출 시 예외 발생 확인
        with pytest.raises(Exception, match="API 호출 실패"):
            call_openai_api(self.test_api_key, self.test_prompt)
    
    @patch('requests.post')
    def test_call_openai_api_connection_error(self, mock_post):
        """OpenAI API 연결 오류 테스트"""
        # Mock 연결 오류 설정
        mock_post.side_effect = Exception("Connection error")
        
        # API 호출 시 예외 발생 확인
        with pytest.raises(Exception, match="Connection error"):
            call_openai_api(self.test_api_key, self.test_prompt)
    
    @patch('requests.post')
    def test_call_openai_api_invalid_response_format(self, mock_post):
        """OpenAI API 잘못된 응답 형식 테스트"""
        # Mock 응답 설정 (잘못된 형식)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": []  # 빈 choices 배열
        }
        mock_post.return_value = mock_response
        
        # API 호출 시 예외 발생 확인
        with pytest.raises(Exception, match="API 응답 형식이 올바르지 않습니다"):
            call_openai_api(self.test_api_key, self.test_prompt)


class TestCategorySuggestion:
    """카테고리 추천 통합 함수 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.test_transaction = {
            'transaction_id': 1,
            'description': '스타벅스 강남점',
            'amount_out': 5500,
            'amount_in': 0,
            'timestamp': '2025-01-15 14:30:00'
        }
        self.test_categories = [
            "식비 > 카페/음료",
            "식비 > 식당/외식",
            "교통비 > 대중교통"
        ]
    
    @patch('ai_smart_ledger.app.core.ai_classifier.call_openai_api')
    @patch('ai_smart_ledger.app.core.ai_classifier.get_setting')
    @patch('ai_smart_ledger.app.core.ai_classifier.get_categories_for_dropdown')
    def test_suggest_category_for_transaction_success(self, mock_get_categories, mock_get_setting, mock_api_call):
        """거래에 대한 카테고리 추천 성공 테스트"""
        # Mock 설정
        mock_get_setting.return_value = "test-api-key-12345"
        mock_get_categories.return_value = self.test_categories
        mock_api_call.return_value = "식비 > 카페/음료"
        
        # 함수 호출
        result = suggest_category_for_transaction(self.test_transaction)
        
        # 결과 검증
        assert result == "식비 > 카페/음료"
        
        # Mock 함수들이 올바르게 호출되었는지 확인
        mock_get_setting.assert_called_once_with('chatgpt_api_key')
        mock_get_categories.assert_called_once()
        mock_api_call.assert_called_once()
    
    @patch('ai_smart_ledger.app.core.ai_classifier.get_setting')
    def test_suggest_category_for_transaction_no_api_key(self, mock_get_setting):
        """API 키가 없는 경우 테스트"""
        # Mock 설정 (API 키 없음)
        mock_get_setting.return_value = None
        
        # 함수 호출 시 예외 발생 확인
        with pytest.raises(ValueError, match="ChatGPT API 키가 설정되지 않았습니다"):
            suggest_category_for_transaction(self.test_transaction)
    
    @patch('ai_smart_ledger.app.core.ai_classifier.call_openai_api')
    @patch('ai_smart_ledger.app.core.ai_classifier.get_setting')
    @patch('ai_smart_ledger.app.core.ai_classifier.get_categories_for_dropdown')
    def test_suggest_category_for_transaction_api_error(self, mock_get_categories, mock_get_setting, mock_api_call):
        """API 호출 오류 시 테스트"""
        # Mock 설정
        mock_get_setting.return_value = "test-api-key-12345"
        mock_get_categories.return_value = self.test_categories
        mock_api_call.side_effect = Exception("API 호출 실패")
        
        # 함수 호출 시 예외 발생 확인
        with pytest.raises(Exception, match="API 호출 실패"):
            suggest_category_for_transaction(self.test_transaction)


class TestConsoleOutput:
    """콘솔 출력 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.test_transaction = {
            'transaction_id': 1,
            'description': '스타벅스 강남점',
            'amount_out': 5500,
            'amount_in': 0,
            'timestamp': '2025-01-15 14:30:00'
        }
    
    @patch('ai_smart_ledger.app.core.ai_classifier.suggest_category_for_transaction')
    @patch('builtins.print')
    def test_console_output_success(self, mock_print, mock_suggest):
        """성공적인 카테고리 추천 시 콘솔 출력 테스트"""
        # Mock 설정
        mock_suggest.return_value = "식비 > 카페/음료"
        
        # 콘솔 출력 함수 호출 (실제 구현에서 만들 예정)
        from ai_smart_ledger.app.core.ai_classifier import print_category_suggestion
        print_category_suggestion(self.test_transaction)
        
        # 콘솔 출력 확인
        mock_print.assert_called()
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        
        # 출력 내용에 거래 정보와 추천 카테고리가 포함되어 있는지 확인
        output_text = ' '.join(print_calls)
        assert "스타벅스 강남점" in output_text
        assert "식비 > 카페/음료" in output_text
        assert "AI 추천 카테고리" in output_text or "추천" in output_text
    
    @patch('ai_smart_ledger.app.core.ai_classifier.suggest_category_for_transaction')
    @patch('builtins.print')
    def test_console_output_error(self, mock_print, mock_suggest):
        """카테고리 추천 실패 시 콘솔 출력 테스트"""
        # Mock 설정 (오류 발생)
        mock_suggest.side_effect = Exception("API 호출 실패")
        
        # 콘솔 출력 함수 호출
        from ai_smart_ledger.app.core.ai_classifier import print_category_suggestion
        print_category_suggestion(self.test_transaction)
        
        # 오류 메시지 출력 확인
        mock_print.assert_called()
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        
        output_text = ' '.join(print_calls)
        assert "오류" in output_text or "실패" in output_text


if __name__ == "__main__":
    pytest.main([__file__]) 