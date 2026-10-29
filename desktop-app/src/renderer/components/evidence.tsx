import React, { useState } from 'react';
import { ShieldCheck, AlertCircle, Clock, FileText, CheckCircle2, XCircle, HelpCircle, ChevronDown, ChevronRight } from 'lucide-react';

export type StatusKind = 'loading' | 'stale' | 'denied' | 'empty' | 'failed' | 'uncertain' | 'completed' | 'ready';

export interface StatusBadgeProps {
  status: StatusKind | string;
  label?: string;
  note?: string;
}

export function StatusBadge({ status, label, note }: StatusBadgeProps) {
  const displayLabel = label || status.replaceAll('_', ' ');
  let icon = <HelpCircle size={13} aria-hidden="true" />;
  let className = 'badge badge-uncertain';

  switch (status) {
    case 'loading':
    case 'running':
    case 'reserved':
      icon = <Clock size={13} className="spin" aria-hidden="true" />;
      className = 'badge badge-loading';
      break;
    case 'stale':
    case 'expired':
      icon = <Clock size={13} aria-hidden="true" />;
      className = 'badge badge-stale';
      break;
    case 'denied':
    case 'revoked':
      icon = <XCircle size={13} aria-hidden="true" />;
      className = 'badge badge-denied';
      break;
    case 'empty':
      icon = <HelpCircle size={13} aria-hidden="true" />;
      className = 'badge badge-empty';
      break;
    case 'failed':
      icon = <AlertCircle size={13} aria-hidden="true" />;
      className = 'badge badge-failed';
      break;
    case 'completed':
    case 'ready':
      icon = <CheckCircle2 size={13} aria-hidden="true" />;
      className = 'badge badge-success';
      break;
    default:
      break;
  }

  return (
    <span className={className} title={note} aria-label={`Status: ${displayLabel}`}>
      {icon}
      <span>{displayLabel}</span>
    </span>
  );
}

export interface ScopeSummaryProps {
  space: string;
  owner?: string;
  task?: string;
  runId?: string;
  sourceCount?: number;
}

export function ScopeSummary({ space, owner, task, runId, sourceCount }: ScopeSummaryProps) {
  return (
    <div className="scope-summary" role="region" aria-label="Execution scope">
      <div className="scope-item">
        <span className="scope-label">Space</span>
        <strong>{space}</strong>
      </div>
      {owner && (
        <div className="scope-item">
          <span className="scope-label">Owner</span>
          <span>{owner}</span>
        </div>
      )}
      {task && (
        <div className="scope-item">
          <span className="scope-label">Task</span>
          <span>{task}</span>
        </div>
      )}
      {runId && (
        <div className="scope-item">
          <span className="scope-label">Run</span>
          <code>{runId.slice(0, 8)}</code>
        </div>
      )}
      {typeof sourceCount === 'number' && (
        <div className="scope-item">
          <span className="scope-label">Sources</span>
          <span>{sourceCount}</span>
        </div>
      )}
    </div>
  );
}

export interface SourceCardProps {
  name: string;
  sha256?: string;
  bytes?: number;
  truncated?: boolean;
  revoked?: boolean;
  onSelect?: () => void;
}

export function SourceCard({ name, sha256, bytes, truncated, revoked, onSelect }: SourceCardProps) {
  return (
    <div
      className={`source-card ${revoked ? 'source-revoked' : ''}`}
      role={onSelect ? 'button' : 'article'}
      tabIndex={onSelect ? 0 : undefined}
      onClick={onSelect}
      onKeyDown={e => {
        if (onSelect && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onSelect();
        }
      }}
      aria-label={`Source file: ${name}`}
    >
      <div className="source-header">
        <FileText size={16} aria-hidden="true" />
        <strong>{name}</strong>
      </div>
      {typeof bytes === 'number' && <small className="source-bytes">{bytes.toLocaleString()} bytes</small>}
      {sha256 && (
        <p className="source-hash">
          <code>{sha256.slice(0, 16)}…</code>
        </p>
      )}
      {truncated && <p className="source-warning">Excerpt bounded to worker budget</p>}
      {revoked && <p className="source-error">Access revoked</p>}
    </div>
  );
}

export interface EvidenceDrawerProps {
  title?: string;
  evidence: Array<{ name: string; sha256: string; content?: string; truncated?: boolean }>;
  initialOpen?: boolean;
}

export function EvidenceDrawer({ title = 'Source evidence and provenance', evidence, initialOpen = false }: EvidenceDrawerProps) {
  const [open, setOpen] = useState(initialOpen);

  return (
    <section className="evidence-drawer" aria-label={title}>
      <button
        className="drawer-toggle"
        aria-expanded={open}
        onClick={() => setOpen(o => !o)}
      >
        {open ? <ChevronDown size={15} aria-hidden="true" /> : <ChevronRight size={15} aria-hidden="true" />}
        <span>{title} ({evidence.length})</span>
      </button>
      {open && (
        <div className="drawer-body">
          {evidence.length === 0 ? (
            <p className="empty-inline">No external sources supplied for this run.</p>
          ) : (
            evidence.map((item, index) => (
              <div key={item.sha256 || index} className="evidence-item">
                <div className="evidence-item-header">
                  <ShieldCheck size={14} aria-hidden="true" />
                  <strong>{item.name}</strong>
                  <code>{item.sha256}</code>
                </div>
                {item.content && (
                  <pre className="evidence-content">{item.content}</pre>
                )}
                {item.truncated && (
                  <p className="hint">Source excerpt truncated to stay within bounded context limits.</p>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </section>
  );
}
