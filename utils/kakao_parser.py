import pandas as pd
import re
from datetime import datetime
import chardet
import io
import streamlit as st

class KakaoParser:
    """카카오톡 채팅 파일을 파싱하는 클래스"""
    
    def __init__(self):
        # 카카오톡 메시지 패턴 (다양한 형식 지원)
        self.patterns = [
            r'(\d{4}\.\d{1,2}\.\d{1,2}\s+\d{1,2}:\d{2}), (.+?) : (.+)',  # 기본 형식
            r'(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{2}:\d{2}), (.+?) : (.+)',  # 대안 형식
            r'(.+?)\s+(\d{4}\.\d{1,2}\.\d{1,2}\s+\d{1,2}:\d{2}), (.+)',  # 사용자 먼저
            r'(.+?), (\d{4}\.\d{1,2}\.\d{1,2}\s+\d{1,2}:\d{2}) : (.+)',  # 다른 형식
            r'(.+?) \[(\d{4}년 \d{1,2}월 \d{1,2}일 .+?)\] (.+)',  # 년월일 형식
        ]
    
    def detect_encoding(self, file_content):
        """파일 인코딩 감지 (성능 최적화)"""
        # 첫 10000바이트만 사용해서 빠르게 감지
        sample = file_content[:10000] if len(file_content) > 10000 else file_content
        detected = chardet.detect(sample)
        return detected['encoding'] or 'utf-8'
    
    def parse_file(self, uploaded_file):
        """파일 파싱 (속도 최적화)"""
        print(f"🔍 파일 파싱 시작: {uploaded_file.name}")
        print(f"📁 파일 크기: {uploaded_file.size} bytes")
        
        # 파일 내용 읽기
        file_content = uploaded_file.read()
        encoding = self.detect_encoding(file_content)
        print(f"🔤 감지된 인코딩: {encoding}")
        
        # 텍스트 디코딩
        try:
            text = file_content.decode(encoding)
        except UnicodeDecodeError:
            text = file_content.decode('utf-8', errors='ignore')
        
        print(f"📝 파일 내용 길이: {len(text)} 문자")
        print(f"📝 첫 500 문자:")
        print(text[:500])
        
        lines = text.strip().split('\n')
        print(f"📄 총 라인 수: {len(lines)}")
        
        # 디버깅: 첫 10줄 출력
        for i, line in enumerate(lines[:10]):
            print(f"라인 {i}: '{line}'")
        
        # 일반 카카오톡 형식으로 파싱 시도
        messages = []
        current_date = None
        
        # 진행률 표시를 위한 progress bar
        if len(lines) > 1000:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        for i, line in enumerate(lines):
            # 진행률 업데이트 (1000줄 이상일 때만)
            if len(lines) > 1000 and i % max(1, len(lines) // 100) == 0:
                progress = min(i / len(lines), 1.0)
                progress_bar.progress(progress)
                status_text.text(f"파싱 진행률: {progress*100:.1f}% ({i:,}/{len(lines):,} 줄)")
            
            # 날짜 라인 체크
            if re.match(r'.*\d{4}년 \d{1,2}월 \d{1,2}일.*', line):
                date_match = re.search(r'(\d{4})년 (\d{1,2})월 (\d{1,2})일', line)
                if date_match:
                    year, month, day = date_match.groups()
                    current_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                continue
            
            # 메시지 파싱
            parsed = self.parse_message(line, current_date)
            if parsed:
                messages.append(parsed)
        
        if len(lines) > 1000:
            progress_bar.empty()
            status_text.empty()
        
        print(f"🎯 일반 형식으로 파싱된 메시지 수: {len(messages)}")
        
        # 일반 형식으로 파싱이 안 되면 CSV 형식으로 시도
        if len(messages) < 10:  # 파싱된 메시지가 너무 적으면
            print("🔄 CSV 형식으로 재시도...")
            try:
                # CSV 파싱 시도
                uploaded_file.seek(0)
                
                # 여러 구분자와 인코딩 조합 시도
                separators = [',', '\t', ';', '|']
                encodings = ['UTF-8-SIG', 'utf-8', 'cp949', 'euc-kr']
                
                df = None
                for sep in separators:
                    for enc in encodings:
                        try:
                            uploaded_file.seek(0)
                            # 첫 1000줄만 시도해서 빠른 검증
                            df_test = pd.read_csv(uploaded_file, encoding=enc, sep=sep, nrows=100)
                            if len(df_test.columns) >= 3:  # 최소 3개 컬럼 필요
                                uploaded_file.seek(0)
                                # pandas 호환성을 위해 kwargs 사용
                                csv_kwargs = {
                                    'encoding': enc,
                                    'sep': sep,
                                    'on_bad_lines': 'skip',  # 문제가 있는 행 건너뛰기
                                    'low_memory': False
                                }
                                try:
                                    df = pd.read_csv(uploaded_file, **csv_kwargs)
                                except TypeError:
                                    # 구버전 pandas의 경우 on_bad_lines 없음
                                    csv_kwargs.pop('on_bad_lines', None)
                                    df = pd.read_csv(uploaded_file, **csv_kwargs)
                                
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