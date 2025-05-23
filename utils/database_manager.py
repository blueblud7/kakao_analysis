import sqlite3
import pandas as pd
import json
from datetime import datetime
import os

class DatabaseManager:
    """분석 결과 저장 및 관리를 위한 데이터베이스 클래스"""
    
    def __init__(self, db_path="kakao_analysis.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 분석 세션 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                file_name TEXT,
                total_messages INTEGER,
                participants_count INTEGER,
                start_date TEXT,
                end_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        ''')
        
        # 채팅 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                datetime TEXT,
                user TEXT,
                message TEXT,
                message_length INTEGER,
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