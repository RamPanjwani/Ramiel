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
  task_id: string;
  task_tag: string;
  model_used: string | null;
  latency_ms: number | null;
}

export interface AdminHealthResponse {
  backend: string;
  vllm_serving: string;
  ollama_serving: string;
  models_registered: string;
  phase: string;
}

export interface RegisteredModel {
  id: string;
  engine: string;
  path: string;
  task_tags: string[];
  min_vram_gb: number;
  fallback: string | null;
}

export interface ModelsResponse {
  models: RegisteredModel[];
  serving_engines: {
    vllm: { status: string; endpoint: string };
    ollama: { status: string; endpoint: string };
  };
  phase: string;
}

export interface RoutePreviewResponse {
  prompt: string;
  task_tag: string;
  selected_model: string;
  engine: string | null;
  fallback_chain: string[];
}

export interface TraceRecord {
  id: number;
  task_id: string;
  session_id: string;
  event_type: string;
  model_id: string | null;
  task_tag?: string;
  prompt: string | null;
  response: string | null;
  latency_ms?: number;
  timestamp: string;
}

export const api = {
  async getHealth(): Promise<{ status: string; phase: string }> {
    const res = await fetch('/health');
    return res.json();
  },

  async getAdminHealth(): Promise<AdminHealthResponse> {
    const res = await fetch('/api/admin/health');
    return res.json();
  },

  async getModels(): Promise<ModelsResponse> {
    const res = await fetch('/api/admin/models');
    return res.json();
  },

  async getRoutePreview(prompt: string): Promise<RoutePreviewResponse> {
    const res = await fetch(`/api/admin/route?prompt=${encodeURIComponent(prompt)}`);
    return res.json();
  },

  async getTraces(limit: number = 50): Promise<{ count: number; traces: TraceRecord[] }> {
    const res = await fetch(`/api/admin/traces?limit=${limit}`);
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
