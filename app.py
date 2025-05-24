import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys
from io import StringIO
import re
from collections import Counter
from streamlit_option_menu import option_menu

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 모듈 임포트
from utils.kakao_parser import KakaoParser
from utils.gpt_analyzer import GPTAnalyzer

# 페이지 설정
st.set_page_config(
    page_title="카카오톡 채팅 분석기",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS - 세련된 다크 모드 테마
st.markdown("""
<style>
/* 전체 배경 */
.main {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    color: #ffffff;
}

/* 사이드바 스타일 */
.css-1d391kg {
    background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
}

/* 메트릭 카드 스타일 */
.stMetric {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 8px 32px 0 rgba(102, 126, 234, 0.37);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    color: white;
    margin-bottom: 20px;
}

/* 제목 스타일 */
h1 {
    color: #667eea;
    text-align: center;
    font-weight: bold;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

/* 버튼 스타일 */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 25px;
    padding: 10px 25px;
    font-weight: bold;
    box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.6);
}

/* 파일 업로더 스타일 */
.uploadedFile {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    padding: 10px;
    color: white;
}

/* 차트 컨테이너 스타일 */
.plot-container {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 20px;
    margin: 20px 0;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}

/* 데이터프레임 스타일 */
.dataframe {
    border-radius: 10px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.95);
}

/* 성공/오류 메시지 스타일 */
.stSuccess {
    background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
    border-radius: 10px;
    border: none;
    color: white;
}

.stError {
    background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%);
    border-radius: 10px;
    border: none;
    color: white;
}

/* 경고 메시지 스타일 */
.stWarning {
    background: linear-gradient(135deg, #fdcb6e 0%, #fd79a8 100%);
    border-radius: 10px;
    border: none;
    color: white;
}

/* 정보 메시지 스타일 */
.stInfo {
    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
    border-radius: 10px;
    border: none;
    color: white;
}

/* 스피너 스타일 */
.stSpinner {
    color: #667eea;
}

/* 선택박스, 입력창 스타일 */
.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
}

/* 카드 스타일 */
.analysis-card {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    border-radius: 15px;
    padding: 25px;
    margin: 20px 0;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
}

/* 텍스트 색상 */
.stMarkdown, .stText {
    color: #ffffff;
}

/* 헤더 스타일 */
h2, h3, h4, h5, h6 {
    color: #667eea;
}

/* 링크 스타일 */
a {
    color: #74b9ff;
}

/* 프로그레스 바 스타일 */
.stProgress > div > div > div {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
""", unsafe_allow_html=True)

# 제목
st.markdown("""
<h1 style='text-align: center; color: #667eea; font-size: 3rem; margin-bottom: 2rem;'>
    💬 카카오톡 채팅 분석기
</h1>
<p style='text-align: center; color: #b2bec3; font-size: 1.2rem; margin-bottom: 3rem;'>
    AI 기반 스마트 채팅 분석 플랫폼
</p>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'chat_data' not in st.session_state:
    st.session_state.chat_data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'selected_room' not in st.session_state:
    st.session_state.selected_room = None

# 사이드바 메뉴
with st.sidebar:
    st.markdown("## 🎛️ 메뉴")
    
    selected = option_menu(
        menu_title=None,
        options=[
            "🏠 홈",
            "📁 파일 업로드", 
            "📊 데이터 분석",
            "🤖 GPT 분석",
            "📈 시각화",
            "💾 데이터 관리",
            "⚙️ 설정"
        ],
        icons=[
            "house",
            "upload", 
            "bar-chart",
            "robot",
            "graph-up",
            "database",
            "gear"
        ],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "transparent"
            },
            "icon": {
                "color": "white",
                "font-size": "18px"
            },
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px",
                "padding": "10px",
                "border-radius": "10px",
                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "color": "white",
                "border": "none"
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
                "color": "white",
                "font-weight": "bold",
                "box-shadow": "0 4px 15px 0 rgba(102, 126, 234, 0.6)"
            },
        }
    )

# 홈 페이지
if selected == "🏠 홈":
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class='analysis-card' style='text-align: center; padding: 40px;'>
            <h2 style='color: #667eea; margin-bottom: 30px;'>🎉 환영합니다!</h2>
            <p style='font-size: 1.1rem; color: #b2bec3; line-height: 1.6;'>
                카카오톡 채팅 분석기는 AI 기반의 스마트한 채팅 분석 도구입니다.<br>
                채팅 데이터를 업로드하고 다양한 인사이트를 얻어보세요!
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 기능 소개
    st.markdown("### 🚀 주요 기능")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; margin: 10px; box-shadow: 0 8px 32px 0 rgba(102, 126, 234, 0.37);'>
            <h3>📁 파일 업로드</h3>
            <p>TXT, CSV 형식의<br>카카오톡 채팅 파일<br>지원</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; margin: 10px; box-shadow: 0 8px 32px 0 rgba(102, 126, 234, 0.37);'>
            <h3>🤖 AI 분석</h3>
            <p>GPT 기반의<br>스마트한 채팅<br>내용 분석</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; margin: 10px; box-shadow: 0 8px 32px 0 rgba(102, 126, 234, 0.37);'>
            <h3>📈 시각화</h3>
            <p>다양한 차트와<br>그래프로<br>데이터 시각화</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 시작하기 가이드
    st.markdown("### 📖 시작하기 가이드")
    
    with st.expander("1️⃣ 파일 업로드 방법", expanded=False):
        st.markdown("""
        1. **카카오톡 채팅방**에서 우상단 메뉴(≡) 클릭
        2. **대화 내보내기** 선택
        3. **텍스트** 또는 **CSV** 형식으로 저장
        4. **📁 파일 업로드** 메뉴에서 파일 업로드
        """)
    
    with st.expander("2️⃣ 데이터 분석 활용법", expanded=False):
        st.markdown("""
        - **📊 데이터 분석**: 기본 통계 및 패턴 분석
        - **🤖 GPT 분석**: AI 기반 고급 분석 및 인사이트
        - **📈 시각화**: 트렌드, 히트맵, 워드클라우드 등
        - **💾 데이터 관리**: 분석 결과 저장 및 관리
        """)
    
    with st.expander("3️⃣ 지원되는 파일 형식", expanded=False):
        st.markdown("""
        - **TXT 파일**: 카카오톡 기본 내보내기 형식
        - **CSV 파일**: 구조화된 데이터 형식
        - **인코딩**: UTF-8, UTF-8-SIG, CP949, EUC-KR 자동 감지
        """)

# 파일 업로드 섹션
elif selected == "📁 파일 업로드":
    st.header("📁 카카오톡 채팅 파일 업로드")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📝 지원되는 파일 형식
        - **TXT 파일**: 카카오톡에서 내보낸 텍스트 파일
        - **CSV 파일**: 구조화된 채팅 데이터
        
        ### 💡 사용 방법
        1. 카카오톡 채팅방에서 대화 내보내기
        2. 텍스트 또는 CSV 파일로 저장
        3. 아래에서 파일을 업로드하세요
        """)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; text-align: center; color: white;'>
            <h4>📋 업로드 가이드</h4>
            <p>최대 파일 크기:<br><strong>200MB</strong></p>
            <p>지원 형식:<br><strong>TXT, CSV</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # 파일 업로드
    uploaded_file = st.file_uploader(
        "채팅 파일을 선택하세요",
        type=['txt', 'csv'],
        help="카카오톡에서 내보낸 .txt 파일 또는 .csv 파일을 업로드하세요"
    )
    
    if uploaded_file is not None:
        try:
            # 파일 크기 및 정보 표시
            file_size_mb = uploaded_file.size / (1024 * 1024)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📄 파일명", uploaded_file.name)
            with col2:
                st.metric("💾 파일 크기", f"{file_size_mb:.1f} MB")
            with col3:
                st.metric("📋 파일 형식", uploaded_file.type)
            
            # 파일 파싱
            with st.spinner('🔄 파일을 파싱하는 중...'):
                parser = KakaoParser()
                chat_data = parser.parse_file(uploaded_file)
                
                if chat_data is not None and not chat_data.empty:
                    st.session_state.chat_data = chat_data
                    
                    # 성공 메시지
                    st.success(f"✅ 파일 파싱 완료! **{len(chat_data):,}개**의 메시지가 발견되었습니다.")
                    
                    # 데이터 미리보기
                    st.subheader("📋 데이터 미리보기")
                    
                    # 스타일링된 데이터프레임
                    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                    st.dataframe(
                        chat_data.head(10),
                        use_container_width=True,
                        hide_index=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 기본 통계
                    st.subheader("📊 기본 통계")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "📝 총 메시지 수",
                            f"{len(chat_data):,}",
                            delta=None
                        )
                    with col2:
                        st.metric(
                            "👥 참여자 수",
                            len(chat_data['user'].unique()),
                            delta=None
                        )
                    with col3:
                        date_range = f"{chat_data['datetime'].dt.date.min()}"
                        st.metric(
                            "📅 시작일",
                            date_range,
                            delta=None
                        )
                    with col4:
                        date_range = f"{chat_data['datetime'].dt.date.max()}"
                        st.metric(
                            "📅 종료일", 
                            date_range,
                            delta=None
                        )
                        
                    # 추가 통계
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        days_diff = (chat_data['datetime'].dt.date.max() - chat_data['datetime'].dt.date.min()).days
                        if days_diff > 0:
                            avg_daily = len(chat_data) / days_diff
                            st.metric("📈 일평균 메시지", f"{avg_daily:.1f}개")
                        else:
                            st.metric("📈 일평균 메시지", f"{len(chat_data)}개")
                    
                    with col2:
                        avg_length = chat_data['message'].str.len().mean()
                        st.metric("📏 평균 메시지 길이", f"{avg_length:.1f}자")
                    
                    with col3:
                        most_active = chat_data['user'].value_counts().index[0]
                        st.metric("🏆 최다 발언자", most_active)
                    
                    with col4:
                        peak_hour = chat_data['datetime'].dt.hour.value_counts().index[0]
                        st.metric("⏰ 최고 활동시간", f"{peak_hour}시")
                        
                else:
                    st.error("❌ 파일 파싱에 실패했습니다. 파일 형식을 확인해주세요.")
                    
        except Exception as e:
            st.error(f"❌ 파일 처리 중 오류가 발생했습니다: {str(e)}")
            st.write("파일이 올바른 카카오톡 채팅 파일인지 확인해주세요.")

# 데이터 분석 섹션
elif selected == "📊 데이터 분석":
    st.header("📊 채팅 데이터 분석")
    
    if st.session_state.chat_data is None:
        st.warning("⚠️ 먼저 **📁 파일 업로드** 메뉴에서 파일을 업로드해주세요!")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📁 파일 업로드하기", use_container_width=True):
                st.rerun()
    else:
        data = st.session_state.chat_data
        
        # 분석 옵션
        analysis_tabs = st.tabs(["👥 사용자 분석", "⏰ 시간 분석", "💬 메시지 분석", "📈 트렌드 분석"])
        
        with analysis_tabs[0]:  # 사용자 분석
            st.subheader("👥 사용자별 활동 분석")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 메시지 수 상위 10명**")
                user_stats = data['user'].value_counts().head(10)
                
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.dataframe(
                    user_stats.reset_index(),
                    column_config={
                        "index": "사용자",
                        "user": "메시지 수"
                    },
                    hide_index=True,
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                fig = px.bar(
                    x=user_stats.values,
                    y=user_stats.index,
                    orientation='h',
                    title="사용자별 메시지 수",
                    labels={'x': '메시지 수', 'y': '사용자'},
                    color=user_stats.values,
                    color_continuous_scale='Reds'
                )
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with analysis_tabs[1]:  # 시간 분석
            st.subheader("⏰ 시간대별 활동 분석")
            
            # 시간별 분포
            data['hour'] = data['datetime'].dt.hour
            hourly_stats = data['hour'].value_counts().sort_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.line(
                    x=hourly_stats.index,
                    y=hourly_stats.values,
                    title="📈 시간대별 메시지 수",
                    labels={'x': '시간', 'y': '메시지 수'},
                    markers=True
                )
                fig.update_traces(line_color='#ff6b6b', marker_color='#ff6b6b')
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # 요일별 분포
                data['weekday'] = data['datetime'].dt.day_name()
                weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                weekday_stats = data['weekday'].value_counts().reindex(weekday_order)
                
                fig = px.bar(
                    x=['월', '화', '수', '목', '금', '토', '일'],
                    y=weekday_stats.values,
                    title="📅 요일별 메시지 수",
                    labels={'x': '요일', 'y': '메시지 수'},
                    color=weekday_stats.values,
                    color_continuous_scale='Reds'
                )
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with analysis_tabs[2]:  # 메시지 분석
            st.subheader("💬 메시지 내용 분석")
            
            # 메시지 길이 분석
            data['message_length'] = data['message'].str.len()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📏 평균 길이", f"{data['message_length'].mean():.1f}자")
            with col2:
                st.metric("📐 최장 메시지", f"{data['message_length'].max()}자")
            with col3:
                st.metric("📊 중간값", f"{data['message_length'].median():.1f}자")
            with col4:
                st.metric("📈 표준편차", f"{data['message_length'].std():.1f}")
            
            # 메시지 길이 히스토그램
            fig = px.histogram(
                data,
                x='message_length',
                nbins=50,
                title="📊 메시지 길이 분포",
                labels={'message_length': '메시지 길이 (문자수)', 'count': '빈도'},
                color_discrete_sequence=['#ff6b6b']
            )
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with analysis_tabs[3]:  # 트렌드 분석
            st.subheader("📈 시간 흐름 트렌드 분석")
            
            # 일별 메시지 수 트렌드
            daily_data = data.groupby(data['datetime'].dt.date).size().reset_index()
            daily_data.columns = ['date', 'count']
            
            fig = px.line(
                daily_data,
                x='date',
                y='count',
                title="📈 일별 메시지 수 변화",
                labels={'date': '날짜', 'count': '메시지 수'},
                markers=True
            )
            fig.update_traces(line_color='#ff6b6b', marker_color='#ff6b6b')
            fig.update_layout(
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 월별 집계
            if len(daily_data) > 30:  # 충분한 데이터가 있을 때만
                data['month'] = data['datetime'].dt.to_period('M')
                monthly_data = data.groupby('month').size().reset_index()
                monthly_data.columns = ['month', 'count']
                monthly_data['month'] = monthly_data['month'].astype(str)
                
                fig = px.bar(
                    monthly_data,
                    x='month',
                    y='count',
                    title="📅 월별 메시지 수",
                    labels={'month': '월', 'count': '메시지 수'},
                    color='count',
                    color_continuous_scale='Reds'
                )
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

# GPT 분석 섹션
elif selected == "🤖 GPT 분석":
    st.header("🤖 GPT 기반 채팅 분석")
    
    if st.session_state.chat_data is None:
        st.warning("⚠️ 먼저 **📁 파일 업로드** 메뉴에서 파일을 업로드해주세요!")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # OpenAI API 키 입력
            api_key = st.text_input(
                "🔑 OpenAI API 키를 입력하세요:",
                type="password",
                value=os.getenv("OPENAI_API_KEY", ""),
                help="OpenAI API 키가 필요합니다. https://platform.openai.com/api-keys"
            )
        
        with col2:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); padding: 20px; border-radius: 15px; text-align: center; color: white; margin-top: 25px;'>
                <h4>🔐 API 키 안내</h4>
                <p>OpenAI 플랫폼에서<br>API 키를 발급받으세요</p>
            </div>
            """, unsafe_allow_html=True)
        
        if api_key:
            st.subheader("🔧 분석 설정")
            
            col1, col2 = st.columns(2)
            with col1:
                sample_size = st.slider(
                    "분석할 메시지 수",
                    100,
                    min(2000, len(st.session_state.chat_data)),
                    500,
                    help="더 많은 메시지를 분석할수록 정확하지만 시간이 오래 걸립니다."
                )
            with col2:
                analysis_type = st.selectbox(
                    "분석 유형",
                    [
                        "종합 분석",
                        "주요 주제 분석", 
                        "감정 분석",
                        "사용자 특성 분석",
                        "트렌드 분석"
                    ],
                    help="원하는 분석 유형을 선택하세요."
                )
            
            # 분석 실행
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 AI 분석 시작", type="primary", use_container_width=True):
                    try:
                        with st.spinner('🤖 GPT가 채팅을 분석하는 중... (1-3분 소요)'):
                            # GPT 분석기 초기화
                            analyzer = GPTAnalyzer(api_key)
                            
                            # 데이터 샘플링 (최신 메시지 우선)
                            sample_data = st.session_state.chat_data.tail(sample_size)
                            
                            # 분석 실행
                            result = analyzer.analyze_chat(sample_data, analysis_type)
                            
                            if result and not result.get('error', False):
                                st.session_state.analysis_results = result
                                st.success("✅ AI 분석이 완료되었습니다!")
                                
                                # 결과 표시
                                st.markdown("---")
                                st.subheader("🎯 AI 분석 결과")
                                
                                if isinstance(result, dict) and 'summary' in result:
                                    # 메인 분석 결과
                                    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                                    st.markdown(result['summary'])
                                    st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    # 추가 정보들을 탭으로 구성
                                    if any(key in result for key in ['keywords', 'insights', 'data_stats']):
                                        result_tabs = st.tabs(["🔍 키워드", "💡 인사이트", "📊 통계"])
                                        
                                        with result_tabs[0]:
                                            if 'keywords' in result and result['keywords']:
                                                st.subheader("🔍 주요 키워드")
                                                keywords = result['keywords'][:15]
                                                
                                                # 키워드를 태그 형태로 표시
                                                keyword_html = ""
                                                for keyword in keywords:
                                                    keyword_html += f'<span style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); color: white; padding: 5px 10px; margin: 3px; border-radius: 15px; display: inline-block;">{keyword}</span>'
                                                
                                                st.markdown(keyword_html, unsafe_allow_html=True)
                                            else:
                                                st.info("키워드 정보가 없습니다.")
                                        
                                        with result_tabs[1]:
                                            if 'insights' in result and result['insights']:
                                                st.subheader("💡 주요 인사이트")
                                                for i, insight in enumerate(result['insights'][:8], 1):
                                                    st.markdown(f"**{i}.** {insight}")
                                            else:
                                                st.info("인사이트 정보가 없습니다.")
                                        
                                        with result_tabs[2]:
                                            if 'data_stats' in result:
                                                stats = result['data_stats']
                                                st.subheader("📊 분석 통계")
                                                
                                                col1, col2, col3 = st.columns(3)
                                                with col1:
                                                    st.metric("📝 분석 메시지", f"{stats.get('total_messages', 0):,}개")
                                                with col2:
                                                    st.metric("👥 참여자", f"{stats.get('unique_users', 0)}명")
                                                with col3:
                                                    st.metric("📅 분석 기간", stats.get('date_range', ''))
                                            else:
                                                st.info("통계 정보가 없습니다.")
                                else:
                                    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                                    st.markdown(str(result))
                                    st.markdown('</div>', unsafe_allow_html=True)
                                
                            else:
                                error_msg = result.get('summary', '알 수 없는 오류가 발생했습니다.') if result else '분석 결과를 받지 못했습니다.'
                                st.error(f"❌ 분석 중 오류가 발생했습니다: {error_msg}")
                                
                    except Exception as e:
                        st.error(f"❌ GPT 분석 중 오류가 발생했습니다: {str(e)}")
        else:
            st.info("💡 OpenAI API 키를 입력하면 AI 기반 채팅 분석을 사용할 수 있습니다.")
            
            with st.expander("🔗 OpenAI API 키 발급 방법", expanded=False):
                st.markdown("""
                1. [OpenAI 플랫폼](https://platform.openai.com/) 접속
                2. 계정 로그인 또는 회원가입
                3. **API keys** 메뉴로 이동
                4. **Create new secret key** 클릭
                5. 생성된 키를 복사하여 위 입력창에 붙여넣기
                
                ⚠️ **주의사항**: API 키는 안전하게 보관하세요.
                """)

# 시각화 섹션
elif selected == "📈 시각화":
    st.header("📈 고급 데이터 시각화")
    
    if st.session_state.chat_data is None:
        st.warning("⚠️ 먼저 **📁 파일 업로드** 메뉴에서 파일을 업로드해주세요!")
    else:
        data = st.session_state.chat_data
        
        # 시각화 유형 선택
        viz_options = [
            "📈 일별 메시지 트렌드",
            "🔥 사용자별 활동 히트맵", 
            "📊 메시지 길이 분포",
            "☁️ 키워드 워드클라우드",
            "⏰ 시간대별 활동 패턴",
            "📅 월별/요일별 분석"
        ]
        
        selected_viz = st.selectbox("🎨 시각화 유형을 선택하세요:", viz_options)
        
        if selected_viz == "📈 일별 메시지 트렌드":
            st.subheader("📈 일별 메시지 수 변화")
            
            # 일별 데이터 집계
            daily_data = data.groupby(data['datetime'].dt.date).size().reset_index()
            daily_data.columns = ['date', 'count']
            
            # 트렌드 차트
            fig = px.line(
                daily_data,
                x='date',
                y='count',
                title="일별 메시지 수 변화",
                labels={'date': '날짜', 'count': '메시지 수'},
                markers=True
            )
            fig.update_traces(line_color='#ff6b6b', marker_color='#ff6b6b')
            fig.update_layout(
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 이동평균 추가
            if len(daily_data) > 7:
                daily_data['moving_avg_7'] = daily_data['count'].rolling(window=7, center=True).mean()
                
                fig2 = px.line(
                    daily_data,
                    x='date',
                    y=['count', 'moving_avg_7'],
                    title="일별 메시지 수 + 7일 이동평균",
                    labels={'date': '날짜', 'value': '메시지 수'}
                )
                fig2.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        elif selected_viz == "🔥 사용자별 활동 히트맵":
            st.subheader("🔥 사용자별 시간대 활동 히트맵")
            
            # 상위 활성 사용자 선택
            top_users = data['user'].value_counts().head(10).index
            heatmap_data = data[data['user'].isin(top_users)].copy()
            heatmap_data['hour'] = heatmap_data['datetime'].dt.hour
            
            # 피벗 테이블 생성
            pivot_table = heatmap_data.pivot_table(
                values='message',
                index='user',
                columns='hour',
                aggfunc='count',
                fill_value=0
            )
            
            # 히트맵 생성
            fig = px.imshow(
                pivot_table.values,
                x=pivot_table.columns,
                y=pivot_table.index,
                title="사용자별 시간대 활동 히트맵",
                labels={'x': '시간', 'y': '사용자', 'color': '메시지 수'},
                color_continuous_scale='Reds',
                aspect='auto'
            )
            fig.update_layout(height=600)
            
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif selected_viz == "📊 메시지 길이 분포":
            st.subheader("📊 메시지 길이 분석")
            
            data['message_length'] = data['message'].str.len()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 히스토그램
                fig = px.histogram(
                    data,
                    x='message_length',
                    nbins=50,
                    title="메시지 길이 분포",
                    labels={'message_length': '메시지 길이 (문자수)', 'count': '빈도'},
                    color_discrete_sequence=['#ff6b6b']
                )
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # 박스플롯
                fig = px.box(
                    data.head(10000),  # 성능을 위해 샘플링
                    y='message_length',
                    title="메시지 길이 박스플롯",
                    labels={'message_length': '메시지 길이 (문자수)'},
                    color_discrete_sequence=['#ff6b6b']
                )
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # 통계 정보
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📏 평균 길이", f"{data['message_length'].mean():.1f}자")
            with col2:
                st.metric("📐 최장 메시지", f"{data['message_length'].max()}자")
            with col3:
                st.metric("📊 중간값", f"{data['message_length'].median():.1f}자")
            with col4:
                st.metric("📈 표준편차", f"{data['message_length'].std():.1f}")
        
        elif selected_viz == "☁️ 키워드 워드클라우드":
            st.subheader("☁️ 주요 키워드 분석")
            
            # 텍스트 전처리 및 키워드 추출
            all_text = ' '.join(data['message'].astype(str))
            korean_words = re.findall(r'[가-힣]{2,}', all_text)
            
            # 불용어 제거
            stopwords = [
                '이거', '그거', '저거', '뭐야', '그냥', '진짜', '정말', '완전', '너무', '엄청',
                '하지만', '그런데', '이런', '그런', '저런', '이제', '지금', '여기', '거기',
                '오늘', '어제', '내일', '시간', '때문', '이번', '다음', '마지막', '처음'
            ]
            filtered_words = [word for word in korean_words if word not in stopwords and len(word) > 1]
            
            # 단어 빈도 계산
            word_freq = Counter(filtered_words).most_common(30)
            
            if word_freq:
                words, frequencies = zip(*word_freq)
                
                # 바 차트로 상위 키워드 표시
                fig = px.bar(
                    x=list(frequencies),
                    y=list(words),
                    orientation='h',
                    title="상위 30개 키워드",
                    labels={'x': '빈도', 'y': '키워드'},
                    color=list(frequencies),
                    color_continuous_scale='Reds'
                )
                fig.update_layout(
                    height=800,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 키워드 태그 클라우드
                st.subheader("🏷️ 키워드 태그")
                keyword_html = ""
                for word, freq in word_freq[:20]:
                    size = min(30, max(12, freq // 10 + 12))
                    keyword_html += f'<span style="font-size: {size}px; background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); color: white; padding: 5px 10px; margin: 5px; border-radius: 15px; display: inline-block;">{word} ({freq})</span>'
                
                st.markdown(f'<div style="text-align: center; padding: 20px;">{keyword_html}</div>', unsafe_allow_html=True)
            else:
                st.info("키워드를 추출할 수 없습니다.")
        
        elif selected_viz == "⏰ 시간대별 활동 패턴":
            st.subheader("⏰ 시간대별 활동 패턴 분석")
            
            data['hour'] = data['datetime'].dt.hour
            data['weekday'] = data['datetime'].dt.day_name()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 시간대별 활동
                hourly_stats = data['hour'].value_counts().sort_index()
                
                fig = px.line(
                    x=hourly_stats.index,
                    y=hourly_stats.values,
                    title="시간대별 메시지 수",
                    labels={'x': '시간', 'y': '메시지 수'},
                    markers=True
                )
                fig.update_traces(line_color='#ff6b6b', marker_color='#ff6b6b')
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # 요일별 활동
                weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                weekday_stats = data['weekday'].value_counts().reindex(weekday_order)
                
                fig = px.bar(
                    x=['월', '화', '수', '목', '금', '토', '일'],
                    y=weekday_stats.values,
                    title="요일별 메시지 수",
                    labels={'x': '요일', 'y': '메시지 수'},
                    color=weekday_stats.values,
                    color_continuous_scale='Reds'
                )
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        elif selected_viz == "📅 월별/요일별 분석":
            st.subheader("📅 월별/요일별 상세 분석")
            
            # 월별 분석
            if len(data) > 100:  # 충분한 데이터가 있을 때만
                data['month'] = data['datetime'].dt.to_period('M')
                monthly_data = data.groupby('month').size().reset_index()
                monthly_data.columns = ['month', 'count']
                monthly_data['month'] = monthly_data['month'].astype(str)
                
                fig = px.bar(
                    monthly_data,
                    x='month',
                    y='count',
                    title="월별 메시지 수",
                    labels={'month': '월', 'count': '메시지 수'},
                    color='count',
                    color_continuous_scale='Reds'
                )
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 주간 패턴 분석
                data['week'] = data['datetime'].dt.isocalendar().week
                data['weekday_num'] = data['datetime'].dt.weekday
                
                # 요일별 시간대 히트맵
                weekday_hour_pivot = data.pivot_table(
                    values='message',
                    index='weekday_num',
                    columns='hour',
                    aggfunc='count',
                    fill_value=0
                )
                
                fig = px.imshow(
                    weekday_hour_pivot.values,
                    x=weekday_hour_pivot.columns,
                    y=['월', '화', '수', '목', '금', '토', '일'],
                    title="요일별 시간대 활동 히트맵",
                    labels={'x': '시간', 'y': '요일', 'color': '메시지 수'},
                    color_continuous_scale='Reds',
                    aspect='auto'
                )
                fig.update_layout(height=400)
                
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

# 데이터 관리 섹션
elif selected == "💾 데이터 관리":
    st.header("💾 데이터 관리")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📋 기능 목록
        - **💾 분석 결과 저장**: 현재 분석 결과를 파일로 저장
        - **📊 데이터 내보내기**: 처리된 데이터를 CSV로 내보내기
        - **🗃️ 세션 데이터 관리**: 현재 세션의 데이터 상태 확인
        - **🔄 데이터 초기화**: 모든 데이터 초기화
        """)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); padding: 20px; border-radius: 15px; text-align: center; color: white;'>
            <h4>💡 데이터 관리 팁</h4>
            <p>정기적으로 중요한<br>분석 결과를 저장하세요</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 현재 세션 상태
    st.subheader("📊 현재 세션 상태")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.chat_data is not None:
            st.metric("📝 채팅 데이터", "✅ 로드됨", delta=f"{len(st.session_state.chat_data):,}개 메시지")
        else:
            st.metric("📝 채팅 데이터", "❌ 없음", delta="파일 업로드 필요")
    
    with col2:
        if st.session_state.analysis_results is not None:
            st.metric("🤖 GPT 분석", "✅ 완료됨", delta="결과 저장 가능")
        else:
            st.metric("🤖 GPT 분석", "❌ 없음", delta="분석 실행 필요")
    
    with col3:
        total_memory = 0
        if st.session_state.chat_data is not None:
            total_memory += st.session_state.chat_data.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric("💾 메모리 사용량", f"{total_memory:.1f} MB", delta="세션 데이터")
    
    st.markdown("---")
    
    # 데이터 관리 기능들
    if st.session_state.chat_data is not None:
        st.subheader("🛠️ 데이터 관리 도구")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📁 CSV 내보내기", use_container_width=True):
                try:
                    csv_data = st.session_state.chat_data.to_csv(index=False)
                    st.download_button(
                        label="💾 CSV 파일 다운로드",
                        data=csv_data,
                        file_name=f"chat_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    st.success("✅ CSV 파일 준비 완료!")
                except Exception as e:
                    st.error(f"❌ CSV 내보내기 실패: {str(e)}")
        
        with col2:
            if st.session_state.analysis_results is not None:
                if st.button("📋 분석 결과 저장", use_container_width=True):
                    try:
                        import json
                        analysis_json = json.dumps(st.session_state.analysis_results, ensure_ascii=False, indent=2)
                        st.download_button(
                            label="💾 분석 결과 다운로드",
                            data=analysis_json,
                            file_name=f"analysis_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                        st.success("✅ 분석 결과 준비 완료!")
                    except Exception as e:
                        st.error(f"❌ 분석 결과 저장 실패: {str(e)}")
            else:
                st.button("📋 분석 결과 없음", disabled=True, use_container_width=True)
        
        with col3:
            if st.button("🗑️ 데이터 초기화", use_container_width=True, type="secondary"):
                if st.button("⚠️ 정말 초기화하시겠습니까?", type="primary", use_container_width=True):
                    st.session_state.chat_data = None
                    st.session_state.analysis_results = None
                    st.session_state.selected_room = None
                    st.success("✅ 모든 데이터가 초기화되었습니다.")
                    st.rerun()
    
    else:
        st.info("💡 데이터 관리 기능을 사용하려면 먼저 채팅 파일을 업로드해주세요.")

# 설정 섹션
elif selected == "⚙️ 설정":
    st.header("⚙️ 설정")
    
    # 환경 설정
    st.subheader("🌍 환경 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔑 API 설정**")
        
        # OpenAI API 키 설정
        openai_key = st.text_input(
            "OpenAI API 키",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            help="OpenAI GPT 분석을 위한 API 키"
        )
        
        if openai_key:
            st.success("✅ OpenAI API 키가 설정되었습니다.")
        else:
            st.warning("⚠️ OpenAI API 키를 설정하면 GPT 분석을 사용할 수 있습니다.")
    
    with col2:
        st.markdown("**🎨 UI 설정**")
        
        # 테마 설정 (현재는 빨간색 고정)
        theme_color = st.selectbox(
            "테마 색상",
            ["빨간색 (Red)", "파란색 (Blue)", "초록색 (Green)", "보라색 (Purple)"],
            index=0,
            disabled=True,
            help="현재 빨간색 테마만 지원됩니다."
        )
        
        # 언어 설정
        language = st.selectbox(
            "언어",
            ["한국어", "English"],
            index=0,
            disabled=True,
            help="현재 한국어만 지원됩니다."
        )
    
    st.markdown("---")
    
    # 분석 설정
    st.subheader("📊 분석 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🤖 GPT 분석 설정**")
        
        default_model = st.selectbox(
            "기본 GPT 모델",
            ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"],
            index=0,
            help="GPT 분석에 사용할 기본 모델"
        )
        
        default_sample_size = st.slider(
            "기본 분석 메시지 수",
            100, 2000, 500,
            help="GPT 분석 시 기본으로 사용할 메시지 수"
        )
    
    with col2:
        st.markdown("**📈 시각화 설정**")
        
        chart_theme = st.selectbox(
            "차트 테마",
            ["빨간색", "기본"],
            index=0,
            help="차트 및 그래프의 기본 색상 테마"
        )
        
        chart_height = st.slider(
            "기본 차트 높이",
            300, 800, 400,
            help="차트의 기본 높이 (픽셀)"
        )
    
    st.markdown("---")
    
    # 시스템 정보
    st.subheader("🖥️ 시스템 정보")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📦 Streamlit 버전", st.__version__)
    
    with col2:
        st.metric("🐍 Python 버전", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    with col3:
        st.metric("💾 세션 ID", str(id(st.session_state))[-6:])
    
    # 고급 설정
    with st.expander("🔧 고급 설정", expanded=False):
        st.markdown("""
        ### 개발자 옵션
        - **디버그 모드**: 상세한 로그 출력
        - **캐시 설정**: 데이터 캐싱 옵션
        - **성능 모니터링**: 실행 시간 측정
        """)
        
        debug_mode = st.checkbox("디버그 모드 활성화", value=False)
        cache_enabled = st.checkbox("데이터 캐싱 활성화", value=True)
        performance_monitoring = st.checkbox("성능 모니터링 활성화", value=False)
        
        if debug_mode:
            st.info("🐛 디버그 모드가 활성화되었습니다.")
        
        if st.button("🔄 설정 초기화"):
            st.success("✅ 모든 설정이 기본값으로 초기화되었습니다.")

# 하단 정보
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em; padding: 20px;'>
    <p>💬 <strong>카카오톡 채팅 분석기 v2.0</strong></p>
    <p>🚀 AI 기반 스마트 채팅 분석 플랫폼 | Made with ❤️ using Streamlit</p>
    <p>🔗 <a href="https://github.com" style="color: #ff6b6b;">GitHub</a> | 
       📧 <a href="mailto:support@example.com" style="color: #ff6b6b;">Support</a> | 
       📚 <a href="#" style="color: #ff6b6b;">Documentation</a></p>
</div>
""", unsafe_allow_html=True) 