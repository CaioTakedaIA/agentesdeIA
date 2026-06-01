import { Outlet, NavLink } from 'react-router-dom';
import { Activity, Database, Bot } from 'lucide-react';
import { cn } from '../utils/cn';

function NavItem({ to, icon: Icon, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => cn(
        "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors font-medium",
        isActive 
          ? "bg-brand/10 text-brand border border-brand/20 shadow-[0_0_15px_rgba(59,130,246,0.15)]" 
          : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
      )}
    >
      <Icon size={20} />
      {children}
    </NavLink>
  );
}

export default function Layout() {
  return (
    <div className="min-h-screen flex bg-dark-900 text-slate-200">
      <aside className="w-64 border-r border-slate-700/50 bg-dark-900/50 backdrop-blur-xl flex flex-col">
        <div className="p-6">
          <div className="flex items-center gap-3 text-brand">
            <Database className="w-8 h-8" />
            <h1 className="text-xl font-bold tracking-tight">CSV AI <span className="text-slate-400 font-light">System</span></h1>
          </div>
        </div>
        
        <nav className="flex-1 px-4 space-y-2 py-4">
          <NavItem to="/" icon={Activity}>Monitoramento</NavItem>
          <NavItem to="/analyzer" icon={Bot}>Análise e Q&A</NavItem>
        </nav>
        
        <div className="p-4 border-t border-slate-800/50">
          <div className="text-xs text-slate-500 text-center">
            Agentic AI Pipeline<br/>Powered by LangGraph & Groq
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-auto bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-800/40 via-dark-900 to-dark-900">
        <Outlet />
      </main>
    </div>
  );
}
