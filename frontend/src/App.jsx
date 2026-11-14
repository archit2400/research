import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import UploadSection from './components/UploadSection';
import QuestionInput from './components/QuestionInput';
import ProgressTracker from './components/ProgressTracker';
import EvidenceModal from './components/EvidenceModal';

import LiteratureReviewTab from './components/tabs/LiteratureReviewTab';
import IndividualPaperTab from './components/tabs/IndividualPaperTab';
import PaperComparisonTab from './components/tabs/PaperComparisonTab';
import FactCheckerTab from './components/tabs/FactCheckerTab';
import ContradictionTab from './components/tabs/ContradictionTab';
import ResearchGapsTab from './components/tabs/ResearchGapsTab';
import EvidenceExplorerTab from './components/tabs/EvidenceExplorerTab';
import ExportReportTab from './components/tabs/ExportReportTab';

import {
  checkHealth,
  uploadPapers,
  loadSamplePapers,
  startResearch,
  getSessionStatus,
  getReport,
} from './services/api';

import {
  BookOpen,
  FileText,
  Columns,
  ShieldCheck,
  Scale,
  Telescope,
  Database,
  Download,
} from 'lucide-react';

const TABS = [
  { id: 'lit_review', label: '1. Literature Review', icon: BookOpen },
  { id: 'individual', label: '2. Paper Analysis', icon: FileText },
  { id: 'comparison', label: '3. Comparison Matrix', icon: Columns },
  { id: 'fact_check', label: '4. Fact Checker', icon: ShieldCheck },
  { id: 'contradiction', label: '5. Contradictions', icon: Scale },
  { id: 'gaps', label: '6. Research Gaps', icon: Telescope },
  { id: 'evidence', label: '7. Evidence Explorer', icon: Database },
  { id: 'export', label: '8. Export Report', icon: Download },
];

