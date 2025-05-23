import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import re
from streamlit_option_menu import option_menu
import os

from utils.kakao_parser import KakaoParser
from utils.gpt_analyzer import GPTAnalyzer
from utils.data_processor import DataProcessor
from utils.report_generator import ReportGenerator
from utils.database_manager import DatabaseManager

# 페이지 설정
st.set_page_config(
    page_title="카카오톡 채팅 분석기",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 제목
st.title("💬 카카오톡 오픈챗 분석기")
st.markdown("---")

# 세션 상태 초기화
if 'chat_data' not in st.session_state:
    st.session_state.chat_data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None

# 데이터베이스 매니저 초기화
db_manager = DatabaseManager()

# 사이드바 - 네비게이션
with st.sidebar:
    selected = option_menu(
        "메뉴",
        ["파일 업로드", "채팅방 히스토리", "데이터 필터링", "GPT 분석", "시각화", "리포트 생성", "데이터 관리", "설정"],
        icons=['upload', 'chat-dots', 'funnel', 'robot', 'bar-chart', 'file-earmark-pdf', 'database', 'gear'],
        menu_icon="cast",
        default_index=0,
    )

# 파일 업로드 섹션 (개선)
if selected == "파일 업로드":
    st.header("📁 카카오톡 채팅 파일 업로드")
    
    # 탭으로 구분
    tab1, tab2 = st.tabs(["🆕 새 파일 업로드", "📚 기존 채팅방에 추가"])
    
    with tab1:
        st.subheader("새로운 채팅 파일 업로드")
        uploaded_file = st.file_uploader(
            "카카오톡 채팅 내역 파일을 업로드하세요 (CSV 또는 TXT)",
            type=['csv', 'txt'],
            help="카카오톡에서 내보낸 채팅 내역 파일을 업로드하세요",
            key="new_file"
        )
        
        if uploaded_file is not None:
            try:
                with st.spinner("파일을 분석하는 중..."):
                    # 파일 저장
                    file_path = f"temp_{uploaded_file.name}"
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # 파일 파싱
                    parser = KakaoParser()
                    chat_data = parser.parse_file(uploaded_file)
                    st.session_state.chat_data = chat_data
                    
                    # 데이터베이스에 저장 (자동)
                    file_id, room_id, new_messages = db_manager.save_chat_file(
                        file_path, uploaded_file.name, chat_data
                    )
                    
                st.success(f"✅ 파일 업로드 완료!")
                
                if new_messages == 0:
                    st.info("ℹ️ 이 파일은 이미 데이터베이스에 존재합니다.")
                else:
                    st.success(f"🆕 {new_messages}개의 새로운 메시지가 추가되었습니다!")
                
                # 데이터 미리보기
                st.subheader("📋 데이터 미리보기")
                st.dataframe(chat_data.head(10))
                
                # 기본 통계
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("총 메시지 수", len(chat_data))
                with col2:
                    st.metric("참여자 수", chat_data['user'].nunique())
                with col3:
                    st.metric("기간", f"{(chat_data['datetime'].max() - chat_data['datetime'].min()).days} 일")
                with col4:
                    st.metric("평균 메시지 길이", f"{chat_data['message'].str.len().mean():.1f} 자")
                    
                # 정리
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
            except Exception as e:
                st.error(f"❌ 파일 처리 중 오류가 발생했습니다: {str(e)}")
    
    with tab2:
        st.subheader("기존 채팅방에 파일 추가")
        
        # 기존 채팅방 목록 조회
        rooms_df = db_manager.get_all_rooms()
        
        if not rooms_df.empty:
            selected_room = st.selectbox(
                "채팅방 선택",
                options=rooms_df['id'].tolist(),
                format_func=lambda x: f"{rooms_df[rooms_df['id']==x]['room_name'].iloc[0]} ({rooms_df[rooms_df['id']==x]['total_messages'].iloc[0]}개 메시지)"
            )
            
            uploaded_file_add = st.file_uploader(
                "추가할 채팅 파일 선택",
                type=['csv', 'txt'],
                key="add_file"
            )
            
            if uploaded_file_add is not None and st.button("📂 채팅방에 추가"):
                try:
                    with st.spinner("파일을 추가하는 중..."):
                        # 파일 저장
                        file_path = f"temp_{uploaded_file_add.name}"
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file_add.getbuffer())
                        
                        # 파일 파싱
                        parser = KakaoParser()
                        new_chat_data = parser.parse_file(uploaded_file_add)
                        
                        # 기존 채팅방에 추가
                        file_id, new_messages = db_manager.update_room_with_new_file(
                            selected_room, file_path, uploaded_file_add.name, new_chat_data
                        )
                        
                    if new_messages > 0:
                        st.success(f"✅ {new_messages}개의 새로운 메시지가 추가되었습니다!")
                    else:
                        st.info("ℹ️ 중복된 메시지입니다. 새로운 메시지가 없습니다.")
                    
                    # 정리
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
                except Exception as e:
                    st.error(f"❌ 파일 추가 중 오류: {str(e)}")
        else:
            st.info("📝 아직 저장된 채팅방이 없습니다. 먼저 새 파일을 업로드해주세요.")

