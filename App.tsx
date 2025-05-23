import React from 'react';
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  useColorScheme,
  View,
  TouchableOpacity,
  Alert,
} from 'react-native';

const App = () => {
  const isDarkMode = useColorScheme() === 'dark';

  const backgroundStyle = {
    backgroundColor: isDarkMode ? '#333' : '#f5f5f5',
    flex: 1,
  };

  const textStyle = {
    color: isDarkMode ? '#fff' : '#333',
  };

  const handlePress = (feature: string) => {
    Alert.alert(
      `${feature} 기능`,
      `${feature} 기능을 선택하셨습니다. 곧 구현될 예정입니다!`,
      [{ text: '확인' }]
    );
  };

  return (
    <SafeAreaView style={backgroundStyle}>
      <ScrollView
        contentInsetAdjustmentBehavior="automatic"
        style={backgroundStyle}
        contentContainerStyle={styles.container}>
        
        <View style={styles.header}>
          <Text style={[styles.title, textStyle]}>
            📱 카카오톡 채팅 분석기
          </Text>
          <Text style={[styles.subtitle, textStyle]}>
            React Native 모바일 앱
          </Text>
        </View>

        <View style={styles.featuresContainer}>
          <TouchableOpacity
            style={[styles.featureCard, styles.uploadCard]}
            onPress={() => handlePress('파일 업로드')}>
            <Text style={styles.featureIcon}>📁</Text>
            <Text style={styles.featureTitle}>파일 업로드</Text>
            <Text style={styles.featureDescription}>
              카카오톡 채팅 파일 업로드
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.featureCard, styles.historyCard]}
            onPress={() => handlePress('채팅방 히스토리')}>
            <Text style={styles.featureIcon}>💬</Text>
            <Text style={styles.featureTitle}>채팅방 히스토리</Text>
            <Text style={styles.featureDescription}>
              저장된 채팅방 관리
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.featureCard, styles.analysisCard]}
            onPress={() => handlePress('GPT 분석')}>
            <Text style={styles.featureIcon}>🤖</Text>
            <Text style={styles.featureTitle}>GPT 분석</Text>
            <Text style={styles.featureDescription}>
              AI 기반 채팅 분석
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.featureCard, styles.chartCard]}
            onPress={() => handlePress('데이터 시각화')}>
            <Text style={styles.featureIcon}>📊</Text>
            <Text style={styles.featureTitle}>데이터 시각화</Text>
            <Text style={styles.featureDescription}>
              차트 및 통계 확인
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.featureCard, styles.settingsCard]}
            onPress={() => handlePress('설정')}>
            <Text style={styles.featureIcon}>⚙️</Text>
            <Text style={styles.featureTitle}>설정</Text>
            <Text style={styles.featureDescription}>
              앱 설정 및 관리
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.footer}>
          <Text style={[styles.footerText, textStyle]}>
            🎉 iOS & Android 크로스 플랫폼 지원
          </Text>
          <Text style={[styles.versionText, textStyle]}>
            버전 1.0.0
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 30,
    paddingVertical: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    opacity: 0.7,
  },
  featuresContainer: {
    flex: 1,
    marginBottom: 30,
  },
  featureCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  uploadCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  historyCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#34C759',
  },
  analysisCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#FF9500',
  },
  chartCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#AF52DE',
  },
  settingsCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#FF3B30',
  },
  featureIcon: {
    fontSize: 32,
    marginBottom: 12,
  },
  featureTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  featureDescription: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 20,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  footerText: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  versionText: {
    fontSize: 12,
    opacity: 0.6,
  },
});

export default App; 