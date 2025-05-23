import SwiftUI

struct AnalysisView: View {
    @State private var apiKey = ""
    @State private var selectedAnalysisType: AnalysisType = .comprehensive
    @State private var isAnalyzing = false
    @State private var analysisResult = ""
    @State private var showResult = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 25) {
                    // 헤더
                    VStack(spacing: 10) {
                        Image(systemName: "brain.head.profile")
                            .font(.system(size: 50))
                            .foregroundColor(.blue)
                        Text("GPT 채팅 분석")
                            .font(.title)
                            .fontWeight(.bold)
                        Text("AI를 활용한 채팅 데이터 분석")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding(.top)
                    
                    // API 키 입력
                    VStack(alignment: .leading, spacing: 10) {
                        Text("OpenAI API 키")
                            .font(.headline)
                        
                        SecureField("API 키를 입력하세요", text: $apiKey)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .autocapitalization(.none)
                            .disableAutocorrection(true)
                        
                        HStack {
                            Image(systemName: "info.circle")
                                .foregroundColor(.blue)
                            Text("API 키는 저장되지 않으며, 분석에만 사용됩니다")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(12)
                    
                    // 분석 유형 선택
                    VStack(alignment: .leading, spacing: 15) {
                        Text("분석 유형 선택")
                            .font(.headline)
                        
                        Picker("분석 유형", selection: $selectedAnalysisType) {
                            Text("종합 분석").tag(AnalysisType.comprehensive)
                            Text("감정 분석").tag(AnalysisType.sentiment)
                            Text("키워드 추출").tag(AnalysisType.keywords)
                            Text("토픽 분석").tag(AnalysisType.topics)
                        }
                        .pickerStyle(SegmentedPickerStyle())
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(12)
                    
                    // 분석 시작 버튼
                    Button(action: startAnalysis) {
                        HStack {
                            if isAnalyzing {
                                ProgressView()
                                    .scaleEffect(0.8)
                            } else {
                                Image(systemName: "play.circle.fill")
                            }
                            Text(isAnalyzing ? "분석 중..." : "🚀 분석 시작")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(
                            canStartAnalysis ? Color.blue : Color.gray
                        )
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    .disabled(!canStartAnalysis || isAnalyzing)
                    
                    // 분석 결과
                    if showResult {
                        VStack(alignment: .leading, spacing: 15) {
                            Text("📊 분석 결과")
                                .font(.headline)
                                .fontWeight(.semibold)
                            
                            Text(analysisResult)
                                .font(.body)
                                .padding()
                                .background(Color.blue.opacity(0.05))
                                .cornerRadius(12)
                        }
                        .padding()
                        .background(Color.white)
                        .cornerRadius(15)
                        .shadow(radius: 2)
                    }
                }
                .padding()
            }
            .navigationTitle("GPT 분석")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
    
    private var canStartAnalysis: Bool {
        !apiKey.isEmpty && !isAnalyzing
    }
    
    private func startAnalysis() {
        guard canStartAnalysis else { return }
        
        isAnalyzing = true
        showResult = false
        
        // 분석 시뮬레이션
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            isAnalyzing = false
            showResult = true
            analysisResult = generateSampleResult(for: selectedAnalysisType)
        }
    }
    
    private func generateSampleResult(for type: AnalysisType) -> String {
        switch type {
        case .comprehensive:
            return "📊 종합 분석 결과\n\n총 메시지 수: 1,247개\n참여자 수: 5명\n가장 활발한 시간대: 오후 8-10시\n\n이 채팅방은 친밀한 관계의 사람들이 일상을 공유하는 공간입니다."
        case .sentiment:
            return "😊 감정 분석 결과\n\n긍정적: 68%\n중립적: 24%\n부정적: 8%\n\n전반적으로 긍정적인 분위기의 채팅방입니다."
        case .keywords:
            return "🔑 주요 키워드\n\n1. 오늘 (89회)\n2. 일 (76회)\n3. 좋아 (64회)\n4. 시간 (58회)\n5. 회사 (45회)\n\n일상적인 대화가 주를 이룹니다."
        case .topics:
            return "📋 토픽 분석\n\n일상 대화 (35%)\n업무/학업 (22%)\n여가 활동 (18%)\n음식/맛집 (12%)\n기타 (13%)\n\n다양한 주제로 균형잡힌 대화를 나누고 있습니다."
        }
    }
}

enum AnalysisType: String, CaseIterable {
    case comprehensive = "comprehensive"
    case sentiment = "sentiment"
    case keywords = "keywords"
    case topics = "topics"
}

#Preview {
    AnalysisView()
} 