type DiagnosticNameSet = Set<string>;
type UseAvailableDiagnosticResult = Map<string, DiagnosticNameSet>;
export default function useAvailableDiagnostics(topic?: string): UseAvailableDiagnosticResult;
export {};
