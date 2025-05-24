import openai
from openai import OpenAI
import pandas as pd
from datetime import datetime
import json
import re
import os

class GPTAnalyzer:
    """GPT를 이용한 채팅 분석 클래스"""
    
    def __init__(self, api_key):
        """OpenAI 클라이언트 초기화"""
        self.model = "gpt-4o-mini"
        
        # API 키 검증
        if not api_key or not api_key.startswith('sk-'):
            raise Exception("유효하지 않은 OpenAI API 키입니다.")
        
        try:
            # OpenAI 1.0+ 버전 방식으로 클라이언트 초기화
            self.client = OpenAI(api_key=api_key)
            
            print(f"✅ OpenAI API 키 설정 완료 (모델: {self.model})")
            
        except Exception as e:
            print(f"❌ OpenAI API 키 설정 실패: {str(e)}")
            raise Exception(f"OpenAI API 설정 실패. 원인: {str(e)}")
    
    def analyze_chat(self, data, analysis_type, target_user="전체", detailed=False, include_context=True):
        """채팅 데이터를 분석"""
        
        # 데이터 전처리
        if target_user != "전체":
            data = data[data['user'] == target_user]
        
        # 메시지가 너무 많으면 최근 메시지로 제한
        limit = 800 if detailed else 500
        if len(data) > limit:
            data = data.tail(limit)
        
        # 분석 타입별 프롬프트 생성
        prompt = self.generate_prompt(data, analysis_type, target_user, include_context, detailed)
        
        try:
            max_tokens = 3000 if detailed else 2000
            
            # OpenAI 1.0+ 버전 API 호출 방식
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 카카오톡 채팅 분석 전문가입니다. 주어진 채팅 데이터를 분석하여 유용한 인사이트를 제공해주세요. 한국어로 자세하고 구체적으로 답변해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            analysis_result = response.choices[0].message.content
            
            # 결과 구조화 (향상된 버전 사용)
            return self.structure_advanced_results(analysis_result, f"{analysis_type} 분석", data)
            
        except Exception as e:
            return {
                "summary": f"분석 중 오류가 발생했습니다: {str(e)}",
                "error": True,
                "analysis_type": analysis_type
            }
    
    def generate_prompt(self, data, analysis_type, target_user, include_context=True, detailed=False):
        """분석 타입에 따른 프롬프트 생성"""
        
        # 데이터 요약
        if include_context:
            messages_text = "\n".join([
                f"[{row['datetime'].strftime('%Y-%m-%d %H:%M')}] {row['user']}: {row['message']}"
                for _, row in data.iterrows()
            ])
        else:
            messages_text = "\n".join([
                f"{row['user']}: {row['message']}"
                for _, row in data.iterrows()
            ])
        
        # 토큰 제한 조정
        max_chars = 6000 if detailed else 4000
        if len(messages_text) > max_chars:
            messages_text = messages_text[:max_chars] + "\n... (더 많은 메시지가 있습니다)"
        
        # 사용자별 통계
        user_stats = data['user'].value_counts().head(3).to_dict()
        stats_text = "\n".join([f"- {user}: {count}개 메시지" for user, count in user_stats.items()])
        
        base_info = f"""
📊 **분석 개요:**
- 분석 대상: {target_user}
- 총 메시지 수: {len(data):,}개
- 참여자 수: {data['user'].nunique()}명
- 분석 기간: {data['datetime'].min().strftime('%Y-%m-%d')} ~ {data['datetime'].max().strftime('%Y-%m-%d')}

👥 **주요 참여자:**
{stats_text}

💬 **채팅 내용:**
{messages_text}
"""
        
        if analysis_type == "종합 분석" or analysis_type == "전체 분석":
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
        
        elif analysis_type == "주요 주제 분석" or analysis_type == "토픽 분석":
            return f"""
다음 카카오톡 채팅의 주요 주제들을 분석해주세요:

{base_info}

분석해주세요:
1. 주요 대화 토픽들 (3-5개)
2. 각 토픽별 비중과 중요도
3. 토픽 간의 연관성
4. 시간의 흐름에 따른 토픽 변화
5. 참여자별 관심 토픽

각 토픽을 구체적인 예시와 함께 한국어로 설명해주세요.
"""
        
        elif analysis_type == "사용자 특성 분석":
            return f"""
다음 카카오톡 채팅에서 사용자들의 특성을 분석해주세요:

{base_info}

분석해주세요:
1. 주요 참여자들의 대화 스타일
2. 각 사용자별 관심사와 화제
3. 메시지 패턴과 활동성
4. 사용자 간의 상호작용 특성
5. 개성적인 언어 사용 패턴

각 사용자의 특징을 구체적으로 한국어로 분석해주세요.
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
        
        else:
            # 기본 분석 (예상치 못한 분석 타입의 경우)
            return f"""
