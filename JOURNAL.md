## Unit 7 — Issue selection

**Issue link:** [#20](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/20)

**Issue title:** Implement a DependencyAuditTool that flags outdated major dependencies in project repos

**Tier:** [ ] Tier 1  [X] Tier 2  [ ] Tier 3

**Issue fit:**
I chose Tier 2 because I’m comfortable writing Python, and working extensively with agents during my summer internship gave me the confidence to take on the orchestrator changes. I can use the existing tool interface and follow how `agent/orchestrator.py` schedules the technology detector when repository files are available. The scope is manageable because I can focus on reading three known file formats, flagging dependencies more than one major version behind, and testing when the orchestrator calls the tool.

**Problem summary:**
When dependencies are several major versions behind, they can cause failures or leave the system vulnerable. The system needs a tool to flag outdated dependencies, including versions that may be deprecated or unsupported. The fix would be to add a dependency audit tool that reads files such as `requirements.txt`, `package.json`, and `pyproject.toml` and flags dependencies that are behind on major releases. The tool description in `agent/orchestrator.py` also needs to explain how and when the orchestrator agent should use it.

**Branch name:** feat/20-dependency-audit-tool

**Setup confirmation:** [X] App runs locally at localhost:5173

**Cohort ledger:** [X] Issue added to cohort ledger
