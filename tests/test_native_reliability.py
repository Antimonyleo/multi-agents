import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "native_reliability",
    Path(__file__).resolve().parents[1] / "scripts/native_calibration.py",
)
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


class TelemetryTest(unittest.TestCase):
    def test_invalid_provider_counts_are_unknown(self):
        for provider in ("claude", "codex"):
            for usage in (
                {},
                None,
                {"input_tokens": 0},
                {"input_tokens": True, "output_tokens": 0},
                {"input_tokens": -1, "output_tokens": 0},
                {"input_tokens": "1", "output_tokens": 0},
                {
                    "input_tokens": 1,
                    "output_tokens": 0,
                    "cache_read_input_tokens": False,
                },
            ):
                with self.subTest(provider=provider, usage=usage):
                    event = {
                        "type": "result" if provider == "claude" else "turn.completed",
                        "usage": usage,
                    }
                    self.assertFalse(
                        native.normalize(provider, [event])[
                            "provider_telemetry_complete"
                        ]
                    )

    def test_zero_totals_valid_and_message_completeness_separate(self):
        for provider in ("claude", "codex"):
            event = {
                "type": "result" if provider == "claude" else "turn.completed",
                "usage": {"input_tokens": 0, "output_tokens": 0},
            }
            metrics = native.normalize(provider, [event])
            self.assertTrue(metrics["provider_telemetry_complete"])
            self.assertFalse(metrics["response_telemetry_complete"])


class BoundaryTest(unittest.TestCase):
    def call(self, ident="a", role="scientific_explorer", parent=None):
        event = {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "name": "Agent",
                        "id": ident,
                        "input": {"subagent_type": role},
                    }
                ]
            },
        }
        if parent:
            event["parent_tool_use_id"] = parent
        return event

    def check(self, stream, arm="workflow", children=None):
        return native.delegation_check(
            arm, native.normalize("claude", stream), children or []
        )

    def test_role_identity_unique_and_depth(self):
        child = {
            "id": "child",
            "parent_tool_use_id": "a",
            "role": "scientific_explorer",
            "depth": 1,
        }
        self.assertTrue(
            self.check([self.call(), self.call()], children=[child])["verified"]
        )
        for stream in (
            [self.call(role="scientific_reviewer")],
            [self.call(role="scientific_worker")],
            [self.call(ident=None)],
            [self.call(), self.call("b")],
            [self.call(), self.call("b", parent="a")],
        ):
            self.assertFalse(self.check(stream, children=[child])["verified"])
        self.assertFalse(
            self.check([self.call()], arm="baseline", children=[child])["verified"]
        )
        self.assertFalse(self.check([self.call()])["verified"])
        self.assertFalse(self.check([], children=[child])["verified"])
        self.assertFalse(
            self.check([self.call()], children=[{**child, "depth": 2}])["verified"]
        )

    def test_codex_repeated_start_conflicts_fail_boundary(self):
        first = {
            "type": "item.completed",
            "item": {
                "id": "start",
                "type": "collab_tool_call",
                "tool": "spawn_agent",
                "agent_type": "scientific_explorer",
                "receiver_thread_ids": ["child"],
            },
        }
        trace = [
            {
                "type": "session_meta",
                "payload": {
                    "id": "child",
                    "parent_thread_id": "parent",
                    "agent_role": "scientific_explorer",
                },
            }
        ]
        identical = native.normalize("codex", [first, first], [trace])
        self.assertEqual(identical["tool_fragment_conflicts"], [])
        self.assertEqual(len(identical["delegate_calls"]), 1)
        self.assertEqual(identical["tools"]["collab_tool_call"], 1)
        self.assertTrue(native.delegation_check("workflow", identical)["verified"])
        for changed in (
            {"agent_type": "scientific_reviewer"},
            {"receiver_thread_ids": ["other-child"]},
            {
                "agent_type": "scientific_reviewer",
                "receiver_thread_ids": ["other-child"],
            },
        ):
            with self.subTest(changed=changed):
                repeated = {
                    "type": "item.completed",
                    "item": {**first["item"], **changed},
                }
                metrics = native.normalize("codex", [first, repeated], [trace])
                self.assertTrue(metrics["tool_fragment_conflicts"])
                self.assertFalse(
                    native.delegation_check("workflow", metrics)["verified"]
                )
                self.assertEqual(len(metrics["delegate_calls"]), 1)


