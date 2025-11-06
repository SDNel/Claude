// client/cas-types.ts
export type CasBackend = "compute-engine" | "remote-sympy" | "giac-wasm" | "pyodide-sympy";

export interface MathJson { [k: string]: unknown; }

export interface CasRequest {
  id: string;
  op:
    | "simplify" | "expand" | "factor"
    | "differentiate" | "integrate" | "limit"
    | "series" | "solve" | "linsolve"
    | "rref" | "eigen" | "steps";
  expr: MathJson;
  vars?: string[];
  assumptions?: Record<string, unknown>;
  options?: {
    form?: "expanded"|"factored"|"canonical";
    timeoutMs?: number;
    degreeLimit?: number;
  };
  want?: ("MathJSON"|"LaTeX"|"Text"|"Steps")[];
}

export interface StepNode {
  rule?: string;
  before?: MathJson;
  after?: MathJson;
  explanation?: string;
  children?: StepNode[];
}

export interface CasResponse {
  id: string;
  ok: boolean;
  result?: {
    mathjson?: MathJson;
    latex?: string;
    text?: string;
    steps?: StepNode;
  };
  error?: { code: string; message: string; details?: unknown };
  stats?: { elapsedMs: number; backend: CasBackend; cached?: boolean };
}
