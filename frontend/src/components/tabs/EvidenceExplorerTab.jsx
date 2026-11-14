import React, { useState } from 'react';
import { Database, Search, FileText, ExternalLink } from 'lucide-react';

export default function EvidenceExplorerTab({ passages = [], onSelectEvidence }) {
  const [search, setSearch] = useState('');

  const filtered = passages.filter((p) => {
    if (!search) return true;
    const term = search.toLowerCase();
    return (
      p.evidence_id?.toLowerCase().includes(term) ||
      p.paper_name?.toLowerCase().includes(term) ||
      p.text?.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6">
      
      {/* Search Bar */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
            <Database className="w-5 h-5 text-indigo-500" />
            <span>Retrieved Sources & Evidence Passages ({passages.length})</span>
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Exact textual evidence passages extracted by the RAG Retrieval Agent with unique evidence IDs and page provenance.
          </p>
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search passage text or ID..."
            className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Evidence Cards */}
      <div className="space-y-4">
        {filtered.map((ep) => (
          <div
            key={ep.evidence_id}
            className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:border-indigo-300 dark:hover:border-indigo-900 transition"
          >
            <div className="flex items-center justify-between gap-3 mb-3">
              <div className="flex items-center space-x-2.5">
                <span className="px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 font-bold text-xs font-mono border border-indigo-200 dark:border-indigo-800">
                  {ep.evidence_id}
                </span>
                <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 flex items-center space-x-1.5">
                  <FileText className="w-3.5 h-3.5 text-indigo-500" />
                  <span>{ep.paper_name} &bull; Page {ep.page_number}</span>
                </span>
              </div>

              <div className="flex items-center space-x-2">
                <span className="text-[11px] font-semibold text-slate-500">
                  Relevance: {(ep.relevance_score * 100).toFixed(0)}%
                </span>
                <button
                  onClick={() => onSelectEvidence(ep.evidence_id)}
                  className="p-1 rounded-lg text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/60 transition"
                  title="Inspect in full modal"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800/80 text-xs text-slate-700 dark:text-slate-300 font-mono leading-relaxed italic">
              "{ep.text}"
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}
