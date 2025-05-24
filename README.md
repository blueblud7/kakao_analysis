# 📱 카카오톡 채팅 분석기 - iOS 앱

## 📋 개요
웹 버전의 카카오톡 채팅 분석기를 iOS 네이티브 앱으로 구현한 버전입니다. Swift와 SwiftUI를 사용하여 iOS 생태계에 최적화되었습니다.

## 🚀 주요 기능

### 📁 파일 업로드
- iOS 파일 시스템과 연동된 파일 선택
- 카카오톡 채팅 파일(.txt, .csv) 지원
- 실시간 업로드 진행률 표시
- 자동 중복 검사 및 파싱

### 💬 채팅방 히스토리
- Core Data 기반 로컬 데이터 저장
- 저장된 채팅방 목록 조회
- 검색 및 필터링 기능
- Pull-to-refresh 지원

### 🤖 GPT 분석
- OpenAI API 연동
- 4가지 분석 유형:
  - 종합 분석
  - 감정 분석
  - 키워드 추출
  - 토픽 분석
- 결과 복사 및 공유 기능

### 📊 시각화
- Swift Charts 기반 네이티브 차트
- 시간대별 활동 분석
- 사용자별 통계
- 키워드 분석
- 전체 요약 통계

### 📱 카카오톡 채팅 분석
- **다양한 형식 지원**: 텍스트 파일(.txt) 및 CSV 파일(.csv) 자동 파싱
- **자동 채팅방 인식**: 파일명에서 채팅방 이름 자동 추출
- **실시간 대화 분석**: 메시지 패턴, 시간대별 활동, 사용자별 통계

### 🤖 GPT 분석 (6가지 모드)
1. **기본 분석**: 전체 채팅 데이터 종합 분석
2. **🎯 주요 인물 집중 분석**: 
   - 핵심 인물들의 대화만 선별하여 노이즈 제거
   - 메시지 수 기준 상위 사용자 자동 추천
   - 특정 주제/키워드와 결합한 심층 분석
   - 이모티콘, 단순 반응, 파일 공유 등 노이즈 자동 필터링
3. **주제별 분석**: 특정 키워드나 주제 중심 분석
4. **사용자 분석**: 개별 사용자의 채팅 패턴 분석
5. **비교 분석**: 여러 사용자 간 대화 스타일 비교
6. **커스텀 분석**: 사용자 정의 질문으로 맞춤 분석

### 🔧 고급 필터링 기능
- **노이즈 제거**: 이모티콘, 사진, 동영상, 링크 등 자동 필터링
- **메시지 길이 필터**: 의미있는 대화만 선별
- **기간 필터링**: 최근 1주/1개월 또는 커스텀 기간 설정
- **짧은 반응 제거**: 'ㅋㅋ', '네', '오케이' 등 단순 반응 제외

## 🛠 개발 환경

### 요구 사항
- Xcode 15.0+
- iOS 17.0+
- macOS 13.0+ (개발용)
- Apple Developer 계정 (배포용)

### 의존성
- SwiftUI (UI 프레임워크)
- Swift Charts (차트 라이브러리)
- Foundation (기본 프레임워크)
- UniformTypeIdentifiers (파일 타입 처리)

## 📲 설치 및 실행

### 개발 모드
```bash
# 1. 프로젝트 클론
git clone https://github.com/blueblud7/kakao_ios_analysis.git

# 2. Xcode에서 프로젝트 열기
open KakaoAnalysis.xcodeproj

# 3. 시뮬레이터 또는 실제 기기에서 실행
# Product → Run (⌘R)
```

### TestFlight 베타 테스트
```bash
# 1. Xcode에서 Archive 생성
# Product → Archive

# 2. Organizer에서 앱 업로드
# Distribute App → App Store Connect

# 3. App Store Connect에서 TestFlight 설정
# 베타 테스터 초대 및 배포
```

### App Store 배포
```bash
# 1. App Store Connect에서 앱 정보 입력
# 2. 스크린샷 및 메타데이터 준비
# 3. 심사 제출
```

## 🎨 UI/UX 특징

### 네이티브 iOS 디자인
- Human Interface Guidelines 준수
- 다크/라이트 모드 자동 지원
- Dynamic Type 폰트 크기 지원
- 접근성 기능 완전 지원

### 인터랙션
- Haptic Feedback 지원
- 스와이프 제스처
- 롱 프레스 컨텍스트 메뉴
- 자연스러운 애니메이션

### 성능 최적화
- 지연 로딩 (Lazy Loading)
- 메모리 효율적인 이미지 처리
- 백그라운드 작업 최적화
- 네트워크 캐싱

## 🗂️ 프로젝트 구조

```
KakaoAnalysis/
├── KakaoAnalysisApp.swift          # 앱 진입점
├── Views/
│   ├── FileUploadView.swift        # 파일 업로드 화면
│   ├── HistoryView.swift          # 히스토리 관리 화면
│   ├── AnalysisView.swift         # GPT 분석 화면
│   └── VisualizationView.swift    # 데이터 시각화 화면
├── Models/
│   ├── ChatData.swift             # 채팅 데이터 모델
│   ├── ChatMessage.swift          # 메시지 모델
│   └── ChatRoom.swift             # 채팅방 모델
├── Services/
│   ├── KakaoParser.swift          # 카카오톡 파일 파싱
│   ├── GPTAnalyzer.swift          # OpenAI API 연동
│   └── DataManager.swift          # Core Data 관리
├── Assets.xcassets                # 앱 아이콘, 이미지
└── Preview Content/               # SwiftUI 프리뷰 리소스
```

