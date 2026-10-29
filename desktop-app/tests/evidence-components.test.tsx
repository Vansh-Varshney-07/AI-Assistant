import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { StatusBadge, ScopeSummary, SourceCard, EvidenceDrawer } from '../src/renderer/components/evidence';

describe('Evidence and state components', () => {
  it('StatusBadge renders distinct loading, stale, denied, empty, failed, and ready states', () => {
    const { rerender } = render(<StatusBadge status="loading" />);
    expect(screen.getByLabelText('Status: loading')).toBeTruthy();

    rerender(<StatusBadge status="stale" />);
    expect(screen.getByLabelText('Status: stale')).toBeTruthy();

    rerender(<StatusBadge status="denied" />);
    expect(screen.getByLabelText('Status: denied')).toBeTruthy();

    rerender(<StatusBadge status="empty" />);
    expect(screen.getByLabelText('Status: empty')).toBeTruthy();

    rerender(<StatusBadge status="failed" />);
    expect(screen.getByLabelText('Status: failed')).toBeTruthy();

    rerender(<StatusBadge status="ready" />);
    expect(screen.getByLabelText('Status: ready')).toBeTruthy();
  });

  it('ScopeSummary shows space and run identity without fabrication', () => {
    render(<ScopeSummary space="prod-space" task="analysis" runId="run-12345678" sourceCount={2} />);
    expect(screen.getByText('prod-space')).toBeTruthy();
    expect(screen.getByText('analysis')).toBeTruthy();
    expect(screen.getByText('run-1234')).toBeTruthy();
    expect(screen.getByText('2')).toBeTruthy();
  });

  it('SourceCard supports click and keyboard Enter activation', () => {
    const onSelect = vi.fn();
    render(<SourceCard name="report.pdf" sha256="abc1234567890def" bytes={2048} onSelect={onSelect} />);
    const card = screen.getByLabelText('Source file: report.pdf');
    fireEvent.click(card);
    expect(onSelect).toHaveBeenCalledTimes(1);

    fireEvent.keyDown(card, { key: 'Enter' });
    expect(onSelect).toHaveBeenCalledTimes(2);
  });

  it('EvidenceDrawer toggles open and close on click and keyboard', () => {
    const evidence = [{ name: 'spec.md', sha256: 'deadbeef1234', content: 'Excerpt text' }];
    render(<EvidenceDrawer evidence={evidence} />);
    expect(screen.queryByText('Excerpt text')).toBeNull();

    const toggle = screen.getByRole('button', { name: /Source evidence and provenance/ });
    fireEvent.click(toggle);
    expect(screen.getByText('Excerpt text')).toBeTruthy();

    fireEvent.click(toggle);
    expect(screen.queryByText('Excerpt text')).toBeNull();
  });
});
