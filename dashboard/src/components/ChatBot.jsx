import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { askQuestion } from '../api/client';
import { cn } from '../utils/cn';
import { useAppContext } from './AppContext';

export default function ChatBot() {
  const { chatMessages: messages, setChatMessages: setMessages } = useAppContext();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const res = await askQuestion(userMsg);
      if (res.status === 'success') {
        const extra = res.grounded ? "\n\n*(Grounded: Respondido estritamente com base nos dados)*" : "";
        setMessages(prev => [...prev, { role: 'assistant', content: res.answer + extra }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: "Erro: Pipeline não foi executada. Envie um arquivo e rode o fluxo primeiro." }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Houve uma falha na conexão. A API backend está online?" }]);
    }
    setLoading(false);
  };

  return (
    <div className="glass-panel flex flex-col h-[500px]">
      <div className="p-4 border-b border-slate-700/50 bg-brand/5 flex items-center gap-3">
        <Bot className="text-brand w-6 h-6" />
        <div>
          <h3 className="font-semibold text-slate-200">Analyst Agent <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-400 align-middle ml-2">Zero-Hallucination</span></h3>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={cn("flex gap-3 max-w-[85%]", msg.role === 'user' ? "ml-auto flex-row-reverse" : "")}>
            <div className={cn("w-8 h-8 rounded-full flex items-center justify-center shrink-0", msg.role === 'user' ? "bg-slate-700 text-slate-300" : "bg-brand/20 text-brand")}>
              {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
            </div>
            <div className={cn("p-3 rounded-2xl text-sm whitespace-pre-wrap leading-relaxed", msg.role === 'user' ? "bg-brand text-white rounded-tr-none" : "bg-slate-800 text-slate-200 rounded-tl-none")}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3 max-w-[85%]">
            <div className="w-8 h-8 rounded-full bg-brand/20 text-brand flex items-center justify-center"><Bot size={16} /></div>
            <div className="p-4 rounded-2xl bg-slate-800 rounded-tl-none flex items-center gap-2">
              <Loader2 size={16} className="animate-spin text-brand" /> <span className="text-sm text-slate-400">Analisando contexto pandas...</span>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-slate-700/50 bg-dark-900/50">
        <div className="relative flex items-center">
          <input
            type="text"
            className="w-full bg-slate-800/50 border border-slate-700 rounded-full pl-4 pr-12 py-3 text-sm text-slate-200 focus:outline-none focus:border-brand/50 focus:ring-1 focus:ring-brand/50"
            placeholder="Pergunte ao analista..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
            <button type="submit" disabled={!input.trim() || loading} className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-brand hover:bg-brand-hover disabled:bg-slate-700 text-white transition-colors">
              <span className="flex items-center justify-center"><Send size={16} /></span>
            </button>
        </div>
      </form>
    </div>
  );
}