export default function App() {
  const [isDark, setIsDark] = useState(true);
  const [serverInfo, setServerInfo] = useState(null);

  // Session State
  const [sessionId, setSessionId] = useState(null);
  const [papers, setPapers] = useState([]);
  const [question, setQuestion] = useState('');

  // Pipeline execution state
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState(null);
  const [isLoadingSample, setIsLoadingSample] = useState(false);

  // Result state
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('lit_review');

  // Evidence modal state
  const [inspectedEvidence, setInspectedEvidence] = useState(null);

  // Apply dark mode class to html
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  // Check backend health on mount
  useEffect(() => {
    checkHealth()
      .then((data) => setServerInfo(data))
      .catch((err) => console.warn('Backend not yet reachable:', err));
  }, []);

  // Poll status while running
  useEffect(() => {
    let interval = null;
    if (isRunning && sessionId) {
      interval = setInterval(async () => {
        try {
          const statusData = await getSessionStatus(sessionId);
          setProgress(statusData.progress);
          setStatusMessage(statusData.status_message);

          if (statusData.status === 'completed') {
            setIsRunning(false);
            clearInterval(interval);
            const reportData = await getReport(sessionId);
            setResult(reportData);
          } else if (statusData.status === 'error') {
            setIsRunning(false);
            clearInterval(interval);
            setError(statusData.error || 'Pipeline execution failed.');
          }
        } catch (e) {
          console.error('Polling error:', e);
        }
      }, 1500);
    }
    return () => clearInterval(interval);
  }, [isRunning, sessionId]);

  // Handle PDF Uploads
  const handleUpload = async (fileList) => {
    try {
      setError(null);
      const res = await uploadPapers(fileList, sessionId);
      setSessionId(res.session_id);
      setPapers((prev) => [
        ...prev,
        ...fileList.map((f) => ({ name: f.name, size: f.size })),
      ]);
    } catch (err) {
      setError('Failed to upload papers: ' + err.message);
    }
  };

  // Remove a paper
  const handleRemovePaper = (index) => {
    setPapers((prev) => prev.filter((_, i) => i !== index));
  };

  // Load sample benchmark papers
  const handleLoadSample = async () => {
    try {
      setIsLoadingSample(true);
      setError(null);
      const res = await loadSamplePapers();
      setSessionId(res.session_id);
      setPapers(res.paper_names.map((name) => ({ name })));
    } catch (err) {
      setError('Failed to load sample benchmark papers: ' + err.message);
    } finally {
      setIsLoadingSample(false);
    }
  };

  // Start research pipeline
  const handleStartResearch = async () => {
    if (!sessionId || papers.length === 0) {
      setError('Please upload at least one PDF paper before starting research.');
      return;
    }
    if (!question.trim()) {
      setError('Please enter a research question.');
      return;
    }

    try {
      setError(null);
      setIsRunning(true);
      setProgress(5);
      setStatusMessage('Initializing multi-agent pipeline...');
      setResult(null);

      await startResearch(sessionId, question.trim());
    } catch (err) {
      setIsRunning(false);
      setError('Failed to start research: ' + err.message);
    }
  };

  // Reset session
  const handleReset = () => {
    setSessionId(null);
    setPapers([]);
    setResult(null);
    setIsRunning(false);
    setProgress(0);
    setStatusMessage('');
    setError(null);
  };

  // Open evidence inspector modal for an evidence ID
  const handleSelectEvidence = (evidenceId) => {
    if (!result?.sources_and_evidence) return;
    const ep = result.sources_and_evidence.find((e) => e.evidence_id === evidenceId);
    if (ep) {
      setInspectedEvidence(ep);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors">
      
      {/* Navigation */}
      <Navbar
        isDark={isDark}
        setIsDark={setIsDark}
        onReset={handleReset}
        serverInfo={serverInfo}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Error Notification */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-200 text-xs font-semibold flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="underline ml-4">
              Dismiss
            </button>
          </div>
        )}

        {/* Input & Upload Stage (Shown when no result or running) */}
        <div className="space-y-6 mb-8">
          <UploadSection
            papers={papers}
            onUpload={handleUpload}
            onRemovePaper={handleRemovePaper}
            onLoadSample={handleLoadSample}
            isLoadingSample={isLoadingSample}
          />

          <QuestionInput
            question={question}
            setQuestion={setQuestion}
            onStart={handleStartResearch}
            isRunning={isRunning}
            hasPapers={papers.length > 0}
          />
        </div>

        {/* Progress Tracker (Shown during execution or upon completion) */}
        {(isRunning || progress > 0) && (
          <ProgressTracker
            progress={progress}
            statusMessage={statusMessage}
            error={error}
          />
        )}

        {/* Results Dashboard */}
        {result && (
          <div className="space-y-6 animate-fade-in">
            
            {/* KPI Metric Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center shadow-sm">
                <div className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
                  {result.individual_paper_analyses?.length || 0}
                </div>
                <div className="text-[10px] font-semibold uppercase text-slate-500 mt-0.5">Papers Profiled</div>
              </div>
              <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center shadow-sm">
                <div className="text-xl font-bold text-purple-600 dark:text-purple-400">
                  {result.sources_and_evidence?.length || 0}
                </div>
                <div className="text-[10px] font-semibold uppercase text-slate-500 mt-0.5">Evidence Passages</div>
              </div>
              <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center shadow-sm">
                <div className="text-xl font-bold text-emerald-500">
                  {result.verified_claims?.length || 0}
                </div>
                <div className="text-[10px] font-semibold uppercase text-slate-500 mt-0.5">Verified Claims</div>
              </div>
              <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center shadow-sm">
                <div className="text-xl font-bold text-rose-500">
                  {result.dropped_claims?.length || 0}
                </div>
                <div className="text-[10px] font-semibold uppercase text-slate-500 mt-0.5">Rejected Claims</div>
              </div>
              <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center shadow-sm">
                <div className="text-xl font-bold text-amber-500">
                  {result.contradiction_analysis?.length || 0}
                </div>
                <div className="text-[10px] font-semibold uppercase text-slate-500 mt-0.5">Contradictions</div>
              </div>
              <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center shadow-sm">
                <div className="text-xl font-bold text-cyan-500">
                  {(result.research_gaps?.explicitly_acknowledged_gaps?.length || 0) +
                    (result.research_gaps?.ai_inferred_gaps?.length || 0)}
                </div>
                <div className="text-[10px] font-semibold uppercase text-slate-500 mt-0.5">Research Gaps</div>
              </div>
            </div>

            {/* Tab Navigation Navigation Bar */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-2 shadow-sm overflow-x-auto">
              <div className="flex space-x-1 min-w-max">
                {TABS.map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold transition ${
                        isActive
                          ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-500/20'
                          : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{tab.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Tab Content Display */}
            <div className="min-h-[400px]">
              {activeTab === 'lit_review' && (
                <LiteratureReviewTab
                  review={result.literature_review}
                  subQueries={result.sub_queries}
                  onSelectEvidence={handleSelectEvidence}
                />
              )}

              {activeTab === 'individual' && (
                <IndividualPaperTab analyses={result.individual_paper_analyses} />
              )}

              {activeTab === 'comparison' && (
                <PaperComparisonTab comparison={result.cross_paper_comparison} />
              )}

              {activeTab === 'fact_check' && (
                <FactCheckerTab
                  verifiedClaims={result.verified_claims}
                  droppedClaims={result.dropped_claims}
                  onSelectEvidence={handleSelectEvidence}
                />
              )}

              {activeTab === 'contradiction' && (
                <ContradictionTab contradictions={result.contradiction_analysis} />
              )}

              {activeTab === 'gaps' && (
                <ResearchGapsTab gaps={result.research_gaps} />
              )}

              {activeTab === 'evidence' && (
                <EvidenceExplorerTab
                  passages={result.sources_and_evidence}
                  onSelectEvidence={handleSelectEvidence}
                />
              )}

              {activeTab === 'export' && (
                <ExportReportTab sessionId={result.session_id} result={result} />
              )}
            </div>

          </div>
        )}

      </main>

      {/* Slide-Over Evidence Inspector Modal */}
      <EvidenceModal
        evidence={inspectedEvidence}
        onClose={() => setInspectedEvidence(null)}
        allClaims={result?.verified_claims || []}
      />

    </div>
  );
}
