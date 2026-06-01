import { useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';
import { cn } from '../utils/cn';
import { useAppContext } from './AppContext';

export default function AgentLogs() {
  const bottomRef = useRef(null);
  const { logs } = useAppContext();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="glass-panel flex flex-col h-96 overflow-hidden">
      <div className="flex items-center gap-2 p-4 border-b border-slate-700/50 bg-dark-900/50">
        <Terminal size={18} className="text-brand" />
        <h3 className="font-semibold text-slate-200">Terminal de Agentes (Live)</h3>
      </div>
      
      <div className="flex-1 overflow-auto p-4 font-mono text-sm space-y-2 bg-[#09090b]">
        {logs.length === 0 && (
          <div className="text-slate-500 italic">Aguardando execução do pipeline...</div>
        )}
        {logs.map((log, i) => (
          <div key={i} className="flex gap-3 text-slate-300">
            <span className="text-slate-500 shrink-0">{log.timestamp}</span>
            <span className={cn(
              "shrink-0 font-medium",
              log.agent === 'Validator Agent' && "text-amber-400",
              log.agent === 'Fixer Agent' && "text-emerald-400",
              log.agent === 'Analyst Agent' && "text-purple-400",
              log.agent === 'Orchestrator' && "text-sky-400",
              log.agent === 'LLM Service' && "text-orange-400"
            )}>
              [{log.agent}]
            </span>
            <span className="break-all">{log.message}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
