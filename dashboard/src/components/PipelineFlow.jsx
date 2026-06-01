import { Activity, Beaker, Wrench, CheckCircle } from 'lucide-react';
import { cn } from '../utils/cn';
import { useAppContext } from './AppContext';

function Node({ icon: Icon, title, subtitle, active, pulse, done }) {
  return (
    <div className={cn(
      "flex flex-col items-center gap-2 p-4 rounded-xl border border-slate-700/50 bg-dark-800/80 backdrop-blur-sm transition-all duration-500 min-w-[110px]",
      done && "border-emerald-500/50 shadow-[0_0_20px_rgba(52,211,153,0.15)] bg-dark-800",
      active && !done && "border-brand shadow-[0_0_20px_rgba(59,130,246,0.3)] bg-dark-800",
      pulse && "animate-pulse border-amber-500 shadow-[0_0_20px_rgba(245,158,11,0.2)]",
    )}>
      <div className={cn(
        "p-3 rounded-full bg-slate-800",
        done && "bg-emerald-500/20 text-emerald-400",
        active && !done && "bg-brand/20 text-brand",
        pulse && "bg-amber-500/20 text-amber-500",
      )}>
        {done ? <CheckCircle size={24} /> : <Icon size={24} />}
      </div>
      <span className="font-medium text-sm text-center text-slate-300">{title}</span>
      {subtitle && <span className="text-xs text-slate-500 text-center">{subtitle}</span>}
    </div>
  );
}

function Arrow({ active }) {
  return (
    <div className={cn("flex-1 h-0.5 relative transition-colors duration-500", active ? "bg-brand/50" : "bg-slate-700/50")}>
      <div className={cn("absolute right-0 top-1/2 -translate-y-1/2 border-solid border-y-transparent border-y-[6px] border-r-0 border-l-[8px] transition-colors duration-500", active ? "border-l-brand/50" : "border-l-slate-700/50")} />
    </div>
  );
}

const STATUS_LABELS = {
  idle: 'Aguardando...',
  validando: 'Validando schema...',
  corrigindo: 'Corrigindo schema...',
  concluido: 'Pipeline concluida!',
  erro: 'Erro na pipeline',
};

export default function PipelineFlow() {
  const { status } = useAppContext();

  const isValidating = status === 'validando';
  const isFixing = status === 'corrigindo';
  const isDone = status === 'concluido';
  const started = status !== 'idle';

  return (
    <div className="glass-panel p-6">
      <h3 className="font-semibold text-slate-200 mb-6 flex items-center gap-2">
        <Activity size={18} className="text-brand" />
        LangGraph Flow (StateGraph)
      </h3>

      <div className="flex items-center justify-between gap-2 max-w-3xl mx-auto px-4 overflow-x-auto pb-4">
        <Node icon={Activity} title="INÍCIO" active={started} done={started} />
        <Arrow active={started} />
        <Node
          icon={Beaker}
          title="Agente Validador"
          subtitle="Verifica schema"
          active={isValidating}
          pulse={isValidating}
          done={isFixing || isDone}
        />
        <Arrow active={isFixing || isDone} />
        <Node
          icon={Wrench}
          title="Agente Corretor"
          subtitle="Repara dados"
          active={isFixing}
          pulse={isFixing}
          done={isDone}
        />
        <Arrow active={isDone} />
        <Node icon={CheckCircle} title="CONCLUÍDO" subtitle="Dados limpos" active={isDone} done={isDone} />
      </div>

      <div className="mt-4 text-center text-sm text-slate-400">
        Status: <span className={cn("font-mono font-medium", isDone ? "text-emerald-400" : "text-brand")}>
          {STATUS_LABELS[status] ?? status}
        </span>
      </div>
    </div>
  );
}
