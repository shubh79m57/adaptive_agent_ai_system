'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { voiceAPI } from '@/lib/api'
import { Phone, PlayCircle, StopCircle, FileText } from 'lucide-react'

export default function VoicePage() {
  const [roomName, setRoomName] = useState('')
  const [participantId, setParticipantId] = useState('')
  const [currentRoom, setCurrentRoom] = useState<string | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [transcript, setTranscript] = useState<string | null>(null)

  const createRoomMutation = useMutation({
    mutationFn: () => voiceAPI.createRoom(roomName),
    onSuccess: (data) => {
      setCurrentRoom(data.room_name)
    },
  })

  const generateTokenMutation = useMutation({
    mutationFn: () => voiceAPI.generateToken(roomName, participantId),
    onSuccess: (data) => {
      setToken(data.token)
    },
  })

  const startRecordingMutation = useMutation({
    mutationFn: () => voiceAPI.startRecording(currentRoom!),
  })

  const stopRecordingMutation = useMutation({
    mutationFn: () => voiceAPI.stopRecording(currentRoom!),
  })

  const getTranscriptMutation = useMutation({
    mutationFn: () => voiceAPI.getTranscript(currentRoom!),
    onSuccess: (data) => {
      setTranscript(data.transcript)
    },
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-teal-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Voice Call Management
        </h1>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center space-x-2">
            <Phone className="w-6 h-6 text-green-600" />
            <span>Create Voice Room</span>
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Room Name
              </label>
              <input
                type="text"
                value={roomName}
                onChange={(e) => setRoomName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                placeholder="sales-call-001"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Participant ID
              </label>
              <input
                type="text"
                value={participantId}
                onChange={(e) => setParticipantId(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                placeholder="agent-001"
              />
            </div>

            <div className="flex space-x-4">
              <button
                onClick={() => createRoomMutation.mutate()}
                disabled={!roomName || createRoomMutation.isPending}
                className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-400"
              >
                Create Room
              </button>

              <button
                onClick={() => generateTokenMutation.mutate()}
                disabled={!roomName || !participantId || generateTokenMutation.isPending}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
              >
                Generate Token
              </button>
            </div>
          </div>

          {currentRoom && (
            <div className="mt-6 p-4 bg-green-50 rounded-lg">
              <p className="font-medium text-green-900">
                Room Created: {currentRoom}
              </p>
            </div>
          )}

          {token && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <p className="font-medium text-blue-900 mb-2">Access Token:</p>
              <p className="text-xs text-blue-700 break-all font-mono">{token}</p>
            </div>
          )}
        </div>

        {currentRoom && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-bold mb-4">Recording Controls</h2>
            
            <div className="flex space-x-4">
              <button
                onClick={() => startRecordingMutation.mutate()}
                disabled={startRecordingMutation.isPending}
                className="flex items-center space-x-2 bg-red-600 text-white py-2 px-6 rounded-lg hover:bg-red-700"
              >
                <PlayCircle className="w-5 h-5" />
                <span>Start Recording</span>
              </button>

              <button
                onClick={() => stopRecordingMutation.mutate()}
                disabled={stopRecordingMutation.isPending}
                className="flex items-center space-x-2 bg-gray-600 text-white py-2 px-6 rounded-lg hover:bg-gray-700"
              >
                <StopCircle className="w-5 h-5" />
                <span>Stop Recording</span>
              </button>

              <button
                onClick={() => getTranscriptMutation.mutate()}
                disabled={getTranscriptMutation.isPending}
                className="flex items-center space-x-2 bg-purple-600 text-white py-2 px-6 rounded-lg hover:bg-purple-700"
              >
                <FileText className="w-5 h-5" />
                <span>Get Transcript</span>
              </button>
            </div>
          </div>
        )}

        {transcript && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4">Transcript</h2>
            <div className="bg-gray-50 rounded-lg p-4">
              <pre className="whitespace-pre-wrap text-sm">{transcript}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
