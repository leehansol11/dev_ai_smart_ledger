"""
슬라이스 3.2 데모 스크립트
Author: leehansol
Created: 2025-05-25

실제 거래 내역으로 AI 카테고리 추천 기능을 테스트합니다.
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_smart_ledger.app.core.ai_classifier import print_category_suggestion
from ai_smart_ledger.app.db.crud import save_setting, get_setting


def setup_demo_api_key():
    """데모용 API 키 설정 (실제 사용 시에는 유효한 API 키 필요)"""
    # API 키가 설정되어 있는지 확인
    current_key = get_setting('chatgpt_api_key')
    
    # 유효하지 않은 테스트 키들 목록
    invalid_test_keys = [
        "your-openai-api-key-here",
        "test-api-key-12345", 
        "new_test_api_key_67890",
        "sk-test",
        None,
        ""
    ]
    
    if not current_key or current_key in invalid_test_keys or current_key.startswith("test") or current_key.startswith("new_test"):
        print("⚠️ 유효한 OpenAI API 키가 설정되지 않았습니다.")
        print("실제 테스트를 위해서는 유효한 API 키가 필요합니다.")
        print("설정 방법:")
        print("1. OpenAI 계정에서 API 키 발급")
        print("2. save_setting('chatgpt_api_key', 'your-actual-api-key') 호출")
        print(f"현재 설정된 키: {current_key}")
        return False
    
    print(f"✅ API 키가 설정되어 있습니다: {current_key[:10]}...")
    return True


def demo_category_suggestions():
    """다양한 거래 내역으로 카테고리 추천 데모"""
    
    # 테스트용 거래 내역들
    test_transactions = [
        {
            'transaction_id': 1,
            'description': '스타벅스 강남점',
            'amount_out': 5500,
            'amount_in': 0,
            'timestamp': '2025-01-15 14:30:00'
        },
        {
            'transaction_id': 2,
            'description': '지하철 교통카드 충전',
            'amount_out': 10000,
            'amount_in': 0,
            'timestamp': '2025-01-16 08:15:00'
        },
        {
            'transaction_id': 3,
            'description': '이마트 생필품 구매',
            'amount_out': 45000,
            'amount_in': 0,
            'timestamp': '2025-01-17 19:20:00'
        },
        {
            'transaction_id': 4,
            'description': '급여 입금',
            'amount_out': 0,
            'amount_in': 3000000,
            'timestamp': '2025-01-25 09:00:00'
        },
        {
            'transaction_id': 5,
            'description': '맥도날드 햄버거',
            'amount_out': 8900,
            'amount_in': 0,
            'timestamp': '2025-01-18 12:30:00'
        }
    ]
    
    print("="*60)
    print("슬라이스 3.2: AI 카테고리 추천 데모")
    print("="*60)
    
    # API 키 확인
    has_valid_api_key = setup_demo_api_key()
    
    if not has_valid_api_key:
        print("\n🔧 Mock 데이터로 데모를 진행합니다...")
        demo_with_mock_data(test_transactions)
        return
    
    print(f"\n📋 총 {len(test_transactions)}개의 거래 내역으로 AI 추천을 테스트합니다.")
    print("⚠️ 실제 OpenAI API를 호출하므로 비용이 발생할 수 있습니다.")
    
    # 사용자 확인
    user_input = input("\n계속 진행하시겠습니까? (y/N): ").strip().lower()
    if user_input not in ['y', 'yes']:
        print("데모를 취소합니다.")
        return
    
    for i, transaction in enumerate(test_transactions, 1):
        print(f"\n[{i}/{len(test_transactions)}] 거래 내역 분석 중...")
        try:
            print_category_suggestion(transaction)
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
            print("API 키가 유효하지 않거나 네트워크 연결을 확인해주세요.")
            print("Mock 데이터 모드로 전환합니다...")
            demo_with_mock_data(test_transactions[i-1:])
            return
        
        # 마지막 거래가 아닌 경우에만 사용자 입력 대기
        if i < len(test_transactions):
            user_input = input("다음 거래로 넘어가시겠습니까? (y/N): ").strip().lower()
            if user_input not in ['y', 'yes']:
                print("데모를 중단합니다.")
                return


def demo_with_mock_data(test_transactions):
    """Mock 데이터로 데모 진행"""
    from ai_smart_ledger.app.core.ai_classifier import build_category_suggestion_prompt
    from ai_smart_ledger.app.db.crud import get_categories_for_dropdown
    
    print("\n📋 프롬프트 구성 예시를 보여드립니다:\n")
    
    # 카테고리 목록 가져오기
    try:
        categories = get_categories_for_dropdown()
        print(f"✅ 사용 가능한 카테고리: {len(categories)}개")
    except Exception as e:
        print(f"❌ 카테고리 로드 실패: {e}")
        # 기본 카테고리 사용
        categories = [
            "식비 > 카페/음료",
            "식비 > 식당/외식",
            "교통비 > 대중교통",
            "생활비 > 마트/편의점",
            "수입 > 급여",
            "계좌 간 이체 (분석 제외)"
        ]
        print(f"기본 카테고리 {len(categories)}개를 사용합니다.")
    
    # 몇 개의 거래에 대해 프롬프트 예시 생성
    demo_transactions = test_transactions[:3]  # 처음 3개만 데모
    
    for i, transaction in enumerate(demo_transactions, 1):
        print(f"\n[{i}/{len(demo_transactions)}] 거래 내역: {transaction['description']}")
        
        try:
            prompt = build_category_suggestion_prompt(transaction, categories)
            print(f"\n📝 생성된 프롬프트:")
            print("-" * 50)
            print(prompt)
            print("-" * 50)
            
            # Mock AI 응답 생성
            mock_response = generate_mock_ai_response(transaction)
            print(f"\n🤖 Mock AI 추천 카테고리: {mock_response}")
            
        except Exception as e:
            print(f"❌ 프롬프트 생성 실패: {e}")
        
        if i < len(demo_transactions):
            input("\n다음 거래로 넘어가려면 Enter를 누르세요...")
    
    print(f"\n✅ Mock 데모가 완료되었습니다!")
    print(f"실제 OpenAI API 키를 설정하면 진짜 AI 추천을 받을 수 있습니다.")


def generate_mock_ai_response(transaction):
    """Mock AI 응답 생성"""
    description = transaction.get('description', '').lower()
    
    # 간단한 키워드 기반 매칭
    if '스타벅스' in description or '카페' in description or '커피' in description:
        return "식비 > 카페/음료"
    elif '지하철' in description or '교통카드' in description or '버스' in description:
        return "교통비 > 대중교통"
    elif '이마트' in description or '마트' in description or '편의점' in description:
        return "생활비 > 마트/편의점"
    elif '급여' in description or '월급' in description:
        return "수입 > 급여"
    elif '맥도날드' in description or '햄버거' in description or '치킨' in description:
        return "식비 > 식당/외식"
    else:
        return "기타 > 분류 필요"


if __name__ == "__main__":
    demo_category_suggestions() 