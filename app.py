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
        ["파일 업로드", "데이터 필터링", "GPT 분석", "시각화", "리포트 생성", "데이터 관리", "설정"],
        icons=['upload', 'funnel', 'robot', 'bar-chart', 'file-earmark-pdf', 'database', 'gear'],
        menu_icon="cast",
        default_index=0,
    )

# 파일 업로드 섹션
if selected == "파일 업로드":
    st.header("📁 카카오톡 채팅 파일 업로드")
    
    uploaded_file = st.file_uploader(
        "카카오톡 채팅 내역 파일을 업로드하세요 (CSV 또는 TXT)",
        type=['csv', 'txt'],
        help="카카오톡에서 내보낸 채팅 내역 파일을 업로드하세요"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("파일을 분석하는 중..."):
                # 파일 파싱
                parser = KakaoParser()
                chat_data = parser.parse_file(uploaded_file)
                st.session_state.chat_data = chat_data
                
            st.success(f"✅ 파일 업로드 완료! {len(chat_data)} 개의 메시지를 불러왔습니다.")
            
            # 데이터베이스에 저장 옵션
            st.subheader("💾 데이터베이스에 저장")
            col1, col2 = st.columns(2)
            
            with col1:
                session_name = st.text_input("세션 이름", value=f"분석_{datetime.now().strftime('%Y%m%d_%H%M')}")
            with col2:
                description = st.text_input("설명 (선택사항)", placeholder="예: 12월 주식 토론방 분석")
            
            if st.button("💾 데이터베이스에 저장"):
                try:
                    session_id = db_manager.save_analysis_session(
                        session_name, 
                        chat_data, 
                        uploaded_file.name,
                        description
                    )
                    st.session_state.current_session_id = session_id
                    st.success(f"✅ 세션이 저장되었습니다! (ID: {session_id})")
                except Exception as e:
                    st.error(f"❌ 저장 중 오류: {str(e)}")
            
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
                
        except Exception as e:
            st.error(f"❌ 파일 처리 중 오류가 발생했습니다: {str(e)}")

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
                        title="시간대별 메시지 수")
            fig.update_xaxis(title="시간")
            fig.update_yaxis(title="메시지 수")
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