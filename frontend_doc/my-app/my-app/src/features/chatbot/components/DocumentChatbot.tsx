// src/features/chatbot/components/DocumentChatbot.tsx
'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useChatbot } from '../services/chatbotApi';
import {
  MessageCircle,
  X,
  Send,
  Upload,
  FileText,
  Loader,
  AlertCircle,
  Minimize2,
  Maximize2,
  RotateCcw,
  Clock,
  Bot,
  User,
} from 'lucide-react';

export default function DocumentChatbot() {
  const { currentDoc, messages, isTyping, uploadDocument, sendMessage, reset } = useChatbot();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  useEffect(() => { scrollToBottom(); }, [messages]);
  useEffect(() => { if (isOpen && !isMinimized && chatInputRef.current) chatInputRef.current.focus(); }, [isOpen, isMinimized, currentDoc]);

  const handleFileUpload = async (files: FileList) => {
    const file = files[0];
    if (!file) return;

    const allowed = ['.pdf', '.xls', '.xlsx', '.doc', '.docx'];
    const ext = '.' + (file.name.split('.').pop()?.toLowerCase() || '');
    if (!allowed.includes(ext)) {
      alert('Please upload PDF, Excel, or Word documents only.');
      return;
    }

    try {
      await uploadDocument(file);
    } catch (e: any) {
      console.error('Upload failed', e);
    }
  };

  const handleSend = async () => {
    if (!inputMessage.trim()) return;
    try {
      await sendMessage(inputMessage.trim());
      setInputMessage('');
    } catch (e) {
      // error already pushed to messages via hook
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // DnD
  const handleDragOver = (e: React.DragEvent) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = (e: React.DragEvent) => { e.preventDefault(); setIsDragging(false); };
  const handleDrop = (e: React.DragEvent) => { e.preventDefault(); setIsDragging(false); handleFileUpload(e.dataTransfer.files); };

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button onClick={() => setIsOpen(true)} className="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-all duration-200 hover:scale-105">
          <MessageCircle size={24} />
        </button>
      </div>
    );
  }

  return (
    <div className={`fixed bottom-6 right-6 z-50 bg-white rounded-lg shadow-2xl border transition-all duration-300 ${isMinimized ? 'w-80 h-14' : 'w-96 h-[600px]'}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-blue-600 text-white rounded-t-lg">
        <div className="flex items-center space-x-2">
          <Bot size={20} />
          <h3 className="font-semibold">Document Assistant</h3>
          {currentDoc && (
            <span className="text-xs bg-blue-500 px-2 py-1 rounded" title={currentDoc.name}>
              {currentDoc.name.length > 15 ? currentDoc.name.substring(0, 15) + '…' : currentDoc.name}
            </span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <button onClick={() => setIsMinimized(!isMinimized)} className="hover:bg-blue-700 p-1 rounded">
            {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
          </button>
          {currentDoc && (
            <button onClick={reset} className="hover:bg-blue-700 p-1 rounded" title="Start new chat">
              <RotateCcw size={16} />
            </button>
          )}
          <button onClick={() => setIsOpen(false)} className="hover:bg-blue-700 p-1 rounded">
            <X size={16} />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Upload area */}
          {!currentDoc && (
            <div className={`m-4 p-8 border-2 border-dashed rounded-lg text-center transition-colors ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}`}
              onDragOver={handleDragOver} onDragLeave={handleDragLeave} onDrop={handleDrop}>
              <Upload className="mx-auto mb-4 text-gray-400" size={48} />
              <h4 className="text-lg font-semibold mb-2">Upload Document to Start Chatting</h4>
              <p className="text-gray-600 mb-4">Drag & drop or click to upload PDF, Excel, or Word documents</p>
              <button onClick={() => fileInputRef.current?.click()} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors">Choose File</button>
              <input ref={fileInputRef} type="file" accept=".pdf,.xls,.xlsx,.doc,.docx" onChange={(e) => e.target.files && handleFileUpload(e.target.files)} className="hidden" />
              <div className="mt-4 text-xs text-gray-500">Supported formats: PDF, Excel (.xls, .xlsx), Word (.doc, .docx)</div>
            </div>
          )}

          {/* Processing status */}
          {currentDoc && currentDoc.status !== 'ready' && (
            <div className="m-4 p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                <FileText className="text-blue-600" size={24} />
                <div className="flex-1">
                  <h4 className="font-medium">{currentDoc.name}</h4>
                  <div className="flex items-center space-x-2 mt-2">
                    {currentDoc.status === 'uploading' && (
                      <>
                        <Loader className="animate-spin text-blue-600" size={16} />
                        <span className="text-sm text-gray-600">Uploading… {currentDoc.uploadProgress}%</span>
                      </>
                    )}
                    {currentDoc.status === 'processing' && (
                      <>
                        <Loader className="animate-spin text-blue-600" size={16} />
                        <span className="text-sm text-gray-600">Processing document…</span>
                      </>
                    )}
                    {currentDoc.status === 'error' && (
                      <>
                        <AlertCircle className="text-red-500" size={16} />
                        <span className="text-sm text-red-600">Upload failed</span>
                      </>
                    )}
                  </div>
                  {currentDoc.status === 'uploading' && (
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div className="bg-blue-600 h-2 rounded-full transition-all duration-300" style={{ width: `${currentDoc.uploadProgress}%` }} />
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Chat */}
          {currentDoc?.status === 'ready' && (
            <>
              <div className="flex-1 overflow-y-auto p-4 space-y-4 h-96">
                {messages.map((m) => (
                  <div key={m.id} className={`flex ${m.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] ${m.type === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'} rounded-lg p-3 shadow-sm`}>
                      <div className="flex items-start space-x-2">
                        {m.type === 'bot' && <Bot size={16} className="mt-0.5 text-blue-600" />}
                        {m.type === 'user' && <User size={16} className="mt-0.5" />}
                        <div className="flex-1">
                          <p className="text-sm whitespace-pre-wrap">{m.content}</p>
                          <div className="flex items-center space-x-1 mt-1 opacity-70">
                            <Clock size={12} />
                            <span className="text-xs">{m.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-lg p-3 shadow-sm">
                      <div className="flex items-center space-x-2">
                        <Bot size={16} className="text-blue-600" />
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="p-4 border-t">
                <div className="flex space-x-2">
                  <input
                    ref={chatInputRef}
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask questions about your document..."
                    className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    disabled={isTyping}
                  />
                  <button onClick={handleSend} disabled={!inputMessage.trim() || isTyping} className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white p-2 rounded-md transition-colors">
                    <Send size={16} />
                  </button>
                </div>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}

