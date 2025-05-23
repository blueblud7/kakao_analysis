import React, {useState} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import {SafeAreaView} from 'react-native-safe-area-context';
import DocumentPicker from 'react-native-document-picker';
import RNFS from 'react-native-fs';
import Icon from 'react-native-vector-icons/MaterialIcons';

interface ChatData {
  fileName: string;
  messageCount: number;
  participantCount: number;
  dateRange: string;
  fileSize: string;
}

const FileUploadScreen = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [chatData, setChatData] = useState(null);

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.pick({
        type: [DocumentPicker.types.allFiles],
        allowMultiSelection: false,
      });

      const file = result[0];
      
      // 파일 타입 검증
      if (!file.name?.endsWith('.txt') && !file.name?.endsWith('.csv')) {
        Alert.alert('오류', '카카오톡 채팅 파일(.txt 또는 .csv)만 업로드 가능합니다.');
        return;
      }

      setSelectedFile(file);
      Alert.alert('파일 선택 완료', `${file.name} 파일이 선택되었습니다.`);
    } catch (err) {
      if (DocumentPicker.isCancel(err)) {
        // 사용자가 취소함
      } else {
        Alert.alert('오류', '파일 선택 중 오류가 발생했습니다.');
      }
    }
  };

  const analyzeFile = async () => {
    if (!selectedFile) {
      Alert.alert('알림', '먼저 파일을 선택해주세요.');
      return;
    }

    setIsUploading(true);

    try {
      // 파일 읽기
      const fileContent = await RNFS.readFile(selectedFile.uri, 'utf8');
      
      // 간단한 파싱 (실제로는 백엔드 API 호출)
      const lines = fileContent.split('\n');
      const messageLines = lines.filter(line => 
        line.includes(':') && (line.includes('오전') || line.includes('오후'))
      );
      
      const participants = new Set<string>();
      messageLines.forEach(line => {
        const match = line.match(/\d{1,2}:\d{2}, (.+?) :/);
        if (match) {
          participants.add(match[1]);
        }
      });

      const fileSize = (selectedFile.size / 1024).toFixed(2);
      
      const data: ChatData = {
        fileName: selectedFile.name,
        messageCount: messageLines.length,
        participantCount: participants.size,
        dateRange: '분석 필요',
        fileSize: `${fileSize} KB`,
      };

      setChatData(data);
      Alert.alert('분석 완료', '파일 분석이 완료되었습니다!');
    } catch (error) {
      Alert.alert('오류', '파일 분석 중 오류가 발생했습니다.');
    } finally {
      setIsUploading(false);
    }
  };

  const uploadToServer = async () => {
    if (!chatData) {
      Alert.alert('알림', '먼저 파일을 분석해주세요.');
      return;
    }

    setIsUploading(true);

    try {
      // 여기서 실제 서버 업로드 로직 구현
      // axios를 사용하여 Python 백엔드로 전송
      
      // 임시 딜레이
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      Alert.alert('업로드 완료', '서버에 성공적으로 업로드되었습니다!');
      
      // 상태 초기화
      setSelectedFile(null);
      setChatData(null);
    } catch (error) {
      Alert.alert('오류', '서버 업로드 중 오류가 발생했습니다.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Icon name="upload-file" size={48} color="#007AFF" />
          <Text style={styles.title}>카카오톡 채팅 파일 업로드</Text>
          <Text style={styles.subtitle}>
            카카오톡에서 내보낸 채팅 내역 파일을 업로드하세요
          </Text>
        </View>

        <View style={styles.uploadSection}>
          <TouchableOpacity
            style={styles.selectButton}
            onPress={pickDocument}
            disabled={isUploading}
          >
            <Icon name="folder-open" size={24} color="#fff" />
            <Text style={styles.selectButtonText}>파일 선택</Text>
          </TouchableOpacity>

          {selectedFile && (
            <View style={styles.fileInfo}>
              <Icon name="description" size={24} color="#007AFF" />
              <View style={styles.fileDetails}>
                <Text style={styles.fileName}>{selectedFile.name}</Text>
                <Text style={styles.fileSize}>
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </Text>
              </View>
            </View>
          )}

          {selectedFile && !chatData && (
            <TouchableOpacity
              style={styles.analyzeButton}
              onPress={analyzeFile}
              disabled={isUploading}
            >
              {isUploading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <>
                  <Icon name="analytics" size={24} color="#fff" />
                  <Text style={styles.buttonText}>파일 분석</Text>
                </>
              )}
            </TouchableOpacity>
          )}

          {chatData && (
            <View style={styles.analysisResult}>
              <Text style={styles.resultTitle}>📊 분석 결과</Text>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>파일명:</Text>
                <Text style={styles.statValue}>{chatData.fileName}</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>총 메시지:</Text>
                <Text style={styles.statValue}>{chatData.messageCount}개</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>참여자:</Text>
                <Text style={styles.statValue}>{chatData.participantCount}명</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>파일 크기:</Text>
                <Text style={styles.statValue}>{chatData.fileSize}</Text>
              </View>

              <TouchableOpacity
                style={styles.uploadButton}
                onPress={uploadToServer}
                disabled={isUploading}
              >
                {isUploading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <>
                    <Icon name="cloud-upload" size={24} color="#fff" />
                    <Text style={styles.buttonText}>서버에 업로드</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
          )}
        </View>

        <View style={styles.infoSection}>
          <Text style={styles.infoTitle}>📋 지원 파일 형식</Text>
          <Text style={styles.infoText}>• 카카오톡 TXT 파일</Text>
          <Text style={styles.infoText}>• CSV 형식 파일</Text>
          <Text style={styles.infoText}>• 파일 크기: 최대 50MB</Text>
        </View>
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
  uploadSection: {
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
  selectButton: {
    backgroundColor: '#007AFF',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
  },
  selectButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  fileInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#f0f8ff',
    borderRadius: 8,
    marginBottom: 15,
  },
  fileDetails: {
    marginLeft: 12,
    flex: 1,
  },
  fileName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  fileSize: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  analyzeButton: {
    backgroundColor: '#34C759',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 8,
  },
  uploadButton: {
    backgroundColor: '#FF9500',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 8,
    marginTop: 15,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  analysisResult: {
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  statValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: 'bold',
  },
  infoSection: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#333',
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 6,
    lineHeight: 20,
  },
});

export default FileUploadScreen; 