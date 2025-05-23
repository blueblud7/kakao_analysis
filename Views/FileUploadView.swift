import SwiftUI
import UniformTypeIdentifiers

struct FileUploadView: View {
    @State private var selectedFile: URL?
    @State private var isFilePickerPresented = false
    @State private var uploadProgress: Double = 0
    @State private var isUploading = false
    @State private var uploadMessage = "파일을 선택하고 업로드 버튼을 눌러주세요"
    @State private var chatData: ChatData?
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // 헤더
                Text("💬 카카오톡 채팅 분석기")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .padding(.top)
                
                // 파일 선택 영역
                VStack(spacing: 15) {
                    Text("카카오톡 채팅 파일을 선택해주세요")
                        .font(.headline)
                        .foregroundColor(.secondary)
                    
                    if let selectedFile = selectedFile {
                        HStack {
                            Image(systemName: "doc.text")
                                .foregroundColor(.blue)
                            Text(selectedFile.lastPathComponent)
                                .lineLimit(1)
                                .truncationMode(.middle)
                        }
                        .padding()
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(10)
                    }
                    
                    Button(action: {
                        isFilePickerPresented = true
                    }) {
                        HStack {
                            Image(systemName: "folder")
                            Text("파일 선택")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                    .fileImporter(
                        isPresented: $isFilePickerPresented,
                        allowedContentTypes: [UTType.text, UTType.commaSeparatedText],
                        allowsMultipleSelection: false
                    ) { result in
                        switch result {
                        case .success(let urls):
                            if let url = urls.first {
                                selectedFile = url
                                uploadMessage = "파일이 선택되었습니다: \(url.lastPathComponent)"
                            }
                        case .failure(let error):
                            uploadMessage = "파일 선택 실패: \(error.localizedDescription)"
                        }
                    }
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(15)
                
                // 업로드 버튼
                Button(action: uploadFile) {
                    HStack {
                        if isUploading {
                            ProgressView()
                                .scaleEffect(0.8)
                        } else {
                            Image(systemName: "arrow.up.circle")
                        }
                        Text(isUploading ? "업로드 중..." : "파일 업로드")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(selectedFile != nil && !isUploading ? Color.green : Color.gray)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                }
                .disabled(selectedFile == nil || isUploading)
                
                // 진행률 표시
                if isUploading {
                    VStack {
                        ProgressView(value: uploadProgress, total: 100)
                            .progressViewStyle(LinearProgressViewStyle())
                        Text("\(Int(uploadProgress))%")
                            .font(.caption)
                    }
                    .padding(.horizontal)
                }
                
                // 상태 메시지
                Text(uploadMessage)
                    .font(.body)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding()
                
                Spacer()
            }
            .padding()
            .navigationTitle("파일 업로드")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
    
    private func uploadFile() {
        guard let fileURL = selectedFile else { return }
        
        isUploading = true
        uploadProgress = 0
        uploadMessage = "파일을 처리하는 중..."
        
        // 파일 업로드 시뮬레이션
        DispatchQueue.global(qos: .userInitiated).async {
            for i in 0...100 {
                DispatchQueue.main.async {
                    uploadProgress = Double(i)
                    
                    switch i {
                    case 30:
                        uploadMessage = "파일을 읽는 중..."
                    case 60:
                        uploadMessage = "데이터를 파싱하는 중..."
                    case 90:
                        uploadMessage = "데이터베이스에 저장하는 중..."
                    case 100:
                        uploadMessage = "✅ 업로드 완료!"
                        isUploading = false
                        
                        // 실제 구현에서는 파일 파싱 및 데이터베이스 저장 로직 추가
                        chatData = parseKakaoFile(from: fileURL)
                    default:
                        break
                    }
                }
                Thread.sleep(forTimeInterval: 0.03) // 3초 총 소요
            }
        }
    }
    
    private func parseKakaoFile(from url: URL) -> ChatData? {
        // 실제 구현에서는 카카오톡 파일 파싱 로직 구현
        // 현재는 더미 데이터 반환
        return ChatData(
            messages: [],
            users: [],
            totalMessages: 0,
            dateRange: Date()...Date()
        )
    }
}

// 데이터 모델
struct ChatData {
    let messages: [ChatMessage]
    let users: [String]
    let totalMessages: Int
    let dateRange: ClosedRange<Date>
}

struct ChatMessage {
    let id = UUID()
    let user: String
    let message: String
    let timestamp: Date
}

#Preview {
    FileUploadView()
} 