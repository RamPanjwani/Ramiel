import React, { useState } from 'react';
import { api } from '../api/client';

interface Message {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  timestamp: string;
  modelUsed?: string | null;
}

export const ChatPanel: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'agent',
      text: 'Ramiel Sovereign Workbench initialized (Phase 0 Skeleton). Ready for task execution.',
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: input,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.sendChatMessage(userMsg.text);
      const agentMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: res.reply,
        timestamp: new Date().toLocaleTimeString(),
        modelUsed: res.model_used,
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: 'Error connecting to local backend at 127.0.0.1:8000.',
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#161B1E] border border-[#2A3236] rounded-md overflow-hidden">
      {/* Panel Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#1E2528] border-b border-[#2A3236]">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-[#D98E2F]" />
          <span className="text-xs font-mono font-bold tracking-wider text-[#E4E9EA]">
            AGENT EXECUTION INTERFACE
          </span>
        </div>
        <span className="text-[10px] font-mono text-[#8B979B]">
          AIR-GAPPED WORKBENCH
        </span>
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 font-sans text-xs">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex flex-col ${
              m.sender === 'user' ? 'items-end' : 'items-start'
            }`}
          >
            <div className="flex items-center space-x-1.5 mb-1 text-[10px] font-mono text-[#8B979B]">
              <span className="font-semibold text-[#E4E9EA]">
                {m.sender === 'user' ? 'OPERATOR' : 'RAMIEL AGENT'}
              </span>
              <span>•</span>
              <span>{m.timestamp}</span>
              {m.modelUsed && (
                <span className="px-1 py-0.5 bg-[#0E1214] text-[#D98E2F] rounded border border-[#2A3236]">
                  {m.modelUsed}
                </span>
              )}
            </div>

            <div
              className={`p-3 rounded max-w-[85%] border ${
                m.sender === 'user'
                  ? 'bg-[#1E2528] text-[#E4E9EA] border-[#2A3236]'
                  : 'bg-[#0E1214] text-[#E4E9EA] border-[#2A3236]'
              }`}
            >
              <p className="whitespace-pre-wrap leading-relaxed">{m.text}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="text-[11px] font-mono text-[#D98E2F] flex items-center space-x-2">
            <span className="animate-spin">◓</span>
            <span>DISPATCHING TASK TO LOCAL ORCHESTRATOR...</span>
          </div>
        )}
      </div>

      {/* Input Box */}
      <form
        onSubmit={handleSend}
        className="p-3 bg-[#1E2528] border-t border-[#2A3236] flex items-center space-x-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter prompt or operational directive..."
          className="flex-1 bg-[#0E1214] border border-[#2A3236] rounded px-3 py-2 text-xs font-mono text-[#E4E9EA] placeholder-[#8B979B] focus:outline-none focus:border-[#D98E2F]"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-[#D98E2F] hover:bg-[#B8701F] text-[#0E1214] font-mono font-bold text-xs px-4 py-2 rounded transition-colors disabled:opacity-50"
        >
          EXECUTE
        </button>
      </form>
    </div>
  );
};
