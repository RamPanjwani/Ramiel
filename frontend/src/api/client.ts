/**
 * Ramiel API Client (Typed)
 * Connects to the local FastAPI backend with graceful offline handling.
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

async function safeFetchJson<T>(url: string, options?: RequestInit, fallback?: T): Promise<T> {
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      if (fallback !== undefined) return fallback;
      throw new Error(`HTTP ${res.status} from ${url}`);
    }
    const text = await res.text();
    if (!text.trim()) {
      if (fallback !== undefined) return fallback;
      throw new Error(`Empty response from ${url}`);
    }
    return JSON.parse(text) as T;
  } catch (err) {
    if (fallback !== undefined) return fallback;
    throw err;
  }
}

export const api = {
  async getHealth(): Promise<{ status: string; phase: string }> {
    return safeFetchJson('/health', undefined, { status: 'offline', phase: 'unknown' });
  },

  async getAdminHealth(): Promise<AdminHealthResponse> {
    return safeFetchJson('/api/admin/health', undefined, {
      backend: 'offline',
      vllm_serving: 'offline',
      ollama_serving: 'offline',
      models_registered: '0',
      phase: 'offline',
    });
  },

  async getModels(): Promise<ModelsResponse> {
    return safeFetchJson('/api/admin/models', undefined, {
      models: [],
      serving_engines: {
        vllm: { status: 'offline', endpoint: 'http://127.0.0.1:8000/v1' },
        ollama: { status: 'offline', endpoint: 'http://127.0.0.1:11434' },
      },
      phase: 'offline',
    });
  },

  async getRoutePreview(prompt: string): Promise<RoutePreviewResponse> {
    return safeFetchJson(`/api/admin/route?prompt=${encodeURIComponent(prompt)}`);
  },

  async getTraces(limit: number = 50): Promise<{ count: number; traces: TraceRecord[] }> {
    return safeFetchJson(`/api/admin/traces?limit=${limit}`, undefined, { count: 0, traces: [] });
  },

  async getEgressStatus(): Promise<EgressStatusResponse> {
    return safeFetchJson('/api/admin/egress', undefined, {
      running: false,
      total_checks: 0,
      violations: [],
      status: 'clean',
    });
  },

  async sendChatMessage(message: string, sessionId?: string): Promise<ChatResponse> {
    return safeFetchJson('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
  },

  async uploadFile(file: File): Promise<{ status: string; filename: string; message: string }> {
    const formData = new FormData();
    formData.append('file', file);
    return safeFetchJson('/api/upload', {
      method: 'POST',
      body: formData,
    });
  },
};
