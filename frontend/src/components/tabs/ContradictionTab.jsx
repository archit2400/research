import React from 'react';
import { AlertCircle, Scale, Quote, BookOpen } from 'lucide-react';

export default function ContradictionTab({ contradictions = [] }) {
  if (!contradictions || contradictions.length === 0) {
    return (
      <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 text-slate-500">
        No direct empirical contradictions detected across the analyzed papers.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
          <Scale className="w-5 h-5 text-amber-500" />
          <span>Cross-Paper Contradiction & Disagreement Analysis ({contradictions.length})</span>
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Identifies conflicting empirical results, conclusions, or operating conditions across papers. Both positions are cited objectively alongside methodological divergence factors.
        </p>
      </div>

      <div className="space-y-6">
        {contradictions.map((c, idx) => (
          <div
            key={idx}
            className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm"
          >
            <div className="flex items-center space-x-2 text-sm font-bold text-slate-900 dark:text-white mb-4">
              <span className="w-6 h-6 rounded-lg bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 flex items-center justify-center text-xs">
                #{idx + 1}
              </span>
              <span>Disputed Topic: {c.topic}</span>
            </div>

            {/* Side-by-side positions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              
              {/* Position A */}
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800/80">
                <div className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 mb-1.5 flex items-center justify-between">
                  <span>Position A</span>
                  <span className="font-mono text-slate-500">Page {c.source_a_page}</span>
                </div>
                <div className="text-xs sm:text-sm font-semibold text-slate-900 dark:text-slate-100 mb-2">
                  {c.position_a}
                </div>
                <div className="text-[11px] text-slate-500 dark:text-slate-400 mb-2">
                  📄 Source: <span className="font-medium text-slate-700 dark:text-slate-300">{c.source_a_paper}</span>
                </div>
                {c.source_a_quote && (
                  <div className="p-2.5 rounded-lg bg-indigo-50/50 dark:bg-indigo-950/20 border-l-2 border-indigo-500 text-xs text-slate-700 dark:text-slate-300 italic">
                    "{c.source_a_quote}"
                  </div>
                )}
              </div>

              {/* Position B */}
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800/80">
                <div className="text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400 mb-1.5 flex items-center justify-between">
                  <span>Position B</span>
                  <span className="font-mono text-slate-500">Page {c.source_b_page}</span>
                </div>
                <div className="text-xs sm:text-sm font-semibold text-slate-900 dark:text-slate-100 mb-2">
                  {c.position_b}
                </div>
                <div className="text-[11px] text-slate-500 dark:text-slate-400 mb-2">
                  📄 Source: <span className="font-medium text-slate-700 dark:text-slate-300">{c.source_b_paper}</span>
                </div>
                {c.source_b_quote && (
                  <div className="p-2.5 rounded-lg bg-amber-50/50 dark:bg-amber-950/20 border-l-2 border-amber-500 text-xs text-slate-700 dark:text-slate-300 italic">
                    "{c.source_b_quote}"
                  </div>
                )}
              </div>

            </div>

            {/* Methodological Divergence Explanation */}
            <div className="p-4 rounded-xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs leading-relaxed text-slate-800 dark:text-slate-200">
              <span className="font-bold text-slate-900 dark:text-white block mb-1">
                🔬 Scientific / Contextual Divergence Explanation:
              </span>
              {c.explanation_of_divergence}
            </div>

          </div>
        ))}
      </div>
    </div>
  );
}
