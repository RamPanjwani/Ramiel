import { useEffect, useState } from 'react';
import { api, type RegisteredModel, type TraceRecord } from '../api/client';

export const TaskTrace = () => {
  const [models, setModels] = useState<RegisteredModel[]>([]);
  const [traces, setTraces] = useState<TraceRecord[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [modelsRes, tracesRes] = await Promise.all([
          api.getModels(),
          api.getTraces(5),
        ]);
        if (modelsRes?.models) {
          setModels(modelsRes.models);
        }
        if (tracesRes?.traces) {
          setTraces(tracesRes.traces);
        }
      } catch (err) {
        console.error('Failed to load trace / model data:', err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-[#161B1E] border border-[#2A3236] rounded-md p-3 font-mono text-xs space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#2A3236] pb-2">
        <span className="text-[#8B979B] font-semibold text-[10px] uppercase tracking-wider">
          TASK ROUTER & RECENT EXECUTION TRACES
        </span>
        <span className="text-[10px] text-[#4A9E6E] font-medium">PHASE 2 (ROUTER ACTIVE)</span>
      </div>

      {/* Model Roster Section */}
      <div>
        <div className="text-[10px] text-[#8B979B] uppercase font-semibold mb-1.5">
          REGISTERED MODEL ROSTER ({models.length} MODELS):
        </div>
        <div className="grid grid-cols-2 gap-2">
          {models.slice(0, 4).map((m) => (
            <div
              key={m.id}
              className="bg-[#0E1214] p-2 rounded border border-[#2A3236] text-[10px]"
            >
              <div className="flex items-center justify-between">
                <span className="text-[#E4E9EA] font-bold">{m.id}</span>
                <span className="text-[#D98E2F] uppercase">{m.engine}</span>
              </div>
              <div className="text-[#8B979B] mt-0.5 truncate">
                Tags: [{m.task_tags.join(', ')}]
              </div>
              {m.fallback && (
                <div className="text-[#8B979B] text-[9px]">↳ Fallback: {m.fallback}</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Recent Traces Section */}
      <div>
        <div className="text-[10px] text-[#8B979B] uppercase font-semibold mb-1.5">
          LIVE EXECUTION TRACE STREAM:
        </div>
        <div className="space-y-1.5 max-h-40 overflow-y-auto">
          {traces.length === 0 ? (
            <div className="bg-[#0E1214] p-2 rounded border border-[#2A3236] text-[#8B979B] text-[10px] text-center">
              No chat execution traces recorded yet. Send a prompt to trigger auto-routing.
            </div>
          ) : (
            traces.map((t) => (
              <div
                key={t.id}
                className="bg-[#0E1214] p-2 rounded border border-[#2A3236] flex items-start justify-between"
              >
                <div className="space-y-0.5">
                  <div className="flex items-center space-x-2 text-[10px]">
                    <span className="text-[#D98E2F] font-bold">{t.task_id}</span>
                    {t.task_tag && (
                      <span className="px-1 py-0.2 bg-[#1E2528] text-[#4A9E6E] rounded border border-[#2A3236]">
                        {t.task_tag}
                      </span>
                    )}
                    <span className="text-[#8B979B]">Model: {t.model_id ?? 'unknown'}</span>
                  </div>
                  <div className="text-[#E4E9EA] text-[11px] truncate max-w-xs">
                    {t.prompt}
                  </div>
                </div>
                {t.latency_ms !== undefined && (
                  <span className="text-[9px] text-[#8B979B] shrink-0 ml-2">
                    {t.latency_ms}ms
                  </span>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
