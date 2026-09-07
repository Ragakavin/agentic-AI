import React, { useState } from 'react';
import { Bot, Send, User, Sparkles, Wrench, RefreshCw, MessageSquare } from 'lucide-react';
import { api } from '../services/api';
import { ChatMessage } from '../types';

export const AiAssistant: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      role: 'assistant',
      content: 'Hello! I am your Intelligent Accounts Payable AI Assistant. I have live access to your invoice repository, vendor masters, and purchase orders. How can I help verify financial compliance today?',
      timestamp: new Date().toLocaleTimeString(),
      tools_used: ['get_portfolio_summary_metrics']
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const suggestedQuestions = [
    'Why was invoice INV-10025 flagged?',
    'Compare invoice INV-20450 with PO-2026-042',
    'What is the tax breakdown for invoice INV-30911?',
    'Are there any duplicate invoices in the system?',
    'Which invoices currently need human review?'
  ];

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.askAi(query);
      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: res.content,
        timestamp: new Date().toLocaleTimeString(),
        tools_used: res.tools_used,
        referenced_invoices: res.referenced_invoices
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages(prev => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: `Apologies, I encountered an error querying application records: ${err.message}`,
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-5 animate-fadeIn pb-16">
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">AI Accounts Payable Assistant</h1>
          <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-purple-50 text-purple-700 border border-purple-200 flex items-center gap-1">
            <Sparkles className="w-3 h-3" /> Grounded RAG + DB Tools
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-0.5">
          Ask questions regarding invoices, PO variances, tax schedules, or risk reasoning. Answers are strictly verified against actual database records.
        </p>
      </div>

      {/* Suggestion Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        {suggestedQuestions.map((q, i) => (
          <button
            key={i}
            onClick={() => handleSend(q)}
            className="px-3 py-1.5 rounded-full bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900 hover:border-slate-300 font-medium whitespace-nowrap shadow-2xs transition-colors"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Chat Container */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[520px] overflow-hidden">
        {/* Messages Feed */}
        <div className="flex-1 p-5 overflow-y-auto space-y-4">
          {messages.map(m => {
            const isUser = m.role === 'user';
            return (
              <div
                key={m.id}
                className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
              >
                <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-white ${
                  isUser ? 'bg-slate-900' : 'bg-gradient-to-tr from-brand-600 to-blue-600'
                }`}>
                  {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                <div className={`max-w-xl rounded-2xl p-4 text-xs leading-relaxed space-y-2 ${
                  isUser
                    ? 'bg-slate-900 text-white rounded-tr-none'
                    : 'bg-slate-50 text-slate-800 border border-slate-200/80 rounded-tl-none'
                }`}>
                  <div className="whitespace-pre-wrap">{m.content}</div>

                  {m.tools_used && m.tools_used.length > 0 && (
                    <div className="border-t border-slate-200/70 pt-2 flex items-center gap-1.5 text-[10px] text-blue-700 font-mono font-medium">
                      <Wrench className="w-3 h-3 text-blue-500" />
                      <span>Tools Grounding: {m.tools_used.join(', ')}</span>
                    </div>
                  )}

                  <div className={`text-[10px] ${isUser ? 'text-slate-400' : 'text-slate-400'}`}>
                    {m.timestamp}
                  </div>
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-brand-600 text-white flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-slate-50 border border-slate-200 p-3 rounded-2xl text-xs text-slate-500 flex items-center gap-2">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-brand-600" />
                <span>Accessing database tools and synthesizing evidence...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-3.5 border-t border-slate-200 bg-slate-50/50 flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask anything about invoices, PO matching, or risk reasons..."
            className="flex-1 px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500/20 text-slate-900"
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
            className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:opacity-40 text-white transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
