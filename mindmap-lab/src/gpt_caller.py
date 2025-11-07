import os
import time
import json
from openai import OpenAI

class GPTCaller:
    """GPT API 호출 래퍼 (temperature=0.0, JSON 강제)"""
    
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"
    
    def call(self, prompt_file, replacements, retry=True):
        """
        GPT API 호출
        
        Args:
            prompt_file: 프롬프트 파일 경로
            replacements: {placeholder: value} 딕셔너리
            retry: 실패 시 재시도 여부
        
        Returns:
            dict: 파싱된 JSON 응답
        """
        # 프롬프트 로드
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read()
        
        # 플레이스홀더 치환
        for key, value in replacements.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False, indent=2)
            prompt = prompt.replace(f'{{{key}}}', str(value))
        
        try:
            # API 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,  # 결정적 출력
                response_format={"type": "json_object"}  # JSON 강제
            )
            
            # JSON 파싱
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"⚠ API 호출 실패: {e}")
            
            # 재시도
            if retry:
                print("⏳ 5초 후 재시도...")
                time.sleep(5)
                return self.call(prompt_file, replacements, retry=False)
            else:
                raise
