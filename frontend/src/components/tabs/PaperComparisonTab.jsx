import React from 'react';
import { Columns, CheckCircle2, AlertOctagon, GitCompare, Info } from 'lucide-react';

export default function PaperComparisonTab({ comparison }) {
  if (!comparison || !comparison.matrix || comparison.matrix.length === 0) {
    return (
      <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 text-slate-500">
        Cross-paper comparison requires at least 2 papers in the corpus.
      </div>
    );
  }

  const { matrix, common_findings, different_approaches, areas_of_agreement, areas_of_disagreement, comparative_summary } = comparison;

  return (
    <div className="space-y-6">
      
      {/* Comparative Synthesis Narrative */}
      {comparative_summary && (
        <div className="bg-indigo-50/60 dark:bg-indigo-950/20 border border-indigo-200 dark:border-indigo-800/80 rounded-2xl p-5">
          <h3 className="text-sm font-bold text-indigo-900 dark:text-indigo-300 flex items-center space-x-2 mb-2">
            <Info className="w-4 h-4 text-indigo-500" />
            <span>Comparative Meta-Synthesis</span>
          </h3>
          <p className="text-xs sm:text-sm text-indigo-800 dark:text-indigo-200 leading-relaxed">
            {comparative_summary}
          </p>
        </div>
      )}

      {/* Comparison Matrix Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm overflow-hidden">
        <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-4">
          <Columns className="w-4 h-4 text-indigo-500" />
          <span>Cross-Paper Comparative Matrix</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60 text-slate-600 dark:text-slate-300 font-bold uppercase tracking-wider">
                <th className="p-3 w-44">Paper Title</th>
                <th className="p-3 min-w-[180px]">Objectives & Problem</th>
                <th className="p-3 min-w-[180px]">Methodology</th>
                <th className="p-3 min-w-[180px]">Datasets & Settings</th>
                <th className="p-3 min-w-[200px]">Results & Conclusions</th>
                <th className="p-3 min-w-[160px]">Strengths & Weaknesses</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {matrix.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition">
                  <td className="p-3 font-semibold text-slate-900 dark:text-white align-top">
                    {row.paper_title}
                  </td>
                  <td className="p-3 text-slate-600 dark:text-slate-400 align-top leading-relaxed">
                    {row.objectives}
                  </td>
                  <td className="p-3 text-slate-600 dark:text-slate-400 align-top leading-relaxed">
                    {row.methodologies}
                  </td>
                  <td className="p-3 text-slate-600 dark:text-slate-400 align-top leading-relaxed font-mono text-[11px]">
                    {row.datasets_and_settings}
                  </td>
                  <td className="p-3 text-slate-700 dark:text-slate-300 align-top leading-relaxed font-medium">
                    {row.results_and_conclusions}
                  </td>
                  <td className="p-3 text-slate-500 dark:text-slate-400 align-top leading-relaxed text-[11px]">
                    {row.strengths_and_weaknesses}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Convergences & Divergences Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Common Findings & Agreements */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-4 pb-2 border-b border-slate-100 dark:border-slate-800">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <span>Shared Findings & Consensus Points</span>
          </h3>
          <div className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
            {common_findings && common_findings.map((cf, i) => (
              <div key={i} className="p-2.5 rounded-xl bg-emerald-50/40 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40 flex items-start space-x-2">
                <span className="text-emerald-500 font-bold">&bull;</span>
                <span>{cf}</span>
              </div>
            ))}
            {areas_of_agreement && areas_of_agreement.map((agr, i) => (
              <div key={i} className="p-2.5 rounded-xl bg-emerald-50/40 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40 flex items-start space-x-2">
                <span className="text-emerald-500 font-bold">&bull;</span>
                <span>{agr}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Disagreements & Methodological Divergences */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-4 pb-2 border-b border-slate-100 dark:border-slate-800">
            <AlertOctagon className="w-4 h-4 text-amber-500" />
            <span>Methodological & Empirical Divergences</span>
          </h3>
          <div className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
            {different_approaches && different_approaches.map((appr, i) => (
              <div key={i} className="p-2.5 rounded-xl bg-amber-50/40 dark:bg-amber-950/20 border border-amber-100 dark:border-amber-900/40 flex items-start space-x-2">
                <span className="text-amber-500 font-bold">&bull;</span>
                <span>{appr}</span>
              </div>
            ))}
            {areas_of_disagreement && areas_of_disagreement.map((dis, i) => (
              <div key={i} className="p-2.5 rounded-xl bg-amber-50/40 dark:bg-amber-950/20 border border-amber-100 dark:border-amber-900/40 flex items-start space-x-2">
                <span className="text-amber-500 font-bold">&bull;</span>
                <span>{dis}</span>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
