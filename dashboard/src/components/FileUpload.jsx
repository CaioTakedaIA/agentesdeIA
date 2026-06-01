import { useState } from 'react';
import { UploadCloud, CheckCircle } from 'lucide-react';
import { uploadFile, runPipeline } from '../api/client';
import { cn } from '../utils/cn';
import { useAppContext } from './AppContext';

export default function FileUpload({ onUploadSuccess }) {
  const { uploadedFile, setUploadedFile, resetState } = useAppContext();
  const [drag, setDrag] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleDrop = async (e) => {
    e.preventDefault();
    setDrag(false);
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) await processFile(file);
  };

  const handleChange = async (e) => {
    const file = e.target.files[0];
    if (file) await processFile(file);
  };

  const processFile = async (file) => {
    setLoading(true);
    resetState(); // Garante o reset 100% sincrono no React antes de comecar
    try {
      await uploadFile(file);
      setSuccess(true);
      setUploadedFile(file.name);
      // Dispara a pipeline instantaneamente em background
      runPipeline().catch(console.error);

      if (onUploadSuccess) onUploadSuccess();
      setTimeout(() => setSuccess(false), 3000);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div className="glass-panel p-6">
      <h3 className="font-semibold text-slate-200 mb-4">Upload de CSV (Análise ou Correção)</h3>
      <label
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={handleDrop}
        className={cn(
          "flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-xl cursor-pointer transition-all",
          drag ? "border-brand bg-brand/5 scale-105" : "border-slate-700 bg-dark-900/50 hover:bg-slate-800/50"
        )}
      >
        <input type="file" accept=".csv" className="hidden" onChange={handleChange} />
        {loading ? (
          <div className="animate-pulse text-brand">Fazendo upload...</div>
        ) : success ? (
          <div className="flex flex-col items-center text-emerald-400">
            <CheckCircle size={32} className="mb-2" />
            <span className="font-medium">Upload Concluído!</span>
          </div>
        ) : uploadedFile ? (
          <div className="flex flex-col items-center text-emerald-400">
            <CheckCircle size={32} className="mb-2" />
            <span className="font-medium">Upload ({uploadedFile})</span>
            <span className="text-xs text-slate-400 mt-1">Arraste outro para substituir</span>
          </div>
        ) : (
          <div className="flex flex-col items-center text-slate-400">
            <UploadCloud size={32} className="mb-3 text-slate-500" />
            <span className="font-medium text-slate-300">Arraste um CSV ou clique aqui</span>
            <span className="text-sm mt-1">Ex: bad_schema.csv</span>
          </div>
        )}
      </label>
    </div>
  );
}