# 채팅방 히스토리 섹션 (새로 추가)
elif selected == "채팅방 히스토리":
    st.header("💬 채팅방 히스토리 관리")
    
    # 모든 채팅방 조회
    try:
        rooms_df = db_manager.get_all_rooms()
        
        if rooms_df.empty:
            st.info("📝 아직 저장된 채팅방이 없습니다. 먼저 파일을 업로드해주세요.")
            st.info("💡 새로운 히스토리 관리 기능을 사용하려면 파일을 새로 업로드해주세요.")
        else:
            st.subheader("📋 채팅방 목록")
            
            # 채팅방 목록 표시
            for _, room in rooms_df.iterrows():
                with st.expander(f"💬 {room['room_name']} ({room['total_messages']}개 메시지)"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**참여자:** {len(room['participants_list'])}명")
                        if len(room['participants_list']) <= 5:
                            st.write(f"👥 {', '.join(room['participants_list'])}")
                    
                    with col2:
                        st.write(f"**파일 수:** {room['file_count']}개")
                        st.write(f"**총 메시지:** {room['total_messages']}개")
                    
                    with col3:
                        if room['first_message']:
                            st.write(f"**시작:** {room['first_message'][:10]}")
                        if room['last_message']:
                            st.write(f"**마지막:** {room['last_message'][:10]}")
                    
                    # 액션 버튼들
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button(f"📊 통계 보기", key=f"stats_{room['id']}"):
                            st.session_state.selected_room_stats = room['id']
                    
                    with col2:
                        if st.button(f"📖 히스토리 보기", key=f"history_{room['id']}"):
                            st.session_state.selected_room_history = room['id']
                    
                    with col3:
                        if st.button(f"💾 데이터 내보내기", key=f"export_{room['id']}"):
                            # 채팅방 데이터 가져오기
                            room_data = db_manager.get_room_history(room['id'])
                            st.session_state.chat_data = room_data
                            st.success("✅ 데이터가 로드되었습니다. 다른 섹션에서 분석하실 수 있습니다.")
                    
                    with col4:
                        if st.button(f"🗑️ 삭제", key=f"delete_{room['id']}", type="secondary"):
                            st.session_state.room_to_delete = room['id']
            
            # 선택된 채팅방 통계 표시
            if 'selected_room_stats' in st.session_state:
                try:
                    st.subheader(f"📊 채팅방 통계")
                    room_stats = db_manager.get_room_statistics(st.session_state.selected_room_stats)
                    
                    # 기본 통계
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("총 메시지", room_stats['basic']['total_messages'])
                    with col2:
                        st.metric("참여자 수", room_stats['basic']['participant_count'])
                    with col3:
                        if room_stats['basic']['first_message']:
                            days = (pd.to_datetime(room_stats['basic']['last_message']) - 
                                   pd.to_datetime(room_stats['basic']['first_message'])).days
                            st.metric("활동 기간", f"{days}일")
                    with col4:
                        st.metric("평균 메시지 길이", f"{room_stats['basic']['avg_message_length']:.1f}자")
                    
                    # 사용자별 통계
                    st.subheader("👥 사용자별 통계")
                    st.dataframe(room_stats['users'])
                    
                    # 시간대별 활동
                    if not room_stats['hourly'].empty:
                        st.subheader("⏰ 시간대별 활동")
                        fig = px.bar(room_stats['hourly'], x='hour', y='message_count', 
                                   title="시간대별 메시지 수")
                        st.plotly_chart(fig)
                    
                    # 파일별 통계
                    if not room_stats['files'].empty:
                        st.subheader("📁 파일별 통계")
                        st.dataframe(room_stats['files'])
                except Exception as e:
                    st.error(f"통계 로드 중 오류: {str(e)}")
            
            # 선택된 채팅방 히스토리 표시
            if 'selected_room_history' in st.session_state:
                try:
                    st.subheader("📖 채팅 히스토리")
                    
                    # 기간 필터
                    col1, col2 = st.columns(2)
                    with col1:
                        start_date = st.date_input("시작 날짜", key="history_start")
                    with col2:
                        end_date = st.date_input("종료 날짜", key="history_end")
                    
                    if st.button("🔍 히스토리 조회"):
                        room_history = db_manager.get_room_history(
                            st.session_state.selected_room_history,
                            start_date.isoformat() if start_date else None,
                            end_date.isoformat() if end_date else None
                        )
                        
                        if not room_history.empty:
                            st.dataframe(room_history)
                            st.info(f"📊 총 {len(room_history)}개의 메시지를 찾았습니다.")
                        else:
                            st.warning("⚠️ 해당 기간에 메시지가 없습니다.")
                except Exception as e:
                    st.error(f"히스토리 로드 중 오류: {str(e)}")
            
            # 채팅방 삭제 확인
            if 'room_to_delete' in st.session_state:
                st.error("⚠️ 정말로 이 채팅방을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ 삭제 확인", type="primary"):
                        try:
                            success = db_manager.delete_chat_room(st.session_state.room_to_delete)
                            if success:
                                st.success("✅ 채팅방이 삭제되었습니다.")
                            else:
                                st.error("❌ 채팅방 삭제에 실패했습니다.")
                        except Exception as e:
                            st.error(f"❌ 삭제 중 오류: {str(e)}")
                        del st.session_state.room_to_delete
                        st.rerun()
                with col2:
                    if st.button("❌ 취소"):
                        del st.session_state.room_to_delete
                        st.rerun()
            
            # 채팅방 검색 기능
            if not rooms_df.empty:
                st.subheader("🔍 채팅방 검색")
                search_room = st.selectbox(
                    "검색할 채팅방",
                    options=rooms_df['id'].tolist(),
                    format_func=lambda x: f"{rooms_df[rooms_df['id']==x]['room_name'].iloc[0]}"
                )
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    search_keyword = st.text_input("키워드 검색", placeholder="예: 주식, 비트코인")
                with col2:
                    selected_room_data = rooms_df[rooms_df['id']==search_room]['participants_list'].iloc[0]
                    search_user = st.selectbox("사용자 선택", ["전체"] + list(selected_room_data))
                with col3:
                    search_date = st.date_input("검색 날짜 (선택사항)")
                
                if st.button("🔍 메시지 검색"):
                    try:
                        search_results = db_manager.search_messages_in_room(
                            search_room,
                            keyword=search_keyword if search_keyword else None,
                            user=search_user if search_user != "전체" else None,
                            start_date=search_date.isoformat() if search_date else None
                        )
                        
                        if not search_results.empty:
                            st.subheader(f"🔍 검색 결과 ({len(search_results)}개)")
                            st.dataframe(search_results)
                        else:
                            st.info("🔍 검색 결과가 없습니다.")
                    except Exception as e:
                        st.error(f"검색 중 오류: {str(e)}")
    
    except Exception as e:
        st.error(f"채팅방 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")
        st.info("💡 기존 데이터베이스와의 호환성 문제일 수 있습니다. 새로운 파일을 업로드해 보세요.")

# 데이터 필터링 섹션
elif selected == "데이터 필터링":
    st.header("🔍 데이터 필터링")
    
    if st.session_state.chat_data is None:
        st.warning("⚠️ 먼저 채팅 파일을 업로드해주세요.")
    else:
        chat_data = st.session_state.chat_data
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 기간 선택")
            min_date = chat_data['datetime'].min().date()
            max_date = chat_data['datetime'].max().date()
            
            start_date = st.date_input("시작 날짜", min_date, min_value=min_date, max_value=max_date)
            end_date = st.date_input("종료 날짜", max_date, min_value=min_date, max_value=max_date)
            
        with col2:
            st.subheader("👤 사용자 선택")
            users = ['전체'] + list(chat_data['user'].unique())
            selected_users = st.multiselect("분석할 사용자 선택", users, default=['전체'])
            
        st.subheader("🎯 키워드 필터링")
        keywords = st.text_input("키워드 입력 (쉼표로 구분)", placeholder="예: 주식, 비트코인, 삼성전자")
        
        # 필터링 적용
        if st.button("🔍 필터 적용"):
            processor = DataProcessor()
            filtered_data = processor.filter_data(
                chat_data, 
                start_date, 
                end_date, 
                selected_users, 
                keywords
            )
            
            st.session_state.filtered_data = filtered_data
            st.success(f"✅ 필터링 완료! {len(filtered_data)} 개의 메시지가 선택되었습니다.")
            
            # 필터링된 데이터 미리보기
            st.dataframe(filtered_data.head(10))

# GPT 분석 섹션
elif selected == "GPT 분석":
    st.header("🤖 GPT 분석")
    
    if st.session_state.chat_data is None:
        st.warning("⚠️ 먼저 채팅 파일을 업로드해주세요.")
    else:
        # OpenAI API 키 입력
        api_key = st.text_input("OpenAI API 키", type="password")
        
        if api_key:
            # 분석 옵션
            st.subheader("🎯 분석 옵션")
            
            col1, col2 = st.columns(2)
            with col1:
                analysis_type = st.selectbox(
                    "분석 유형",
                    ["종합 분석", "감정 분석", "주요 키워드 추출", "토픽 분석", "요약"]
                )
            
            with col2:
                target_user = st.selectbox(
                    "분석 대상",
                    ["전체"] + list(st.session_state.chat_data['user'].unique())
                )
            
            # 분석 실행
            if st.button("🚀 분석 시작"):
                data_to_analyze = st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.chat_data
                
                with st.spinner("GPT가 채팅을 분석하는 중..."):
                    analyzer = GPTAnalyzer(api_key)
                    results = analyzer.analyze_chat(data_to_analyze, analysis_type, target_user)
                    results['target_user'] = target_user  # 대상 사용자 정보 추가
                    st.session_state.analysis_results = results
                
                st.success("✅ 분석 완료!")
                
                # 결과를 데이터베이스에 저장
                if st.session_state.current_session_id:
                    try:
                        db_manager.save_gpt_analysis(st.session_state.current_session_id, results)
                        st.info("📊 분석 결과가 데이터베이스에 저장되었습니다.")
                    except Exception as e:
                        st.warning(f"⚠️ 분석 결과 저장 중 오류: {str(e)}")
                
                # 결과 표시
                st.subheader("📊 분석 결과")
                st.markdown(results['summary'])
                
                if 'keywords' in results:
                    st.subheader("🔑 주요 키워드")
                    for keyword in results['keywords']:
                        st.write(f"• {keyword}")

# 시각화 섹션
elif selected == "시각화":
    st.header("📊 데이터 시각화")
    
    if st.session_state.chat_data is None:
        st.warning("⚠️ 먼저 채팅 파일을 업로드해주세요.")
    else:
        data = st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.chat_data
        
        # 시각화 옵션
        viz_type = st.selectbox(
            "시각화 유형",
            ["시간대별 활동", "사용자별 메시지 수", "워드클라우드", "감정 분석"]
        )
        
        if viz_type == "시간대별 활동":
            st.subheader("⏰ 시간대별 활동 패턴")
            
            # 시간별 메시지 수
            hourly_data = data.groupby(data['datetime'].dt.hour).size()
            fig = px.bar(x=hourly_data.index, y=hourly_data.values, 
                        title="시간대별 메시지 수",
                        labels={'x': '시간', 'y': '메시지 수'})
            fig.update_layout(xaxis_title="시간", yaxis_title="메시지 수")
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "사용자별 메시지 수":
            st.subheader("👥 사용자별 활동량")
            
            user_counts = data['user'].value_counts()
            fig = px.pie(values=user_counts.values, names=user_counts.index,
                        title="사용자별 메시지 비율")
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "워드클라우드":
            st.subheader("☁️ 워드클라우드")
            
            # 텍스트 전처리 및 워드클라우드 생성
            text = ' '.join(data['message'].dropna())
            if text:
                wordcloud = WordCloud(
                    font_path='./fonts/NanumGothic.ttf',  # 한글 폰트 경로
                    width=800, 
                    height=400,
                    background_color='white'
                ).generate(text)
                
                fig, ax = plt.subplots()
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)

