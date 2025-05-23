import React, {useState} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  TextInput,
  Alert,
  ActivityIndicator,
  Clipboard,
} from 'react-native';
import {SafeAreaView} from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';

interface AnalysisResult {
  type: string;
  title: string;
  content: string;
  timestamp: string;
}

const AnalysisScreen: React.FC = () => {
  const [selectedRoom, setSelectedRoom] = useState<string>('');
  const [analysisType, setAnalysisType] = useState<string>('comprehensive');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<AnalysisResult[]>([]);

  const analysisTypes = [
    { id: 'comprehensive', title: '종합 분석', icon: 'assessment' },
    { id: 'sentiment', title: '감정 분석', icon: 'mood' },
    { id: 'keywords', title: '키워드 추출', icon: 'label' },
    { id: 'topics', title: '토픽 분석', icon: 'topic' },
  ];

  const chatRooms = [
    '미국 홍콩 독일 영국 중국 한국 성직자방',
    '프로젝트 팀 채팅',
    '가족 단톡방',
  ];

  const startAnalysis = async () => {
    if (!selectedRoom) {
      Alert.alert('알림', '분석할 채팅방을 선택해주세요.');
      return;
    }

    setIsAnalyzing(true);

    try {
      // 실제로는 서버 API 호출
      await new Promise(resolve => setTimeout(resolve, 3000));

      const mockResult: AnalysisResult = {
        type: analysisType,
        title: analysisTypes.find(t => t.id === analysisType)?.title || '분석',
        content: generateMockAnalysis(analysisType),
        timestamp: new Date().toLocaleString('ko-KR'),
      };

      setResults(prev => [mockResult, ...prev]);
      Alert.alert('완료', 'GPT 분석이 완료되었습니다!');
    } catch (error) {
      Alert.alert('오류', 'GPT 분석 중 오류가 발생했습니다.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const generateMockAnalysis = (type: string): string => {
    const analyses = {
      comprehensive: `📊 **종합 분석 결과**

**대화 패턴:**
- 활발한 토론이 이루어지는 채팅방입니다
- 주로 오후 7-9시에 가장 활발한 대화가 진행됩니다
- 평균 메시지 길이: 47자

**주요 특징:**
- 정보 공유가 활발함
- 긍정적인 분위기 유지
- 다양한 주제에 대한 토론

**참여도:**
- 모든 참여자가 고른 참여도를 보임
- 질문-답변 패턴이 자주 관찰됨`,

      sentiment: `😊 **감정 분석 결과**

**전체 감정 분포:**
- 긍정: 65%
- 중립: 25% 
- 부정: 10%

**주요 감정 키워드:**
- 긍정: 좋다, 감사, 최고, 훌륭
- 부정: 아쉽다, 걱정, 힘들다

**시간대별 감정 변화:**
- 오전: 중립적
- 오후: 긍정적
- 저녁: 매우 긍정적`,

      keywords: `🏷️ **키워드 추출 결과**

**빈도수 Top 10:**
1. 회의 (45회)
2. 프로젝트 (32회)
3. 일정 (28회)
4. 확인 (25회)
5. 감사 (22회)
6. 진행 (19회)
7. 완료 (17회)
8. 공유 (15회)
9. 참석 (13회)
10. 검토 (11회)

**주요 토픽:**
- 업무 관련: 60%
- 일상 대화: 25%
- 정보 공유: 15%`,

      topics: `📈 **토픽 분석 결과**

**주요 토픽 (LDA 모델링):**

**토픽 1: 업무 진행 (35%)**
- 키워드: 회의, 일정, 진행, 완료
- 설명: 프로젝트 진행 상황 논의

**토픽 2: 정보 공유 (30%)**  
- 키워드: 공유, 확인, 자료, 링크
- 설명: 정보 및 자료 공유

**토픽 3: 일상 대화 (25%)**
- 키워드: 안녕, 수고, 감사, 오늘
- 설명: 인사 및 일상적 소통

**토픽 4: 일정 조율 (10%)**
- 키워드: 시간, 참석, 가능, 언제
- 설명: 스케줄 조율 및 약속`
    };

    return analyses[type as keyof typeof analyses] || '분석 결과가 없습니다.';
  };

  const copyToClipboard = (content: string) => {
    Clipboard.setString(content);
    Alert.alert('복사 완료', '분석 결과가 클립보드에 복사되었습니다.');
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Icon name="psychology" size={48} color="#007AFF" />
          <Text style={styles.title}>🤖 GPT 분석</Text>
          <Text style={styles.subtitle}>
            AI를 활용한 채팅 내용 분석 및 인사이트 도출
          </Text>
        </View>

        <View style={styles.analysisForm}>
          <Text style={styles.sectionTitle}>채팅방 선택</Text>
          <View style={styles.roomSelector}>
            {chatRooms.map((room, index) => (
              <TouchableOpacity
                key={index}
                style={[
                  styles.roomOption,
                  selectedRoom === room && styles.selectedRoom,
                ]}
                onPress={() => setSelectedRoom(room)}
              >
                <Icon 
                  name="chat" 
                  size={16} 
                  color={selectedRoom === room ? '#fff' : '#666'} 
                />
                <Text 
                  style={[
                    styles.roomText,
                    selectedRoom === room && styles.selectedRoomText,
                  ]}
                  numberOfLines={1}
                >
                  {room}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.sectionTitle}>분석 유형</Text>
          <View style={styles.analysisTypes}>
            {analysisTypes.map((type) => (
              <TouchableOpacity
                key={type.id}
                style={[
                  styles.typeOption,
                  analysisType === type.id && styles.selectedType,
                ]}
                onPress={() => setAnalysisType(type.id)}
              >
                <Icon 
                  name={type.icon} 
                  size={20} 
                  color={analysisType === type.id ? '#fff' : '#007AFF'} 
                />
                <Text 
                  style={[
                    styles.typeText,
                    analysisType === type.id && styles.selectedTypeText,
                  ]}
                >
                  {type.title}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <TouchableOpacity
            style={[styles.analyzeButton, isAnalyzing && styles.disabledButton]}
            onPress={startAnalysis}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Icon name="smart-toy" size={24} color="#fff" />
            )}
            <Text style={styles.analyzeButtonText}>
              {isAnalyzing ? '분석 중...' : 'GPT 분석 시작'}
            </Text>
          </TouchableOpacity>
        </View>

        {results.length > 0 && (
          <View style={styles.resultsSection}>
            <Text style={styles.sectionTitle}>📋 분석 결과</Text>
            {results.map((result, index) => (
              <View key={index} style={styles.resultCard}>
                <View style={styles.resultHeader}>
                  <Text style={styles.resultTitle}>{result.title}</Text>
                  <TouchableOpacity
                    onPress={() => copyToClipboard(result.content)}
                    style={styles.copyButton}
                  >
                    <Icon name="content-copy" size={20} color="#007AFF" />
                  </TouchableOpacity>
                </View>
                <Text style={styles.resultTimestamp}>{result.timestamp}</Text>
                <ScrollView style={styles.resultContent} nestedScrollEnabled>
                  <Text style={styles.resultText}>{result.content}</Text>
                </ScrollView>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 30,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 8,
    textAlign: 'center',
    lineHeight: 22,
  },
  analysisForm: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  roomSelector: {
    marginBottom: 20,
  },
  roomOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#f8f9fa',
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  selectedRoom: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  roomText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#666',
    flex: 1,
  },
  selectedRoomText: {
    color: '#fff',
  },
  analysisTypes: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 20,
  },
  typeOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#f0f8ff',
    borderWidth: 1,
    borderColor: '#007AFF',
    minWidth: '45%',
  },
  selectedType: {
    backgroundColor: '#007AFF',
  },
  typeText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
  },
  selectedTypeText: {
    color: '#fff',
  },
  analyzeButton: {
    backgroundColor: '#34C759',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 8,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  analyzeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  resultsSection: {
    marginBottom: 20,
  },
  resultCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  copyButton: {
    padding: 4,
  },
  resultTimestamp: {
    fontSize: 12,
    color: '#666',
    marginBottom: 12,
  },
  resultContent: {
    maxHeight: 200,
  },
  resultText: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
});

export default AnalysisScreen; 