다음 카카오톡 채팅을 "{analysis_type}" 관점에서 분석해주세요:

{base_info}

요청하신 "{analysis_type}" 분석을 수행하고, 관련된 인사이트와 패턴을 찾아서 한국어로 자세히 설명해주세요.
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
    
    def analyze_chat_with_custom_prompt(self, data, custom_prompt, target_user="전체", detailed=False, include_context=True):
        """커스텀 프롬프트로 채팅 데이터 분석"""
        
        # 데이터 전처리
        if target_user != "전체" and target_user != "비교 분석":
            data = data[data['user'] == target_user]
        
        # 메시지가 너무 많으면 샘플링
        if len(data) > 1000:
            if detailed:
                # 상세 분석 시에는 더 많은 데이터 사용
                data = data.tail(800)
            else:
                data = data.tail(500)
        
        # 프롬프트 생성
        full_prompt = self.generate_custom_prompt(data, custom_prompt, include_context, detailed)
        
        try:
            # 토큰 수에 따라 모델 선택
            max_tokens = 3000 if detailed else 2000
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 카카오톡 채팅 분석 전문가입니다. 주어진 채팅 데이터를 정확하고 통찰력 있게 분석하여 유용한 인사이트를 제공해주세요. 한국어로 자세하고 구체적으로 답변해주세요."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            analysis_result = response.choices[0].message.content
            
            # 결과 구조화 (향상된 버전)
            return self.structure_advanced_results(analysis_result, custom_prompt, data)
            
        except Exception as e:
            return {
                "summary": f"분석 중 오류가 발생했습니다: {str(e)}",
                "error": True,
                "analysis_mode": "커스텀 분석"
            }
    
    def generate_custom_prompt(self, data, custom_prompt, include_context=True, detailed=False):
        """커스텀 프롬프트 생성"""
        
        # 데이터 요약 정보
        total_messages = len(data)
        unique_users = data['user'].nunique()
        date_range = f"{data['datetime'].min().strftime('%Y-%m-%d')} ~ {data['datetime'].max().strftime('%Y-%m-%d')}"
        
        # 사용자별 메시지 수 통계
        user_stats = data['user'].value_counts().head(5).to_dict()
        stats_text = "\n".join([f"- {user}: {count}개 메시지" for user, count in user_stats.items()])
        
        # 메시지 텍스트 준비
        if include_context:
            # 시간 순서와 대화 맥락 포함
            messages_text = "\n".join([
                f"[{row['datetime'].strftime('%m-%d %H:%M')}] {row['user']}: {row['message']}"
                for _, row in data.iterrows()
            ])
        else:
            # 단순 메시지만
            messages_text = "\n".join([
                f"{row['user']}: {row['message']}"
                for _, row in data.iterrows()
            ])
        
        # 토큰 제한 (detailed 모드에 따라 조정)
        max_chars = 6000 if detailed else 4000
        if len(messages_text) > max_chars:
            messages_text = messages_text[:max_chars] + "\n... (메시지가 더 있습니다)"
        
        base_info = f"""
📊 **데이터 개요:**
- 총 메시지 수: {total_messages:,}개
- 참여자 수: {unique_users}명
- 분석 기간: {date_range}

👥 **주요 참여자별 메시지 수:**
{stats_text}

💬 **채팅 내용:**
{messages_text}
"""
        
        full_prompt = f"""
{custom_prompt}

{base_info}

위 데이터를 바탕으로 요청된 분석을 수행해주세요. 구체적인 예시와 데이터를 인용하며 분석해주세요.
"""
        
        return full_prompt
    
    def structure_advanced_results(self, analysis_result, custom_prompt, data):
        """향상된 분석 결과 구조화"""
        
        # 키워드 추출 (향상된 버전)
        keywords = self.extract_advanced_keywords(analysis_result)
        
        # 인사이트 추출
        insights = self.extract_insights(analysis_result)
        
        # 권장사항 추출
        recommendations = self.extract_recommendations(analysis_result)
        
        result = {
            "summary": analysis_result,
            "custom_prompt": custom_prompt[:100] + "..." if len(custom_prompt) > 100 else custom_prompt,
            "timestamp": datetime.now().isoformat(),
            "keywords": keywords,
            "insights": insights,
            "recommendations": recommendations,
            "data_stats": {
                "total_messages": len(data),
                "unique_users": data['user'].nunique(),
                "date_range": f"{data['datetime'].min().strftime('%Y-%m-%d')} ~ {data['datetime'].max().strftime('%Y-%m-%d')}"
            }
        }
        
        return result
    
    def extract_advanced_keywords(self, text):
        """향상된 키워드 추출"""
        keywords = []
        
        # 다양한 패턴으로 키워드 추출
        patterns = [
            r'주요 키워드[:\s]*([^\n]+)',
            r'핵심 키워드[:\s]*([^\n]+)',
            r'키워드[:\s]*([^\n]+)',
            r'\*\*([^*]+)\*\*',  # **키워드** 형태
            r'「([^」]+)」',      # 「키워드」 형태
            r'\'([^\']+)\'',     # '키워드' 형태
            r'\"([^\"]+)\"',     # "키워드" 형태
            r'\d+\.\s*([^\n:]+)[:\n]',  # 번호 리스트
            r'[-•]\s*([^\n:]+)[:\n]',   # 불릿 포인트
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean_keyword = match.strip().replace(':', '').replace('\n', ' ')
                if 2 <= len(clean_keyword) <= 50:  # 적절한 길이의 키워드만
                    keywords.append(clean_keyword)
        
        # 중복 제거 및 상위 키워드 반환
        unique_keywords = list(dict.fromkeys(keywords))
        return unique_keywords[:15]
    
    def extract_insights(self, text):
        """인사이트 추출"""
        insights = []
        
        # 인사이트를 나타내는 패턴들
        insight_patterns = [
            r'인사이트[:\s]*([^\n]+)',
            r'통찰[:\s]*([^\n]+)',
            r'주목할[^:]*[:\s]*([^\n]+)',
            r'흥미로운[^:]*[:\s]*([^\n]+)',
            r'특징적인[^:]*[:\s]*([^\n]+)',
            r'눈에 띄는[^:]*[:\s]*([^\n]+)',
            r'중요한 점[:\s]*([^\n]+)',
            r'핵심[^:]*[:\s]*([^\n]+)'
        ]
        
        for pattern in insight_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean_insight = match.strip()
                if 10 <= len(clean_insight) <= 200:
                    insights.append(clean_insight)
        
        return insights[:8]
    
    def extract_recommendations(self, text):
        """권장사항 추출"""
        recommendations = []
        
        # 권장사항을 나타내는 패턴들
        recommendation_patterns = [
            r'권장[^:]*[:\s]*([^\n]+)',
            r'제안[^:]*[:\s]*([^\n]+)',
            r'개선[^:]*[:\s]*([^\n]+)',
            r'향후[^:]*[:\s]*([^\n]+)',
            r'앞으로[^:]*[:\s]*([^\n]+)',
            r'고려사항[:\s]*([^\n]+)',
            r'주의[^:]*[:\s]*([^\n]+)'
        ]
        
        for pattern in recommendation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean_rec = match.strip()
                if 10 <= len(clean_rec) <= 200:
                    recommendations.append(clean_rec)
        
        return recommendations[:5]
    
    def analyze_topic(self, data, topic, analysis_type="토픽 분석"):
        """특정 주제 분석"""
        # 주제 관련 메시지 필터링
        topic_data = data[data['message'].str.contains(topic, case=False, na=False)]
        
        if len(topic_data) == 0:
            return {
                "summary": f"'{topic}' 관련 메시지를 찾을 수 없습니다.",
                "keywords": [],
                "insights": [],
                "analysis_type": f"{topic} 분석"
            }
        
        prompt = f"""
다음은 '{topic}' 주제와 관련된 카카오톡 채팅 메시지들입니다:

총 {len(topic_data)}개의 관련 메시지 (전체 {len(data)}개 중)
기간: {topic_data['datetime'].min().strftime('%Y-%m-%d')} ~ {topic_data['datetime'].max().strftime('%Y-%m-%d')}

관련 메시지들:
{chr(10).join([f"[{row['datetime'].strftime('%m-%d %H:%M')}] {row['user']}: {row['message']}" for _, row in topic_data.head(100).iterrows()])}

'{topic}' 주제에 대해 다음을 분석해주세요:
1. 주제에 대한 전반적인 의견과 분위기
2. 주요 논점들과 쟁점
3. 참여자들의 관심도와 반응
4. 관련 키워드와 언급 빈도
5. 시간의 흐름에 따른 변화

한국어로 구체적으로 분석해주세요.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 주제별 채팅 분석 전문가입니다. 특정 주제에 대한 대화 내용을 심층 분석해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.7
            )
            
            analysis_result = response.choices[0].message.content
            return self.structure_advanced_results(analysis_result, f"{topic} 분석", topic_data)
            
        except Exception as e:
            return {
                "summary": f"'{topic}' 분석 중 오류가 발생했습니다: {str(e)}",
                "error": True,
                "analysis_type": f"{topic} 분석"
            }
    
    def analyze_user(self, data, user, analysis_type="사용자 분석"):
        """특정 사용자 분석"""
        user_data = data[data['user'] == user]
        
        if len(user_data) == 0:
            return {
                "summary": f"'{user}' 사용자의 메시지를 찾을 수 없습니다.",
                "keywords": [],
                "insights": [],
                "analysis_type": f"{user} 분석"
            }
        
        # 사용자 통계
        total_messages = len(user_data)
        time_range = f"{user_data['datetime'].min().strftime('%Y-%m-%d')} ~ {user_data['datetime'].max().strftime('%Y-%m-%d')}"
        avg_length = user_data['message'].str.len().mean()
        
        prompt = f"""
'{user}' 사용자의 채팅 패턴을 분석해주세요:

📊 기본 통계:
- 총 메시지 수: {total_messages}개
- 활동 기간: {time_range}
- 평균 메시지 길이: {avg_length:.1f}자

최근 메시지들:
{chr(10).join([f"[{row['datetime'].strftime('%m-%d %H:%M')}] {row['message']}" for _, row in user_data.tail(50).iterrows()])}

다음을 분석해주세요:
1. 주요 관심사와 화제
2. 메시지 스타일과 특징
3. 활동 패턴 (시간대, 빈도 등)
4. 자주 사용하는 키워드
5. 대화 참여 스타일과 성향

한국어로 구체적으로 분석해주세요.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 사용자 행동 분석 전문가입니다. 개인의 채팅 패턴과 특성을 분석해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.7
            )
            
            analysis_result = response.choices[0].message.content
            return self.structure_advanced_results(analysis_result, f"{user} 분석", user_data)
            
        except Exception as e:
            return {
                "summary": f"'{user}' 분석 중 오류가 발생했습니다: {str(e)}",
                "error": True,
                "analysis_type": f"{user} 분석"
            }
    
    def compare_users(self, data, users, analysis_type="비교 분석"):
        """여러 사용자 비교 분석"""
        if len(users) < 2:
            return {
                "summary": "비교 분석을 위해서는 최소 2명의 사용자가 필요합니다.",
                "keywords": [],
                "insights": [],
                "analysis_type": "비교 분석"
            }
        
        # 각 사용자별 데이터 수집
        user_stats = {}
        user_messages = {}
        
        for user in users:
            user_data = data[data['user'] == user]
            if len(user_data) > 0:
                user_stats[user] = {
                    "message_count": len(user_data),
                    "avg_length": user_data['message'].str.len().mean(),
                    "date_range": f"{user_data['datetime'].min().strftime('%m-%d')} ~ {user_data['datetime'].max().strftime('%m-%d')}"
                }
                user_messages[user] = user_data.tail(20)  # 최근 20개 메시지
        
        # 통계 텍스트 생성
        stats_text = "\n".join([
            f"**{user}**: {stats['message_count']}개 메시지, 평균 {stats['avg_length']:.1f}자, 활동기간: {stats['date_range']}"
            for user, stats in user_stats.items()
        ])
        
        # 메시지 샘플 생성
        messages_text = ""
        for user, messages in user_messages.items():
            messages_text += f"\n### {user}의 최근 메시지:\n"
            messages_text += "\n".join([f"- {row['message']}" for _, row in messages.iterrows()])
            messages_text += "\n"
        
        prompt = f"""
다음 사용자들을 비교 분석해주세요: {', '.join(users)}

📊 기본 통계:
{stats_text}

📝 메시지 샘플:
{messages_text}

다음을 비교 분석해주세요:
1. 각 사용자의 커뮤니케이션 스타일
2. 관심사와 주제 선호도 차이
3. 메시지 패턴과 활동성
4. 언어 사용 특징 (이모티콘, 줄임말 등)
5. 대화 참여 방식의 차이점

각 사용자의 특징을 구체적으로 비교해서 한국어로 분석해주세요.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 사용자 비교 분석 전문가입니다. 여러 사용자의 채팅 패턴을 비교하여 각자의 특징과 차이점을 분석해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            analysis_result = response.choices[0].message.content
            
            # 비교 분석용 데이터 결합
            compare_data = pd.concat([data[data['user'] == user] for user in users if user in data['user'].values])
            
            return self.structure_advanced_results(analysis_result, f"{', '.join(users)} 비교 분석", compare_data)
            
        except Exception as e:
            return {
                "summary": f"사용자 비교 분석 중 오류가 발생했습니다: {str(e)}",
                "error": True,
                "analysis_type": "비교 분석"
            }
    
    def custom_analysis(self, data, custom_prompt):
        """커스텀 분석"""
        return self.analyze_chat_with_custom_prompt(data, custom_prompt)