# 리포트 생성 섹션
elif selected == "리포트 생성":
    st.header("📄 리포트 생성")
    
    if st.session_state.chat_data is None:
        st.warning("⚠️ 먼저 채팅 파일을 업로드해주세요.")
    else:
        st.subheader("📋 리포트 옵션")
        
        col1, col2 = st.columns(2)
        with col1:
            report_type = st.selectbox("리포트 형식", ["PDF", "Excel", "둘 다"])
        with col2:
            include_analysis = st.checkbox("GPT 분석 결과 포함", value=True)
        
        # 리포트 생성
        if st.button("📄 리포트 생성"):
            report_gen = ReportGenerator()
            data_to_use = st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.chat_data
            analysis_results = st.session_state.analysis_results if include_analysis else None
            
            with st.spinner("리포트를 생성하는 중..."):
                try:
                    if report_type in ["PDF", "둘 다"]:
                        # PDF 리포트 생성
                        pdf_data = report_gen.generate_pdf_report(
                            st.session_state.chat_data, 
                            analysis_results, 
                            data_to_use
                        )
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        pdf_filename = f"카카오톡_분석_리포트_{timestamp}.pdf"
                        
                        st.download_button(
                            label="📥 PDF 리포트 다운로드",
                            data=pdf_data,
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )
                    
                    if report_type in ["Excel", "둘 다"]:
                        # Excel 리포트 생성
                        excel_data = report_gen.generate_excel_report(
                            st.session_state.chat_data, 
                            analysis_results, 
                            data_to_use
                        )
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        excel_filename = f"카카오톡_분석_데이터_{timestamp}.xlsx"
                        
                        st.download_button(
                            label="📥 Excel 리포트 다운로드",
                            data=excel_data,
                            file_name=excel_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    st.success("✅ 리포트가 생성되었습니다!")
                    
                except Exception as e:
                    st.error(f"❌ 리포트 생성 중 오류: {str(e)}")

# 데이터 관리 섹션
elif selected == "데이터 관리":
    st.header("🗃️ 데이터 관리")
    
    # 데이터베이스 정보
    db_info = db_manager.get_database_info()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("저장된 세션 수", db_info['total_sessions'])
    with col2:
        st.metric("총 메시지 수", f"{db_info['total_messages']:,}")
    with col3:
        st.metric("분석 결과 수", db_info['total_analyses'])
    with col4:
        st.metric("DB 크기", f"{db_info['db_size_mb']:.2f} MB")
    
    st.markdown("---")
    
    # 저장된 세션 목록
    st.subheader("📂 저장된 분석 세션")
    
    sessions_df = db_manager.get_analysis_sessions()
    
    if not sessions_df.empty:
        # 세션 선택
        selected_session = st.selectbox(
            "세션 선택",
            options=sessions_df['id'].tolist(),
            format_func=lambda x: f"[{x}] {sessions_df[sessions_df['id']==x]['session_name'].iloc[0]} ({sessions_df[sessions_df['id']==x]['total_messages'].iloc[0]}개 메시지)"
        )
        
        if selected_session:
            session_info = sessions_df[sessions_df['id'] == selected_session].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 세션 불러오기"):
                    # 세션 데이터 불러오기
                    session_data = db_manager.get_session_data(selected_session)
                    st.session_state.chat_data = session_data
                    st.session_state.current_session_id = selected_session
                    st.success(f"✅ 세션 '{session_info['session_name']}'을 불러왔습니다!")
            
            with col2:
                if st.button("📄 분석 결과 보기"):
                    # 분석 결과 조회
                    analysis_results = db_manager.get_session_analysis_results(selected_session)
                    if not analysis_results.empty:
                        st.subheader("🤖 저장된 분석 결과")
                        for _, result in analysis_results.iterrows():
                            st.write(f"**{result['analysis_type']}** (대상: {result['target_user']})")
                            st.write(f"분석 시간: {result['created_at']}")
                            st.markdown(result['summary'])
                            st.markdown("---")
                    else:
                        st.info("저장된 분석 결과가 없습니다.")
            
            with col3:
                if st.button("🗑️ 세션 삭제", type="secondary"):
                    if st.checkbox(f"'{session_info['session_name']}' 세션을 정말 삭제하시겠습니까?"):
                        db_manager.delete_session(selected_session)
                        st.success("✅ 세션이 삭제되었습니다!")
                        st.rerun()
        
        # 세션 목록 테이블
        st.subheader("📋 전체 세션 목록")
        display_columns = ['id', 'session_name', 'total_messages', 'participants_count', 'start_date', 'end_date', 'created_at']
        st.dataframe(sessions_df[display_columns])
        
    else:
        st.info("저장된 세션이 없습니다. 먼저 채팅 파일을 업로드하고 저장해주세요.")

# 설정 섹션
elif selected == "설정":
    st.header("⚙️ 설정")
    
    st.subheader("🔧 일반 설정")
    
    # 테마 설정
    theme = st.selectbox("테마", ["라이트", "다크"])
    
    # 언어 설정
    language = st.selectbox("언어", ["한국어", "English"])
    
    # 분석 설정
    st.subheader("🤖 분석 설정")
    
    max_tokens = st.slider("GPT 최대 토큰 수", 100, 4000, 2000)
    temperature = st.slider("GPT 창의성 (Temperature)", 0.0, 1.0, 0.7)
    
    # 데이터베이스 설정
    st.subheader("🗃️ 데이터베이스 설정")
    
    if st.button("🔄 데이터베이스 초기화"):
        if st.checkbox("정말로 모든 데이터를 삭제하시겠습니까?"):
            try:
                import os
                if os.path.exists("kakao_analysis.db"):
                    os.remove("kakao_analysis.db")
                st.success("✅ 데이터베이스가 초기화되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 초기화 중 오류: {str(e)}")
    
    if st.button("💾 설정 저장"):
        st.success("✅ 설정이 저장되었습니다!")

# 푸터
st.markdown("---")
st.markdown("💡 **Tip**: 더 정확한 분석을 위해 키워드와 기간을 구체적으로 설정해보세요!") 