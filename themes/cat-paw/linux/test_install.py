"""Installer integration tests use a temporary fake home and mocked desktop settings."""
from pathlib import Path
from types import SimpleNamespace
import json
import os
import tempfile
import unittest
from unittest.mock import patch
import install


class InstallerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='catpaw-installer-test-')
        self.root = Path(self.temp.name)
        self.home = self.root / 'user'
        self.home.mkdir()
        self.package = self.root / 'package'
        for name in install.NAMES:
            target = self.package / 'themes' / name
            (target / 'cursors').mkdir(parents=True)
            (target / '.catpaw-linux').write_text(install.OWNER)
            (target / 'cursors/left_ptr').write_bytes(b'fixture')
        self.values = {'cursor-theme': "'Original'", 'cursor-size': '24'}
        self.patches = [patch.object(install, 'HERE', self.package),
                        patch.dict(os.environ, {'XDG_DATA_HOME': str(self.home / '.local/share'), 'XDG_STATE_HOME': str(self.home / '.local/state')}),
                        patch.object(install, 'settings', side_effect=lambda: self.values.copy()),
                        patch.object(install, 'set_values', side_effect=lambda values: self.values.update(values))]
        for p in self.patches:
            p.start()
        self.args = SimpleNamespace(color='Pink', mode='animated', size=32, all=False, no_apply=False, action='install')

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.temp.cleanup()

    def test_install_switch_restore_uninstall(self):
        install.perform(self.args, self.home)
        baseline = self.home / '.local/state/CatPaw-Linux/before-catpaw.json'
        original = baseline.read_bytes()
        self.assertEqual(self.values['cursor-theme'], "'CatPaw-Pink-Animated'")
        self.args.color = 'Coffee'
        self.args.mode = 'static'
        install.perform(self.args, self.home)
        self.assertEqual(self.values['cursor-theme'], "'CatPaw-Coffee-Static'")
        self.assertEqual(baseline.read_bytes(), original)
        self.args.action = 'restore'
        install.perform(self.args, self.home)
        self.assertEqual(self.values, {'cursor-theme': "'Original'", 'cursor-size': '24'})
        self.args.action = 'uninstall'
        install.perform(self.args, self.home)
        self.assertFalse((self.home / '.local/share/icons/CatPaw-Coffee-Static').exists())
        self.assertTrue(list((self.home / '.local/state/CatPaw-Linux/removed').glob('*/CatPaw-Coffee-Static')))

    def test_refuse_unowned_directory(self):
        target = self.home / '.local/share/icons/CatPaw-Pink-Animated'
        target.mkdir(parents=True)
        (target / 'user-file').write_text('preserve')
        with self.assertRaises(RuntimeError):
            install.perform(self.args, self.home)
        self.assertEqual((target / 'user-file').read_text(), 'preserve')

    def test_failed_apply_rolls_back(self):
        install.perform(self.args, self.home)
        previous = self.values.copy()
        self.args.color = 'Coffee'
        def update(value):
            if value['cursor-theme'] == "'CatPaw-Coffee-Animated'":
                raise RuntimeError('simulated desktop rejection')
            self.values.update(value)
        with patch.object(install, 'set_values', side_effect=update):
            with self.assertRaises(RuntimeError):
                install.perform(self.args, self.home)
        self.assertEqual(previous, self.values)
        self.assertFalse((self.home / '.local/share/icons/CatPaw-Coffee-Animated').exists())
        self.assertFalse((self.home / '.icons/CatPaw-Coffee-Animated').is_symlink())

    def test_no_apply_all_colors(self):
        self.args.all = True
        self.args.no_apply = True
        install.perform(self.args, self.home)
        self.assertEqual(self.values['cursor-theme'], "'Original'")
        self.assertEqual(len(list((self.home / '.local/share/icons').glob('CatPaw-*'))), 4)
        self.assertFalse((self.home / '.local/state/CatPaw-Linux/before-catpaw.json').exists())


    def test_no_apply_can_uninstall_without_backup_or_settings(self):
        self.args.no_apply = True
        with patch.object(install, 'settings', side_effect=AssertionError('must not read desktop')):
            install.perform(self.args, self.home)
            self.args.action = 'uninstall'
            install.perform(self.args, self.home)
        self.assertFalse((self.home / '.local/share/icons/CatPaw-Pink-Animated').exists())
        self.assertEqual(self.values['cursor-theme'], "'Original'")

    def test_active_uninstall_restores_initial_theme(self):
        install.perform(self.args, self.home)
        self.args.action = 'uninstall'
        install.perform(self.args, self.home)
        self.assertEqual(self.values, {'cursor-theme': "'Original'", 'cursor-size': '24'})

    def test_uninstall_preserves_later_theme_and_icegem_files(self):
        install.perform(self.args, self.home)
        other = self.home / '.local/share/icons/IceGem-IceBlue-Animated'
        other.mkdir(); (other/'sentinel').write_text('untouched')
        self.values['cursor-theme'] = "'IceGem-IceBlue-Animated'"
        self.args.action = 'uninstall'
        install.perform(self.args, self.home)
        self.assertEqual(self.values['cursor-theme'], "'IceGem-IceBlue-Animated'")
        self.assertEqual((other/'sentinel').read_text(), 'untouched')

    def test_reject_source_alias_escape_before_install(self):
        source = self.package / 'themes/CatPaw-Pink-Animated/cursors'
        (source/'bad-alias').symlink_to(self.root / 'outside')
        with self.assertRaises(RuntimeError): install.perform(self.args, self.home)
        self.assertFalse((self.home / '.local/share/icons/CatPaw-Pink-Animated').exists())
        self.assertEqual(self.values['cursor-theme'], "'Original'")

    def test_uninstall_move_failure_rolls_back_files_and_settings(self):
        install.perform(self.args, self.home)
        current = self.values.copy()
        original_move = install.shutil.move
        def fail_second(source, destination):
            if str(source).endswith('CatPaw-Pink-Static') and 'removed' in str(destination):
                raise OSError('simulated archive failure')
            return original_move(source, destination)
        self.args.action = 'uninstall'
        with patch.object(install.shutil, 'move', side_effect=fail_second):
            with self.assertRaises(OSError): install.perform(self.args, self.home)
        self.assertEqual(self.values, current)
        for name in ('CatPaw-Pink-Animated','CatPaw-Pink-Static'):
            self.assertTrue((self.home / '.local/share/icons' / name).is_dir())
            self.assertTrue((self.home / '.icons' / name).is_symlink())

    def test_icon_parent_symlink_escape_is_rejected(self):
        parent=self.home / '.local/share'; parent.mkdir(parents=True)
        outside=self.root/'outside'; outside.mkdir()
        (parent/'icons').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(RuntimeError): install.perform(self.args, self.home)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
