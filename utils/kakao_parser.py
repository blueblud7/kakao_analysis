import pandas as pd
import re
from datetime import datetime
import chardet
import io

class KakaoParser:
    """카카오톡 채팅 파일을 파싱하는 클래스"""
    
    def __init__(self):
        # 카카오톡 메시지 패턴 (다양한 형식 지원)
        self.patterns = [
            # 패턴 1: [이름] [오후 1:23] 메시지
            r'\[([^\]]+)\] \[([^\]]+)\] (.+)',
            # 패턴 2: 2023년 12월 1일 오후 1:23, 이름 : 메시지
            r'(\d{4}년 \d{1,2}월 \d{1,2}일 [^\s]+ \d{1,2}:\d{2}), ([^:]+) : (.+)',
            # 패턴 3: 오후 1:23, 이름 : 메시지
            r'([^\s]+ \d{1,2}:\d{2}), ([^:]+) : (.+)',
        ]
    
    def detect_encoding(self, file_content):
        """파일 인코딩 감지"""
        detected = chardet.detect(file_content)
        return detected.get('encoding', 'utf-8')
    
    def parse_file(self, uploaded_file):
        """업로드된 파일을 파싱하여 DataFrame 반환"""
        
        # 파일 내용 읽기
        file_content = uploaded_file.read()
        encoding = self.detect_encoding(file_content)
        
        # 문자열로 변환
        try:
            content = file_content.decode(encoding)
        except:
            content = file_content.decode('utf-8', errors='ignore')
        
        lines = content.split('\n')
        
        messages = []
        current_date = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 날짜 라인 체크
            date_match = re.match(r'(\d{4})년 (\d{1,2})월 (\d{1,2})일', line)
            if date_match:
                year, month, day = date_match.groups()
                current_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                continue
            
            # 메시지 파싱
            message_data = self.parse_message(line, current_date)
            if message_data:
                messages.append(message_data)
        
        if not messages:
            # CSV 형식으로 시도
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=encoding)
                return self.process_csv_format(df)
            except:
                raise ValueError("지원하지 않는 파일 형식입니다.")
        
        df = pd.DataFrame(messages)
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df.sort_values('datetime')
    
    def parse_message(self, line, current_date):
        """메시지 라인을 파싱"""
        
        try:
            for pattern in self.patterns:
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()
                    
                    if len(groups) == 3:
                        # 패턴에 따라 다른 처리
                        if '년' in groups[1] and '월' in groups[1]:  # 날짜가 포함된 경우
                            datetime_str = groups[0]  # 첫 번째 그룹이 datetime
                            user = groups[1]
                            message = groups[2]
                            
                            # 날짜 파싱 시도
                            try:
                                parsed_date = pd.to_datetime(datetime_str)
                                datetime_str = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                # 파싱 실패 시 기본값 사용
                                datetime_str = f"{current_date or datetime.now().strftime('%Y-%m-%d')} 12:00:00"
                        else:
                            user = groups[0]
                            time_str = groups[1]
                            message = groups[2]
                            
                            # 시간 파싱
                            datetime_str = self.parse_time(time_str, current_date)
                    
                        return {
                            'datetime': datetime_str,
                            'user': user.strip(),
                            'message': message.strip()
                        }
        except Exception:
            # 파싱 실패 시 None 반환
            pass
        
        return None
    
    def parse_time(self, time_str, current_date):
        """시간 문자열을 datetime으로 변환"""
        if not current_date:
            current_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # 오전/오후 처리
            if '오후' in time_str:
                time_part = time_str.replace('오후', '').strip()
                # 콜론으로 분리하여 시간과 분 추출
                time_parts = time_part.split(':')
                if len(time_parts) != 2:
                    return f"{current_date} 12:00:00"  # 기본값
                
                try:
                    hour, minute = int(time_parts[0]), int(time_parts[1])
                    if hour != 12:
                        hour += 12
                except ValueError:
                    return f"{current_date} 12:00:00"  # 기본값
                    
            elif '오전' in time_str:
                time_part = time_str.replace('오전', '').strip()
                time_parts = time_part.split(':')
                if len(time_parts) != 2:
                    return f"{current_date} 00:00:00"  # 기본값
                
                try:
                    hour, minute = int(time_parts[0]), int(time_parts[1])
                    if hour == 12:
                        hour = 0
                except ValueError:
                    return f"{current_date} 00:00:00"  # 기본값
            else:
                # 24시간 형식
                time_parts = time_str.split(':')
                if len(time_parts) != 2:
                    return f"{current_date} 12:00:00"  # 기본값
                
                try:
                    hour, minute = int(time_parts[0]), int(time_parts[1])
                except ValueError:
                    return f"{current_date} 12:00:00"  # 기본값
            
            # 시간 범위 검증
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                return f"{current_date} 12:00:00"  # 기본값
            
            return f"{current_date} {hour:02d}:{minute:02d}:00"
        
        except Exception:
            # 모든 예외 상황에서 기본값 반환
            return f"{current_date} 12:00:00"
    
    def process_csv_format(self, df):
        """CSV 형식 데이터 처리"""
        # CSV 컬럼명 매핑
        column_mapping = {
            'Date': 'datetime',
            'User': 'user', 
            'Message': 'message',
            '날짜': 'datetime',
            '사용자': 'user',
            '메시지': 'message'
        }
        
        # 컬럼명 변경
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # 필수 컬럼 확인
        required_columns = ['datetime', 'user', 'message']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"필수 컬럼이 누락되었습니다: {missing_columns}")
        
        # 날짜 형식 변환
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        return df 