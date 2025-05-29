"""
AI 분류기 모듈 - 슬라이스 3.2
Author: leehansol
Created: 2025-05-25

OpenAI API를 사용하여 거래 내역에 대한 카테고리를 추천하는 기능을 제공합니다.
"""

import json
import requests
from typing import Dict, List, Any, Optional
from ..db.crud import get_setting, get_categories_for_dropdown


class AIClassifier:
    """OpenAI API를 사용한 AI 분류기 클래스"""
    
    def __init__(self, api_key: str):
        """
        AI 분류기 초기화
        
        Args:
            api_key (str): OpenAI API 키
        
        Raises:
            ValueError: API 키가 없거나 빈 문자열인 경우
        """
        if not api_key:
            raise ValueError("API 키가 필요합니다")
        
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4.1-mini-2025-04-14"


def build_category_suggestion_prompt(transaction: Dict[str, Any], categories: List[str]) -> str:
    """
    거래 내역과 카테고리 목록을 기반으로 AI 추천용 프롬프트를 구성합니다.
    
    Args:
        transaction (Dict[str, Any]): 거래 내역 정보
        categories (List[str]): 사용 가능한 카테고리 목록
    
    Returns:
        str: 구성된 프롬프트 문자열
    
    Raises:
        ValueError: 필수 정보가 누락된 경우
    """
    # 입력 검증
    if not categories:
        raise ValueError("카테고리 목록이 비어있습니다")
    
    description = transaction.get('description', '').strip()
    if not description:
        raise ValueError("거래 설명이 필요합니다")
    
    # 거래 유형 판단 (수입/지출)
    amount_in = transaction.get('amount_in', 0) or 0
    amount_out = transaction.get('amount_out', 0) or 0
    
    if amount_in > 0:
        transaction_type = "수입"
        amount = amount_in
    else:
        transaction_type = "지출"
        amount = amount_out
    
    # 프롬프트 구성
    prompt = f"""다음 거래 내역을 분석하여 가장 적절한 카테고리를 추천해주세요.

거래 정보:
- 설명: {description}
- 금액: {amount:,}원 ({transaction_type})
- 일시: {transaction.get('timestamp', '알 수 없음')}

사용 가능한 카테고리 목록:
{chr(10).join([f"- {category}" for category in categories])}

위 카테고리 목록 중에서 가장 적절한 카테고리 하나만 정확히 선택하여 답변해주세요.
카테고리명만 정확히 반환하고, 추가 설명은 하지 마세요."""

    return prompt


def call_openai_api(api_key: str, prompt: str) -> str:
    """
    OpenAI API를 호출하여 카테고리 추천을 받습니다.
    
    Args:
        api_key (str): OpenAI API 키
        prompt (str): 전송할 프롬프트
    
    Returns:
        str: AI가 추천한 카테고리명
    
    Raises:
        Exception: API 호출 실패 또는 응답 형식 오류
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 100,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API 호출 실패: HTTP {response.status_code} - {response.text}")
        
        response_data = response.json()
        
        # 응답 형식 검증
        if 'choices' not in response_data or not response_data['choices']:
            raise Exception("API 응답 형식이 올바르지 않습니다")
        
        suggested_category = response_data['choices'][0]['message']['content'].strip()
        return suggested_category
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"네트워크 오류: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON 파싱 오류: {str(e)}")
    except Exception as e:
        raise e


def suggest_category_for_transaction(transaction: Dict[str, Any]) -> str:
    """
    거래 내역에 대한 카테고리를 추천합니다.
    
    Args:
        transaction (Dict[str, Any]): 거래 내역 정보
    
    Returns:
        str: 추천된 카테고리명
    
    Raises:
        ValueError: API 키가 설정되지 않은 경우
        Exception: API 호출 실패 또는 기타 오류
    """
    # API 키 확인
    api_key = get_setting('chatgpt_api_key')
    if not api_key:
        raise ValueError("ChatGPT API 키가 설정되지 않았습니다")
    
    # 카테고리 목록 가져오기
    categories = get_categories_for_dropdown()
    
    # 프롬프트 구성
    prompt = build_category_suggestion_prompt(transaction, categories)
    
    # API 호출
    suggested_category = call_openai_api(api_key, prompt)
    
    return suggested_category


def print_category_suggestion(transaction: Dict[str, Any]) -> None:
    """
    거래 내역에 대한 AI 카테고리 추천 결과를 콘솔에 출력합니다.
    
    Args:
        transaction (Dict[str, Any]): 거래 내역 정보
    """
    try:
        print(f"\n{'='*50}")
        print("AI 카테고리 추천 결과")
        print(f"{'='*50}")
        
        # 거래 정보 출력
        description = transaction.get('description', '알 수 없음')
        amount_in = transaction.get('amount_in', 0) or 0
        amount_out = transaction.get('amount_out', 0) or 0
        timestamp = transaction.get('timestamp', '알 수 없음')
        
        print(f"거래 설명: {description}")
        if amount_in > 0:
            print(f"수입 금액: {amount_in:,}원")
        else:
            print(f"지출 금액: {amount_out:,}원")
        print(f"거래 일시: {timestamp}")
        
        # AI 추천 실행
        print("\nAI 분석 중...")
        suggested_category = suggest_category_for_transaction(transaction)
        
        print(f"\n✅ AI 추천 카테고리: {suggested_category}")
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"\n❌ 카테고리 추천 중 오류 발생: {str(e)}")
        print(f"{'='*50}\n") 