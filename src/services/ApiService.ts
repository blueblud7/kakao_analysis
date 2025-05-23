import axios from 'axios';

// 백엔드 서버 URL (실제 배포 시 수정 필요)
const BASE_URL = 'http://localhost:5000'; // Streamlit 앱이 실행되는 포트

interface UploadResponse {
  success: boolean;
  fileId: string;
  roomId: string;
  newMessages: number;
  message: string;
}

interface ChatRoom {
  id: string;
  name: string;
  messageCount: number;
  participantCount: number;
  lastMessage: string;
  fileCount: number;
  participants: string[];
}

interface AnalysisRequest {
  roomId: string;
  analysisType: 'comprehensive' | 'sentiment' | 'keywords' | 'topics';
}

interface AnalysisResponse {
  success: boolean;
  result: string;
  message: string;
}

class ApiService {
  private api = axios.create({
    baseURL: BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // 파일 업로드
  async uploadFile(filePath: string, fileName: string): Promise<UploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: filePath,
        type: 'text/plain',
        name: fileName,
      } as any);

      const response = await this.api.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('File upload error:', error);
      throw new Error('파일 업로드에 실패했습니다.');
    }
  }

  // 채팅방 목록 조회
  async getChatRooms(): Promise<ChatRoom[]> {
    try {
      const response = await this.api.get('/api/rooms');
      return response.data.rooms || [];
    } catch (error) {
      console.error('Get chat rooms error:', error);
      throw new Error('채팅방 목록을 불러오는데 실패했습니다.');
    }
  }

  // 채팅방 삭제
  async deleteChatRoom(roomId: string): Promise<boolean> {
    try {
      const response = await this.api.delete(`/api/rooms/${roomId}`);
      return response.data.success;
    } catch (error) {
      console.error('Delete chat room error:', error);
      throw new Error('채팅방 삭제에 실패했습니다.');
    }
  }

  // GPT 분석 요청
  async requestAnalysis(request: AnalysisRequest): Promise<AnalysisResponse> {
    try {
      const response = await this.api.post('/api/analyze', request);
      return response.data;
    } catch (error) {
      console.error('Analysis error:', error);
      throw new Error('GPT 분석에 실패했습니다.');
    }
  }

  // 시각화 데이터 조회
  async getVisualizationData(roomId: string) {
    try {
      const response = await this.api.get(`/api/visualization/${roomId}`);
      return response.data;
    } catch (error) {
      console.error('Visualization data error:', error);
      throw new Error('시각화 데이터를 불러오는데 실패했습니다.');
    }
  }

  // 데이터 내보내기
  async exportData(roomId?: string): Promise<string> {
    try {
      const url = roomId ? `/api/export/${roomId}` : '/api/export';
      const response = await this.api.get(url);
      return response.data.downloadUrl;
    } catch (error) {
      console.error('Export data error:', error);
      throw new Error('데이터 내보내기에 실패했습니다.');
    }
  }

  // 앱 설정 저장
  async saveSettings(settings: any): Promise<boolean> {
    try {
      const response = await this.api.post('/api/settings', settings);
      return response.data.success;
    } catch (error) {
      console.error('Save settings error:', error);
      throw new Error('설정 저장에 실패했습니다.');
    }
  }

  // OpenAI API 키 검증
  async validateApiKey(apiKey: string): Promise<boolean> {
    try {
      const response = await this.api.post('/api/validate-key', { apiKey });
      return response.data.valid;
    } catch (error) {
      console.error('API key validation error:', error);
      return false;
    }
  }
}

export default new ApiService(); 