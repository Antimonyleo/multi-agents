import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='workflow-install-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / 'source'
        # No dependency on machine-specific historical benchmark fixtures.
        for folder in ('skill', 'agents', 'scripts'):
            shutil.copytree(ROOT / folder, self.repo / folder)
        self.claude = self.base / 'claude'
        self.codex = self.base / 'codex'
        self.agents = self.base / 'agents'
        self.state = self.base / 'state'
        self.env = dict(os.environ, CLAUDE_HOME=str(self.claude),
                        CODEX_HOME=str(self.codex), AGENTS_HOME=str(self.agents))
        self.script = self.repo / 'scripts/install.sh'

    def run_cli(self, *args, ok=True):
        result = subprocess.run(['bash', str(self.script), '--state-dir', str(self.state), *args],
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result

    def receipt(self):
        receipts = list(self.state.glob('transactions/*/receipt.json'))
        self.assertEqual(len(receipts), 1)
        return receipts[0]

    def preexisting(self):
        skill = self.agents / 'skills/scientific-workflow'
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text('prior Codex skill')
        profile = self.codex / 'agents/scientific_reviewer.toml'
        profile.parent.mkdir(parents=True)
        profile.write_text('prior reviewer')
        return skill, profile

    def test_default_claude_preserves_settings(self):
        self.claude.mkdir()
        settings = self.claude / 'settings.json'
        settings.write_text('{"other":true}')
        self.run_cli()
        self.run_cli('--check')
        self.assertEqual(settings.read_text(), '{"other":true}')
        self.assertFalse(self.codex.exists())
        self.assertFalse(self.agents.exists())
        self.assertEqual(len(list((self.claude / 'agents').glob('*'))), 5)

    def test_codex_does_not_touch_claude(self):
        self.claude.mkdir()
        marker = self.claude / 'existing-agent'
        marker.write_text('untouched')
        self.run_cli('--target', 'codex')
        self.run_cli('--target', 'codex', '--check')
        self.assertEqual(list(self.claude.iterdir()), [marker])
        self.assertEqual(marker.read_text(), 'untouched')
        for profile in (self.codex / 'agents').glob('*.toml'):
            self.assertFalse(profile.is_symlink())
        self.assertFalse((self.codex / 'skills').exists())

    def test_both_and_idempotence(self):
        self.run_cli('--target', 'both')
        receipt = self.receipt()
        original = receipt.read_bytes()
        self.run_cli('--target', 'both')
        self.assertEqual(receipt.read_bytes(), original)
        self.run_cli('--target', 'both', '--check')
        self.assertEqual(os.readlink(self.claude / 'skills/scientific-workflow'),
                         os.readlink(self.agents / 'skills/scientific-workflow'))

    def test_dry_run_has_no_writes(self):
        self.run_cli('--target', 'both', '--dry-run')
        self.assertFalse(self.state.exists())
        for target in (self.claude, self.codex, self.agents):
            self.assertFalse(target.exists())

    def test_late_conflict_blocks_every_destination(self):
        path = self.claude / 'agents/scientific_worker.md'
        path.parent.mkdir(parents=True)
        path.write_text('unrelated worker')
        self.run_cli(ok=False)
        self.assertFalse((self.claude / 'skills').exists())
        self.assertEqual(list(path.parent.iterdir()), [path])
        self.assertEqual(path.read_text(), 'unrelated worker')
        self.assertFalse(self.state.exists())

    def test_migration_and_full_rollback(self):
        skill, profile = self.preexisting()
        manual = self.base / 'SCIENTIFIC_AGENT_WORKFLOW.md'
        manual.write_text('old manual')
        self.run_cli('--target', 'codex', '--migrate', '--legacy-manual', str(manual))
        self.assertTrue(skill.is_symlink())
        self.run_cli('--target', 'codex', '--check', '--legacy-manual', str(manual))
        receipt = self.receipt()
        record = json.loads(receipt.read_text())
        self.assertEqual(record['status'], 'complete')
        for entry in record['entries']:
            if entry.get('backup'):
                self.assertNotIn('/skills/', entry['backup'])
                self.assertNotIn('/agents/', entry['backup'].split('/.scientific-workflow-backups/')[0])
        self.run_cli('--rollback', str(receipt))
        self.assertFalse(skill.is_symlink())
        self.assertEqual((skill / 'SKILL.md').read_text(), 'prior Codex skill')
        self.assertEqual(profile.read_text(), 'prior reviewer')
        self.assertEqual(manual.read_text(), 'old manual')
        self.assertEqual(list(profile.parent.glob('*.toml')), [profile])

    def test_drift_blocks_rollback_without_partial_restoration(self):
        skill, profile = self.preexisting()
        self.run_cli('--target', 'codex', '--migrate')
        profile.write_text('later edit')
        self.run_cli('--rollback', str(self.receipt()), ok=False)
        self.assertTrue(skill.is_symlink())
        self.assertEqual(profile.read_text(), 'later edit')

    def test_backup_drift_blocks_rollback(self):
        self.preexisting()
        self.run_cli('--target', 'codex', '--migrate')
        receipt = self.receipt()
        record = json.loads(receipt.read_text())
        backup = next(Path(e['backup']) for e in record['entries']
                      if e.get('backup') and e['before']['type'] == 'file')
        backup.write_text('later backup edit')
        self.run_cli('--rollback', str(receipt), ok=False)
        self.assertTrue((self.agents / 'skills/scientific-workflow').is_symlink())

    def test_broken_symlink_conflict_can_restore(self):
        path = self.claude / 'agents/scientific_worker.md'
        path.parent.mkdir(parents=True)
        path.symlink_to(self.base / 'missing')
        self.run_cli(ok=False)
        self.run_cli('--migrate')
        self.run_cli('--rollback', str(self.receipt()))
        self.assertEqual(os.readlink(path), str(self.base / 'missing'))
        self.assertFalse(path.exists())

    def test_uninstall_preserves_unrelated_files(self):
        self.run_cli()
        profile = self.claude / 'agents/scientific_worker.md'
        profile.unlink()
        profile.write_text('user worker')
        self.run_cli('--uninstall')
        self.assertEqual(profile.read_text(), 'user worker')
        self.assertFalse((self.claude / 'skills/scientific-workflow').exists())

    def test_codex_uninstall_requires_receipt(self):
        self.run_cli('--target', 'codex')
        self.run_cli('--target', 'codex', '--uninstall', ok=False)
        self.run_cli('--target', 'codex', '--check')

    def test_profile_drift_is_detected(self):
        self.run_cli('--target', 'codex')
        (self.codex / 'agents/scientific_worker.toml').write_text('later change')
        self.run_cli('--target', 'codex', '--check', ok=False)
        self.run_cli('--target', 'codex', ok=False)

    def test_missing_source_blocks_install(self):
        (self.repo / 'agents/codex/scientific_worker.toml').unlink()
        self.run_cli('--target', 'codex', ok=False)
        self.assertFalse(self.state.exists())
        self.assertFalse(self.agents.exists())

    def test_injected_partial_copy_failure_restores_all(self):
        skill, profile = self.preexisting()
        spec = importlib.util.spec_from_file_location('tested_install', self.repo / 'scripts/install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        copy2 = module.shutil.copy2

        def failing_copy(src, dst):
            if Path(src).name == 'scientific_reviewer.toml':
                Path(dst).write_text('partial write')
                raise OSError('injected I/O failure')
            return copy2(src, dst)

        with patch.dict(os.environ, self.env), patch.object(module.shutil, 'copy2', failing_copy), \
             patch('sys.argv', ['install', '--target', 'codex', '--migrate', '--state-dir', str(self.state)]):
            self.assertEqual(module.main(), 1)
        self.assertEqual((skill / 'SKILL.md').read_text(), 'prior Codex skill')
        self.assertEqual(profile.read_text(), 'prior reviewer')
        self.assertFalse(skill.is_symlink())
        self.assertEqual(list(profile.parent.glob('*.toml')), [profile])
        self.assertEqual(json.loads(self.receipt().read_text())['status'], 'failed_restored')

    def test_failure_recovery_preserves_intervening_destination_edit(self):
        skill, profile = self.preexisting()
        spec = importlib.util.spec_from_file_location('concurrent_install', self.repo / 'scripts/install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        copy2 = module.shutil.copy2
        edited = self.codex / 'agents/scientific_analyst.toml'

        def edit_then_fail(src, dst):
            if Path(src).name == 'scientific_reviewer.toml':
                edited.write_text('concurrent work must survive')
                Path(dst).write_text('partial temporary write')
                raise OSError('injected later failure')
            return copy2(src, dst)

        with patch.dict(os.environ, self.env), patch.object(module.shutil, 'copy2', edit_then_fail), \
             patch('sys.argv', ['install', '--target', 'codex', '--migrate', '--state-dir', str(self.state)]):
            self.assertEqual(module.main(), 1)
        self.assertEqual(edited.read_text(), 'concurrent work must survive')
        self.assertEqual((skill / 'SKILL.md').read_text(), 'prior Codex skill')
        self.assertEqual(profile.read_text(), 'prior reviewer')
        record = json.loads(self.receipt().read_text())
        self.assertEqual(record['status'], 'failed_conflicts')
        self.assertTrue(any(str(edited) in msg for msg in record['conflicts']))
        self.assertFalse(list(self.base.rglob('*.workflow-install-*')))

    def test_failure_recovery_preserves_intervening_backup_edit(self):
        skill, profile = self.preexisting()
        spec = importlib.util.spec_from_file_location('backup_install', self.repo / 'scripts/install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        copy2 = module.shutil.copy2

        def edit_backup_then_fail(src, dst):
            if Path(src).name == 'scientific_reviewer.toml':
                backup = next(self.agents.glob('.scientific-workflow-backups/*/scientific-workflow/SKILL.md'))
                backup.write_text('concurrent backup edit')
                raise OSError('injected later failure')
            return copy2(src, dst)

        with patch.dict(os.environ, self.env), patch.object(module.shutil, 'copy2', edit_backup_then_fail), \
             patch('sys.argv', ['install', '--target', 'codex', '--migrate', '--state-dir', str(self.state)]):
            self.assertEqual(module.main(), 1)
        self.assertTrue(skill.is_symlink())
        backup = next(self.agents.glob('.scientific-workflow-backups/*/scientific-workflow/SKILL.md'))
        self.assertEqual(backup.read_text(), 'concurrent backup edit')
        self.assertEqual(json.loads(self.receipt().read_text())['status'], 'failed_conflicts')

    def test_destination_overlap_rejected(self):
        self.env['CLAUDE_HOME'] = str(self.agents)
        self.run_cli('--target', 'both', ok=False)
        self.assertFalse(self.state.exists())

    def test_parent_file_blocks_before_any_mutation(self):
        self.codex.mkdir()
        (self.codex / 'agents').write_text('parent is a file')
        self.run_cli('--target', 'both', ok=False)
        self.assertFalse(self.claude.exists())
        self.assertFalse(self.state.exists())

    def test_aliasing_runtime_homes_is_rejected(self):
        self.agents.mkdir()
        self.claude.symlink_to(self.agents, target_is_directory=True)
        self.run_cli('--target', 'both', ok=False)
        self.assertFalse((self.agents / 'skills').exists())
        self.assertFalse(self.state.exists())

    def test_legacy_manual_requires_codex(self):
        self.run_cli('--legacy-manual', str(self.base / 'manual'), ok=False)
        self.assertFalse(self.state.exists())

    def test_rollback_does_not_remove_preexisting_matching_profiles(self):
        self.codex.joinpath('agents').mkdir(parents=True)
        profile = self.codex / 'agents/scientific_worker.toml'
        shutil.copy2(self.repo / 'agents/codex' / profile.name, profile)
        original = profile.read_bytes()
        self.run_cli('--target', 'codex')
        self.run_cli('--rollback', str(self.receipt()))
        self.assertEqual(profile.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
