// This policy applies only to the bounded read-only diagnostic subprocess.
export function diagnosticPolicy(body,enabled) {
  if(enabled && process.env.DSH_DIAGNOSTIC_MODEL)body={...body,model:process.env.DSH_DIAGNOSTIC_MODEL};
  if(!enabled)return body;
  const result={...body,max_tokens:Math.min(body.max_tokens??6144,6144)};
  if(!/^MiniMax/i.test(result.model||''))result.response_format={type:'json_object'};
  if(/^qwen/i.test(result.model||'')&&!/-flash(?:-|$)/i.test(result.model||'')){result.enable_thinking=true;result.thinking_budget=2048;}
  else{delete result.enable_thinking;delete result.thinking_budget;}
  delete result.reasoning_effort;
  delete result.tools;delete result.tool_choice;delete result.parallel_tool_calls;
  return result;
}
