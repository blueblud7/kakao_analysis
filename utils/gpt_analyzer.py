import openai
import pandas as pd
from datetime import datetime
import json
import re

class GPTAnalyzer:
    """GPT를 이용한 채팅 분석 클래스"""
    
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
    
    def analyze_chat(self, data, analysis_type, target_user="전체"):
        """채팅 데이터를 분석"""
        
        # 데이터 전처리
        if target_user != "전체":
            data = data[data['user'] == target_user]
        
        # 메시지가 너무 많으면 최근 메시지로 제한
        if len(data) > 500:
            data = data.tail(500)
        
        # 분석 타입별 프롬프트 생성
        prompt = self.generate_prompt(data, analysis_type, target_user)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 카카오톡 채팅 분석 전문가입니다. 주어진 채팅 데이터를 분석하여 유용한 인사이트를 제공해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            analysis_result = response.choices[0].message.content
            
            # 결과 구조화
            return self.structure_results(analysis_result, analysis_type)
            
        except Exception as e:
            return {
                "summary": f"분석 중 오류가 발생했습니다: {str(e)}",
                "error": True
            }
    
    def generate_prompt(self, data, analysis_type, target_user):
        """분석 타입에 따른 프롬프트 생성"""
        
        # 데이터 요약
        messages_text = "\n".join([
            f"[{row['datetime'].strftime('%Y-%m-%d %H:%M')}] {row['user']}: {row['message']}"
            for _, row in data.iterrows()
        ])
        
        base_info = f"""
분석 대상: {target_user}
총 메시지 수: {len(data)}
기간: {data['datetime'].min().strftime('%Y-%m-%d')} ~ {data['datetime'].max().strftime('%Y-%m-%d')}

채팅 내용:
{messages_text[:4000]}  # 토큰 제한을 위해 앞 부분만
"""
        
        if analysis_type == "종합 분석":
            return f"""
다음 카카오톡 채팅 내용을 종합적으로 분석해주세요:

{base_info}

분석해주세요:
1. 주요 대화 주제들
2. 참여자들의 대화 패턴
3. 중요한 키워드나 이슈
4. 전반적인 분위기나 톤
5. 주목할만한 인사이트

한국어로 상세하게 분석 결과를 제공해주세요.
"""
        
        elif analysis_type == "감정 분석":
            return f"""
다음 카카오톡 채팅의 감정을 분석해주세요:

{base_info}

분석해주세요:
1. 전체적인 감정 톤 (긍정/부정/중립의 비율)
2. 시간대별 감정 변화
3. 주요 감정 표현들
4. 감정이 급변한 지점과 원인
5. 참여자별 감정 특성

결과를 구체적인 예시와 함께 한국어로 제공해주세요.
"""
        
        elif analysis_type == "주요 키워드 추출":
            return f"""
다음 카카오톡 채팅에서 주요 키워드를 추출해주세요:

{base_info}

추출해주세요:
1. 가장 자주 언급된 키워드 TOP 10
2. 인물/기업/제품명
3. 주식/투자 관련 키워드 (있다면)
4. 트렌드/이슈 키워드
5. 감정 키워드

각 키워드의 언급 빈도와 문맥을 포함해서 한국어로 정리해주세요.
"""
        
        elif analysis_type == "토픽 분석":
            return f"""
다음 카카오톡 채팅의 대화 토픽을 분석해주세요:

{base_info}

분석해주세요:
1. 주요 대화 토픽들 (3-5개)
2. 각 토픽별 비중과 중요도
3. 토픽 간의 연관성
4. 시간의 흐름에 따른 토픽 변화
5. 참여자별 관심 토픽

각 토픽을 구체적인 예시와 함께 한국어로 설명해주세요.
"""
        
        elif analysis_type == "요약":
            return f"""
다음 카카오톡 채팅을 요약해주세요:

{base_info}

요약해주세요:
1. 핵심 내용 3-5줄 요약
2. 주요 결정사항이나 합의점
3. 중요한 정보나 공지사항
4. 후속 조치가 필요한 내용
5. 놓치면 안 되는 중요 포인트

간결하고 명확하게 한국어로 요약해주세요.
"""
    
    def structure_results(self, analysis_result, analysis_type):
        """분석 결과를 구조화"""
        
        # 키워드 추출 시도
        keywords = self.extract_keywords_from_text(analysis_result)
        
        result = {
            "summary": analysis_result,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "keywords": keywords
        }
        
        return result
    
    def extract_keywords_from_text(self, text):
        """텍스트에서 키워드 추출"""
        # 간단한 키워드 추출 (개선 가능)
        keywords = []
        
        # 번호 리스트 패턴 (1., 2., - 등)
        patterns = [
            r'\d+\.\s*([^\n]+)',
            r'[-•]\s*([^\n]+)',
            r'TOP\s*\d+[:\s]*([^\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            keywords.extend([match.strip() for match in matches])
        
        return keywords[:10]  # 상위 10개만 반환
    
    def analyze_sentiment_batch(self, messages):
        """메시지 일괄 감정 분석"""
        
        # 메시지를 적절한 크기로 묶어서 분석
        batch_size = 20
        results = []
        
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i+batch_size]
            batch_text = "\n".join([f"{idx}: {msg}" for idx, msg in enumerate(batch)])
            
            prompt = f"""
다음 메시지들의 감정을 분석해서 각각에 대해 '긍정', '부정', '중립' 중 하나로 분류해주세요:

{batch_text}

결과를 다음 형식으로 제공해주세요:
0: 긍정
1: 중립
2: 부정
...
"""
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "당신은 텍스트 감정 분석 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                
                batch_results = self.parse_sentiment_results(response.choices[0].message.content)
                results.extend(batch_results)
                
            except:
                # 오류 시 중립으로 처리
                results.extend(['중립'] * len(batch))
        
        return results
    
    def parse_sentiment_results(self, text):
        """감정 분석 결과 파싱"""
        sentiments = []
        lines = text.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                sentiment = line.split(':')[1].strip()
                if sentiment in ['긍정', '부정', '중립']:
                    sentiments.append(sentiment)
        
        return sentiments 