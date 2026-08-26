import { useEffect, useState } from 'react';
import { api, type EgressStatusResponse } from '../api/client';

export const EgressMonitorStrip = () => {
  const [data, setData] = useState<EgressStatusResponse | null>(null);
  const [error, setError] = useState<boolean>(false);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await api.getEgressStatus();
        setData(res);
        setError(false);
      } catch {
        setError(true);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const violationCount = data?.violations?.length ?? 0;
  const isClean = data?.status === 'clean' && violationCount === 0;

  return (
    <div className="flex items-center space-x-3 px-3 py-1.5 bg-[#161B1E] border border-[#2A3236] rounded text-xs font-mono">
      <div className="flex items-center space-x-2">
        <span
          className={`w-2 h-2 rounded-full ${
            error
              ? 'bg-[#C4453B]'
              : isClean
              ? 'bg-[#4A9E6E] animate-pulse'
              : 'bg-[#C4453B] animate-bounce'
          }`}
        />
        <span className="text-[#8B979B] uppercase tracking-wider font-semibold text-[10px]">
          AIR-GAP EGRESS:
        </span>
      </div>

      <div className="text-[#E4E9EA]">
        {error ? (
          <span className="text-[#C4453B]">DISCONNECTED</span>
        ) : isClean ? (
          <span className="text-[#4A9E6E] font-medium">0 CALLS OUT (VERIFIED)</span>
        ) : (
          <span className="text-[#C4453B] font-bold">{violationCount} VIOLATIONS</span>
        )}
      </div>

      {data && (
        <span className="text-[#8B979B] border-l border-[#2A3236] pl-2 text-[10px]">
          CHECKS: {data.total_checks}
        </span>
      )}
    </div>
  );
};

export const EgressMonitorPanel = ({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) => {
  const [data, setData] = useState<EgressStatusResponse | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    const fetchStatus = async () => {
      try {
        const res = await api.getEgressStatus();
        setData(res);
      } catch (err) {
        console.error(err);
      }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 1500);
    return () => clearInterval(interval);
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-[#161B1E] border border-[#2A3236] rounded-md max-w-2xl w-full p-5 shadow-2xl">
        <div className="flex items-center justify-between border-b border-[#2A3236] pb-3 mb-4">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#4A9E6E]" />
            <h2 className="text-sm font-mono font-bold tracking-wider text-[#E4E9EA]">
              LIVE NETWORK EGRESS AUDIT
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-xs font-mono text-[#8B979B] hover:text-[#E4E9EA] px-2 py-1 bg-[#1E2528] rounded border border-[#2A3236]"
          >
            [ESC] CLOSE
          </button>
        </div>

        <div className="space-y-4 text-xs font-mono">
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-[#0E1214] p-3 rounded border border-[#2A3236]">
              <div className="text-[#8B979B] text-[10px]">MONITOR STATE</div>
              <div className="text-sm font-bold text-[#4A9E6E]">
                {data?.running ? 'ACTIVE POLLING' : 'IDLE'}
              </div>
            </div>
            <div className="bg-[#0E1214] p-3 rounded border border-[#2A3236]">
              <div className="text-[#8B979B] text-[10px]">TOTAL SOCKET CHECKS</div>
              <div className="text-sm font-bold text-[#E4E9EA]">{data?.total_checks ?? 0}</div>
            </div>
            <div className="bg-[#0E1214] p-3 rounded border border-[#2A3236]">
              <div className="text-[#8B979B] text-[10px]">OUTBOUND ATTEMPTS</div>
              <div
                className={`text-sm font-bold ${
                  (data?.violations.length ?? 0) === 0 ? 'text-[#4A9E6E]' : 'text-[#C4453B]'
                }`}
              >
                {data?.violations.length ?? 0}
              </div>
            </div>
          </div>

          <div>
            <div className="text-[#8B979B] mb-1.5 font-semibold text-[11px]">
              OUTBOUND VIOLATIONS LOG (ZERO TOLERANCE):
            </div>
            <div className="bg-[#0E1214] border border-[#2A3236] rounded p-3 h-48 overflow-y-auto font-mono text-[11px]">
              {!data?.violations || data.violations.length === 0 ? (
                <div className="text-[#4A9E6E] flex items-center justify-center h-full">
                  ✓ NO EXTERNAL OUTBOUND TRAFFIC DETECTED. SOVEREIGN AIR-GAP INTACT.
                </div>
              ) : (
                data.violations.map((v, i: number) => (
                  <div key={i} className="text-[#C4453B] mb-2 pb-2 border-b border-[#2A3236]/50">
                    <div>[{v.timestamp}] ALERT: OUTBOUND CONNECTION ATTEMPT</div>
                    <div>Target: {v.remote_addr}:{v.remote_port} | Process: {v.process_name} (PID {v.pid})</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
