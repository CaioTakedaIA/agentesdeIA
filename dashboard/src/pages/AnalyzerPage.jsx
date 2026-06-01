import FileUpload from '../components/FileUpload';
import ChatBot from '../components/ChatBot';
import { useAppContext } from '../components/AppContext';
import { CheckCircle, Clock, Upload, MessageSquare } from 'lucide-react';

const STATUS_LABELS = {
  idle: { label: 'Aguardando Upload', color: 'text-slate-400', icon: Upload },
  validando: { label: 'Agente Validador analisando...', color: 'text-amber-400', icon: Clock },
  corrigindo: { label: 'Agente Corretor corrigindo schema...', color: 'text-orange-400', icon: Clock },
  concluido: { label: 'Pipeline concluída! Chatbot liberado.', color: 'text-emerald-400', icon: CheckCircle },
  erro: { label: 'Erro na pipeline', color: 'text-red-400', icon: null },
};

export default function AnalyzerPage() {
  const { status, results, chatReady } = useAppContext();
  const info = STATUS_LABELS[status] ?? STATUS_LABELS.idle;
  const Icon = info.icon;

  return (
    <div className="p-6 md:p-8 max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white mb-1">Análise Interativa</h1>
        <p className="text-slate-400">Upload do CSV → validação automática → chatbot com os dados limpos.</p>
      </div>

      {/* Status banner */}
      <div className={`flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800/60 border border-slate-700 ${info.color}`}>
        {Icon && <Icon size={16} />}
        <span className="text-sm font-medium">{info.label}</span>
        {results && status === 'concluido' && (
          <span className="ml-auto text-xs text-slate-400">
            {results.valid_files ?? 0} válido(s) · {results.fixed_files ?? 0} corrigido(s) · {results.clean_records ?? 0} registros
          </span>
        )}
      </div>

      <div className="grid lg:grid-cols-[1fr_2fr] gap-6 items-start">
        {/* Left: Upload + Instructions */}
        <div className="space-y-4">
          <FileUpload />

          <div className="glass-panel p-5 bg-brand/5 border-brand/20">
            <h3 className="text-brand font-semibold mb-3 flex items-center gap-2"><Upload size={14}/> Fluxo</h3>
            <ol className="list-decimal pl-4 space-y-2 text-sm text-slate-300">
              <li>Faça upload do seu CSV.</li>
              <li>O <strong>Agente Validador</strong> analisa o schema.</li>
              <li>Se houver erros, o <strong>Agente Corretor</strong> repara automaticamente.</li>
              <li>Após validação, o <strong>Chatbot</strong> é liberado.</li>
            </ol>
          </div>
        </div>

        {/* Right: ChatBot or Locked State */}
        <div>
          {chatReady ? (
            <ChatBot />
          ) : (
            <div className="glass-panel p-8 flex flex-col items-center justify-center text-center gap-4 min-h-[400px]">
              <MessageSquare size={48} className="text-slate-600" />
              <div>
                <p className="text-slate-300 font-medium">
                  {status === 'idle'
                    ? 'Faça o upload de um CSV para começar.'
                    : status === 'validando'
                    ? 'Agente Validador analisando seus dados...'
                    : status === 'corrigindo'
                    ? 'Agente Corretor reparando o schema...'
                    : 'Aguarde a pipeline concluir.'}
                </p>
                <p className="text-slate-500 text-sm mt-1">O chatbot será liberado automaticamente após a validação.</p>
              </div>
              {(status === 'validando' || status === 'corrigindo') && (
                <div className="flex gap-1">
                  <span className="w-2 h-2 rounded-full bg-brand animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 rounded-full bg-brand animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 rounded-full bg-brand animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
