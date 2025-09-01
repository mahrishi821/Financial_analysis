// src/features/chatbot/services/chatbotApi.ts
// Minimal API client and React hook for the chatbot endpoints

import api from "@/service/api";

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface UploadResponse {
  message: string;
  upload_id: number;
}

export interface QueryResponse {
  answer: string;
  session_id: number;
}

export interface ChatSessionDto {
  id: number;
  question: string;
  answer: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

export interface UploadedDoc {
  id: number;
  name: string;
  status: 'uploading' | 'processing' | 'ready' | 'error';
  uploadProgress: number;
  error?: string;
}

// Helper to handle both wrapped {success, data} responses and plain payloads
function unwrapOrThrow<T>(payload: any, defaultError: string): T {
  if (payload && typeof payload === 'object' && 'success' in payload) {
    const resp = payload as ApiResponse<T>;
    if (!resp.success) throw new Error(resp.message || defaultError);
    return resp.data as T;
  }
  return payload as T;
}

class ChatbotApiService {
  async uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await api.post('/chatbot/upload/', formData);
    return unwrapOrThrow<UploadResponse>(res.data, 'Upload failed');
  }

  async processDocument(uploadId: number): Promise<void> {
    const res = await api.post(`/chatbot/process/${uploadId}/`);
    // If wrapped, will throw on !success; otherwise HTTP ok is enough
    unwrapOrThrow<{}>(res.data, 'Processing failed');
  }

  async queryDocument(uploadId: number, question: string): Promise<QueryResponse> {
    const res = await api.post(`/chatbot/query/${uploadId}/`, { question });
    return unwrapOrThrow<QueryResponse>(res.data, 'Query failed');
  }

  async getChatHistory(uploadId: number): Promise<ChatSessionDto[]> {
    const res = await api.get(`/chatbot/history/${uploadId}/`);
    try {
      return unwrapOrThrow<ChatSessionDto[]>(res.data, 'History failed') || [];
    } catch (e) {
      throw e;
    }
  }

  async uploadAndProcessDocument(
    file: File,
    onProgress?: (stage: 'uploading' | 'processing', progress: number) => void
  ): Promise<number> {
    onProgress?.('uploading', 0);
    const upload = await this.uploadDocument(file);
    onProgress?.('uploading', 100);

    onProgress?.('processing', 0);
    await this.processDocument(upload.upload_id);
    onProgress?.('processing', 100);

    return upload.upload_id;
  }
}

export const chatbotApi = new ChatbotApiService();

// React hook glue for UI
import { useCallback, useState } from 'react';

export const useChatbot = () => {
  const [currentDoc, setCurrentDoc] = useState<UploadedDoc | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);

  const uploadDocument = useCallback(async (file: File) => {
    const temp: UploadedDoc = {
      id: Date.now(),
      name: file.name,
      status: 'uploading',
      uploadProgress: 0,
    };
    setCurrentDoc(temp);

    try {
      const uploadId = await chatbotApi.uploadAndProcessDocument(file, (stage, progress) => {
        setCurrentDoc(prev => (prev ? { ...prev, status: stage, uploadProgress: progress } : null));
      });

      const processed: UploadedDoc = { ...temp, id: uploadId, status: 'ready', uploadProgress: 100 };
      setCurrentDoc(processed);

      // Prefill history
      try {
        const history = await chatbotApi.getChatHistory(uploadId);
        if (history.length) {
          const histMsgs: ChatMessage[] = history
            .map(s => ([
              { id: `u-${s.id}`, type: 'user' as const, content: s.question, timestamp: new Date(s.created_at) },
              { id: `b-${s.id}`, type: 'bot' as const, content: s.answer, timestamp: new Date(s.created_at) },
            ]))
            .flat();
          setMessages(histMsgs);
        } else {
          setMessages([{
            id: String(Date.now()),
            type: 'bot',
            content: `Great! I've processed "${file.name}". Ask me anything about it.\n\n• What are the main topics?\n• Summarize key points\n• Important dates or numbers?`,
            timestamp: new Date(),
          }]);
        }
      } catch {
        // ignore history failures in UI
      }

      return processed;
    } catch (e: any) {
      setCurrentDoc({ ...temp, status: 'error', error: e?.message || 'Upload failed', uploadProgress: 0 });
      throw e;
    }
  }, []);

  const sendMessage = useCallback(async (question: string) => {
    if (!currentDoc || currentDoc.status !== 'ready') throw new Error('No ready document');

    const userMsg: ChatMessage = { id: String(Date.now()), type: 'user', content: question, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const res = await chatbotApi.queryDocument(currentDoc.id, question);
      const botMsg: ChatMessage = { id: String(Date.now() + 1), type: 'bot', content: res.answer, timestamp: new Date() };
      setMessages(prev => [...prev, botMsg]);
      return botMsg;
    } catch (e) {
      const errMsg: ChatMessage = { id: String(Date.now() + 1), type: 'bot', content: 'Sorry, something went wrong.', timestamp: new Date() };
      setMessages(prev => [...prev, errMsg]);
      throw e;
    } finally {
      setIsTyping(false);
    }
  }, [currentDoc]);

  const reset = useCallback(() => {
    setCurrentDoc(null);
    setMessages([]);
  }, []);

  return { currentDoc, messages, isTyping, uploadDocument, sendMessage, reset };
};

