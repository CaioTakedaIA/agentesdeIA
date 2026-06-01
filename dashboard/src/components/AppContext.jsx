import { createContext, useContext, useState, useEffect } from 'react';
import { getEventSource } from '../api/client';

const AppContext = createContext();

export function AppProvider({ children }) {
  const [status, setStatus] = useState('idle');     // idle | validando | corrigindo | concluido | erro
  const [results, setResults] = useState(null);
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({ prompt: 0, completion: 0, total: 0 });
  const [chatReady, setChatReady] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [chatMessages, setChatMessages] = useState([
    { role: 'assistant', content: 'Olá! Sou seu Analyst Agent. Posso responder qualquer pergunta em linguagem natural sobre os dados estruturados e limpos da sua última pipeline. O que você gostaria de saber?' }
  ]);

  const resetState = () => {
    setStatus('idle');
    setLogs([]);
    setResults(null);
    setChatReady(false);
    setStats({ prompt: 0, completion: 0, total: 0 });
    setChatMessages([{ role: 'assistant', content: 'Olá! Sou seu Analyst Agent. Posso responder qualquer pergunta em linguagem natural sobre os dados estruturados e limpos da sua última pipeline. O que você gostaria de saber?' }]);
  };

  useEffect(() => {
    const sse = getEventSource();
    sse.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data);

        if (payload.type === 'pipeline_status') {
          const s = payload.data.status;
          if (s === 'running') setStatus('validando');
          if (s === 'completed') {
            setStatus('concluido');
            setResults(payload.data);
            // Libera o chatbot sempre que a pipeline conclui (dados já foram validados/corrigidos)
            setChatReady(true);
          }
          if (s === 'error') setStatus('erro');
        }

        if (payload.type === 'log') {
          const agent = payload.data?.agent ?? '';
          setStatus((prev) => {
            if (prev === 'concluido' || prev === 'erro') return prev;
            if (agent === 'Agente Corretor') return 'corrigindo';
            if (agent === 'Agente Validador') return 'validando';
            return prev;
          });
          setLogs((prev) => [...prev, payload.data].slice(-150));
        }

        if (payload.type === 'token_usage') {
          setStats((s) => ({
            prompt: s.prompt + payload.data.prompt_tokens,
            completion: s.completion + payload.data.completion_tokens,
            total: s.total + payload.data.total_tokens,
          }));
        }

        if (payload.type === 'upload') {
          // Reset tb chamado via SSE por seguranca (caso de multiplos clients)
          resetState();
        }
      } catch (err) {}
    };
    return () => sse.close();
  }, []);

  return (
    <AppContext.Provider value={{ status, setStatus, results, setResults, logs, stats, chatReady, uploadedFile, setUploadedFile, chatMessages, setChatMessages, resetState }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  return useContext(AppContext);
}
