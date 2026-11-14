import React, { useState } from 'react';
import { FileText, Target, Cpu, TrendingUp, AlertTriangle, Compass, Calendar, User, ExternalLink } from 'lucide-react';

export default function IndividualPaperTab({ analyses = [] }) {
  const [selectedIdx, setSelectedIdx] = useState(0);

  if (!analyses || analyses.length === 0) {
    return (
      <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 text-slate-500">
        No individual paper profiles extracted.
      </div>
    );
  }

  const paper = analyses[selectedIdx] || analyses[0];
  const { metadata, objectives, methodology, results, limitations, future_work } = paper;

  return (
    <div className="space-y-6">
      {/* Paper Selector Dropdown */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <label className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-2">
          <FileText className="w-4 h-4 text-indigo-500" />
          <span>Select Paper to Inspect:</span>
        </label>
        <select
          value={selectedIdx}
          onChange={(e) => setSelectedIdx(Number(e.target.value))}
          className="px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-xs font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          {analyses.map((p, idx) => (
            <option key={idx} value={idx}>
              [{p.paper_id}] {p.metadata?.title || p.filename}
            </option>
          ))}
        </select>
      </div>

      {/* Section A: Paper Information Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2 leading-snug">
          {metadata?.title || paper.filename}
        </h2>
        
        <div className="flex flex-wrap gap-y-2 gap-x-4 text-xs text-slate-500 dark:text-slate-400 mb-4 pb-4 border-b border-slate-100 dark:border-slate-800">
          <span className="flex items-center space-x-1">
            <User className="w-3.5 h-3.5 text-indigo-500" />
            <span>{metadata?.authors?.join(', ') || 'Not found in paper'}</span>
          </span>
          <span className="flex items-center space-x-1">
            <Calendar className="w-3.5 h-3.5 text-indigo-500" />
            <span>Year: {metadata?.publication_year || 'Not found'}</span>
          </span>
          {metadata?.venue && metadata.venue !== 'Not found in paper' && (
            <span>&bull; {metadata.venue}</span>
          )}
          {metadata?.doi && metadata.doi !== 'Not found in paper' && (
            <span className="font-mono text-indigo-600 dark:text-indigo-400">&bull; DOI: {metadata.doi}</span>
          )}
        </div>

        {metadata?.keywords && metadata.keywords.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {metadata.keywords.map((kw, i) => (
              <span key={i} className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-[11px] font-medium text-slate-700 dark:text-slate-300">
                #{kw}
              </span>
            ))}
          </div>
        )}

        <div>
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Abstract</h4>
          <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
            {metadata?.abstract || 'Not found in paper'}
          </p>
        </div>
      </div>

      {/* Grid: Objectives & Methodology */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Section B: Objectives */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-4 pb-2 border-b border-slate-100 dark:border-slate-800">
            <Target className="w-4 h-4 text-indigo-500" />
            <span>Research Objectives & Problem</span>
          </h3>
          <div className="space-y-3 text-xs sm:text-sm">
            <div>
              <span className="font-semibold text-slate-800 dark:text-slate-200">Main Problem:</span>
              <p className="text-slate-600 dark:text-slate-400 mt-0.5">{objectives?.main_problem || 'Not found in paper'}</p>
            </div>
            {objectives?.objectives && objectives.objectives.length > 0 && (
              <div>
                <span className="font-semibold text-slate-800 dark:text-slate-200">Specific Objectives:</span>
                <ul className="list-disc list-inside space-y-1 text-slate-600 dark:text-slate-400 mt-1">
                  {objectives.objectives.map((o, i) => (
                    <li key={i}>{o}</li>
                  ))}
                </ul>
              </div>
            )}
            {objectives?.hypotheses && objectives.hypotheses.length > 0 && (
              <div>
                <span className="font-semibold text-slate-800 dark:text-slate-200">Hypotheses:</span>
                <ul className="list-disc list-inside space-y-1 text-slate-600 dark:text-slate-400 mt-1 italic">
                  {objectives.hypotheses.map((h, i) => (
                    <li key={i}>{h}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Section C: Methodology */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-4 pb-2 border-b border-slate-100 dark:border-slate-800">
            <Cpu className="w-4 h-4 text-indigo-500" />
            <span>Methodology & Experimental Design</span>
          </h3>
          <div className="space-y-2.5 text-xs sm:text-sm">
            <div>
              <span className="font-semibold text-slate-800 dark:text-slate-200">Design:</span>
              <span className="text-slate-600 dark:text-slate-400 ml-1.5">{methodology?.methodology || 'Not found in paper'}</span>
            </div>
            <div>
              <span className="font-semibold text-slate-800 dark:text-slate-200">Sample Size:</span>
              <span className="text-slate-600 dark:text-slate-400 ml-1.5 font-mono bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded">{methodology?.sample_size || 'N/A'}</span>
            </div>
            <div>
              <span className="font-semibold text-slate-800 dark:text-slate-200">Datasets:</span>
              <span className="text-slate-600 dark:text-slate-400 ml-1.5">{methodology?.datasets_used?.join(', ') || 'Empirical field data'}</span>
            </div>
            <div>
              <span className="font-semibold text-slate-800 dark:text-slate-200">Algorithms & Models:</span>
              <span className="text-slate-600 dark:text-slate-400 ml-1.5">{methodology?.algorithms_and_models?.join(', ') || 'Field instrumentation'}</span>
            </div>
            <div>
              <span className="font-semibold text-slate-800 dark:text-slate-200">Metrics:</span>
              <span className="text-slate-600 dark:text-slate-400 ml-1.5">{methodology?.evaluation_metrics?.join(', ') || 'Standard performance metrics'}</span>
            </div>
          </div>
        </div>

      </div>

      {/* Grid: Results & Limitations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Section D: Results */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-4 pb-2 border-b border-slate-100 dark:border-slate-800">
            <TrendingUp className="w-4 h-4 text-emerald-500" />
            <span>Major Findings & Numerical Results</span>
          </h3>
          
          {/* Numerical Results Badges */}
          {results?.numerical_results && results.numerical_results.length > 0 && (
            <div className="mb-4">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1.5">Quantified Findings:</span>
              <div className="flex flex-wrap gap-2">
                {results.numerical_results.map((num, i) => (
                  <span key={i} className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 font-bold text-xs border border-emerald-200 dark:border-emerald-800">
                    {num}
                  </span>
                ))}
              </div>
            </div>
          )}

          {results?.major_findings && results.major_findings.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Key Outcomes:</span>
              <ul className="space-y-1.5 text-xs text-slate-700 dark:text-slate-300">
                {results.major_findings.map((f, i) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-emerald-500 font-bold">&bull;</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {results?.authors_conclusions && (
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-400">
              <span className="font-semibold text-slate-800 dark:text-slate-200">Conclusion:</span> {results.authors_conclusions}
            </div>
          )}
        </div>

        {/* Section E: Limitations */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-4 pb-2 border-b border-slate-100 dark:border-slate-800">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            <span>Limitations & Weaknesses</span>
          </h3>
          <div className="space-y-3 text-xs">
            {limitations?.author_acknowledged && limitations.author_acknowledged.length > 0 ? (
              <div>
                <span className="font-semibold text-slate-800 dark:text-slate-200">Author-Acknowledged:</span>
                <ul className="space-y-1 text-slate-600 dark:text-slate-400 mt-1">
                  {limitations.author_acknowledged.map((lim, i) => (
                    <li key={i} className="flex items-start space-x-1.5">
                      <span className="text-amber-500 font-bold">&bull;</span>
                      <span>{lim}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <p className="text-slate-500 italic">No explicit limitations noted in document.</p>
            )}

            {limitations?.dataset_limitations && limitations.dataset_limitations.length > 0 && (
              <div>
                <span className="font-semibold text-slate-800 dark:text-slate-200">Dataset Constraints:</span>
                <p className="text-slate-600 dark:text-slate-400 mt-0.5">{limitations.dataset_limitations.join(', ')}</p>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Section F: Future Work */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-4 pb-2 border-b border-slate-100 dark:border-slate-800">
          <Compass className="w-4 h-4 text-cyan-500" />
          <span>Future Research Directions (Author Formulated)</span>
        </h3>
        {future_work?.future_directions && future_work.future_directions.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {future_work.future_directions.map((fd, i) => (
              <div key={i} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 flex items-start space-x-2">
                <span className="text-cyan-500 font-bold font-mono">0{i + 1}.</span>
                <span>{fd}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500 italic">Not explicitly mentioned in paper.</p>
        )}
      </div>

    </div>
  );
}
