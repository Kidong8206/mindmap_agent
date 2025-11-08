import os
import time
import json
from anthropic import Anthropic

class GPTCaller:
    """Anthropic Claude API 호출 래퍼"""
    
    def __init__(self, api_key=None):
        self.client = Anthropic(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-sonnet-4-5-20250929"
    
    def call(self, prompt_file, replacements, retry=True):
        """
        Claude API 호출
        
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
        
        # JSON 출력 강제 지시 추가
        prompt += "\n\n중요: 반드시 유효한 JSON 형식으로만 응답하세요. 다른 텍스트는 포함하지 마세요."
        
        try:
            # Claude API 호출
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 응답 텍스트 추출
            response_text = response.content[0].text.strip()
            
            # ```json ... ``` 제거
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # JSON 파싱
            result = json.loads(response_text)
            return result
            
        except json.JSONDecodeError as e:
            print(f"⚠ JSON 파싱 실패: {e}")
            print(f"응답: {response_text[:200]}...")
            
            if retry:
                print("⏳ 5초 후 재시도...")
                time.sleep(5)
                return self.call(prompt_file, replacements, retry=False)
            else:
                raise
                
        except Exception as e:
            print(f"⚠ API 호출 실패: {e}")
            
            if retry:
                print("⏳ 5초 후 재시도...")
                time.sleep(5)
                return self.call(prompt_file, replacements, retry=False)
            else:
                raise
