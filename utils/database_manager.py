import sqlite3
import pandas as pd
import json
from datetime import datetime
import os
import hashlib

class DatabaseManager:
    """분석 결과 저장 및 관리를 위한 데이터베이스 클래스"""
    
    def __init__(self, db_path="kakao_analysis.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """안전한 데이터베이스 연결 획득"""
        conn = sqlite3.connect(
            self.db_path,
            timeout=30.0,  # 30초 타임아웃
            check_same_thread=False  # 멀티스레드 지원
        )
        # WAL 모드로 설정 (여러 연결이 동시에 읽을 수 있음)
        conn.execute('PRAGMA journal_mode=WAL;')
        # 외래 키 제약 조건 활성화
        conn.execute('PRAGMA foreign_keys=ON;')
        return conn

    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 기존 테이블 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = [row[0] for row in cursor.fetchall()]
        
            # 채팅방 테이블 (새로 추가)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_name TEXT NOT NULL,
                    room_hash TEXT UNIQUE,  -- 채팅방 식별용 해시
                    participants TEXT,      -- JSON 형태로 참여자 목록 저장
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 파일 정보 테이블 (새로 추가)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER,
                    file_name TEXT NOT NULL,
                    file_path TEXT,
                    file_hash TEXT UNIQUE,  -- 파일 중복 검사용
                    file_size INTEGER,
                    message_count INTEGER,
                    start_date TEXT,
                    end_date TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (room_id) REFERENCES chat_rooms (id)
                )
            ''')
            
            # 분석 세션 테이블 (기존 호환성 유지)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    room_id INTEGER,
                    file_ids TEXT,  -- JSON 형태로 파일 ID 목록
                    file_name TEXT,  -- 기존 호환성 유지
                    total_messages INTEGER,
                    participants_count INTEGER,
                    start_date TEXT,
                    end_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    FOREIGN KEY (room_id) REFERENCES chat_rooms (id)
                )
            ''')
            
            # 채팅 데이터 테이블 - 기존 테이블 구조 확인 후 마이그레이션
            if 'chat_messages' in existing_tables:
                # 기존 테이블의 컬럼 확인
                cursor.execute("PRAGMA table_info(chat_messages)")
                columns = [row[1] for row in cursor.fetchall()]
                
                # 새로운 컬럼이 없으면 추가
                if 'room_id' not in columns:
                    cursor.execute('ALTER TABLE chat_messages ADD COLUMN room_id INTEGER')
                if 'file_id' not in columns:
                    cursor.execute('ALTER TABLE chat_messages ADD COLUMN file_id INTEGER')
                if 'message_hash' not in columns:
                    cursor.execute('ALTER TABLE chat_messages ADD COLUMN message_hash TEXT')
            else:
                # 새로운 테이블 생성
                cursor.execute('''
                    CREATE TABLE chat_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        room_id INTEGER,
                        file_id INTEGER,
                        session_id INTEGER,  -- 기존 호환성 유지
                        datetime TEXT,
                        user TEXT,
                        message TEXT,
                        message_length INTEGER,
                        message_hash TEXT,  -- 중복 방지용 해시
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (room_id) REFERENCES chat_rooms (id),
                        FOREIGN KEY (file_id) REFERENCES chat_files (id),
                        FOREIGN KEY (session_id) REFERENCES analysis_sessions (id)
                    )
                ''')
            
            # GPT 분석 결과 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gpt_analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    analysis_type TEXT,
                    target_user TEXT,
                    summary TEXT,
                    keywords TEXT,  -- JSON 형태로 저장
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES analysis_sessions (id)
                )
            ''')
            
            # 사용자 통계 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    user TEXT,
                    message_count INTEGER,
                    avg_message_length REAL,
                    most_active_hour INTEGER,
                    first_message TEXT,
                    last_message TEXT,
                    FOREIGN KEY (session_id) REFERENCES analysis_sessions (id)
                )
            ''')
            
            # 시간대별 통계 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS time_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    hour INTEGER,
                    message_count INTEGER,
                    FOREIGN KEY (session_id) REFERENCES analysis_sessions (id)
                )
            ''')
            
            # 분석 결과 히스토리 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_name TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    analysis_mode TEXT,
                    target_user TEXT,
                    prompt TEXT,
                    result_summary TEXT,
                    keywords TEXT,
                    insights TEXT,
                    recommendations TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            if 'conn' in locals():
                conn.close()
            raise
    
    def create_message_hash(self, datetime_str, user, message):
        """메시지 중복 방지용 해시 생성"""
        content = f"{datetime_str}|{user}|{message}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def create_room_hash(self, participants):
        """채팅방 식별용 해시 생성"""
        sorted_participants = sorted(participants)
        content = "|".join(sorted_participants)
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def create_file_hash(self, file_path, file_name):
        """파일 중복 검사용 해시 생성"""
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()
        else:
            # 파일이 없는 경우 파일명과 현재 시간으로 해시 생성
            content = f"{file_name}|{datetime.now().isoformat()}"
            return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get_or_create_chat_room(self, participants):
        """채팅방 조회 또는 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        room_hash = self.create_room_hash(participants)
        
        # 기존 채팅방 확인
        cursor.execute('SELECT id FROM chat_rooms WHERE room_hash = ?', (room_hash,))
        result = cursor.fetchone()
        
        if result:
            room_id = result[0]
        else:
            # 새 채팅방 생성
            room_name = f"채팅방 ({len(participants)}명)"
            if len(participants) <= 3:
                room_name = ", ".join(participants[:3])
            
            cursor.execute('''
                INSERT INTO chat_rooms (room_name, room_hash, participants)
                VALUES (?, ?, ?)
            ''', (room_name, room_hash, json.dumps(participants, ensure_ascii=False)))
            
            room_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return room_id
    
    def get_all_rooms(self):
        """모든 채팅방 목록 조회"""
        conn = self.get_connection()
        
        try:
            # 테이블 존재 여부 확인
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_rooms';")
            chat_rooms_exists = cursor.fetchone() is not None
            
            if not chat_rooms_exists:
                # 채팅방 테이블이 없으면 빈 DataFrame 반환
                conn.close()
                return pd.DataFrame(columns=['id', 'room_name', 'participants', 'file_count', 'total_messages', 'first_message', 'last_message', 'participants_list', 'participant_count', 'created_at', 'last_activity'])
            
            # 컬럼 존재 여부 확인
            cursor.execute("PRAGMA table_info(chat_messages)")
            columns = [row[1] for row in cursor.fetchall()]
            has_room_id = 'room_id' in columns
            
            if has_room_id:
                # 새로운 스키마 사용
                rooms_df = pd.read_sql_query('''
                    SELECT cr.id, cr.room_name, cr.participants, cr.created_at,
                           COUNT(DISTINCT cf.id) as file_count,
                           COUNT(cm.id) as total_messages,
                           COUNT(DISTINCT cm.user) as participant_count,
                           MIN(cm.datetime) as first_message,
                           MAX(cm.datetime) as last_message,
                           MAX(cm.datetime) as last_activity
                    FROM chat_rooms cr
                    LEFT JOIN chat_files cf ON cr.id = cf.room_id
                    LEFT JOIN chat_messages cm ON cr.id = cm.room_id
                    GROUP BY cr.id, cr.room_name, cr.participants, cr.created_at
                    ORDER BY last_message DESC
                ''', conn)
            else:
                # 기존 스키마 사용
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis_sessions';")
                if cursor.fetchone():
                    rooms_df = pd.read_sql_query('''
                        SELECT id, session_name as room_name, 
                               '[]' as participants,
                               1 as file_count,
                               total_messages,
                               participants_count as participant_count,
                               start_date as first_message,
                               end_date as last_message,
                               created_at,
                               end_date as last_activity
                        FROM analysis_sessions
                        ORDER BY created_at DESC
                    ''', conn)
                else:
                    rooms_df = pd.DataFrame(columns=['id', 'room_name', 'participants', 'file_count', 'total_messages', 'first_message', 'last_message', 'participant_count', 'created_at', 'last_activity'])
            
            # participants JSON 파싱
            if not rooms_df.empty and 'participants' in rooms_df.columns:
                rooms_df['participants_list'] = rooms_df['participants'].apply(
                    lambda x: json.loads(x) if x and x != '[]' else []
                )
            else:
                rooms_df['participants_list'] = [[] for _ in range(len(rooms_df))]
            
            # 누락된 컬럼 추가
            required_columns = ['participant_count', 'created_at', 'last_activity']
            for col in required_columns:
                if col not in rooms_df.columns:
                    rooms_df[col] = 0 if 'count' in col else ''
        
        except Exception as e:
            print(f"Database error in get_all_rooms: {e}")
            rooms_df = pd.DataFrame(columns=['id', 'room_name', 'participants', 'file_count', 'total_messages', 'first_message', 'last_message', 'participants_list', 'participant_count', 'created_at', 'last_activity'])
        finally:
            conn.close()
        
        return rooms_df
    
    def delete_chat_room(self, room_id):
        """채팅방 완전 삭제 (모든 관련 데이터 포함)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 컬럼 존재 여부 확인
            cursor.execute("PRAGMA table_info(chat_messages)")
            columns = [row[1] for row in cursor.fetchall()]
            has_room_id = 'room_id' in columns
            
            if has_room_id:
                # 새로운 스키마 사용
                cursor.execute('DELETE FROM chat_messages WHERE room_id = ?', (room_id,))
                cursor.execute('DELETE FROM chat_files WHERE room_id = ?', (room_id,))
                
                # 분석 세션과 관련 데이터 삭제
                cursor.execute('SELECT id FROM analysis_sessions WHERE room_id = ?', (room_id,))
                session_ids = [row[0] for row in cursor.fetchall()]
                
                for session_id in session_ids:
                    cursor.execute('DELETE FROM gpt_analysis_results WHERE session_id = ?', (session_id,))
                    cursor.execute('DELETE FROM user_statistics WHERE session_id = ?', (session_id,))
                    cursor.execute('DELETE FROM time_statistics WHERE session_id = ?', (session_id,))
                
                cursor.execute('DELETE FROM analysis_sessions WHERE room_id = ?', (room_id,))
                cursor.execute('DELETE FROM chat_rooms WHERE id = ?', (room_id,))
            else:
                # 기존 스키마 사용
                cursor.execute('DELETE FROM gpt_analysis_results WHERE session_id = ?', (room_id,))
                cursor.execute('DELETE FROM user_statistics WHERE session_id = ?', (room_id,))
                cursor.execute('DELETE FROM time_statistics WHERE session_id = ?', (room_id,))
                cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (room_id,))
                cursor.execute('DELETE FROM analysis_sessions WHERE id = ?', (room_id,))
            
            conn.commit()
            deleted_count = cursor.rowcount
            
        except Exception as e:
            conn.rollback()
            print(f"Delete room error: {e}")
            raise e
        finally:
            conn.close()
        
        return deleted_count > 0
    
    def save_analysis_session(self, session_name, chat_data, file_name=None, description=None):
        """분석 세션 저장"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 세션 정보 저장
        cursor.execute('''
            INSERT INTO analysis_sessions 
            (session_name, file_name, total_messages, participants_count, start_date, end_date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_name,
            file_name,
            len(chat_data),
            chat_data['user'].nunique(),
            chat_data['datetime'].min().isoformat(),
            chat_data['datetime'].max().isoformat(),
            description
        ))
        
        session_id = cursor.lastrowid
        
        # 채팅 메시지 저장
        chat_records = []
        for _, row in chat_data.iterrows():
            chat_records.append((
                session_id,
                row['datetime'].isoformat(),
                row['user'],
                row['message'],
                len(row['message']) if pd.notna(row['message']) else 0
            ))
        
        cursor.executemany('''
            INSERT INTO chat_messages 
            (session_id, datetime, user, message, message_length)
            VALUES (?, ?, ?, ?, ?)
        ''', chat_records)
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def get_session_data(self, session_id):
        """특정 세션의 채팅 데이터 조회"""
        conn = self.get_connection()
        
        chat_df = pd.read_sql_query('''
            SELECT datetime, user, message, message_length
            FROM chat_messages 
            WHERE session_id = ?
            ORDER BY datetime
        ''', conn, params=[session_id])
        
        # datetime 컬럼을 datetime 타입으로 변환
        chat_df['datetime'] = pd.to_datetime(chat_df['datetime'])
        
        conn.close()
        return chat_df 
    
    def save_chat_file(self, room_id, file_name, file_path, file_size, message_count, start_date, end_date):
        """채팅 파일 정보 저장"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        file_hash = self.create_file_hash(file_path, file_name)
        
        # 기존 파일 확인
        cursor.execute('SELECT id FROM chat_files WHERE file_hash = ?', (file_hash,))
        result = cursor.fetchone()
        
        if result:
            file_id = result[0]
        else:
            # 새 파일 정보 저장
            cursor.execute('''
                INSERT INTO chat_files 
                (room_id, file_name, file_path, file_hash, file_size, message_count, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (room_id, file_name, file_path, file_hash, file_size, message_count, start_date, end_date))
            
            file_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return file_id
    
    def save_messages(self, room_id, file_id, session_id, chat_data):
        """채팅 메시지 저장"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 채팅 메시지 저장
        chat_records = []
        for _, row in chat_data.iterrows():
            message_hash = self.create_message_hash(
                row['datetime'].isoformat(),
                row['user'],
                row['message']
            )
            
            # 중복 메시지 확인
            cursor.execute('SELECT id FROM chat_messages WHERE message_hash = ?', (message_hash,))
            if cursor.fetchone() is None:
                chat_records.append((
                    room_id,
                    file_id,
                    session_id,
                    row['datetime'].isoformat(),
                    row['user'],
                    row['message'],
                    len(row['message']) if pd.notna(row['message']) else 0,
                    message_hash
                ))
        
        if chat_records:
            cursor.executemany('''
                INSERT INTO chat_messages 
                (room_id, file_id, session_id, datetime, user, message, message_length, message_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', chat_records)
        
        conn.commit()
        conn.close()
        return len(chat_records)
    
    def save_chat_file_complete(self, file_path, file_name, chat_data):
        """완전한 채팅 파일 저장 (채팅방 생성 + 파일 정보 + 메시지)"""
        try:
            # 참여자 목록 추출
            participants = chat_data['user'].unique().tolist()
            
            # 채팅방 생성 또는 조회
            room_id = self.get_or_create_chat_room(participants)
            
            # 파일 정보 저장
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            message_count = len(chat_data)
            start_date = chat_data['datetime'].min().isoformat()
            end_date = chat_data['datetime'].max().isoformat()
            
            file_id = self.save_chat_file(room_id, file_name, file_path, file_size, message_count, start_date, end_date)
            
            # 분석 세션 생성
            session_id = self.save_analysis_session(
                f"{file_name} 분석",
                chat_data,
                file_name,
                f"자동 생성된 분석 세션"
            )
            
            # 메시지 저장
            new_messages = self.save_messages(room_id, file_id, session_id, chat_data)
            
            return file_id, room_id, new_messages
            
        except Exception as e:
            print(f"Complete save error: {e}")
            raise e
    
    def update_room_with_new_file(self, room_id, file_path, file_name, chat_data):
        """기존 채팅방에 새로운 파일 추가"""
        try:
            # 파일 정보 저장
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            message_count = len(chat_data)
            start_date = chat_data['datetime'].min().isoformat()
            end_date = chat_data['datetime'].max().isoformat()
            
            file_id = self.save_chat_file(room_id, file_name, file_path, file_size, message_count, start_date, end_date)
            
            # 분석 세션 생성
            session_id = self.save_analysis_session(
                f"{file_name} 추가 분석",
                chat_data,
                file_name,
                f"기존 채팅방에 추가된 파일"
            )
            
            # 메시지 저장
            new_messages = self.save_messages(room_id, file_id, session_id, chat_data)
            
            return file_id, new_messages
            
        except Exception as e:
            print(f"Update room error: {e}")
            raise e
    
    def get_session_analysis_results(self, session_id):
        """세션의 분석 결과 조회"""
        conn = self.get_connection()
        
        try:
            results_df = pd.read_sql_query('''
                SELECT analysis_type, target_user, summary, keywords, created_at
                FROM gpt_analysis_results 
                WHERE session_id = ?
                ORDER BY created_at DESC
            ''', conn, params=[session_id])
            
            return results_df
        except Exception as e:
            print(f"Get analysis results error: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def save_analysis_result(self, room_name, analysis_type, analysis_mode, target_user, prompt, result):
        """분석 결과를 히스토리에 저장"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 결과에서 필요한 정보 추출
            summary = result.get('summary', '')
            keywords = json.dumps(result.get('keywords', []), ensure_ascii=False)
            insights = json.dumps(result.get('insights', []), ensure_ascii=False)
            recommendations = json.dumps(result.get('recommendations', []), ensure_ascii=False)
            
            cursor.execute('''
                INSERT INTO analysis_history 
                (room_name, analysis_type, analysis_mode, target_user, prompt, 
                 result_summary, keywords, insights, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (room_name, analysis_type, analysis_mode, target_user, prompt,
                  summary, keywords, insights, recommendations))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"분석 결과 저장 오류: {e}")
            return False
    
    def get_analysis_history(self, limit=50):
        """분석 히스토리 조회"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, room_name, analysis_type, analysis_mode, target_user, 
                       prompt, result_summary, keywords, insights, recommendations,
                       timestamp, created_at
                FROM analysis_history 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            # 결과를 딕셔너리 리스트로 변환
            history = []
            for row in results:
                try:
                    keywords = json.loads(row[7]) if row[7] else []
                    insights = json.loads(row[8]) if row[8] else []
                    recommendations = json.loads(row[9]) if row[9] else []
                except:
                    keywords = []
                    insights = []
                    recommendations = []
                
                history.append({
                    'id': row[0],
                    'room_name': row[1],
                    'analysis_type': row[2],
                    'analysis_mode': row[3],
                    'target_user': row[4],
                    'prompt': row[5],
                    'summary': row[6],
                    'keywords': keywords,
                    'insights': insights,
                    'recommendations': recommendations,
                    'timestamp': row[10],
                    'created_at': row[11]
                })
            
            return history
            
        except Exception as e:
            print(f"히스토리 조회 오류: {e}")
            return []
    
    def delete_analysis_history(self, analysis_id):
        """특정 분석 결과 삭제"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM analysis_history WHERE id = ?', (analysis_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"히스토리 삭제 오류: {e}")
            return False
    
    def clear_analysis_history(self):
        """모든 분석 히스토리 삭제"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM analysis_history')
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"히스토리 전체 삭제 오류: {e}")
            return False