class DiscoveryTest(unittest.TestCase):
    def test_cross_cwd_descendants_and_missing_capture(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            out = home / "out"
            out.mkdir()
            state = home / ".codex"
            state.mkdir()
            con = sqlite3.connect(state / "state_5.sqlite")
            con.execute(
                "create table threads (id text, rollout_path text, source text, cwd text)"
            )
            for ident, parent, cwd in [
                ("parent", None, out / "workspace"),
                ("child", "parent", home / "changed"),
                ("grandchild", "child", home / "changed"),
                ("unrelated", None, out / "workspace"),
            ]:
                path = home / (ident + ".jsonl")
                meta = {"id": ident, "parent_thread_id": parent}
                path.write_text(
                    json.dumps({"type": "session_meta", "payload": meta}) + "\n"
                )
                con.execute(
                    "insert into threads values (?, ?, ?, ?)",
                    (ident, str(path), "subagent" if parent else "exec", str(cwd)),
                )
            con.commit()
            con.close()
            with patch.object(native.Path, "home", return_value=home):
                traces = native.collect_codex(
                    out, [{"type": "thread.started", "thread_id": "parent"}]
                )
            self.assertEqual(
                {t[0]["payload"]["id"] for t in traces},
                {"parent", "child", "grandchild"},
            )
            self.assertFalse((out / "native/unrelated.jsonl").exists())

    def test_non_object_jsonl_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "trace.jsonl"
            for value in ("[]", "null", "3"):
                p.write_text(value + "\n")
                with self.assertRaises(ValueError):
                    native.events(p)


import test_native_calibration as calibration_tests

native = calibration_tests.native
import sys
import os


class RunReliabilityTest(unittest.TestCase):
    setUp = calibration_tests.PairControlTest.setUp
    pair = calibration_tests.PairControlTest.pair

    def prepare_fake(
        self, event=None, child_role=None, malformed=False, extra_events=None
    ):
        runner = Path(
            os.environ.get("NATIVE_CALIBRATION_TEST_RUNNER", str(native.LEGACY))
        )
        self.runner_patch = patch.object(native, "LEGACY", runner)
        self.runner_patch.start()
        self.addCleanup(self.runner_patch.stop)

        def command(out, manifest):
            truth = json.loads((out / "truth.json").read_text())
            payload = {
                "type": "result",
                "is_error": False,
                "usage": {"input_tokens": 0, "output_tokens": 0},
                "structured_output": truth,
            }
            if event is not None:
                payload.update(event)
            output = (
                "{bad}"
                if malformed
                else "\n".join(json.dumps(e) for e in (extra_events or []) + [payload])
            )
            return [
                sys.executable,
                "-c",
                "print(" + repr(output) + ")",
                "--tools",
                native.toolset(manifest["arm"], manifest["comparison"]),
                "--allowedTools",
                native.toolset(manifest["arm"], manifest["comparison"]),
            ]

        self.command_patch = patch.object(native, "build_command", side_effect=command)
        self.command_patch.start()
        self.addCleanup(self.command_patch.stop)
        a, b = self.pair()
        for out in (a, b):
            manifest = json.loads((out / "manifest.json").read_text())
            sid = manifest["session_id_requested"]
            project = self.home / ".claude/projects/scratch"
            project.mkdir(parents=True, exist_ok=True)
            (project / (sid + ".jsonl")).write_text("{}\n")
        return a, b

    def test_fake_runner_complete_zero_usage(self):
        a, b = self.prepare_fake()
        native.run(a, b)
        metrics = json.loads((a / "metrics.json").read_text())
        self.assertTrue(metrics["quality_pass"])
        self.assertFalse(metrics["response_telemetry_complete"])
        native.run(b, a)
        self.assertTrue(json.loads((b / "metrics.json").read_text())["quality_pass"])

    def test_empty_telemetry_blocks_continuation(self):
        a, b = self.prepare_fake({"usage": {}})
        native.run(a, b)
        metrics = json.loads((a / "metrics.json").read_text())
        self.assertFalse(metrics["quality_pass"])
        self.assertIsNone(metrics["usable_provider_usage"])
        with patch.object(
            native.importlib.util,
            "spec_from_file_location",
            side_effect=AssertionError("runner imported"),
        ):
            with self.assertRaisesRegex(ValueError, "usage_present"):
                native.run(b, a)

    def test_malformed_trace_leaves_incomplete_receipt(self):
        a, b = self.prepare_fake(malformed=True)
        native.run(a, b)
        metrics = json.loads((a / "metrics.json").read_text())
        self.assertFalse(metrics["checks"]["capture_complete"])
        self.assertEqual(metrics["execution_state"], "incomplete")
        self.assertTrue(metrics["capture_errors"])
        with self.assertRaises(ValueError):
            native.run(b, a)

    def test_missing_receipt_leaves_incomplete_record(self):
        a, _ = self.prepare_fake()
        manifest = json.loads((a / "manifest.json").read_text())
        native.capture(a, manifest)
        metrics = json.loads((a / "metrics.json").read_text())
        self.assertEqual(metrics["execution_state"], "incomplete")
        self.assertFalse(metrics["checks"]["terminal_success"])
        self.assertFalse(metrics["checks"]["cleanup_verified"])

    def test_every_failed_peer_gate_blocks_before_import(self):
        a, b = self.prepare_fake()
        native.run(a, b)
        original = json.loads((a / "metrics.json").read_text())
        for name in (
            "exact_output",
            "usage_present",
            "support_cap",
            "cleanup_verified",
            "capture_complete",
            "terminal_success",
            "workspace_unchanged",
        ):
            metrics = json.loads(json.dumps(original))
            metrics["checks"][name] = False
            native.write(a / "metrics.json", metrics)
            with patch.object(
                native.importlib.util,
                "spec_from_file_location",
                side_effect=AssertionError("runner imported"),
            ):
                with self.assertRaisesRegex(ValueError, name):
                    native.run(b, a)
        native.write(a / "metrics.json", original)
        with self.assertRaisesRegex(ValueError, "retry"):
            native.run(a, b)

    def test_malformed_peer_receipt_blocks_before_import(self):
        a, b = self.prepare_fake()
        (a / "execution.json").write_text("[]")
        native.write(a / "metrics.json", {"checks": {}})
        with patch.object(
            native.importlib.util,
            "spec_from_file_location",
            side_effect=AssertionError("runner imported"),
        ):
            with self.assertRaises(ValueError):
                native.run(b, a)

    def test_fake_runner_native_role_and_linkage(self):
        event = {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "a",
                        "name": "Agent",
                        "input": {"subagent_type": "scientific_explorer"},
                    }
                ]
            },
        }
        a, b = self.prepare_fake(extra_events=[event, event])
        manifest = json.loads((b / "manifest.json").read_text())
        sid = manifest["session_id_requested"]
        project = self.home / ".claude/projects/scratch"
        folder = project / sid / "subagents"
        folder.mkdir(parents=True)
        (project / (sid + ".jsonl")).write_text(
            json.dumps(
                {
                    "type": "user",
                    "message": {
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": "a",
                                "content": "agentId: child",
                            }
                        ]
                    },
                }
            )
            + "\n"
        )
        (folder / "agent-child.jsonl").write_text(
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "id": "child-message",
                        "model": "native-explorer-model",
                        "content": [],
                        "usage": {"input_tokens": 1, "output_tokens": 1},
                    },
                }
            )
            + "\n"
        )
        (folder / "agent-child.meta.json").write_text(
            json.dumps({"agentType": "scientific_explorer"})
        )
        native.run(b, a)
        metrics = json.loads((b / "metrics.json").read_text())
        self.assertTrue(metrics["quality_pass"])
        self.assertEqual(metrics["delegation_boundary"]["unique_starts"], 1)
        self.assertEqual(metrics["whole_family_accounting"], "unverified")
        # Same native call shape with a prohibited observed role fails capture boundary.
        (folder / "agent-child.meta.json").write_text(
            json.dumps({"agentType": "scientific_reviewer"})
        )
        native.capture(b, manifest)
        self.assertFalse(
            json.loads((b / "metrics.json").read_text())["checks"]["support_cap"]
        )

    def test_missing_child_capture_fails_native_reconciliation(self):
        event = {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "a",
                        "name": "Agent",
                        "input": {"subagent_type": "scientific_explorer"},
                    }
                ]
            },
        }
        a, b = self.prepare_fake(extra_events=[event])
        native.run(b, a)
        self.assertFalse(
            json.loads((b / "metrics.json").read_text())["checks"]["support_cap"]
        )

    def test_semantic_fixture_version_bound(self):
        a, b = self.pair(task="semantic")
        self.assertTrue(native.audit_pair(a, b)["controls_match"])
        manifest = json.loads((b / "manifest.json").read_text())
        manifest["semantic_fixture_sha256"] = "wrong"
        native.write(b / "manifest.json", manifest)
        self.assertFalse(native.audit_pair(a, b)["controls_match"])

    def test_qualification_requires_frozen_purpose_and_one_helper(self):
        from types import SimpleNamespace

        output = self.root / "qualification"
        native.prepare(
            SimpleNamespace(
                output=str(output),
                provider="claude",
                arm="workflow",
                comparison="routing",
                task="inventory",
                budget_usd=0.4,
                qualification=True,
            )
        )
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(
            len(json.loads((output / "truth.json").read_text())["entries"]), 1
        )
        with patch.object(native, "execute") as execute:
            native.run_qualification(output)
            execute.assert_called_once()
        manifest["purpose"] = "comparison"
        native.write(output / "manifest.json", manifest)
        with patch.object(
            native.importlib.util,
            "spec_from_file_location",
            side_effect=AssertionError("imported"),
        ):
            with self.assertRaises(ValueError):
                native.run_qualification(output)


