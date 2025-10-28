import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const agentAPI = {
  executeTask: async (task: string, context?: any, agentType?: string) => {
    const response = await api.post('/api/agents/execute', {
      task,
      context,
      agent_type: agentType,
    })
    return response.data
  },

  generateEmail: async (prospectData: {
    prospect_name: string
    prospect_company: string
    prospect_role: string
    context?: string
  }) => {
    const response = await api.post('/api/agents/generate-email', prospectData)
    return response.data
  },

  getStatus: async () => {
    const response = await api.get('/api/agents/status')
    return response.data
  },
}

export const voiceAPI = {
  createRoom: async (roomName: string) => {
    const response = await api.post('/api/voice/room/create', { room_name: roomName })
    return response.data
  },

  generateToken: async (roomName: string, participantIdentity: string) => {
    const response = await api.post('/api/voice/token/generate', {
      room_name: roomName,
      participant_identity: participantIdentity,
    })
    return response.data
  },

  processConversation: async (roomName: string, transcript: string) => {
    const response = await api.post('/api/voice/conversation/process', {
      room_name: roomName,
      transcript,
    })
    return response.data
  },

  startRecording: async (roomName: string) => {
    const response = await api.post(`/api/voice/recording/start/${roomName}`)
    return response.data
  },

  stopRecording: async (roomName: string) => {
    const response = await api.post(`/api/voice/recording/stop/${roomName}`)
    return response.data
  },

  getTranscript: async (roomName: string) => {
    const response = await api.get(`/api/voice/recording/transcript/${roomName}`)
    return response.data
  },
}

export const analyticsAPI = {
  getAgentPerformance: async (agentType: string, days: number = 7) => {
    const response = await api.get(`/api/analytics/performance/${agentType}?days=${days}`)
    return response.data
  },

  getVoiceCallAnalytics: async (days: number = 7) => {
    const response = await api.get(`/api/analytics/voice-calls?days=${days}`)
    return response.data
  },

  getDashboardMetrics: async () => {
    const response = await api.get('/api/analytics/dashboard')
    return response.data
  },
}
