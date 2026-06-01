import { Cpu, Zap } from 'lucide-react';
import { useAppContext } from './AppContext';

export default function TokenStats() {
  const { stats } = useAppContext();

  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="glass-panel p-4 flex flex-col items-center justify-center relative overflow-hidden">
        <div className="absolute top-0 right-0 p-2 opacity-10"><Cpu size={48} /></div>
        <div className="text-sm font-medium text-slate-400 mb-1">Prompt Tokens</div>
        <div className="text-3xl font-bold text-sky-400">{stats.prompt.toLocaleString()}</div>
      </div>
      
      <div className="glass-panel p-4 flex flex-col items-center justify-center relative overflow-hidden">
        <div className="absolute top-0 right-0 p-2 opacity-10"><Zap size={48} /></div>
        <div className="text-sm font-medium text-slate-400 mb-1">Completion Tokens</div>
        <div className="text-3xl font-bold text-amber-400">{stats.completion.toLocaleString()}</div>
      </div>

      <div className="glass-panel p-4 flex flex-col items-center justify-center relative overflow-hidden ring-1 ring-brand/30 bg-brand/5">
        <div className="text-sm font-medium text-brand mb-1">Custo Total (Gratuito Groq)</div>
        <div className="text-4xl font-black text-slate-100">{stats.total.toLocaleString()}</div>
        <div className="text-xs text-brand/60 mt-2">Tokens Processados</div>
      </div>
    </div>
  );
}
