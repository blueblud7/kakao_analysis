import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Alert,
  RefreshControl,
} from 'react-native';
import {SafeAreaView} from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';

interface ChatRoom {
  id: string;
  name: string;
  messageCount: number;
  participantCount: number;
  lastMessage: string;
  fileCount: number;
  participants: string[];
}

const HistoryScreen: React.FC = () => {
  const [chatRooms, setChatRooms] = useState<ChatRoom[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // 샘플 데이터
  const sampleData: ChatRoom[] = [
    {
      id: '1',
      name: '미국 홍콩 독일 영국 중국 한국 성직자방',
      messageCount: 1250,
      participantCount: 6,
      lastMessage: '2024-01-15',
      fileCount: 3,
      participants: ['김철수', '이영희', '박민수', '최지혜', '정동욱', '한미영'],
    },
    {
      id: '2',
      name: '프로젝트 팀 채팅',
      messageCount: 890,
      participantCount: 4,
      lastMessage: '2024-01-10',
      fileCount: 2,
      participants: ['홍길동', '김영수', '이지은', '박준호'],
    },
  ];

  useEffect(() => {
    loadChatRooms();
  }, []);

  const loadChatRooms = async () => {
    try {
      // 실제로는 서버에서 데이터를 가져옴
      setChatRooms(sampleData);
    } catch (error) {
      Alert.alert('오류', '채팅방 목록을 불러오는데 실패했습니다.');
    }
  };

  const onRefresh = async () => {
    setIsRefreshing(true);
    await loadChatRooms();
    setIsRefreshing(false);
  };

  const deleteChatRoom = (roomId: string) => {
    Alert.alert(
      '삭제 확인',
      '이 채팅방을 삭제하시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '삭제',
          style: 'destructive',
          onPress: () => {
            setChatRooms(prev => prev.filter(room => room.id !== roomId));
            Alert.alert('완료', '채팅방이 삭제되었습니다.');
          },
        },
      ]
    );
  };

  const renderChatRoom = ({ item }: { item: ChatRoom }) => (
    <TouchableOpacity style={styles.roomCard}>
      <View style={styles.roomHeader}>
        <View style={styles.roomTitleContainer}>
          <Icon name="chat" size={24} color="#007AFF" />
          <Text style={styles.roomName} numberOfLines={1}>
            {item.name}
          </Text>
        </View>
        <TouchableOpacity
          onPress={() => deleteChatRoom(item.id)}
          style={styles.deleteButton}
        >
          <Icon name="delete" size={20} color="#FF3B30" />
        </TouchableOpacity>
      </View>

      <View style={styles.roomStats}>
        <View style={styles.statItem}>
          <Icon name="message" size={16} color="#666" />
          <Text style={styles.statText}>{item.messageCount}개 메시지</Text>
        </View>
        <View style={styles.statItem}>
          <Icon name="people" size={16} color="#666" />
          <Text style={styles.statText}>{item.participantCount}명 참여</Text>
        </View>
        <View style={styles.statItem}>
          <Icon name="folder" size={16} color="#666" />
          <Text style={styles.statText}>{item.fileCount}개 파일</Text>
        </View>
      </View>

      <View style={styles.participantsSection}>
        <Text style={styles.participantsTitle}>참여자:</Text>
        <Text style={styles.participantsList} numberOfLines={2}>
          {item.participants.join(', ')}
        </Text>
      </View>

      <View style={styles.roomFooter}>
        <Text style={styles.lastMessage}>마지막 메시지: {item.lastMessage}</Text>
        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.analyzeButton}>
            <Icon name="analytics" size={16} color="#fff" />
            <Text style={styles.actionButtonText}>분석</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.exportButton}>
            <Icon name="download" size={16} color="#fff" />
            <Text style={styles.actionButtonText}>내보내기</Text>
          </TouchableOpacity>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>💬 채팅방 히스토리</Text>
        <Text style={styles.subtitle}>
          저장된 채팅방 목록을 관리하고 분석할 수 있습니다
        </Text>
      </View>

      {chatRooms.length === 0 ? (
        <View style={styles.emptyState}>
          <Icon name="chat-bubble-outline" size={64} color="#ccc" />
          <Text style={styles.emptyText}>저장된 채팅방이 없습니다</Text>
          <Text style={styles.emptySubtext}>
            파일 업로드 탭에서 채팅 파일을 먼저 업로드해주세요
          </Text>
        </View>
      ) : (
        <FlatList
          data={chatRooms}
          renderItem={renderChatRoom}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.listContainer}
          refreshControl={
            <RefreshControl refreshing={isRefreshing} onRefresh={onRefresh} />
          }
          showsVerticalScrollIndicator={false}
        />
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    paddingBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 20,
  },
  listContainer: {
    padding: 20,
    paddingTop: 10,
  },
  roomCard: {
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
  roomHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  roomTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  roomName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginLeft: 8,
    flex: 1,
  },
  deleteButton: {
    padding: 4,
  },
  roomStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 12,
    paddingVertical: 8,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  participantsSection: {
    marginBottom: 12,
  },
  participantsTitle: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
    fontWeight: '500',
  },
  participantsList: {
    fontSize: 14,
    color: '#333',
    lineHeight: 18,
  },
  roomFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  lastMessage: {
    fontSize: 12,
    color: '#666',
    flex: 1,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  analyzeButton: {
    backgroundColor: '#007AFF',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  exportButton: {
    backgroundColor: '#34C759',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 4,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#666',
    marginTop: 16,
    textAlign: 'center',
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    marginTop: 8,
    textAlign: 'center',
    lineHeight: 20,
  },
});

export default HistoryScreen; 