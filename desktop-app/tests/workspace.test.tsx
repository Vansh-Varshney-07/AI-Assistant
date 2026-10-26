import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { WorkspaceHome, ConnectionsPanel, PermissionsPanel } from '../src/renderer/Workspace';
import type { DesktopAPI } from '../src/shared/types';

const backend = { state: 'ready' as const, capabilities: { documents: false, git_branch: true } };
const snapshot = { observed_at: Date.now(), jobs: [{ id: 'read-one', status: 'running' }], workflows: [], actions: [{ id: 'review', status: 'pending' }, { id: 'uncertain', status: 'outcome_unknown' }] };

describe('New GitHub command workspace with real-state projections', () => {
  it('routes the Home entry to the explicit conversation service', async () => {
    const go = vi.fn(); render(<WorkspaceHome backend={backend} snapshot={snapshot} spaceName="Synthetic space" go={go} />);
    await userEvent.click(screen.getByRole('button', { name: 'Open chat' })); expect(go).toHaveBeenCalledWith('chat');

    await userEvent.click(screen.getByRole('button', { name: /Analyze a document/ }));
    expect(go).toHaveBeenCalledWith('documents');
    expect(screen.queryByText(/8 Connected services/)).toBeNull();
  });
  it('shows observed counts and never fabricates telemetry or sample runs', () => {
    render(<WorkspaceHome backend={backend} snapshot={snapshot} spaceName="Synthetic space" go={vi.fn()} />);
    expect(screen.getByRole('button', { name: /Active read runs/ }).textContent).toContain('1');
    expect(screen.getByRole('button', { name: /Pending reviews/ }).textContent).toContain('1');
    expect(screen.getByRole('button', { name: /Needs checking/ }).textContent).toContain('1');
    expect(screen.getByText(/Tokens, model cost and device utilization are not reported/)).toBeTruthy();
    expect(screen.queryByText(/W03 Task Plan for Sprint/)).toBeNull();
  });
  it('uses an unknown count until a snapshot has actually arrived', () => {
    render(<WorkspaceHome backend={backend} snapshot={{ jobs: [], workflows: [], actions: [] }} spaceName="Synthetic" go={vi.fn()} />);
    expect(screen.getByRole('button', { name: /Active read runs/ }).textContent).toContain('—');
    expect(screen.getAllByText('Waiting for the first snapshot')).toHaveLength(4);
  });
  it('separates imported Google credentials from a live check',async()=>{
    const connectionsStatus=vi.fn(async()=>({configured:{google:true},checks:{}}));
    const checkConnection=vi.fn(async()=>({configured:{google:true},checks:{google:{passed:true,label:'Read checks verified'}}}));
    render(<ConnectionsPanel backend={backend} space="owned-space" api={{connectionsStatus,checkConnection} as unknown as DesktopAPI} busy={false} act={async()=>{}} go={vi.fn()}/>);
    expect(await screen.findByText('Imported \u00b7 check pending')).toBeTruthy();
    await userEvent.click(screen.getByRole('button',{name:'Check Google connection'}));
    expect(await screen.findByText('Live check passed')).toBeTruthy();expect(checkConnection).toHaveBeenCalledWith('owned-space','google');
  });
  it('routes a review request to the actual review list rather than an inline approval', async () => {
    const go = vi.fn(); render(<PermissionsPanel snapshot={snapshot} go={go} />);
    expect(screen.queryByRole('button', { name: /^Approve/ })).toBeNull();
    await userEvent.click(screen.getByRole('button', { name: /Open actual reviews and audit/ }));
    expect(go).toHaveBeenCalledWith('runs');
  });
});
