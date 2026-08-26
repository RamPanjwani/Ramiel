/**
 * Ramiel API Client (Typed)
 * Connects to the local FastAPI backend.
 */

export interface EgressStatusResponse {
  running: boolean;
  total_checks: number;
  violations: Array<{
    remote_addr: string;
    remote_port: number;
    pid: number | null;
    process_name: string;
    timestamp: string;
  }>;
  status: 'clean' | 'VIOLATION_DETECTED';
}

export interface ChatResponse {
  reply: string;
  session_id: string;
  model_used: string | null;
}

export interface AdminHealthResponse {
  backend: string;
  models_loaded: string;
  egress_violations: string;
  phase: string;
}

export const api = {
  async getHealth(): Promise<{ status: string }> {
    const res = await fetch('/health');
    return res.json();
  },

  async getAdminHealth(): Promise<AdminHealthResponse> {
    const res = await fetch('/api/admin/health');
    return res.json();
  },

  async getEgressStatus(): Promise<EgressStatusResponse> {
    const res = await fetch('/api/admin/egress');
    return res.json();
  },

  async sendChatMessage(message: string, sessionId?: string): Promise<ChatResponse> {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    return res.json();
  },

  async uploadFile(file: File): Promise<{ status: string; filename: string; message: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    });
    return res.json();
  },
};
