import React, { useState } from 'react';
import { ShieldCheck, CheckCircle2, AlertTriangle, XCircle, AlertOctagon, Hash } from 'lucide-react';

export default function FactCheckerTab({ verifiedClaims = [], droppedClaims = [], onSelectEvidence }) {
  const [filter, setFilter] = useState('ALL');

  // Combine for audit inspection view
  const allAudited = [
    ...verifiedClaims.map((c) => ({
      claim_id: c.claim_id,
      claim: c.claim,
      status: 'Supported',
      reason: c.critic_reasoning || 'All assertions and numbers directly substantiated by source text.',
      evidence_ids: c.evidence_ids || [],
      cited_papers: c.cited_papers || [],
      cited_pages: c.cited_pages || [],
      is_exaggerated: false,
    })),
    ...droppedClaims.map((d) => ({
      claim_id: d.claim_id,
      claim: d.claim,
      status: d.status || 'Unsupported',
      reason: d.reason,
      evidence_ids: [],
      cited_papers: [],
      cited_pages: [],
      is_exaggerated: true,
    })),
  ];

  const filtered = allAudited.filter((item) => {
    if (filter === 'ALL') return true;
    if (filter === 'SUPPORTED') return item.status === 'Supported';
    if (filter === 'PARTIAL') return item.status.includes('Partially');
    if (filter === 'UNSUPPORTED') return item.status === 'Unsupported';
    if (filter === 'CONTRADICTED') return item.status === 'Contradicted';
    return true;
  });

  return (
    <div className="space-y-6">
      
      {/* Header & Filter Bar */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-indigo-500" />
            <span>Evidence-Based Fact-Check Critic Audit</span>
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Every candidate claim is verified against linked passages. Claims lacking evidence or overstating numbers are excluded from the final report.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          {[
            { id: 'ALL', label: `All (${allAudited.length})` },
            { id: 'SUPPORTED', label: `Supported (${verifiedClaims.length})`, color: 'emerald' },
            { id: 'UNSUPPORTED', label: `Rejected (${droppedClaims.length})`, color: 'rose' },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setFilter(f.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                filter === f.id
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Claims List */}
      <div className="space-y-4">
        {filtered.map((item, idx) => {
          const isSupported = item.status === 'Supported';
          const isPartial = item.status.includes('Partially');
          const isContra = item.status.includes('Contradicted');

          const badgeClasses = isSupported
            ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
            : isPartial
            ? 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-800'
            : 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border-rose-200 dark:border-rose-800';

          const icon = isSupported ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
          ) : isPartial ? (
            <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />
          ) : (
            <XCircle className="w-4 h-4 text-rose-500 shrink-0" />
          );

          return (
            <div
              key={idx}
              className={`p-5 rounded-2xl bg-white dark:bg-slate-900 border shadow-sm transition ${
                isSupported
                  ? 'border-slate-200 dark:border-slate-800'
                  : 'border-rose-200 dark:border-rose-950/80 bg-rose-50/10'
              }`}
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex items-start space-x-2.5">
                  <div className="mt-0.5">{icon}</div>
                  <div>
                    <span className="font-mono text-xs font-bold text-slate-400 mr-2">[{item.claim_id}]</span>
                    <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">{item.claim}</span>
                  </div>
                </div>

                <span className={`px-2.5 py-1 rounded-lg text-xs font-bold border shrink-0 ${badgeClasses}`}>
                  {item.status}
                </span>
              </div>

              {/* Critic Reasoning */}
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800/80 text-xs text-slate-700 dark:text-slate-300 leading-relaxed mb-3">
                <span className="font-semibold text-slate-900 dark:text-white mr-1.5">Critic Verification Note:</span>
                {item.reason}
              </div>

              {/* Citations & Evidence Pills */}
              <div className="flex flex-wrap items-center gap-2 text-xs">
                {item.evidence_ids && item.evidence_ids.length > 0 ? (
                  <>
                    <span className="text-slate-500 font-semibold">Evidence Passages:</span>
                    {item.evidence_ids.map((eid) => (
                      <button
                        key={eid}
                        onClick={() => onSelectEvidence(eid)}
                        className="px-2 py-0.5 rounded-md bg-indigo-100 hover:bg-indigo-200 dark:bg-indigo-950 dark:hover:bg-indigo-900 text-indigo-700 dark:text-indigo-300 font-bold border border-indigo-200 dark:border-indigo-800 transition"
                      >
                        [{eid}]
                      </button>
                    ))}
                    {item.cited_papers && item.cited_papers.length > 0 && (
                      <span className="text-slate-500 ml-2">
                        {item.cited_papers.join(', ')} {item.cited_pages && item.cited_pages.length > 0 ? `(p. ${item.cited_pages.join(', ')})` : ''}
                      </span>
                    )}
                  </>
                ) : (
                  <span className="text-rose-500 font-semibold italic text-xs">
                    Excluded from Literature Review: Lacks valid retrieved evidence passage grounding.
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}
