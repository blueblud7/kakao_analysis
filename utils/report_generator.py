import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import base64
from datetime import datetime
import tempfile
import os

class ReportGenerator:
    """분석 결과 리포트 생성 클래스"""
    
    def __init__(self):
        # 폰트 설정 (한글 지원)
        try:
            # macOS/Windows에서 사용 가능한 한글 폰트 찾기
            font_paths = [
                '/System/Library/Fonts/AppleSDGothicNeo.ttc',  # macOS
                'C:/Windows/Fonts/malgun.ttf',  # Windows
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',  # Linux
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Korean', font_path))
                    break
        except:
            pass  # 폰트 등록 실패 시 기본 폰트 사용
        
        self.styles = getSampleStyleSheet()
        
        # 한글 스타일 추가
        try:
            self.korean_style = ParagraphStyle(
                'Korean',
                parent=self.styles['Normal'],
                fontName='Korean',
                fontSize=10,
                leading=14,
                encoding='utf-8'
            )
            
            self.korean_title = ParagraphStyle(
                'KoreanTitle',
                parent=self.styles['Title'],
                fontName='Korean',
                fontSize=16,
                leading=20,
                encoding='utf-8'
            )
        except:
            self.korean_style = self.styles['Normal']
            self.korean_title = self.styles['Title']
    
    def generate_pdf_report(self, chat_data, analysis_results=None, filtered_data=None):
        """PDF 리포트 생성"""
        
        # 임시 파일 생성
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        
        # 문서 요소들
        story = []
        
        # 제목
        title = Paragraph("카카오톡 채팅 분석 리포트", self.korean_title)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # 분석 날짜
        date_str = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        date_para = Paragraph(f"분석일시: {date_str}", self.korean_style)
        story.append(date_para)
        story.append(Spacer(1, 20))
        
        # 기본 통계
        story.append(Paragraph("📊 기본 통계", self.korean_title))
        story.append(Spacer(1, 12))
        
        data_to_use = filtered_data if filtered_data is not None else chat_data
        
        stats_data = [
            ['항목', '값'],
            ['총 메시지 수', f"{len(data_to_use):,} 개"],
            ['참여자 수', f"{data_to_use['user'].nunique()} 명"],
            ['분석 기간', f"{data_to_use['datetime'].min().strftime('%Y-%m-%d')} ~ {data_to_use['datetime'].max().strftime('%Y-%m-%d')}"],
            ['총 일수', f"{(data_to_use['datetime'].max() - data_to_use['datetime'].min()).days} 일"],
            ['평균 메시지 길이', f"{data_to_use['message'].str.len().mean():.1f} 자"]
        ]
        
        stats_table = Table(stats_data)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Korean'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # 사용자별 통계
        story.append(Paragraph("👥 사용자별 통계", self.korean_title))
        story.append(Spacer(1, 12))
        
        user_stats = data_to_use['user'].value_counts().head(10)
        user_data = [['사용자', '메시지 수', '비율']]
        total_messages = len(data_to_use)
        
        for user, count in user_stats.items():
            percentage = (count / total_messages) * 100
            user_data.append([user, f"{count:,}", f"{percentage:.1f}%"])
        
        user_table = Table(user_data)
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Korean'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(user_table)
        story.append(PageBreak())
        
        # GPT 분석 결과
        if analysis_results:
            story.append(Paragraph("🤖 GPT 분석 결과", self.korean_title))
            story.append(Spacer(1, 12))
            
            # 분석 유형
            analysis_type = analysis_results.get('analysis_type', '종합 분석')
            type_para = Paragraph(f"분석 유형: {analysis_type}", self.korean_style)
            story.append(type_para)
            story.append(Spacer(1, 12))
            
            # 분석 내용
            summary = analysis_results.get('summary', '분석 결과가 없습니다.')
            # 긴 텍스트를 여러 단락으로 나누기
            paragraphs = summary.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), self.korean_style))
                    story.append(Spacer(1, 8))
            
            story.append(Spacer(1, 20))
        
        # 차트 이미지 추가 (시간대별 활동)
        story.append(Paragraph("📈 시간대별 활동 패턴", self.korean_title))
        story.append(Spacer(1, 12))
        
        # 시간대별 차트 생성
        chart_buffer = self.create_hourly_chart(data_to_use)
        if chart_buffer:
            img = Image(chart_buffer, width=6*inch, height=4*inch)
            story.append(img)
        
        # PDF 생성
        doc.build(story)
        pdf_buffer.seek(0)
        
        return pdf_buffer.getvalue()
    
    def create_hourly_chart(self, data):
        """시간대별 차트 생성"""
        try:
            hourly_data = data.groupby(data['datetime'].dt.hour).size()
            
            plt.figure(figsize=(10, 6))
            plt.bar(hourly_data.index, hourly_data.values, color='skyblue')
            plt.title('시간대별 메시지 수', fontsize=14, pad=20)
            plt.xlabel('시간', fontsize=12)
            plt.ylabel('메시지 수', fontsize=12)
            plt.xticks(range(0, 24, 2))
            plt.grid(axis='y', alpha=0.3)
            
            # 임시 파일로 저장
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        except:
            return None
    
    def generate_excel_report(self, chat_data, analysis_results=None, filtered_data=None):
        """Excel 리포트 생성"""
        
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            data_to_use = filtered_data if filtered_data is not None else chat_data
            
            # 워크북과 워크시트 가져오기
            workbook = writer.book
            
            # 셀 형식 정의
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # 1. 요약 시트
            summary_data = {
                '항목': ['총 메시지 수', '참여자 수', '분석 기간 시작', '분석 기간 종료', '총 일수', '평균 메시지 길이'],
                '값': [
                    len(data_to_use),
                    data_to_use['user'].nunique(),
                    data_to_use['datetime'].min().strftime('%Y-%m-%d'),
                    data_to_use['datetime'].max().strftime('%Y-%m-%d'),
                    (data_to_use['datetime'].max() - data_to_use['datetime'].min()).days,
                    f"{data_to_use['message'].str.len().mean():.1f} 자"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='요약', index=False)
            
            worksheet = writer.sheets['요약']
            for col_num, value in enumerate(summary_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # 2. 전체 데이터 시트
            data_to_export = data_to_use.copy()
            data_to_export['날짜'] = data_to_export['datetime'].dt.strftime('%Y-%m-%d')
            data_to_export['시간'] = data_to_export['datetime'].dt.strftime('%H:%M:%S')
            export_cols = ['날짜', '시간', 'user', 'message']
            data_to_export[export_cols].to_excel(writer, sheet_name='전체 데이터', index=False)
            
            # 3. 사용자별 통계 시트
            user_stats = data_to_use['user'].value_counts().reset_index()
            user_stats.columns = ['사용자', '메시지 수']
            user_stats['비율(%)'] = (user_stats['메시지 수'] / len(data_to_use) * 100).round(1)
            user_stats.to_excel(writer, sheet_name='사용자별 통계', index=False)
            
            # 4. 시간대별 통계 시트
            hourly_stats = data_to_use.groupby(data_to_use['datetime'].dt.hour).size().reset_index()
            hourly_stats.columns = ['시간', '메시지 수']
            hourly_stats.to_excel(writer, sheet_name='시간대별 통계', index=False)
            
            # 5. GPT 분석 결과 시트 (있는 경우)
            if analysis_results:
                analysis_data = {
                    '항목': ['분석 유형', '분석 시간', '요약'],
                    '내용': [
                        analysis_results.get('analysis_type', ''),
                        analysis_results.get('timestamp', ''),
                        analysis_results.get('summary', '')
                    ]
                }
                
                analysis_df = pd.DataFrame(analysis_data)
                analysis_df.to_excel(writer, sheet_name='GPT 분석 결과', index=False)
                
                # 키워드가 있는 경우
                if 'keywords' in analysis_results and analysis_results['keywords']:
                    keywords_df = pd.DataFrame(analysis_results['keywords'], columns=['주요 키워드'])
                    keywords_df.to_excel(writer, sheet_name='주요 키워드', index=False)
        
        excel_buffer.seek(0)
        return excel_buffer.getvalue()
    
    def create_download_link(self, file_data, filename, file_type):
        """다운로드 링크 생성"""
        b64 = base64.b64encode(file_data).decode()
        
        if file_type == 'pdf':
            mime_type = 'application/pdf'
        elif file_type == 'excel':
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            mime_type = 'application/octet-stream'
        
        href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}">📥 {filename} 다운로드</a>'
        return href 