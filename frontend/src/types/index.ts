export type AgentStatus = 'idle' | 'processing' | 'completed' | 'error';
export type RiskLevel = 'critical' | 'high' | 'medium' | 'low';

export interface AgentNode {
  id: string;
  name: string;
  model: string;
  status: AgentStatus;
  icon: string;
  gpu_id?: string;
}

export interface RiskAssessment {
  risk_level: RiskLevel;
  description: string;
  affected_clauses: string[];
}

export interface AuditResult {
  document_id: string;
  summary: string;
  risks: RiskAssessment[];
  recommendations: string[];
  metadata: Record<string, any>;
}
