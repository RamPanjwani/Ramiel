import React from 'react';

export const DeliverablePreview: React.FC = () => {
  return (
    <div className="bg-[#161B1E] border border-[#2A3236] rounded-md p-3 font-mono text-xs flex flex-col h-full">
      <div className="flex items-center justify-between border-b border-[#2A3236] pb-2 mb-2">
        <span className="text-[#8B979B] font-semibold text-[10px] uppercase tracking-wider">
          DELIVERABLE PREVIEW (.DOCX / .PPTX / .XLSX / CODE)
        </span>
        <span className="text-[10px] text-[#8B979B]">NO ACTIVE DELIVERABLE</span>
      </div>

      <div className="flex-1 flex flex-col items-center justify-center bg-[#0E1214] border border-[#2A3236] rounded p-6 text-center">
        <div className="w-8 h-8 rounded border border-[#2A3236] flex items-center justify-center text-[#8B979B] mb-2 font-mono text-xs">
          📄
        </div>
        <div className="text-[#E4E9EA] font-medium text-xs mb-1">
          No generated artifacts in current session
        </div>
        <p className="text-[#8B979B] text-[11px] max-w-xs leading-normal">
          Agent-generated approval notes, presentations, calculation workbooks, and verified code will render here.
        </p>
      </div>
    </div>
  );
};
