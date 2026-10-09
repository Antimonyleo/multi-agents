# Native extraction calibration adapter

Current entrypoint: `scripts/native_calibration.py`. Prepare two isolated arms before running either:

```sh
python scripts/native_calibration.py prepare --provider claude --comparison routing --arm baseline --output /tmp/calibration-baseline
python scripts/native_calibration.py prepare --provider claude --comparison routing --arm workflow --output /tmp/calibration-workflow
python scripts/native_calibration.py check-pair --output /tmp/calibration-baseline --peer /tmp/calibration-workflow
```

Preparation and pair checking make no model calls. `run --output ARM_DIR --peer OTHER_DIR` requires separately authorized inference, a passing pair check and frozen versions. It refuses an existing local trace or a peer that started without successful terminal completion. The existing finite timeout/process-group runner remains the executor; this is not a new orchestrator or a hard overall spending scheduler.

`routing` matches tools and local skill availability, varying explicit workflow use and optional delegation. `deployment` intentionally varies local skill availability and Claude Agent/Skill tools. The latter measures those deployment differences, not an isolated instruction effect. Global catalogs can remain loaded in both modes; neither mode models an entirely uninstalled runtime. Match native model/effort, settings and user agent/skill-entrypoint inventories, source, task/schema/truth, declared budgets, permissions and effective command controls. Each launch command must also equal the canonical command built from its own declared controls and checked workspace. Local inventories detect additions and changes; they do not cover plugin contents, built-ins, remote catalogs or transitive skill resources. Separately validate effective runtime capabilities before causal attribution. Actual runtime context/cache variation still needs measurement.

Both the 96-file inventory and the existing 40-file prose fixture remain available (`--task inventory|prose`). Both have deterministic reference extraction. They are correctness/overhead controls; file count or prose packaging does not establish useful delegation, implementation quality or review benefit. See the [maintenance evaluation guidance](../../skill/scientific-workflow/maintenance.md#efficiency-evaluation) before choosing another workload or claim.

The collector preserves native evidence and provider totals. Latest usage per stable Claude assistant-message ID supplies response/context observations without counting repeated fragments twice. Mixed missing identities or usage leave aggregate totals unknown; a later fragment can complete an identified response. These are not server request counts. Child/cumulative accounting remains conservative: missing data is unknown, parent and child totals are not automatically added, and no automatic net-savings verdict is issued. Recurring task versus one-time setup/coordinator/review scope must be reported explicitly.

Codex candidate transcript collection currently uses the exact workspace cwd, so a child that changes cwd may be missed. Validate live child discovery, restrictions and usage inclusion before delegated-cost claims. The timeout runner's process-group cleanup does not prove arbitrary external children stopped. Native permissions and tools differ across providers; compare within a runtime.

The four original pilot runs and `pilot-evidence/used_adapter.py` remain frozen. Legacy preparations cannot pass the new matched-pair check; retain their original execution records instead of silently replaying them through a changed adapter. The original Claude pair had unequal tools and different startup skill/plugin catalogs and cannot isolate workflow instructions. Costs observed there remain valid deployment observations subject to its stated cache/order limits.

The wrapper depends on the existing host harness recorded in each manifest. No global agents/settings are rewritten. Offline tests make no model calls. Project2 remains paused.
