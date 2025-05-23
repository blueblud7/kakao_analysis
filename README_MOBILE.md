# 📱 카카오톡 채팅 분석기 - React Native 모바일 앱

## 📋 개요
기존 웹 버전과 iOS 네이티브 앱의 모든 기능을 포함하는 **크로스 플랫폼 모바일 앱**입니다. React Native를 사용하여 iOS와 Android에서 모두 작동합니다.

## 🚀 주요 기능

### 📁 파일 업로드
- 카카오톡 채팅 파일(.txt, .csv) 업로드
- 실시간 파일 분석 및 미리보기
- 자동 중복 검사 및 통계 표시
- 서버 업로드 진행률 표시

### 💬 채팅방 히스토리
- 저장된 채팅방 목록 관리
- 참여자 정보 및 통계 확인
- 채팅방별 분석 및 내보내기
- Pull-to-refresh 지원

### 🤖 GPT 분석
- 4가지 분석 유형:
  - 종합 분석 (대화 패턴, 특징, 참여도)
  - 감정 분석 (긍정/중립/부정 분포)
  - 키워드 추출 (빈도수 기반 키워드)
  - 토픽 분석 (LDA 모델링 기반)
- 분석 결과 복사 및 공유
- 실시간 분석 진행률 표시

### 📊 데이터 시각화
- 시간대별 메시지 활동 차트
- 사용자별 참여도 통계
- 키워드 빈도 분석 차트
- 감정 분포 파이 차트
- 주요 인사이트 요약

### ⚙️ 설정
- 알림 설정
- 다크 모드 지원
- 자동 백업 설정
- OpenAI API 키 관리
- 데이터 관리 (캐시 삭제, 내보내기, 전체 삭제)

## 🛠 개발 환경

### 요구 사항
- Node.js 16.0+
- React Native CLI
- iOS: Xcode 14.0+ (iOS 13.0+)
- Android: Android Studio (API 21+)

### 의존성
- React Native 0.79.2
- React Navigation 6.x
- React Native Vector Icons
- React Native Chart Kit
- React Native Document Picker
- Axios (API 통신)

## 📲 설치 및 실행

### 개발 환경 설정
```bash
# 프로젝트 클론
git clone [repository-url]
cd KakaoAnalysisMobile

# 의존성 설치
npm install

# iOS 의존성 설치
cd ios && bundle install && bundle exec pod install && cd ..
```

### iOS 실행
```bash
# iOS 시뮬레이터에서 실행
npx react-native run-ios

# 특정 기기에서 실행
npx react-native run-ios --device "iPhone 15"
```

### Android 실행
```bash
# Android 에뮬레이터 시작 후
npx react-native run-android
```

### 개발 서버 시작
```bash
# Metro 서버 시작
npx react-native start

# 캐시 클리어 후 시작
npx react-native start --reset-cache
```

## 🏗️ 프로젝트 구조

```
KakaoAnalysisMobile/
├── src/
│   ├── screens/           # 화면 컴포넌트
│   │   ├── FileUploadScreen.tsx
│   │   ├── HistoryScreen.tsx
│   │   ├── AnalysisScreen.tsx
│   │   ├── VisualizationScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── components/        # 재사용 컴포넌트
│   ├── services/          # API 서비스
│   │   └── ApiService.ts
│   └── utils/             # 유틸리티 함수
├── App.tsx               # 메인 앱 컴포넌트
├── package.json
├── react-native.config.js
├── ios/                  # iOS 네이티브 코드
└── android/              # Android 네이티브 코드
```

## 🔧 백엔드 연동

### Python Streamlit 서버
모바일 앱은 기존 Python Streamlit 백엔드와 연동됩니다:

```bash
# 백엔드 서버 실행 (별도 터미널)
cd ../  # 상위 프로젝트 폴더로 이동
streamlit run app.py --server.port 5000
```

### API 엔드포인트
- `POST /api/upload` - 파일 업로드
- `GET /api/rooms` - 채팅방 목록
- `DELETE /api/rooms/:id` - 채팅방 삭제
- `POST /api/analyze` - GPT 분석
- `GET /api/visualization/:id` - 시각화 데이터
- `GET /api/export` - 데이터 내보내기

## 📱 플랫폼별 특징

### iOS
- iOS 13.0+ 지원
- Human Interface Guidelines 준수
- 다크/라이트 모드 자동 지원
- Haptic Feedback 지원
- Share Extension 준비

### Android
- API Level 21+ (Android 5.0+) 지원
- Material Design 3 적용
- 백 버튼 처리
- 권한 관리 자동화

## 🎨 UI/UX 특징

### 디자인 시스템
- iOS 스타일 기반 디자인
- 반응형 레이아웃
- 카드 기반 인터페이스
- 직관적인 네비게이션

### 접근성
- VoiceOver/TalkBack 지원
- 동적 폰트 크기 지원
- 고대비 모드 대응
- 키보드 네비게이션

### 애니메이션
- 자연스러운 화면 전환
- 로딩 인디케이터
- Pull-to-refresh 애니메이션
- 버튼 피드백 효과

## 🔐 보안 및 프라이버시

### 데이터 보호
- 민감 데이터 기기 내 저장
- API 키 안전 저장 (Keychain/Keystore)
- HTTPS 통신 강제
- 백그라운드 모드 시 화면 보안

### 권한 관리
- 최소 권한 원칙
- 파일 접근 권한 요청
- 네트워크 상태 확인

## 📊 성능 최적화

### 메모리 관리
- 이미지 지연 로딩
- 대용량 리스트 가상화
- 메모리 누수 방지
- 백그라운드 작업 최적화

### 네트워크 최적화
- 요청 캐싱
- 재시도 로직
- 오프라인 모드 대응
- 배치 업로드

## 🚀 배포

### iOS App Store
```bash
# Release 빌드
npx react-native run-ios --configuration Release

# Archive 생성 (Xcode에서)
Product → Archive → Distribute App
```

### Google Play Store
```bash
# Release APK 생성
cd android
./gradlew assembleRelease

# AAB 생성 (권장)
./gradlew bundleRelease
```

## 🧪 테스트

### 단위 테스트
```bash
npm test
```

### E2E 테스트
```bash
# Detox 설정 후
npm run test:e2e:ios
npm run test:e2e:android
```

## 🛠 문제 해결

### 일반적인 이슈

#### Metro 번들러 오류
```bash
npx react-native start --reset-cache
```

#### iOS 빌드 오류
```bash
cd ios && pod deintegrate && pod install && cd ..
```

#### Android 빌드 오류
```bash
cd android && ./gradlew clean && cd ..
```

#### 폰트 아이콘 표시 안됨
```bash
npx react-native-asset
```

## 📞 지원 및 문의

### 기능 요청
- GitHub Issues에 Feature Request 등록
- 상세한 사용 사례 설명 포함

### 버그 리포트
- 재현 단계 상세 기술
- 기기 정보 및 로그 첨부
- 스크린샷 포함

### 기술 지원
- 개발 환경 관련 문제
- API 연동 이슈
- 성능 최적화 문의

## 🗺️ 로드맵

### v1.1.0 (예정)
- [ ] 실시간 채팅 분석
- [ ] 워드클라우드 시각화
- [ ] 데이터 동기화 기능

### v1.2.0 (예정)
- [ ] 다국어 지원
- [ ] 테마 커스터마이징
- [ ] 고급 필터링 옵션

### v2.0.0 (예정)
- [ ] AI 자동 분석 스케줄링
- [ ] 클라우드 백업 연동
- [ ] 팀 공유 기능

---

## 📄 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여
Pull Request와 Issue 제출을 환영합니다! 