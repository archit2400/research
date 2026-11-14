import React from 'react';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

const STAGES = [
  { id: 1, name: 'PDF Extraction', agent: 'PyMuPDF', minPct: 10 },
  { id: 2, name: 'Vector Storage', agent: 'ChromaDB', minPct: 20 },
  { id: 3, name: 'Query Agent', agent: 'Agent 1', minPct: 30 },
  { id: 4, name: 'Retrieval Agent', agent: 'Agent 2 (RAG)', minPct: 40 },
  { id: 5, name: 'Summary Agent', agent: 'Agent 3', minPct: 50 },
  { id: 6, name: 'Fact-Check Critic', agent: 'Agent 4 (Critic)', minPct: 65 },
  { id: 7, name: 'Contradiction Agent', agent: 'Agent 5', minPct: 75 },
  { id: 8, name: 'Writer Agent', agent: 'Agent 6', minPct: 92 },
];

export default function ProgressTracker({ progress, statusMessage, error }) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
            {error ? (
              <AlertCircle className="w-5 h-5 text-rose-500" />
            ) : progress >= 100 ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-500" />
            ) : (
              <Loader2 className="w-5 h-5 animate-spin" />
            )}
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              {error ? 'Execution Encountered An Issue' : progress >= 100 ? 'Academic Intelligence Ready' : 'Multi-Agent Pipeline Executing...'}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {statusMessage || 'Processing research documents...'}
            </p>
          </div>
        </div>

        <span className="text-sm font-bold text-indigo-600 dark:text-indigo-400">
          {progress}%
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 mb-6 overflow-hidden">
        <div
          className={`h-full transition-all duration-500 rounded-full ${
            error ? 'bg-rose-500' : 'bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-400'
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* 8 Agent Stages Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
        {STAGES.map((s) => {
          const isDone = progress >= s.minPct;
          const isCurrent = progress >= s.minPct - 15 && progress < s.minPct + 10;
          return (
            <div
              key={s.id}
              className={`p-2.5 rounded-xl border text-center transition ${
                isDone
                  ? 'bg-emerald-50/60 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800/60 text-emerald-700 dark:text-emerald-300'
                  : isCurrent
                  ? 'bg-indigo-50 dark:bg-indigo-950/40 border-indigo-300 dark:border-indigo-700 text-indigo-700 dark:text-indigo-300 ring-2 ring-indigo-500/20'
                  : 'bg-slate-50 dark:bg-slate-950/40 border-slate-200 dark:border-slate-800 text-slate-400 dark:text-slate-600'
              }`}
            >
              <div className="text-[10px] font-semibold uppercase tracking-wider opacity-75">{s.agent}</div>
              <div className="text-xs font-bold truncate mt-0.5">{s.name}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
