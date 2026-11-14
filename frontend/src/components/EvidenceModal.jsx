import React from 'react';
import { X, BookOpen, FileText, CheckCircle, Award } from 'lucide-react';

export default function EvidenceModal({ evidence, onClose, allClaims = [] }) {
  if (!evidence) return null;

  // Find claims that cite this evidence passage
  const relatedClaims = allClaims.filter(
    (c) => c.evidence_ids && c.evidence_ids.includes(evidence.evidence_id)
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto shadow-2xl p-6 relative">
        
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-950/80 border border-indigo-100 dark:border-indigo-900 flex items-center justify-center text-indigo-600 dark:text-indigo-400 font-bold text-sm">
            {evidence.evidence_id}
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Evidence Passage Inspector
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center space-x-1.5">
              <FileText className="w-3.5 h-3.5" />
              <span>{evidence.paper_name} &bull; Page {evidence.page_number}</span>
            </p>
          </div>
        </div>

        {/* Metadata Badges */}
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="px-2.5 py-1 text-xs font-semibold rounded-md bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
            Relevance Score: {(evidence.relevance_score * 100).toFixed(0)}%
          </span>
          <span className="px-2.5 py-1 text-xs font-semibold rounded-md bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
            Source: {evidence.paper_name}
          </span>
        </div>

        {/* Verbatim Excerpt */}
        <div className="mb-5">
          <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1.5">
            Verbatim Passage Extracted from Paper:
          </label>
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-sm leading-relaxed text-slate-800 dark:text-slate-200 font-mono italic">
            "{evidence.text}"
          </div>
        </div>

        {/* Claims citing this passage */}
        {relatedClaims.length > 0 && (
          <div>
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-2">
              Claims Grounded by this Evidence ({relatedClaims.length}):
            </label>
            <div className="space-y-2">
              {relatedClaims.map((c, i) => (
                <div
                  key={i}
                  className="p-3 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800/60 flex items-start space-x-2"
                >
                  <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                  <div className="text-xs text-slate-800 dark:text-slate-200">
                    <span className="font-semibold text-emerald-700 dark:text-emerald-300">[{c.claim_id}]</span> {c.claim}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 transition"
          >
            Close Inspector
          </button>
        </div>

      </div>
    </div>
  );
}
