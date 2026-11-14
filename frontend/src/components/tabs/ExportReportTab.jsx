import React from 'react';
import { Download, FileDown, Code, CheckCircle, FileText } from 'lucide-react';
import { getExportMarkdownUrl, getExportJsonUrl } from '../../services/api';

export default function ExportReportTab({ sessionId, result }) {
  if (!result) return null;

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-2">
          <Download className="w-5 h-5 text-indigo-500" />
          <span>Export Research Intelligence Report</span>
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-6">
          Download the comprehensive research synthesis including claim-level citations, verified evidence passages, dropped claims audit, contradictions, and research gaps.
        </p>

        {/* Download Buttons */}
        <div className="flex flex-wrap gap-4">
          <a
            href={getExportMarkdownUrl(sessionId)}
            download={`researchpilot_${sessionId}.md`}
            className="flex items-center space-x-2 px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-md shadow-indigo-500/20 transition"
          >
            <FileDown className="w-4 h-4" />
            <span>Download Academic Markdown (.md)</span>
          </a>

          <a
            href={getExportJsonUrl(sessionId)}
            download={`researchpilot_${sessionId}.json`}
            className="flex items-center space-x-2 px-5 py-3 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold text-xs border border-slate-300 dark:border-slate-700 transition"
          >
            <Code className="w-4 h-4" />
            <span>Download Structured JSON (.json)</span>
          </a>
        </div>
      </div>

      {/* Summary Stats Overview */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center">
          <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
            {result.individual_paper_analyses?.length || 0}
          </div>
          <div className="text-[11px] font-semibold uppercase text-slate-500 mt-1">Papers Profiled</div>
        </div>
        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center">
          <div className="text-2xl font-bold text-emerald-500">
            {result.verified_claims?.length || 0}
          </div>
          <div className="text-[11px] font-semibold uppercase text-slate-500 mt-1">Verified Claims</div>
        </div>
        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center">
          <div className="text-2xl font-bold text-rose-500">
            {result.dropped_claims?.length || 0}
          </div>
          <div className="text-[11px] font-semibold uppercase text-slate-500 mt-1">Dropped Claims</div>
        </div>
        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center">
          <div className="text-2xl font-bold text-amber-500">
            {result.contradiction_analysis?.length || 0}
          </div>
          <div className="text-[11px] font-semibold uppercase text-slate-500 mt-1">Contradictions</div>
        </div>
      </div>

      {/* Epistemological Banner */}
      <div className="p-4 rounded-xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 text-xs text-amber-800 dark:text-amber-200 leading-relaxed">
        <span className="font-bold">⚠️ Epistemological Guarantee:</span> {result.disclaimer}
      </div>
    </div>
  );
}
