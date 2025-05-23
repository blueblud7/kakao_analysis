import SwiftUI

@main
struct KakaoAnalysisApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            FileUploadView()
                .tabItem {
                    Image(systemName: "folder")
                    Text("파일 업로드")
                }
                .tag(0)
            
            HistoryView()
                .tabItem {
                    Image(systemName: "clock")
                    Text("히스토리")
                }
                .tag(1)
            
            AnalysisView()
                .tabItem {
                    Image(systemName: "brain.head.profile")
                    Text("GPT 분석")
                }
                .tag(2)
            
            VisualizationView()
                .tabItem {
                    Image(systemName: "chart.bar")
                    Text("시각화")
                }
                .tag(3)
        }
        .accentColor(.blue)
    }
}

#Preview {
    ContentView()
} 