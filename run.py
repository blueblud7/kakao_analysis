#!/usr/bin/env python3
"""
카카오톡 채팅 분석기 실행 스크립트
"""

import subprocess
import sys
import os

def check_requirements():
    """필요한 패키지가 설치되어 있는지 확인"""
    try:
        import streamlit
        import pandas
        import openai
        import plotly
        import wordcloud
        print("✅ 모든 필수 패키지가 설치되어 있습니다.")
        return True
    except ImportError as e:
        print(f"❌ 필수 패키지가 누락되었습니다: {e}")
        print("다음 명령어로 설치해주세요:")
        print("pip install -r requirements.txt")
        return False

def run_app():
    """Streamlit 앱 실행"""
    print("🚀 카카오톡 채팅 분석기를 시작합니다...")
    print("브라우저에서 http://localhost:8501 에 접속하세요")
    print("종료하려면 Ctrl+C를 누르세요")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 카카오톡 채팅 분석기를 종료합니다.")
    except Exception as e:
        print(f"❌ 실행 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    print("💬 카카오톡 오픈챗 분석기")
    print("=" * 50)
    
    # 현재 디렉토리 확인
    if not os.path.exists("app.py"):
        print("❌ app.py 파일을 찾을 수 없습니다.")
        print("프로젝트 루트 디렉토리에서 실행해주세요.")
        sys.exit(1)
    
    # 패키지 확인
    if not check_requirements():
        sys.exit(1)
    
    # 앱 실행
    run_app() 