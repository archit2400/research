import React from 'react';
import { Telescope, HelpCircle, AlertCircle, Compass, FileText, Lightbulb } from 'lucide-react';

export default function ResearchGapsTab({ gaps }) {
  if (!gaps) {
    return (
      <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 text-slate-500">
        No research gap analysis available.
      </div>
    );
  }

  const {
    under_explored_topics = [],
    unanswered_research_questions = [],
    common_limitations_across_studies = [],
    explicitly_acknowledged_gaps = [],
    ai_inferred_gaps = [],
    future_research_directions = [],
  } = gaps;

  return (
    <div className="space-y-6">
      
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Under-explored Topics */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center space-x-1.5 mb-3">
            <Telescope className="w-4 h-4 text-cyan-500" />
            <span>Under-Explored Domains</span>
          </h4>
          <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
            {under_explored_topics.map((t, i) => (
              <li key={i} className="flex items-start space-x-2">
                <span className="text-cyan-500 font-bold">&bull;</span>
                <span>{t}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Common Limitations */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center space-x-1.5 mb-3">
            <AlertCircle className="w-4 h-4 text-amber-500" />
            <span>Common Limitations</span>
          </h4>
          <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
            {common_limitations_across_studies.map((lim, i) => (
              <li key={i} className="flex items-start space-x-2">
                <span className="text-amber-500 font-bold">&bull;</span>
                <span>{lim}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Unanswered Questions */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center space-x-1.5 mb-3">
            <HelpCircle className="w-4 h-4 text-purple-500" />
            <span>Unanswered Questions</span>
          </h4>
          <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
            {unanswered_research_questions.map((q, i) => (
              <li key={i} className="flex items-start space-x-2">
                <span className="text-purple-500 font-bold">?</span>
                <span className="font-medium">{q}</span>
              </li>
            ))}
          </ul>
        </div>

      </div>

      {/* Explicit vs AI-Inferred Gaps */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Explicitly Acknowledged Gaps */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-2">
            <FileText className="w-4 h-4 text-indigo-500" />
            <span>Explicitly Acknowledged Gaps (Original Authors)</span>
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            Research gaps specifically recognized by paper authors in their original texts.
          </p>

          <div className="space-y-3">
            {explicitly_acknowledged_gaps.map((eg, i) => (
              <div key={i} className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                <h5 className="text-xs font-bold text-indigo-600 dark:text-indigo-400 mb-1">{eg.topic}</h5>
                <p className="text-xs text-slate-700 dark:text-slate-300 mb-2 leading-relaxed">{eg.description}</p>
                {eg.source_papers && eg.source_papers.length > 0 && (
                  <span className="text-[11px] text-slate-500 font-mono">
                    Cited In: {eg.source_papers.join(', ')}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* AI-Inferred Gaps */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-2">
            <Lightbulb className="w-4 h-4 text-purple-500" />
            <span>AI-Inferred Potential Research Gaps</span>
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            Structural blind spots synthesized by meta-analytically comparing multiple papers.
          </p>

          <div className="space-y-3">
            {ai_inferred_gaps.map((ig, i) => (
              <div key={i} className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                <h5 className="text-xs font-bold text-purple-600 dark:text-purple-400 mb-1">{ig.topic}</h5>
                <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">{ig.description}</p>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Actionable Future Horizons */}
      {future_research_directions.length > 0 && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-4">
            <Compass className="w-4 h-4 text-emerald-500" />
            <span>Actionable Future Research Directions</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {future_research_directions.map((fd, i) => (
              <div key={i} className="p-3.5 rounded-xl bg-emerald-50/30 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/50 text-xs text-slate-800 dark:text-slate-200 flex items-start space-x-2">
                <span className="font-bold text-emerald-600 dark:text-emerald-400">0{i + 1}.</span>
                <span>{fd}</span>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
