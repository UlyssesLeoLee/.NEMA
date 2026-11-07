(()=>{'use strict';
const before="\tT001 1\nBuildLoginFlow PreventDataLeak ValidateAPI Codex Today AuthService\n\tT002 1\nReviewHTTPStatus ExplainUnexpectedFailure AuditLogs Claude Tomorrow Gateway\n\tT003 1\nFixTokenCache AvoidExpiredSessions AddTests Argo Today Redis\n\tT004 1\nDocumentReleasePlan ImproveSharedContext ReviewChanges Codex Friday Repository\n\tT005 1\nAnalyzeGraphEdges PreventInvalidDirections VerifyTopology Claude Today IDE\n\tT006 1\nPrepareAgentHandoff ReduceTokenWaste ReviewDependencies Argo Tomorrow Project";
const after="\t$12\nExplainUnexpectedFailure\nAnalyzeGraphEdges\nImproveSharedContext\nAvoidExpiredSessions\nDocumentReleasePlan\nPreventInvalidDirections\nPrepareAgentHandoff\nReduceTokenWaste\nVerifyTopology\nToday\nTomorrow\nClaude\n\tT001 1\nBuildLoginFlow PreventDataLeak ValidateAPI Codex ^9 AuthService\n\t002 1\nReviewHTTPStatus ^0 AuditLogs ^11 ^10 Gateway\n\t003 1";
document.getElementById('raw').textContent=before;
document.getElementById('wire').textContent=after;
const rows=window.NEMA_LAB_V12?.scenarios||[];
const fields=[['english_60',0],['table_200',1],['graph_40n_160e',2]];
for(const [name,index] of fields){const x=rows.find(y=>y.scenario===name)?.models?.bpe;if(!x)continue;
const node=document.querySelectorAll('.codec-stat strong')[index];
node.textContent=((x.nema-x.nemat)/x.nema*100).toFixed(2)+'%';
}
})();
