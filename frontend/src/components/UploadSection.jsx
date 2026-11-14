import React, { useRef } from 'react';
import { UploadCloud, FileText, Trash2, Sparkles, CheckCircle2 } from 'lucide-react';

export default function UploadSection({
  papers,
  onUpload,
  onRemovePaper,
  onLoadSample,
  isLoadingSample,
}) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onUpload(Array.from(e.target.files));
      e.target.value = '';
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const pdfs = Array.from(e.dataTransfer.files).filter((f) =>
        f.name.toLowerCase().endsWith('.pdf')
      );
      if (pdfs.length > 0) {
        onUpload(pdfs);
      }
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-5">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center space-x-2">
            <span>📄 Research Corpus Documents</span>
            {papers.length > 0 && (
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                {papers.length} {papers.length === 1 ? 'Paper' : 'Papers'} Loaded
              </span>
            )}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Upload PDF research papers. Isolated vector storage is created specifically for your session.
          </p>
        </div>

        <button
          type="button"
          onClick={onLoadSample}
          disabled={isLoadingSample}
          className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 hover:from-indigo-500/20 hover:to-pink-500/20 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 text-xs font-semibold transition shadow-sm"
        >
          <Sparkles className="w-4 h-4 text-indigo-500" />
          <span>{isLoadingSample ? 'Loading Benchmark...' : 'Load Benchmark Papers'}</span>
        </button>
      </div>

      {/* Drag & Drop Box */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-indigo-500 dark:hover:border-indigo-500 rounded-xl p-8 text-center cursor-pointer bg-slate-50/50 dark:bg-slate-950/40 transition group"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          multiple
          className="hidden"
          onChange={handleFileChange}
        />
        <div className="w-12 h-12 rounded-full bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-100 dark:border-indigo-900 flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition text-indigo-600 dark:text-indigo-400">
          <UploadCloud className="w-6 h-6" />
        </div>
        <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
          Click to upload or drag & drop research papers
        </p>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          PDF format supported (text-extracted & page-indexed via PyMuPDF)
        </p>
      </div>

      {/* Uploaded Papers List */}
      {papers.length > 0 && (
        <div className="mt-5 space-y-2">
          <div className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider mb-2">
            Uploaded Papers ({papers.length})
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
            {papers.map((p, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 rounded-xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80 group hover:border-slate-300 dark:hover:border-slate-600 transition"
              >
                <div className="flex items-center space-x-2.5 overflow-hidden">
                  <FileText className="w-4 h-4 text-indigo-500 shrink-0" />
                  <span className="text-xs font-medium text-slate-800 dark:text-slate-200 truncate" title={p.name}>
                    {p.name}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemovePaper(idx);
                  }}
                  className="p-1 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition shrink-0 ml-2"
                  title="Remove paper"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
