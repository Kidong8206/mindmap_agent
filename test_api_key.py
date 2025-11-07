#!/usr/bin/env python3
"""
Quick script to test if the OpenAI API key is valid
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_api_key():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ API 키를 찾을 수 없습니다. .env 파일을 확인하세요.")
        return False

    print(f"🔑 API 키 확인 중... (앞 20자: {api_key[:20]}...)")

    try:
        client = OpenAI(api_key=api_key)

        # Test 1: List models
        print("\n📋 테스트 1: 사용 가능한 모델 목록 가져오기...")
        models = client.models.list()
        print(f"✅ 성공! {len(list(models.data))}개의 모델을 찾았습니다.")

        # Test 2: Simple chat completion
        print("\n💬 테스트 2: 간단한 채팅 완성 테스트...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'API key is working!' in Korean"}
            ],
            max_tokens=50
        )
        print(f"✅ 성공! 응답: {response.choices[0].message.content}")

        print("\n" + "="*50)
        print("🎉 API 키가 정상적으로 작동합니다!")
        print("="*50)
        return True

    except Exception as e:
        print(f"\n❌ API 키 검증 실패!")
        print(f"에러: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_key()
