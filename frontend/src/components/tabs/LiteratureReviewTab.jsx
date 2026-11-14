import React, { useState } from 'react';
import { BookOpen, Tag, ChevronDown, ChevronUp, Quote, Search } from 'lucide-react';

export default function LiteratureReviewTab({ review, subQueries = [], onSelectEvidence }) {
  const [showQueries, setShowQueries] = useState(false);
  const [expandedQuotes, setExpandedQuotes] = useState({});

  const toggleQuote = (claimId) => {
    setExpandedQuotes((prev) => ({ ...prev, [claimId]: !prev[claimId] }));
  };

  return (
    <div className="space-y-6">
      {/* Sub-Queries Expander */}
      {subQueries.length > 0 && (
        <div className="bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-xl p-4">
          <button
            onClick={() => setShowQueries(!showQueries)}
            className="flex items-center justify-between w-full text-left font-semibold text-xs text-slate-700 dark:text-slate-300"
          >
            <span className="flex items-center space-x-2">
              <Search className="w-3.5 h-3.5 text-indigo-500" />
              <span>Query Agent: Formulated Search Sub-Queries ({subQueries.length})</span>
            </span>
            {showQueries ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          {showQueries && (
            <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-800 space-y-1.5">
              {subQueries.map((q, i) => (
                <div key={i} className="text-xs text-slate-600 dark:text-slate-400 font-mono bg-white dark:bg-slate-950 p-2 rounded-lg border border-slate-200 dark:border-slate-800">
                  <span className="text-indigo-500 font-bold mr-2">Q{i + 1}:</span> {q}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Thematic Review Sections */}
      {review?.themes && review.themes.length > 0 ? (
        review.themes.map((themeBlock, tIdx) => (
          <div
            key={tIdx}
            className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm"
          >
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2.5 mb-4 border-b border-slate-100 dark:border-slate-800 pb-3">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
              <span>{themeBlock.theme}</span>
            </h3>

            <div className="space-y-4">
              {themeBlock.claims && themeBlock.claims.map((c) => {
                const isExplicit = c.statement_type !== 'ai_inferred';
                return (
                  <div
                    key={c.claim_id}
                    className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/80 hover:border-indigo-300 dark:hover:border-indigo-900/60 transition"
                  >
                    <div className="text-sm font-medium text-slate-900 dark:text-slate-100 leading-relaxed mb-3">
                      {c.claim}
                    </div>

                    <div className="flex flex-wrap items-center gap-2 text-xs">
                      {/* Evidence ID pills */}
                      {c.evidence_ids && c.evidence_ids.map((eid) => (
                        <button
                          key={eid}
                          onClick={() => onSelectEvidence(eid)}
                          className="px-2 py-0.5 rounded-md bg-indigo-100 hover:bg-indigo-200 dark:bg-indigo-950 dark:hover:bg-indigo-900 text-indigo-700 dark:text-indigo-300 font-bold border border-indigo-200 dark:border-indigo-800 transition"
                          title="Click to inspect supporting passage"
                        >
                          [{eid}]
                        </button>
                      ))}

                      {/* Statement Type Badge */}
                      <span className={`px-2 py-0.5 rounded-md font-semibold text-[11px] ${
                        isExplicit
                          ? 'bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300 border border-blue-200 dark:border-blue-800'
                          : 'bg-purple-50 text-purple-700 dark:bg-purple-950/60 dark:text-purple-300 border border-purple-200 dark:border-purple-800'
                      }`}>
                        {isExplicit ? 'Explicitly Stated' : 'AI-Inferred'}
                      </span>

                      {/* Source Papers */}
                      {c.cited_papers && c.cited_papers.length > 0 && (
                        <span className="text-slate-500 dark:text-slate-400 text-xs">
                          &bull; {c.cited_papers.join(', ')} {c.cited_pages && c.cited_pages.length > 0 ? `(p. ${c.cited_pages.join(', ')})` : ''}
                        </span>
                      )}

                      {/* Quote dropdown toggle */}
                      {c.evidence_quotes && c.evidence_quotes.length > 0 && (
                        <button
                          onClick={() => toggleQuote(c.claim_id)}
                          className="ml-auto text-xs font-semibold text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 flex items-center space-x-1"
                        >
                          <Quote className="w-3 h-3" />
                          <span>{expandedQuotes[c.claim_id] ? 'Hide Quote' : 'View Quote'}</span>
                        </button>
                      )}
                    </div>

                    {/* Verbatim Quote Box */}
                    {expandedQuotes[c.claim_id] && c.evidence_quotes && c.evidence_quotes.length > 0 && (
                      <div className="mt-3 p-3 rounded-lg bg-indigo-50/50 dark:bg-indigo-950/30 border-l-4 border-indigo-500 text-xs text-slate-700 dark:text-slate-300 italic">
                        "{c.evidence_quotes[0]}"
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))
      ) : (
        <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 text-slate-500">
          No literature review claims generated yet.
        </div>
      )}
    </div>
  );
}
