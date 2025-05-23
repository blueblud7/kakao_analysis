import React, {useState} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Dimensions,
} from 'react-native';
import {SafeAreaView} from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {LineChart, BarChart, PieChart} from 'react-native-chart-kit';

const screenWidth = Dimensions.get('window').width;

const VisualizationScreen: React.FC = () => {
  const [selectedChart, setSelectedChart] = useState('activity');

  const chartTypes = [
    {id: 'activity', title: '시간대별 활동', icon: 'timeline'},
    {id: 'users', title: '사용자별 통계', icon: 'people'},
    {id: 'keywords', title: '키워드 분석', icon: 'label'},
    {id: 'sentiment', title: '감정 분포', icon: 'mood'},
  ];

  // 샘플 데이터
  const activityData = {
    labels: ['06', '09', '12', '15', '18', '21', '24'],
    datasets: [
      {
        data: [10, 45, 30, 70, 120, 95, 25],
        color: (opacity = 1) => `rgba(0, 122, 255, ${opacity})`,
        strokeWidth: 2,
      },
    ],
  };

  const userActivityData = {
    labels: ['김철수', '이영희', '박민수', '최지혜', '정동욱'],
    datasets: [
      {
        data: [220, 180, 165, 140, 95],
      },
    ],
  };

  const keywordData = {
    labels: ['회의', '프로젝트', '일정', '확인', '감사'],
    datasets: [
      {
        data: [45, 32, 28, 25, 22],
      },
    ],
  };

  const sentimentData = [
    {
      name: '긍정',
      population: 65,
      color: '#34C759',
      legendFontColor: '#333',
      legendFontSize: 15,
    },
    {
      name: '중립',
      population: 25,
      color: '#FF9500',
      legendFontColor: '#333',
      legendFontSize: 15,
    },
    {
      name: '부정',
      population: 10,
      color: '#FF3B30',
      legendFontColor: '#333',
      legendFontSize: 15,
    },
  ];

  const chartConfig = {
    backgroundColor: '#fff',
    backgroundGradientFrom: '#fff',
    backgroundGradientTo: '#fff',
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(0, 122, 255, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(51, 51, 51, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: '#007AFF',
    },
  };

  const renderChart = () => {
    switch (selectedChart) {
      case 'activity':
        return (
          <View style={styles.chartContainer}>
            <Text style={styles.chartTitle}>📈 시간대별 메시지 활동</Text>
            <LineChart
              data={activityData}
              width={screenWidth - 60}
              height={220}
              chartConfig={chartConfig}
              bezier
              style={styles.chart}
            />
            <Text style={styles.chartDescription}>
              가장 활발한 시간: 오후 6시 (120개 메시지)
            </Text>
          </View>
        );

      case 'users':
        return (
          <View style={styles.chartContainer}>
            <Text style={styles.chartTitle}>👥 사용자별 메시지 수</Text>
            <BarChart
              data={userActivityData}
              width={screenWidth - 60}
              height={220}
              chartConfig={{
                ...chartConfig,
                color: (opacity = 1) => `rgba(52, 199, 89, ${opacity})`,
              }}
              style={styles.chart}
              verticalLabelRotation={30}
            />
            <Text style={styles.chartDescription}>
              가장 활발한 사용자: 김철수 (220개 메시지)
            </Text>
          </View>
        );

      case 'keywords':
        return (
          <View style={styles.chartContainer}>
            <Text style={styles.chartTitle}>🏷️ 주요 키워드 빈도</Text>
            <BarChart
              data={keywordData}
              width={screenWidth - 60}
              height={220}
              chartConfig={{
                ...chartConfig,
                color: (opacity = 1) => `rgba(255, 149, 0, ${opacity})`,
              }}
              style={styles.chart}
              verticalLabelRotation={30}
            />
            <Text style={styles.chartDescription}>
              가장 많이 언급된 키워드: 회의 (45회)
            </Text>
          </View>
        );

      case 'sentiment':
        return (
          <View style={styles.chartContainer}>
            <Text style={styles.chartTitle}>😊 감정 분포</Text>
            <PieChart
              data={sentimentData}
              width={screenWidth - 60}
              height={220}
              chartConfig={chartConfig}
              accessor={'population'}
              backgroundColor={'transparent'}
              paddingLeft={'15'}
              style={styles.chart}
            />
            <Text style={styles.chartDescription}>
              전체적으로 긍정적인 분위기 (65%)
            </Text>
          </View>
        );

      default:
        return null;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Icon name="bar-chart" size={48} color="#007AFF" />
          <Text style={styles.title}>📊 데이터 시각화</Text>
          <Text style={styles.subtitle}>
            채팅 데이터를 다양한 차트로 시각화하여 인사이트를 발견하세요
          </Text>
        </View>

        <View style={styles.chartSelector}>
          <Text style={styles.sectionTitle}>차트 유형 선택</Text>
          <View style={styles.chartTypes}>
            {chartTypes.map((type) => (
              <TouchableOpacity
                key={type.id}
                style={[
                  styles.typeButton,
                  selectedChart === type.id && styles.selectedTypeButton,
                ]}
                onPress={() => setSelectedChart(type.id)}
              >
                <Icon
                  name={type.icon}
                  size={24}
                  color={selectedChart === type.id ? '#fff' : '#007AFF'}
                />
                <Text
                  style={[
                    styles.typeButtonText,
                    selectedChart === type.id && styles.selectedTypeButtonText,
                  ]}
                >
                  {type.title}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {renderChart()}

        <View style={styles.statsSection}>
          <Text style={styles.sectionTitle}>📋 전체 통계</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Icon name="message" size={32} color="#007AFF" />
              <Text style={styles.statValue}>1,250</Text>
              <Text style={styles.statLabel}>총 메시지</Text>
            </View>
            <View style={styles.statCard}>
              <Icon name="people" size={32} color="#34C759" />
              <Text style={styles.statValue}>6</Text>
              <Text style={styles.statLabel}>참여자</Text>
            </View>
            <View style={styles.statCard}>
              <Icon name="schedule" size={32} color="#FF9500" />
              <Text style={styles.statValue}>15</Text>
              <Text style={styles.statLabel}>활동 일수</Text>
            </View>
            <View style={styles.statCard}>
              <Icon name="trending-up" size={32} color="#FF3B30" />
              <Text style={styles.statValue}>83</Text>
              <Text style={styles.statLabel}>일평균 메시지</Text>
            </View>
          </View>
        </View>

        <View style={styles.insights}>
          <Text style={styles.sectionTitle}>💡 주요 인사이트</Text>
          <View style={styles.insightCard}>
            <Icon name="lightbulb" size={24} color="#007AFF" />
            <View style={styles.insightContent}>
              <Text style={styles.insightTitle}>최고 활동 시간</Text>
              <Text style={styles.insightText}>
                오후 6시경에 가장 활발한 대화가 이루어집니다
              </Text>
            </View>
          </View>
          <View style={styles.insightCard}>
            <Icon name="lightbulb" size={24} color="#34C759" />
            <View style={styles.insightContent}>
              <Text style={styles.insightTitle}>참여도</Text>
              <Text style={styles.insightText}>
                모든 참여자가 고르게 대화에 참여하고 있습니다
              </Text>
            </View>
          </View>
          <View style={styles.insightCard}>
            <Icon name="lightbulb" size={24} color="#FF9500" />
            <View style={styles.insightContent}>
              <Text style={styles.insightTitle}>주요 주제</Text>
              <Text style={styles.insightText}>
                업무 관련 대화가 전체의 60%를 차지합니다
              </Text>
            </View>
          </View>
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
  chartSelector: {
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
  chartTypes: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  typeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#f0f8ff',
    borderWidth: 1,
    borderColor: '#007AFF',
    minWidth: '45%',
  },
  selectedTypeButton: {
    backgroundColor: '#007AFF',
  },
  typeButtonText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
    flex: 1,
  },
  selectedTypeButtonText: {
    color: '#fff',
  },
  chartContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    alignItems: 'center',
  },
  chartTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
    textAlign: 'center',
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  chartDescription: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 10,
    fontStyle: 'italic',
  },
  statsSection: {
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
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 15,
  },
  statCard: {
    flex: 1,
    minWidth: '40%',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
    textAlign: 'center',
  },
  insights: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  insightCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    marginBottom: 12,
  },
  insightContent: {
    marginLeft: 12,
    flex: 1,
  },
  insightTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  insightText: {
    fontSize: 12,
    color: '#666',
    lineHeight: 16,
  },
});

export default VisualizationScreen; 