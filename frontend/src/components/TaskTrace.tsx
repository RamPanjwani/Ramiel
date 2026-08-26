import React from 'react';

export interface TaskStep {
  stepIndex: number;
  description: string;
  taskTag: 'code' | 'document' | 'vision' | 'calc' | 'general_qa';
  modelId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

export const TaskTrace: React.FC = () => {
  const sampleSteps: TaskStep[] = [
    {
      stepIndex: 1,
      description: 'System initialization and skeleton validation',
      taskTag: 'general_qa',
      modelId: 'reasoning-fallback (stub)',
      status: 'completed',
    },
    {
      stepIndex: 2,
      description: 'Egress monitoring daemon verification',
      taskTag: 'calc',
      modelId: 'system-monitor',
      status: 'completed',
    },
    {
      stepIndex: 3,
      description: 'Awaiting operator prompt dispatch',
      taskTag: 'document',
      modelId: 'reasoning-primary',
      status: 'pending',
    },
  ];

  return (
    <div className="bg-[#161B1E] border border-[#2A3236] rounded-md p-3 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-[#2A3236] pb-2 mb-2">
        <span className="text-[#8B979B] font-semibold text-[10px] uppercase tracking-wider">
          AGENT EXECUTION TRACE & MODEL ROUTING
        </span>
        <span className="text-[10px] text-[#4A9E6E]">PHASE 0 READY</span>
      </div>

      <div className="space-y-2">
        {sampleSteps.map((step) => (
          <div
            key={step.stepIndex}
            className="flex items-start justify-between bg-[#0E1214] p-2 rounded border border-[#2A3236]"
          >
            <div className="flex items-start space-x-2">
              <span
                className={`w-1.5 h-1.5 rounded-full mt-1.5 ${
                  step.status === 'completed'
                    ? 'bg-[#4A9E6E]'
                    : step.status === 'running'
                    ? 'bg-[#D98E2F] animate-ping'
                    : 'bg-[#8B979B]'
                }`}
              />
              <div>
                <div className="text-[#E4E9EA] font-medium text-[11px]">
                  Step {step.stepIndex}: {step.description}
                </div>
                <div className="text-[#8B979B] text-[10px] mt-0.5">
                  Tag: <span className="text-[#D98E2F]">{step.taskTag}</span> | Model:{' '}
                  <span className="text-[#E4E9EA]">{step.modelId}</span>
                </div>
              </div>
            </div>

            <span
              className={`text-[9px] uppercase px-1.5 py-0.5 rounded border ${
                step.status === 'completed'
                  ? 'text-[#4A9E6E] border-[#4A9E6E]/30 bg-[#4A9E6E]/10'
                  : 'text-[#8B979B] border-[#2A3236]'
              }`}
            >
              {step.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
