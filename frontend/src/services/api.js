/**
 * API client communicating with FastAPI backend.
 */

const API_BASE = '/api';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function uploadPapers(files, sessionId = null) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  if (sessionId) {
    formData.append('session_id', sessionId);
  }

  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to upload PDF papers');
  return res.json();
}

export async function loadSamplePapers() {
  const res = await fetch(`${API_BASE}/load-sample`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to load sample papers');
  return res.json();
}

export async function startResearch(sessionId, question) {
  const res = await fetch(`${API_BASE}/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, question }),
  });
  if (!res.ok) throw new Error('Failed to initiate research pipeline');
  return res.json();
}

export async function getSessionStatus(sessionId) {
  const res = await fetch(`${API_BASE}/session/${sessionId}/status`);
  if (!res.ok) throw new Error('Failed to poll status');
  return res.json();
}

export async function getReport(sessionId) {
  const res = await fetch(`${API_BASE}/session/${sessionId}/report`);
  if (!res.ok) throw new Error('Failed to fetch research report');
  return res.json();
}

export function getExportMarkdownUrl(sessionId) {
  return `${API_BASE}/session/${sessionId}/export/markdown`;
}

export function getExportJsonUrl(sessionId) {
  return `${API_BASE}/session/${sessionId}/export/json`;
}
