import pandas as pd
import re
from datetime import datetime, timedelta

class DataProcessor:
    """데이터 필터링 및 전처리 클래스"""
    
    def __init__(self):
        # 불용어 리스트 (한국어)
        self.stopwords = [
            '이', '그', '저', '것', '들', '은', '는', '이', '가', '을', '를', '에', '의', '와', '과',
            '도', '만', '부터', '까지', '로', '으로', '에서', '한테', '께', '한테서', '께서',
            '이다', '아니다', '있다', '없다', '되다', '하다', '좋다', '나쁘다', '크다', '작다',
            'ㅋㅋ', 'ㅎㅎ', 'ㅠㅠ', 'ㅜㅜ', 'ㅠ', 'ㅜ', '...'
        ]
    
    def filter_data(self, data, start_date, end_date, selected_users, keywords):
        """데이터 필터링"""
        
        filtered_data = data.copy()
        
        # 날짜 필터링
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date) + timedelta(days=1)
        
        filtered_data = filtered_data[
            (filtered_data['datetime'] >= start_datetime) & 
            (filtered_data['datetime'] < end_datetime)
        ]
        
        # 사용자 필터링
        if selected_users and '전체' not in selected_users:
            filtered_data = filtered_data[filtered_data['user'].isin(selected_users)]
        
        # 키워드 필터링
        if keywords:
            keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
            if keyword_list:
                # 키워드 중 하나라도 포함된 메시지만 선택
                keyword_pattern = '|'.join(re.escape(kw) for kw in keyword_list)
                filtered_data = filtered_data[
                    filtered_data['message'].str.contains(keyword_pattern, case=False, na=False)
                ]
        
        return filtered_data.reset_index(drop=True)
    
    def clean_message(self, message):
        """메시지 텍스트 정리"""
        if pd.isna(message):
            return ""
        
        # 특수 문자 및 이모티콘 제거 (선택적)
        # 기본적인 정리만 수행
        cleaned = str(message).strip()
        
        # 과도한 반복 문자 제거 (예: ㅋㅋㅋㅋㅋ -> ㅋㅋ)
        cleaned = re.sub(r'(.)\1{3,}', r'\1\1', cleaned)
        
        return cleaned
    
    def extract_mentions(self, data):
        """멘션(@) 추출"""
        mentions = []
        
        for message in data['message']:
            if pd.isna(message):
                continue
            
            # @로 시작하는 멘션 찾기
            mention_pattern = r'@([^\s]+)'
            found_mentions = re.findall(mention_pattern, str(message))
            mentions.extend(found_mentions)
        
        return list(set(mentions))  # 중복 제거
    
    def extract_hashtags(self, data):
        """해시태그(#) 추출"""
        hashtags = []
        
        for message in data['message']:
            if pd.isna(message):
                continue
            
            # #로 시작하는 해시태그 찾기
            hashtag_pattern = r'#([^\s]+)'
            found_hashtags = re.findall(hashtag_pattern, str(message))
            hashtags.extend(found_hashtags)
        
        return list(set(hashtags))  # 중복 제거
    
    def get_user_statistics(self, data):
        """사용자별 통계 생성"""
        stats = {}
        
        for user in data['user'].unique():
            user_data = data[data['user'] == user]
            
            stats[user] = {
                'message_count': len(user_data),
                'avg_message_length': user_data['message'].str.len().mean(),
                'first_message': user_data['datetime'].min(),
                'last_message': user_data['datetime'].max(),
                'most_active_hour': user_data['datetime'].dt.hour.mode().iloc[0] if len(user_data) > 0 else 0
            }
        
        return stats
    
    def get_time_statistics(self, data):
        """시간별 통계 생성"""
        stats = {}
        
        # 시간대별 메시지 수
        hourly_counts = data.groupby(data['datetime'].dt.hour).size()
        stats['hourly_distribution'] = hourly_counts.to_dict()
        
        # 요일별 메시지 수
        daily_counts = data.groupby(data['datetime'].dt.dayofweek).size()
        day_names = ['월', '화', '수', '목', '금', '토', '일']
        stats['daily_distribution'] = {
            day_names[i]: daily_counts.get(i, 0) for i in range(7)
        }
        
        # 월별 메시지 수
        monthly_counts = data.groupby(data['datetime'].dt.to_period('M')).size()
        stats['monthly_distribution'] = {
            str(period): count for period, count in monthly_counts.items()
        }
        
        return stats
    
    def detect_conversation_threads(self, data, time_threshold_minutes=30):
        """대화 스레드 감지 (연속적인 대화 세션)"""
        data = data.sort_values('datetime').copy()
        data['time_diff'] = data['datetime'].diff().dt.total_seconds() / 60  # 분 단위
        
        # 새로운 스레드 시작점 찾기
        data['new_thread'] = (data['time_diff'] > time_threshold_minutes) | (data['time_diff'].isna())
        data['thread_id'] = data['new_thread'].cumsum()
        
        threads = []
        for thread_id in data['thread_id'].unique():
            thread_data = data[data['thread_id'] == thread_id]
            
            threads.append({
                'thread_id': thread_id,
                'start_time': thread_data['datetime'].min(),
                'end_time': thread_data['datetime'].max(),
                'duration_minutes': (thread_data['datetime'].max() - thread_data['datetime'].min()).total_seconds() / 60,
                'message_count': len(thread_data),
                'participants': thread_data['user'].unique().tolist(),
                'first_message': thread_data.iloc[0]['message']
            })
        
        return threads
    
    def extract_keywords_frequency(self, data, min_length=2, top_n=20):
        """메시지에서 키워드 빈도 추출"""
        
        # 모든 메시지 결합
        all_text = ' '.join(data['message'].dropna().astype(str))
        
        # 한글만 추출 (공백 포함)
        korean_text = re.sub(r'[^가-힣\s]', ' ', all_text)
        
        # 단어 분리 (간단한 공백 기준)
        words = korean_text.split()
        
        # 길이 조건 및 불용어 제거
        filtered_words = [
            word for word in words 
            if len(word) >= min_length and word not in self.stopwords
        ]
        
        # 빈도 계산
        word_freq = pd.Series(filtered_words).value_counts()
        
        return word_freq.head(top_n).to_dict()
    
    def analyze_response_patterns(self, data):
        """응답 패턴 분석"""
        data = data.sort_values('datetime').copy()
        
        patterns = []
        
        for i in range(1, len(data)):
            current_msg = data.iloc[i]
            prev_msg = data.iloc[i-1]
            
            # 응답 시간 계산
            response_time = (current_msg['datetime'] - prev_msg['datetime']).total_seconds()
            
            # 같은 사용자의 연속 메시지가 아닌 경우만
            if current_msg['user'] != prev_msg['user'] and response_time < 3600:  # 1시간 이내
                patterns.append({
                    'from_user': prev_msg['user'],
                    'to_user': current_msg['user'],
                    'response_time_seconds': response_time,
                    'prev_message': prev_msg['message'],
                    'response_message': current_msg['message']
                })
        
        # 평균 응답 시간 계산
        if patterns:
            avg_response_time = pd.DataFrame(patterns)['response_time_seconds'].mean()
            return {
                'patterns': patterns,
                'avg_response_time_seconds': avg_response_time,
                'total_conversations': len(patterns)
            }
        
        return {'patterns': [], 'avg_response_time_seconds': 0, 'total_conversations': 0} 