class MissingDiscoveryTest(unittest.TestCase):
    def test_missing_malformed_duplicate_and_string_source(self):
        for mode in ("missing", "malformed", "duplicate", "string_source"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as td:
                home = Path(td)
                out = home / "out"
                out.mkdir()
                state = home / ".codex"
                state.mkdir()
                parent = home / "parent.jsonl"
                parent.write_text(
                    json.dumps(
                        {
                            "type": "session_meta",
                            "payload": {"id": "parent", "source": "exec"},
                        }
                    )
                    + "\n"
                )
                child = home / "child.jsonl"
                source = {"subagent": {"thread_spawn": {"parent_thread_id": "parent"}}}
                if mode != "missing":
                    child.write_text(
                        json.dumps(
                            {
                                "type": "session_meta",
                                "payload": {
                                    "id": "child",
                                    "source": json.dumps(source),
                                },
                            }
                        )
                        + "\n"
                        + ("{bad}\n" if mode == "malformed" else "")
                    )
                for number in range(2 if mode == "duplicate" else 1):
                    con = sqlite3.connect(state / f"state_{number}.sqlite")
                    con.execute(
                        "create table threads (id text, rollout_path text, source text, cwd text)"
                    )
                    con.execute(
                        "insert into threads values (?,?,?,?)",
                        ("parent", str(parent), "exec", str(out / "workspace")),
                    )
                    con.execute(
                        "insert into threads values (?,?,?,?)",
                        ("child", str(child), json.dumps(source), str(home / "other")),
                    )
                    # Unrelated malformed transcript never enters the exported family.
                    other = home / "unrelated.jsonl"
                    other.write_text("{bad}\n")
                    con.execute(
                        "insert into threads values (?,?,?,?)",
                        ("unrelated", str(other), "exec", str(out / "workspace")),
                    )
                    con.commit()
                    con.close()
                with patch.object(native.Path, "home", return_value=home):
                    traces = native.collect_codex(
                        out, [{"type": "thread.started", "thread_id": "parent"}]
                    )
                report = json.loads((out / "native_capture.json").read_text())
                self.assertEqual(
                    report["complete"], mode in ("duplicate", "string_source")
                )
                self.assertEqual(len(traces), 2 if report["complete"] else 1)
                self.assertFalse((out / "native/unrelated.jsonl").exists())


class UnauthorizedRunTest(unittest.TestCase):
    setUp = RunReliabilityTest.setUp
    pair = RunReliabilityTest.pair
    prepare_fake = RunReliabilityTest.prepare_fake

    # One isolated end-to-end reproduction of the audit's count-only role defect.
    def test_unauthorized_requested_and_observed_role(self):
        event = {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "a",
                        "name": "Agent",
                        "input": {"subagent_type": "scientific_reviewer"},
                    }
                ]
            },
        }
        a, b = self.prepare_fake(extra_events=[event])
        manifest = json.loads((b / "manifest.json").read_text())
        sid = manifest["session_id_requested"]
        project = self.home / ".claude/projects/scratch"
        folder = project / sid / "subagents"
        folder.mkdir(parents=True)
        (project / (sid + ".jsonl")).write_text(
            json.dumps(
                {
                    "type": "user",
                    "message": {
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": "a",
                                "content": "agentId: child",
                            }
                        ]
                    },
                }
            )
            + "\n"
        )
        (folder / "agent-child.jsonl").write_text(
            json.dumps(
                {
                    "type": "assistant",
                    "message": {"model": "reviewer-native", "content": []},
                }
            )
            + "\n"
        )
        (folder / "agent-child.meta.json").write_text(
            json.dumps({"agentType": "scientific_reviewer"})
        )
        native.run(b, a)
        self.assertFalse(
            json.loads((b / "metrics.json").read_text())["checks"]["support_cap"]
        )
