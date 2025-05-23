import SwiftUI

struct HistoryView: View {
    @State private var chatRooms: [ChatRoom] = []
    @State private var isLoading = false
    @State private var searchText = ""
    
    var body: some View {
        NavigationView {
            VStack {
                if chatRooms.isEmpty {
                    VStack(spacing: 15) {
                        Image(systemName: "message")
                            .font(.system(size: 50))
                            .foregroundColor(.gray)
                        Text("저장된 채팅방이 없습니다")
                            .font(.headline)
                            .foregroundColor(.gray)
                        Text("먼저 파일을 업로드해주세요")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                } else {
                    List(chatRooms) { room in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(room.name)
                                .font(.headline)
                            Text("\(room.totalMessages)개 메시지")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .padding(.vertical, 4)
                    }
                }
            }
            .navigationTitle("채팅방 히스토리")
            .onAppear {
                loadRooms()
            }
        }
    }
    
    private func loadRooms() {
        // 더미 데이터
        chatRooms = [
            ChatRoom(id: "1", name: "친구들과의 대화", totalMessages: 1250),
            ChatRoom(id: "2", name: "회사 팀 채팅", totalMessages: 890),
            ChatRoom(id: "3", name: "가족 단톡방", totalMessages: 2340)
        ]
    }
}

struct ChatRoom: Identifiable {
    let id: String
    let name: String
    let totalMessages: Int
}

#Preview {
    HistoryView()
} 