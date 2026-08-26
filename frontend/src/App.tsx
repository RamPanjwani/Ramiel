import { useState } from 'react';
import { EgressMonitorStrip, EgressMonitorPanel } from './components/EgressMonitorPanel';
import { ChatPanel } from './components/ChatPanel';
import { FileUpload } from './components/FileUpload';
import { TaskTrace } from './components/TaskTrace';
import { DeliverablePreview } from './components/DeliverablePreview';

export function App() {
  const [egressModalOpen, setEgressModalOpen] = useState(false);

  return (
    <div className="flex flex-col h-screen bg-[#0E1214] text-[#E4E9EA] font-sans selection:bg-[#D98E2F] selection:text-[#0E1214]">
      {/* Persistent Top Navigation Bar / Instrument Header */}
      <header className="h-12 border-b border-[#2A3236] bg-[#161B1E] flex items-center justify-between px-4 z-10 shrink-0">
        <div className="flex items-center space-x-3">
          <div className="w-5 h-5 bg-[#D98E2F] text-[#0E1214] font-mono font-bold flex items-center justify-center text-xs rounded-sm">
            R
          </div>
          <div>
            <span className="font-mono font-bold text-xs tracking-wider text-[#E4E9EA]">
              RAMIEL
            </span>
            <span className="ml-2 text-[10px] font-mono text-[#8B979B] hidden sm:inline">
              SOVEREIGN ON-PREMISE AI WORKBENCH
            </span>
          </div>
        </div>

        {/* Center: Live Egress Status Strip (Clickable for full modal) */}
        <div
          onClick={() => setEgressModalOpen(true)}
          className="cursor-pointer hover:opacity-90 transition-opacity"
          title="Click to view real-time network egress audit"
        >
          <EgressMonitorStrip />
        </div>

        {/* Right: Workstation / Mode Info */}
        <div className="flex items-center space-x-3 text-xs font-mono text-[#8B979B]">
          <div className="hidden md:flex items-center space-x-1.5 bg-[#0E1214] px-2.5 py-1 rounded border border-[#2A3236]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#4A9E6E]" />
            <span className="text-[10px] text-[#E4E9EA]">ON-PREM GPU</span>
          </div>
          <span className="text-[10px] bg-[#1E2528] px-2 py-1 rounded border border-[#2A3236] text-[#D98E2F]">
            PHASE 2
          </span>
        </div>
      </header>

      {/* Main Work Surface Grid */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-3 p-3 overflow-hidden min-h-0">
        {/* Left / Center Column: Chat & Prompt Execution (7 cols) */}
        <div className="lg:col-span-7 flex flex-col h-full min-h-0 space-y-3">
          <div className="flex-1 min-h-0">
            <ChatPanel />
          </div>
        </div>

        {/* Right Column: Ingestion, Trace & Deliverables (5 cols) */}
        <div className="lg:col-span-5 flex flex-col h-full min-h-0 space-y-3 overflow-y-auto">
          <FileUpload />
          <TaskTrace />
          <div className="flex-1 min-h-[220px]">
            <DeliverablePreview />
          </div>
        </div>
      </main>

      {/* Full Network Egress Modal */}
      <EgressMonitorPanel
        isOpen={egressModalOpen}
        onClose={() => setEgressModalOpen(false)}
      />
    </div>
  );
}

export default App;
