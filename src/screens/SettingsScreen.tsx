import React, {useState} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Switch,
  Alert,
  TextInput,
  Modal,
} from 'react-native';
import {SafeAreaView} from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';

const SettingsScreen: React.FC = () => {
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [autoBackup, setAutoBackup] = useState(true);
  const [showApiModal, setShowApiModal] = useState(false);
  const [apiKey, setApiKey] = useState('');

  const settingsSections = [
    {
      title: '일반',
      items: [
        {
          id: 'notifications',
          title: '알림',
          subtitle: '앱 알림 설정',
          icon: 'notifications',
          type: 'switch',
          value: notifications,
          onToggle: setNotifications,
        },
        {
          id: 'darkMode',
          title: '다크 모드',
          subtitle: '어두운 테마 사용',
          icon: 'dark-mode',
          type: 'switch',
          value: darkMode,
          onToggle: setDarkMode,
        },
        {
          id: 'autoBackup',
          title: '자동 백업',
          subtitle: '데이터 자동 백업',
          icon: 'backup',
          type: 'switch',
          value: autoBackup,
          onToggle: setAutoBackup,
        },
      ],
    },
    {
      title: 'AI 설정',
      items: [
        {
          id: 'apiKey',
          title: 'OpenAI API 키',
          subtitle: 'GPT 분석을 위한 API 키',
          icon: 'vpn-key',
          type: 'button',
          onPress: () => setShowApiModal(true),
        },
      ],
    },
    {
      title: '데이터',
      items: [
        {
          id: 'clearCache',
          title: '캐시 삭제',
          subtitle: '임시 파일 삭제',
          icon: 'clear',
          type: 'button',
          onPress: () => handleClearCache(),
        },
        {
          id: 'exportData',
          title: '데이터 내보내기',
          subtitle: '모든 데이터를 파일로 내보내기',
          icon: 'file-download',
          type: 'button',
          onPress: () => handleExportData(),
        },
        {
          id: 'deleteAll',
          title: '모든 데이터 삭제',
          subtitle: '모든 채팅방 데이터 삭제',
          icon: 'delete-forever',
          type: 'button',
          onPress: () => handleDeleteAllData(),
          danger: true,
        },
      ],
    },
    {
      title: '정보',
      items: [
        {
          id: 'version',
          title: '앱 버전',
          subtitle: '1.0.0',
          icon: 'info',
          type: 'info',
        },
        {
          id: 'help',
          title: '도움말',
          subtitle: '사용법 및 문의',
          icon: 'help',
          type: 'button',
          onPress: () => handleHelp(),
        },
        {
          id: 'privacy',
          title: '개인정보 처리방침',
          subtitle: '데이터 처리 정책',
          icon: 'privacy-tip',
          type: 'button',
          onPress: () => handlePrivacy(),
        },
      ],
    },
  ];

  const handleClearCache = () => {
    Alert.alert(
      '캐시 삭제',
      '캐시를 삭제하시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '삭제',
          onPress: () => {
            // 캐시 삭제 로직
            Alert.alert('완료', '캐시가 삭제되었습니다.');
          },
        },
      ]
    );
  };

  const handleExportData = () => {
    Alert.alert(
      '데이터 내보내기',
      '모든 데이터를 JSON 파일로 내보내시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '내보내기',
          onPress: () => {
            // 데이터 내보내기 로직
            Alert.alert('완료', '데이터가 내보내기되었습니다.');
          },
        },
      ]
    );
  };

  const handleDeleteAllData = () => {
    Alert.alert(
      '⚠️ 경고',
      '모든 채팅방 데이터가 삭제됩니다. 이 작업은 되돌릴 수 없습니다.',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '삭제',
          style: 'destructive',
          onPress: () => {
            // 모든 데이터 삭제 로직
            Alert.alert('완료', '모든 데이터가 삭제되었습니다.');
          },
        },
      ]
    );
  };

  const handleHelp = () => {
    Alert.alert(
      '도움말',
      '앱 사용법:\n\n1. 파일 업로드: 카카오톡 채팅 파일을 업로드\n2. 히스토리: 저장된 채팅방 관리\n3. 분석: GPT를 통한 채팅 분석\n4. 시각화: 데이터 차트 확인\n\n문의사항이 있으시면 개발자에게 연락주세요.'
    );
  };

  const handlePrivacy = () => {
    Alert.alert(
      '개인정보 처리방침',
      '이 앱은 사용자의 채팅 데이터를 기기 내에서만 처리하며, 외부로 전송하지 않습니다. GPT 분석 시에만 OpenAI API를 사용합니다.'
    );
  };

  const saveApiKey = () => {
    if (!apiKey.trim()) {
      Alert.alert('오류', 'API 키를 입력해주세요.');
      return;
    }
    
    // API 키 저장 로직 (실제로는 안전한 저장소에 저장)
    Alert.alert('저장 완료', 'API 키가 저장되었습니다.');
    setShowApiModal(false);
    setApiKey('');
  };

  const renderSettingItem = (item: any) => {
    return (
      <TouchableOpacity
        key={item.id}
        style={[styles.settingItem, item.danger && styles.dangerItem]}
        onPress={item.onPress}
        disabled={item.type === 'info'}
      >
        <View style={styles.settingLeft}>
          <Icon 
            name={item.icon} 
            size={24} 
            color={item.danger ? '#FF3B30' : '#007AFF'} 
          />
          <View style={styles.settingText}>
            <Text style={[styles.settingTitle, item.danger && styles.dangerText]}>
              {item.title}
            </Text>
            <Text style={styles.settingSubtitle}>{item.subtitle}</Text>
          </View>
        </View>
        
        {item.type === 'switch' && (
          <Switch
            value={item.value}
            onValueChange={item.onToggle}
            trackColor={{ false: '#767577', true: '#007AFF' }}
            thumbColor={item.value ? '#fff' : '#f4f3f4'}
          />
        )}
        
        {item.type === 'button' && (
          <Icon name="chevron-right" size={24} color="#ccc" />
        )}
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Icon name="settings" size={48} color="#007AFF" />
          <Text style={styles.title}>⚙️ 설정</Text>
          <Text style={styles.subtitle}>
            앱 설정을 관리하고 기본 설정을 변경하세요
          </Text>
        </View>

        {settingsSections.map((section, sectionIndex) => (
          <View key={sectionIndex} style={styles.section}>
            <Text style={styles.sectionTitle}>{section.title}</Text>
            <View style={styles.sectionContent}>
              {section.items.map(renderSettingItem)}
            </View>
          </View>
        ))}

        {/* API Key Modal */}
        <Modal
          visible={showApiModal}
          transparent
          animationType="slide"
          onRequestClose={() => setShowApiModal(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>OpenAI API 키 설정</Text>
                <TouchableOpacity
                  onPress={() => setShowApiModal(false)}
                  style={styles.closeButton}
                >
                  <Icon name="close" size={24} color="#666" />
                </TouchableOpacity>
              </View>
              
              <Text style={styles.modalDescription}>
                GPT 분석 기능을 사용하려면 OpenAI API 키가 필요합니다.
              </Text>
              
              <TextInput
                style={styles.apiKeyInput}
                placeholder="API 키를 입력하세요"
                value={apiKey}
                onChangeText={setApiKey}
                secureTextEntry
                autoCapitalize="none"
              />
              
              <View style={styles.modalButtons}>
                <TouchableOpacity
                  style={styles.cancelButton}
                  onPress={() => setShowApiModal(false)}
                >
                  <Text style={styles.cancelButtonText}>취소</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={styles.saveButton}
                  onPress={saveApiKey}
                >
                  <Text style={styles.saveButtonText}>저장</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>
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
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
    marginLeft: 10,
  },
  sectionContent: {
    backgroundColor: '#fff',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  dangerItem: {
    backgroundColor: '#fff5f5',
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingText: {
    marginLeft: 12,
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 2,
  },
  dangerText: {
    color: '#FF3B30',
  },
  settingSubtitle: {
    fontSize: 13,
    color: '#666',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    width: '90%',
    maxWidth: 400,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  closeButton: {
    padding: 4,
  },
  modalDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
    lineHeight: 20,
  },
  apiKeyInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 20,
  },
  modalButtons: {
    flexDirection: 'row',
    gap: 10,
  },
  cancelButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#f8f9fa',
    alignItems: 'center',
  },
  cancelButtonText: {
    fontSize: 16,
    color: '#666',
    fontWeight: '500',
  },
  saveButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#007AFF',
    alignItems: 'center',
  },
  saveButtonText: {
    fontSize: 16,
    color: '#fff',
    fontWeight: 'bold',
  },
});

export default SettingsScreen; 