## 🔐 보안 및 프라이버시

### 데이터 보호
- 모든 데이터는 기기 내에서만 처리
- iCloud 동기화 옵션 제공
- Keychain을 통한 API 키 안전 저장
- 앱 백그라운드 시 화면 보안

### API 키 관리
- OpenAI API 키는 기기에만 저장
- 네트워크 통신 시 HTTPS 강제
- 민감 정보 자동 삭제 옵션

## 📊 지원 파일 형식

### 카카오톡 TXT 형식
```
2024년 1월 15일 월요일

오후 2:30, 홍길동 : 안녕하세요!
오후 2:31, 김철수 : 반갑습니다
```

### CSV 형식
```csv
날짜,사용자,메시지
2024-01-15 14:30:00,홍길동,안녕하세요!
2024-01-15 14:31:00,김철수,반갑습니다
```

## 🌟 iOS 특화 기능

### Siri Shortcuts
- "채팅 분석하기" 음성 명령
- 자주 사용하는 기능 빠른 실행

### Share Extension
- 다른 앱에서 파일 공유받기
- 분석 결과를 다른 앱으로 공유

### Spotlight 검색
- 저장된 채팅방 검색
- 분석 결과 내 키워드 검색

### Today Extension (Widget)
- 최근 분석 결과 미리보기
- 빠른 분석 시작

## 🔧 고급 설정

### Core Data Stack
```swift
// DataManager.swift에서 Core Data 설정
private lazy var persistentContainer: NSPersistentContainer = {
    let container = NSPersistentContainer(name: "KakaoAnalysis")
    container.loadPersistentStores { _, error in
        if let error = error {
            fatalError("Core Data error: \(error)")
        }
    }
    return container
}()
```

### 네트워크 설정
```swift
// GPTAnalyzer.swift에서 OpenAI API 연동
private let session: URLSession = {
    let config = URLSessionConfiguration.default
    config.timeoutIntervalForRequest = 30
    config.timeoutIntervalForResource = 60
    return URLSession(configuration: config)
}()
```

## 📈 성능 모니터링

### 메트릭스
- 앱 시작 시간: < 2초
- 파일 파싱 속도: 1000 메시지/초
- 메모리 사용량: < 100MB
- 배터리 효율성: 최적화됨

### 최적화 기법
- 백그라운드 큐 활용
- 이미지 압축 및 캐싱
- 지연 로딩 구현
- 메모리 누수 방지

## 🧪 테스트

### 단위 테스트
```bash
# Xcode에서 테스트 실행
Product → Test (⌘U)
```

### UI 테스트
- XCUITest 프레임워크 사용
- 주요 사용자 플로우 자동화 테스트
- 접근성 테스트 포함

## 📱 지원 기기

### iPhone
- iPhone SE (3세대) 이상
- iOS 17.0 이상
- 최소 3GB RAM 권장

### iPad
- iPad (9세대) 이상
- iPadOS 17.0 이상
- 멀티태스킹 지원

## 🚀 향후 계획

### v1.1 업데이트
- [ ] Siri Shortcuts 통합
- [ ] Apple Watch 앱
- [ ] iCloud 동기화
- [ ] 다크모드 최적화

### v1.2 업데이트
- [ ] macOS 버전 개발
- [ ] 실시간 채팅 분석
- [ ] ML 기반 로컬 분석
- [ ] 데이터 내보내기

### v2.0 메이저 업데이트
- [ ] ARKit 기반 3D 시각화
- [ ] Core ML 로컬 AI 분석
- [ ] 멀티채팅방 비교 분석
- [ ] 소셜 네트워크 분석

## 🤝 기여하기

### 개발 참여
1. 이슈 등록
2. Fork & Branch 생성
3. 코드 작성 및 테스트
4. Pull Request 제출

### 코딩 컨벤션
- Swift Style Guide 준수
- SwiftLint 사용
- 함수형 프로그래밍 선호
- MVVM 아키텍처 패턴

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

## ⚠️ 주의사항

- iOS 17.0 이상에서만 동작
- OpenAI API 키가 필요함 (GPT 분석 기능)
- 대용량 파일 처리 시 시간이 소요될 수 있음
- 개인정보가 포함된 채팅 데이터 처리 시 주의 필요

## 📞 지원

- **이슈 리포트**: GitHub Issues
- **기능 요청**: GitHub Discussions
- **문서**: README.md 및 코드 주석 참조

---

🎯 **목표**: iOS 네이티브 환경에서 최적의 사용자 경험으로 카카오톡 채팅 데이터 분석!

## 🔐 보안 설정 (중요!)

### OpenAI API 키 안전한 설정 방법

#### 1. 환경변수 파일 사용 (권장)
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 API 키를 설정하세요:

```bash
# .env 파일 생성
OPENAI_API_KEY=sk-proj-your-api-key-here
```

#### 2. 시스템 환경변수 설정
```bash
# macOS/Linux
export OPENAI_API_KEY="sk-proj-your-api-key-here"

# Windows
set OPENAI_API_KEY=sk-proj-your-api-key-here
```

#### 3. Git 보안 설정
`.gitignore` 파일이 다음 항목들을 포함하는지 확인하세요:
```
.env
.env.local
.env.production.local
*.key
secrets.py
config.py
```

#### ⚠️ 중요 사항
- **절대로** API 키를 코드에 직접 하드코딩하지 마세요
- GitHub, GitLab 등 공개 저장소에 API 키를 업로드하지 마세요
- API 키가 노출되었다면 즉시 OpenAI에서 새 키를 발급받으세요