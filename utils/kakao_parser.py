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
        
        print(f"🔍 파일 파싱 시작: {uploaded_file.name}")
        
        # 파일 내용 읽기
        file_content = uploaded_file.read()
        print(f"📁 파일 크기: {len(file_content)} bytes")
        
        encoding = self.detect_encoding(file_content)
        print(f"🔤 감지된 인코딩: {encoding}")
        
        # 문자열로 변환
        try:
            content = file_content.decode(encoding)
        except:
            content = file_content.decode('utf-8', errors='ignore')
            print("⚠️ 인코딩 변경: utf-8로 fallback")
        
        print(f"📝 파일 내용 길이: {len(content)} 문자")
        print(f"📝 첫 500 문자:\n{content[:500]}")
        
        lines = content.split('\n')
        print(f"📄 총 라인 수: {len(lines)}")
        
        messages = []
        current_date = None
        
        for i, line in enumerate(lines[:10]):  # 처음 10줄만 디버깅
            line = line.strip()
            print(f"라인 {i}: '{line}'")
            if not line:
                continue
                
            # 날짜 라인 체크
            date_match = re.match(r'(\d{4})년 (\d{1,2})월 (\d{1,2})일', line)
            if date_match:
                year, month, day = date_match.groups()
                current_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                print(f"📅 날짜 라인 감지: {current_date}")
                continue
            
            # 메시지 파싱
            message_data = self.parse_message(line, current_date)
            if message_data:
                messages.append(message_data)
                print(f"✅ 메시지 파싱 성공: {message_data}")
        
        print(f"🎯 일반 형식으로 파싱된 메시지 수: {len(messages)}")
        
        if not messages:
            print("🔄 CSV 형식으로 재시도...")
            # CSV 형식으로 시도
            try:
                uploaded_file.seek(0)
                
                # 다양한 구분자와 인코딩으로 시도
                separators = [',', '\t', ';', '|']
                encodings = [encoding, 'utf-8', 'cp949', 'euc-kr']
                
                df = None
                for sep in separators:
                    for enc in encodings:
                        try:
                            uploaded_file.seek(0)
                            df = pd.read_csv(uploaded_file, encoding=enc, sep=sep)
                            print(f"✅ CSV 읽기 성공 - 구분자: '{sep}', 인코딩: {enc}")
                            print(f"📊 읽은 데이터 크기: {len(df)} 행, {len(df.columns)} 열")
                            print(f"📊 컬럼명: {df.columns.tolist()}")
                            break
                        except Exception as e:
                            print(f"❌ 시도 실패 (구분자: '{sep}', 인코딩: {enc}): {str(e)}")
                            continue
                    if df is not None:
                        break
                
                if df is None:
                    raise ValueError("모든 CSV 파싱 시도 실패")
                
                return self.process_csv_format(df)
            except Exception as e:
                print(f"❌ CSV 파싱 완전 실패: {str(e)}")
                raise ValueError(f"지원하지 않는 파일 형식입니다: {str(e)}")
        
        print("✅ 일반 형식으로 파싱 완료")
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
        print(f"📊 원본 CSV 데이터 크기: {len(df)} 행")  # 디버깅용
        print(f"📊 컬럼명: {df.columns.tolist()}")  # 디버깅용
        
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
        
        # 빈 행 제거
        df = df.dropna(subset=['datetime', 'user', 'message'])
        print(f"📊 빈 행 제거 후: {len(df)} 행")  # 디버깅용
        
        # 날짜 형식 변환 (새로운 형식 지원)
        def parse_datetime(date_str):
            if pd.isna(date_str):
                return None
                
            date_str = str(date_str).strip()
            
            # 여러 날짜 형식 시도
            formats = [
                '%Y.%m.%d %H:%M',     # 2024.1.20 16:25
                '%Y-%m-%d %H:%M:%S',  # 2024-01-20 16:25:00
                '%Y/%m/%d %H:%M',     # 2024/1/20 16:25
                '%Y.%m.%d %H:%M:%S',  # 2024.1.20 16:25:00
                '%Y-%m-%d',           # 2024-01-20
                '%Y.%m.%d',           # 2024.1.20
            ]
            
            for fmt in formats:
                try:
                    return pd.to_datetime(date_str, format=fmt)
                except ValueError:
                    continue
            
            # 마지막으로 pandas의 자동 파싱 시도
            try:
                return pd.to_datetime(date_str)
            except:
                print(f"⚠️ 날짜 파싱 실패: {date_str}")
                return None
        
        # 모든 행에 날짜 파싱 적용
        df['datetime'] = df['datetime'].apply(parse_datetime)
        
        # 파싱 실패한 행 제거
        before_count = len(df)
        df = df.dropna(subset=['datetime'])
        after_count = len(df)
        
        if before_count != after_count:
            print(f"⚠️ 날짜 파싱 실패로 {before_count - after_count}개 행 제거됨")
        
        print(f"📊 최종 데이터 크기: {len(df)} 행")  # 디버깅용
        
        return df.sort_values('datetime') 