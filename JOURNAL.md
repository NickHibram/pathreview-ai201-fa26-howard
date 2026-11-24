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

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** [link to commit documenting the reproduced issue]

**Reproduction summary:**
I ran the orchestrator locally with PathReview’s own manifests and checked the frontend lockfile, which uses Vite 5.4.21 and Vitest 1.6.1 while their current major releases are 8 and 5. Both dependencies should be flagged under issue #20, but `agent/orchestrator.py` only schedules technology detection and market analysis for these inputs, so the output identifies JavaScript and Node.js without reporting either outdated dependency.

**Reproduction steps:** Run this from the repo root after local setup.

```bash
.venv/bin/python - <<'PY'
import json
from pathlib import Path

from agent.orchestrator import Orchestrator
from agent.tools.market_analyzer import MarketAnalyzer
from agent.tools.tech_detector import TechDetector

lock = json.loads(Path("frontend/package-lock.json").read_text())["packages"]
for name in ("vite", "vitest"):
    print(name, lock[f"node_modules/{name}"]["version"])

tools = (TechDetector(), MarketAnalyzer())
orchestrator = Orchestrator({tool.name: tool for tool in tools})
files = ["pyproject.toml", "frontend/package.json", "frontend/package-lock.json"]
result = orchestrator.run("issue-20-repro", {"files": files})
print("Tool results:", sorted(result["tool_results"]))
print("Technology detection:", result["tool_results"]["tech_detector"])
PY
```

**PLAN.md link:** [link to PLAN.md in your fork]

**Walkthrough video (recommended):** [link to your Loom video, ≤2 min — recommended, not graded]

**Blockers or open questions:**
[Anything you're still uncertain about going into Unit 9, or leave blank]
