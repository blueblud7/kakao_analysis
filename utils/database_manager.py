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
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
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
        
        conn.commit()
        conn.close()
    
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
        conn = sqlite3.connect(self.db_path)
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
    
    def save_chat_file(self, file_path, file_name, chat_data):
        """채팅 파일 저장 (중복 체크 포함)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 파일 해시 생성
        file_hash = self.create_file_hash(file_path, file_name)
        
        # 기존 파일 확인
        cursor.execute('SELECT id, room_id FROM chat_files WHERE file_hash = ?', (file_hash,))
        result = cursor.fetchone()
        
        if result:
            conn.close()
            return result[0], result[1], 0  # file_id, room_id, new_messages_count
        
        # 참여자 목록 추출
        participants = chat_data['user'].unique().tolist()
        room_id = self.get_or_create_chat_room(participants)
        
        # 파일 정보 저장
        cursor.execute('''
            INSERT INTO chat_files 
            (room_id, file_name, file_path, file_hash, file_size, message_count, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            room_id,
            file_name,
            file_path,
            file_hash,
            os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            len(chat_data),
            chat_data['datetime'].min().isoformat(),
            chat_data['datetime'].max().isoformat()
        ))
        
        file_id = cursor.lastrowid
        
        # 채팅 메시지 저장 (중복 체크)
        new_messages_count = 0
        for _, row in chat_data.iterrows():
            message_hash = self.create_message_hash(
                row['datetime'].isoformat(),
                row['user'],
                row['message'] if pd.notna(row['message']) else ''
            )
            
            # 중복 메시지 확인
            cursor.execute('SELECT id FROM chat_messages WHERE message_hash = ?', (message_hash,))
            if cursor.fetchone() is None:
                cursor.execute('''
                    INSERT INTO chat_messages 
                    (room_id, file_id, datetime, user, message, message_length, message_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    room_id,
                    file_id,
                    row['datetime'].isoformat(),
                    row['user'],
                    row['message'] if pd.notna(row['message']) else '',
                    len(row['message']) if pd.notna(row['message']) else 0,
                    message_hash
                ))
                new_messages_count += 1
        
        conn.commit()
        conn.close()
        
        return file_id, room_id, new_messages_count
    
    def get_room_history(self, room_id, start_date=None, end_date=None):
        """채팅방 전체 히스토리 조회"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT cm.datetime, cm.user, cm.message, cf.file_name
            FROM chat_messages cm
            JOIN chat_files cf ON cm.file_id = cf.id
            WHERE cm.room_id = ?
        '''
        params = [room_id]
        
        if start_date:
            query += ' AND cm.datetime >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND cm.datetime <= ?'
            params.append(end_date)
        
        query += ' ORDER BY cm.datetime'
        
        chat_df = pd.read_sql_query(query, conn, params=params)
        
        if not chat_df.empty:
            chat_df['datetime'] = pd.to_datetime(chat_df['datetime'])
        
        conn.close()
        return chat_df
    
    def get_all_rooms(self):
        """모든 채팅방 목록 조회"""
        conn = sqlite3.connect(self.db_path)
        
        # 테이블 존재 여부 확인
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_rooms';")
        chat_rooms_exists = cursor.fetchone() is not None
        
        if not chat_rooms_exists:
            # 채팅방 테이블이 없으면 빈 DataFrame 반환
            conn.close()
            return pd.DataFrame(columns=['id', 'room_name', 'participants', 'file_count', 'total_messages', 'first_message', 'last_message', 'participants_list'])
        
        # 컬럼 존재 여부 확인
        cursor.execute("PRAGMA table_info(chat_messages)")
        columns = [row[1] for row in cursor.fetchall()]
        has_room_id = 'room_id' in columns
        
        if has_room_id:
            # 새로운 스키마 사용
            rooms_df = pd.read_sql_query('''
                SELECT cr.id, cr.room_name, cr.participants, 
                       COUNT(DISTINCT cf.id) as file_count,
                       COUNT(cm.id) as total_messages,
                       MIN(cm.datetime) as first_message,
                       MAX(cm.datetime) as last_message
                FROM chat_rooms cr
                LEFT JOIN chat_files cf ON cr.id = cf.room_id
                LEFT JOIN chat_messages cm ON cr.id = cm.room_id
                GROUP BY cr.id, cr.room_name, cr.participants
                ORDER BY last_message DESC
            ''', conn)
        else:
            # 기존 스키마 사용 - 빈 결과 반환
            rooms_df = pd.DataFrame(columns=['id', 'room_name', 'participants', 'file_count', 'total_messages', 'first_message', 'last_message'])
        
        # participants JSON 파싱
        if not rooms_df.empty and 'participants' in rooms_df.columns:
            rooms_df['participants_list'] = rooms_df['participants'].apply(
                lambda x: json.loads(x) if x else []
            )
        else:
            rooms_df['participants_list'] = [[] for _ in range(len(rooms_df))]
        
        conn.close()
        return rooms_df
    
    def update_room_with_new_file(self, room_id, file_path, file_name, new_chat_data):
        """기존 채팅방에 새 파일 추가 (증분 업데이트)"""
        file_id, _, new_messages_count = self.save_chat_file(file_path, file_name, new_chat_data)
        return file_id, new_messages_count
    
    def delete_chat_room(self, room_id):
        """채팅방 완전 삭제 (모든 관련 데이터 포함)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 1. 채팅 메시지 삭제
            cursor.execute('DELETE FROM chat_messages WHERE room_id = ?', (room_id,))
            
            # 2. 파일 정보 삭제
            cursor.execute('DELETE FROM chat_files WHERE room_id = ?', (room_id,))
            
            # 3. 분석 세션과 관련 데이터 삭제
            cursor.execute('SELECT id FROM analysis_sessions WHERE room_id = ?', (room_id,))
            session_ids = [row[0] for row in cursor.fetchall()]
            
            for session_id in session_ids:
                cursor.execute('DELETE FROM gpt_analysis_results WHERE session_id = ?', (session_id,))
                cursor.execute('DELETE FROM user_statistics WHERE session_id = ?', (session_id,))
                cursor.execute('DELETE FROM time_statistics WHERE session_id = ?', (session_id,))
            
            cursor.execute('DELETE FROM analysis_sessions WHERE room_id = ?', (room_id,))
            
            # 4. 채팅방 삭제
            cursor.execute('DELETE FROM chat_rooms WHERE id = ?', (room_id,))
            
            conn.commit()
            deleted_count = cursor.rowcount
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
        
        return deleted_count > 0
    
    def get_room_files(self, room_id):
        """특정 채팅방의 파일 목록 조회"""
        conn = sqlite3.connect(self.db_path)
        
        files_df = pd.read_sql_query('''
            SELECT id, file_name, file_path, file_size, message_count, 
                   start_date, end_date, uploaded_at
            FROM chat_files 
            WHERE room_id = ?
            ORDER BY uploaded_at
        ''', conn, params=[room_id])
        
        conn.close()
        return files_df
    
    def search_messages_in_room(self, room_id, keyword=None, user=None, start_date=None, end_date=None):
        """채팅방 내 메시지 검색"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT cm.datetime, cm.user, cm.message, cf.file_name
            FROM chat_messages cm
            JOIN chat_files cf ON cm.file_id = cf.id
            WHERE cm.room_id = ?
        '''
        params = [room_id]
        
        if keyword:
            query += ' AND cm.message LIKE ?'
            params.append(f'%{keyword}%')
        
        if user:
            query += ' AND cm.user = ?'
            params.append(user)
        
        if start_date:
            query += ' AND cm.datetime >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND cm.datetime <= ?'
            params.append(end_date)
        
        query += ' ORDER BY cm.datetime'
        
        results_df = pd.read_sql_query(query, conn, params=params)
        
        if not results_df.empty:
            results_df['datetime'] = pd.to_datetime(results_df['datetime'])
        
        conn.close()
        return results_df
    
    def get_room_participant_activity(self, room_id):
        """채팅방 참여자별 활동 분석"""
        conn = sqlite3.connect(self.db_path)
        
        # 월별 활동
        monthly_activity = pd.read_sql_query('''
            SELECT 
                user,
                strftime('%Y-%m', datetime) as month,
                COUNT(*) as message_count
            FROM chat_messages 
            WHERE room_id = ?
            GROUP BY user, month
            ORDER BY month, message_count DESC
        ''', conn, params=[room_id])
        
        # 요일별 활동
        weekday_activity = pd.read_sql_query('''
            SELECT 
                user,
                CASE CAST(strftime('%w', datetime) AS INTEGER)
                    WHEN 0 THEN '일요일'
                    WHEN 1 THEN '월요일'
                    WHEN 2 THEN '화요일'
                    WHEN 3 THEN '수요일'
                    WHEN 4 THEN '목요일'
                    WHEN 5 THEN '금요일'
                    WHEN 6 THEN '토요일'
                END as weekday,
                COUNT(*) as message_count
            FROM chat_messages 
            WHERE room_id = ?
            GROUP BY user, weekday
            ORDER BY message_count DESC
        ''', conn, params=[room_id])
        
        conn.close()
        
        return {
            'monthly': monthly_activity,
            'weekday': weekday_activity
        }
    
    def get_room_statistics(self, room_id):
        """채팅방 통계 정보"""
        conn = sqlite3.connect(self.db_path)
        
        # 기본 통계
        basic_stats = pd.read_sql_query('''
            SELECT 
                COUNT(*) as total_messages,
                COUNT(DISTINCT user) as participant_count,
                MIN(datetime) as first_message,
                MAX(datetime) as last_message,
                AVG(message_length) as avg_message_length
            FROM chat_messages 
            WHERE room_id = ?
        ''', conn, params=[room_id]).iloc[0]
        
        # 사용자별 통계
        user_stats = pd.read_sql_query('''
            SELECT 
                user,
                COUNT(*) as message_count,
                AVG(message_length) as avg_length,
                MIN(datetime) as first_message,
                MAX(datetime) as last_message
            FROM chat_messages 
            WHERE room_id = ?
            GROUP BY user
            ORDER BY message_count DESC
        ''', conn, params=[room_id])
        
        # 시간대별 통계
        hourly_stats = pd.read_sql_query('''
            SELECT 
                strftime('%H', datetime) as hour,
                COUNT(*) as message_count
            FROM chat_messages 
            WHERE room_id = ?
            GROUP BY hour
            ORDER BY hour
        ''', conn, params=[room_id])
        
        # 파일별 통계
        file_stats = pd.read_sql_query('''
            SELECT 
                cf.file_name,
                cf.uploaded_at,
                COUNT(cm.id) as message_count
            FROM chat_files cf
            LEFT JOIN chat_messages cm ON cf.id = cm.file_id
            WHERE cf.room_id = ?
            GROUP BY cf.id, cf.file_name, cf.uploaded_at
            ORDER BY cf.uploaded_at
        ''', conn, params=[room_id])
        
        conn.close()
        
        return {
            'basic': basic_stats,
            'users': user_stats,
            'hourly': hourly_stats,
            'files': file_stats
        }
    
    def save_analysis_session(self, session_name, chat_data, file_name=None, description=None):
        """분석 세션 저장"""
        conn = sqlite3.connect(self.db_path)
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
        
        # 사용자별 통계 저장
        user_stats = self.calculate_user_statistics(chat_data)
        for user, stats in user_stats.items():
            cursor.execute('''
                INSERT INTO user_statistics 
                (session_id, user, message_count, avg_message_length, most_active_hour, first_message, last_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                user,
                stats['message_count'],
                stats['avg_message_length'],
                stats['most_active_hour'],
                stats['first_message'].isoformat(),
                stats['last_message'].isoformat()
            ))
        
        # 시간대별 통계 저장
        hourly_stats = chat_data.groupby(chat_data['datetime'].dt.hour).size()
        for hour, count in hourly_stats.items():
            cursor.execute('''
                INSERT INTO time_statistics (session_id, hour, message_count)
                VALUES (?, ?, ?)
            ''', (session_id, hour, count))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def save_gpt_analysis(self, session_id, analysis_results):
        """GPT 분석 결과 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        keywords_json = json.dumps(analysis_results.get('keywords', []), ensure_ascii=False)
        
        cursor.execute('''
            INSERT INTO gpt_analysis_results 
            (session_id, analysis_type, target_user, summary, keywords)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            session_id,
            analysis_results.get('analysis_type', ''),
            analysis_results.get('target_user', '전체'),
            analysis_results.get('summary', ''),
            keywords_json
        ))
        
        conn.commit()
        conn.close()
        
        return cursor.lastrowid
    
    def get_analysis_sessions(self):
        """저장된 분석 세션 목록 조회"""
        conn = sqlite3.connect(self.db_path)
        
        sessions_df = pd.read_sql_query('''
            SELECT id, session_name, file_name, total_messages, participants_count, 
                   start_date, end_date, created_at, description
            FROM analysis_sessions 
            ORDER BY created_at DESC
        ''', conn)
        
        conn.close()
        return sessions_df
    
    def get_session_data(self, session_id):
        """특정 세션의 채팅 데이터 조회"""
        conn = sqlite3.connect(self.db_path)
        
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
    
    def get_session_analysis_results(self, session_id):
        """특정 세션의 GPT 분석 결과 조회"""
        conn = sqlite3.connect(self.db_path)
        
        results_df = pd.read_sql_query('''
            SELECT analysis_type, target_user, summary, keywords, created_at
            FROM gpt_analysis_results 
            WHERE session_id = ?
            ORDER BY created_at DESC
        ''', conn, params=[session_id])
        
        # keywords JSON 파싱
        if not results_df.empty:
            results_df['keywords'] = results_df['keywords'].apply(
                lambda x: json.loads(x) if x else []
            )
        
        conn.close()
        return results_df
    
    def get_user_statistics(self, session_id):
        """특정 세션의 사용자 통계 조회"""
        conn = sqlite3.connect(self.db_path)
        
        stats_df = pd.read_sql_query('''
            SELECT user, message_count, avg_message_length, most_active_hour, 
                   first_message, last_message
            FROM user_statistics 
            WHERE session_id = ?
            ORDER BY message_count DESC
        ''', conn, params=[session_id])
        
        conn.close()
        return stats_df
    
    def get_time_statistics(self, session_id):
        """특정 세션의 시간대별 통계 조회"""
        conn = sqlite3.connect(self.db_path)
        
        time_df = pd.read_sql_query('''
            SELECT hour, message_count
            FROM time_statistics 
            WHERE session_id = ?
            ORDER BY hour
        ''', conn, params=[session_id])
        
        conn.close()
        return time_df
    
    def delete_session(self, session_id):
        """분석 세션 삭제"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 관련된 모든 데이터 삭제
        cursor.execute('DELETE FROM time_statistics WHERE session_id = ?', [session_id])
        cursor.execute('DELETE FROM user_statistics WHERE session_id = ?', [session_id])
        cursor.execute('DELETE FROM gpt_analysis_results WHERE session_id = ?', [session_id])
        cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', [session_id])
        cursor.execute('DELETE FROM analysis_sessions WHERE id = ?', [session_id])
        
        conn.commit()
        conn.close()
    
    def search_messages(self, session_id, keyword=None, user=None, start_date=None, end_date=None):
        """메시지 검색"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT datetime, user, message
            FROM chat_messages 
            WHERE session_id = ?
        '''
        params = [session_id]
        
        if keyword:
            query += ' AND message LIKE ?'
            params.append(f'%{keyword}%')
        
        if user:
            query += ' AND user = ?'
            params.append(user)
        
        if start_date:
            query += ' AND datetime >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND datetime <= ?'
            params.append(end_date)
        
        query += ' ORDER BY datetime'
        
        results_df = pd.read_sql_query(query, conn, params=params)
        results_df['datetime'] = pd.to_datetime(results_df['datetime'])
        
        conn.close()
        return results_df
    
    def calculate_user_statistics(self, chat_data):
        """사용자별 통계 계산"""
        stats = {}
        
        for user in chat_data['user'].unique():
            user_data = chat_data[chat_data['user'] == user]
            
            stats[user] = {
                'message_count': len(user_data),
                'avg_message_length': user_data['message'].str.len().mean(),
                'first_message': user_data['datetime'].min(),
                'last_message': user_data['datetime'].max(),
                'most_active_hour': user_data['datetime'].dt.hour.mode().iloc[0] if len(user_data) > 0 else 0
            }
        
        return stats
    
    def export_session_to_csv(self, session_id, output_path=None):
        """세션 데이터를 CSV로 내보내기"""
        chat_data = self.get_session_data(session_id)
        
        if output_path is None:
            output_path = f"session_{session_id}_export.csv"
        
        chat_data.to_csv(output_path, index=False, encoding='utf-8-sig')
        return output_path
    
    def get_database_info(self):
        """데이터베이스 정보 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        info = {}
        
        # 총 세션 수
        cursor.execute('SELECT COUNT(*) FROM analysis_sessions')
        info['total_sessions'] = cursor.fetchone()[0]
        
        # 총 메시지 수
        cursor.execute('SELECT COUNT(*) FROM chat_messages')
        info['total_messages'] = cursor.fetchone()[0]
        
        # 총 분석 결과 수
        cursor.execute('SELECT COUNT(*) FROM gpt_analysis_results')
        info['total_analyses'] = cursor.fetchone()[0]
        
        # DB 파일 크기
        if os.path.exists(self.db_path):
            info['db_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
        else:
            info['db_size_mb'] = 0
        
        conn.close()
        return info 