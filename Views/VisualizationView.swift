import SwiftUI
import Charts

struct VisualizationView: View {
    @State private var selectedVisualization: VisualizationType = .timeAnalysis
    @State private var showResults = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 25) {
                    // 헤더
                    VStack(spacing: 10) {
                        Image(systemName: "chart.bar.fill")
                            .font(.system(size: 50))
                            .foregroundColor(.blue)
                        Text("데이터 시각화")
                            .font(.title)
                            .fontWeight(.bold)
                        Text("채팅 데이터를 시각적으로 분석")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding(.top)
                    
                    // 시각화 유형 선택
                    VStack(alignment: .leading, spacing: 15) {
                        Text("시각화 유형")
                            .font(.headline)
                        
                        Picker("시각화 유형", selection: $selectedVisualization) {
                            Text("시간대별 활동").tag(VisualizationType.timeAnalysis)
                            Text("사용자별 통계").tag(VisualizationType.userStats)
                            Text("키워드 분석").tag(VisualizationType.keywordAnalysis)
                            Text("전체 요약").tag(VisualizationType.summary)
                        }
                        .pickerStyle(SegmentedPickerStyle())
                        .onChange(of: selectedVisualization) { _ in
                            generateVisualization()
                        }
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(12)
                    
                    // 시각화 결과
                    if showResults {
                        VStack(alignment: .leading, spacing: 15) {
                            Text("📊 \(selectedVisualization.title)")
                                .font(.headline)
                                .fontWeight(.semibold)
                            
                            switch selectedVisualization {
                            case .timeAnalysis:
                                TimeAnalysisChart()
                            case .userStats:
                                UserStatsChart()
                            case .keywordAnalysis:
                                KeywordAnalysisView()
                            case .summary:
                                SummaryStatsView()
                            }
                        }
                        .padding()
                        .background(Color.white)
                        .cornerRadius(15)
                        .shadow(radius: 2)
                    } else {
                        VStack(spacing: 15) {
                            Image(systemName: "chart.pie")
                                .font(.system(size: 40))
                                .foregroundColor(.gray)
                            Text("시각화 유형을 선택해주세요")
                                .font(.headline)
                                .foregroundColor(.gray)
                        }
                        .padding(.vertical, 50)
                    }
                }
                .padding()
            }
            .navigationTitle("시각화")
            .navigationBarTitleDisplayMode(.inline)
            .onAppear {
                generateVisualization()
            }
        }
    }
    
    private func generateVisualization() {
        showResults = true
    }
}

struct TimeAnalysisChart: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            // 간단한 막대 차트 시뮬레이션
            HStack(alignment: .bottom, spacing: 8) {
                ForEach(0..<24, id: \.self) { hour in
                    let height = CGFloat.random(in: 20...100)
                    Rectangle()
                        .fill(Color.blue.gradient)
                        .frame(width: 8, height: height)
                        .cornerRadius(2)
                }
            }
            .frame(height: 120)
            
            Text("📈 가장 활발한 시간: 오후 8시")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
}

struct UserStatsChart: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            HStack {
                ForEach(["김철수", "이영희", "박민수"], id: \.self) { user in
                    VStack {
                        Circle()
                            .fill(Color.blue.opacity(0.3))
                            .frame(width: 50, height: 50)
                            .overlay(
                                Text("\(Int.random(in: 20...40))%")
                                    .font(.caption)
                                    .fontWeight(.bold)
                            )
                        Text(user)
                            .font(.caption2)
                    }
                }
            }
            
            Text("👥 가장 활발한 사용자: 김철수")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
}

struct KeywordAnalysisView: View {
    let keywords = ["오늘", "일", "좋아", "시간", "회사", "집", "밥"]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 3), spacing: 10) {
                ForEach(keywords, id: \.self) { keyword in
                    Text(keyword)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(8)
                }
            }
            
            Text("🔍 일상적인 키워드가 주를 이룹니다")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
}

struct SummaryStatsView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 15) {
                StatCard(icon: "message.fill", title: "총 메시지", value: "1,247")
                StatCard(icon: "person.3.fill", title: "참여자", value: "5명")
                StatCard(icon: "calendar", title: "활동 기간", value: "90일")
                StatCard(icon: "clock.fill", title: "평균 응답시간", value: "12분")
            }
        }
    }
}

struct StatCard: View {
    let icon: String
    let title: String
    let value: String
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.blue)
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.headline)
                .fontWeight(.bold)
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(10)
    }
}

enum VisualizationType: String, CaseIterable {
    case timeAnalysis = "time"
    case userStats = "users"
    case keywordAnalysis = "keywords"
    case summary = "summary"
    
    var title: String {
        switch self {
        case .timeAnalysis: return "시간대별 활동"
        case .userStats: return "사용자별 통계"
        case .keywordAnalysis: return "키워드 분석"
        case .summary: return "전체 요약"
        }
    }
}

#Preview {
    VisualizationView()
} 