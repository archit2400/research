import React from 'react';
import { Search, Play } from 'lucide-react';

export default function QuestionInput({
  question,
  setQuestion,
  onStart,
  isRunning,
  hasPapers,
}) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <label className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2">
          <Search className="w-4 h-4 text-indigo-500" />
          <span>Research Question / Synthesis Topic</span>
        </label>
      </div>

      <div className="space-y-4">
        <div className="relative">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Enter your research question or synthesis topic..."
            className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
          />
        </div>

        {/* Action Button */}
        <div className="flex justify-end">
          <button
            type="button"
            onClick={onStart}
            disabled={isRunning || !hasPapers || !question.trim()}
            className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-bold text-sm shadow-md transition ${
              isRunning || !hasPapers || !question.trim()
                ? 'bg-slate-200 text-slate-400 dark:bg-slate-800 dark:text-slate-600 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-500/25 active:scale-95'
            }`}
          >
            <Play className={`w-4 h-4 ${isRunning ? 'animate-spin' : ''}`} />
            <span>{isRunning ? 'Multi-Agent Pipeline Running...' : 'Launch Academic Intelligence Pipeline'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
