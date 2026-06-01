import PipelineFlow from '../components/PipelineFlow';
import AgentLogs from '../components/AgentLogs';
import TokenStats from '../components/TokenStats';
import { runPipeline } from '../api/client';
import { Play, CheckCircle, RefreshCw } from 'lucide-react';
import { useAppContext } from '../components/AppContext';

const BUSY = ['validando', 'corrigindo'];

export default function DashboardPage() {
  const { status, setStatus, setResults, results } = useAppContext();
  const isBusy = BUSY.includes(status);

  const handleRerun = async () => {
    setStatus('validando');
    setResults(null);
    try {
      await runPipeline();
    } catch (err) {
      console.error(err);
      setStatus('idle');
    }
  };

  return (
    <div className="p-6 md:p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-1">Monitoramento LangGraph</h1>
          <p className="text-slate-400">Acompanhe a execução dos agentes e consumo de LLM em tempo real.</p>
        </div>

        {/* Botão re-rodar só aparece após o primeiro upload/pipeline não automática */}
        {(status === 'concluido' || status === 'erro' || status === 'idle') && (
          <button
            onClick={handleRerun}
            disabled={isBusy}
            className="flex items-center gap-2 bg-brand hover:bg-brand-hover disabled:bg-slate-700 disabled:cursor-not-allowed text-white px-5 py-2.5 rounded-xl font-medium transition-colors shadow-[0_0_20px_rgba(59,130,246,0.3)]"
          >
            <span className="flex items-center gap-2">
              <RefreshCw size={16} /> Re-rodar Pipeline
            </span>
          </button>
        )}

        {isBusy && (
          <div className="flex items-center gap-2 text-amber-400 text-sm font-medium px-4 py-2 bg-amber-500/10 border border-amber-500/20 rounded-xl">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            Processando...
          </div>
        )}
      </div>

      <TokenStats />

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <PipelineFlow />

          {results && status === 'concluido' && (
            <div className="glass-panel p-6 bg-emerald-900/10 border-emerald-500/20">
              <h3 className="font-semibold text-emerald-400 flex items-center gap-2 mb-4">
                <CheckCircle size={20} /> Pipeline Concluída com Sucesso
              </h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="text-slate-400">Arquivos processados: <span className="text-white font-medium">{results.files_processed}</span></div>
                <div className="text-slate-400">Registros limpos: <span className="text-emerald-400 font-bold">{results.clean_records}</span></div>
                <div className="text-slate-400">Válidos: <span className="text-white">{results.valid_files}</span></div>
                <div className="text-slate-400">Corrigidos: <span className="text-white">{results.fixed_files}</span></div>
              </div>
            </div>
          )}
        </div>

        <div>
          <AgentLogs />
        </div>
      </div>
    </div>
  );
}
