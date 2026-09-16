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
        self.temp = tempfile.TemporaryDirectory(prefix='icegem-installer-test-')
        self.root = Path(self.temp.name)
        self.home = self.root / 'user'
        self.home.mkdir()
        self.package = self.root / 'package'
        for name in install.NAMES:
            target = self.package / 'themes' / name
            (target / 'cursors').mkdir(parents=True)
            (target / '.icegem-linux').write_text(install.OWNER)
            (target / 'cursors/left_ptr').write_bytes(b'fixture')
        self.values = {'cursor-theme': "'Original'", 'cursor-size': '24'}
        self.patches = [patch.object(install, 'HERE', self.package),
                        patch.dict(os.environ, {'XDG_DATA_HOME': str(self.home / '.local/share'), 'XDG_STATE_HOME': str(self.home / '.local/state')}),
                        patch.object(install, 'settings', side_effect=lambda: self.values.copy()),
                        patch.object(install, 'set_values', side_effect=lambda values: self.values.update(values))]
        for p in self.patches:
            p.start()
        self.args = SimpleNamespace(color='IceBlue', mode='animated', size=32, all=False, no_apply=False, action='install')

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.temp.cleanup()

    def test_install_switch_restore_uninstall(self):
        install.perform(self.args, self.home)
        baseline = self.home / '.local/state/IceGem-Linux/before-icegem.json'
        original = baseline.read_bytes()
        self.assertEqual(self.values['cursor-theme'], "'IceGem-IceBlue-Animated'")
        self.args.color = 'Violet'
        self.args.mode = 'static'
        install.perform(self.args, self.home)
        self.assertEqual(self.values['cursor-theme'], "'IceGem-Violet-Static'")
        self.assertEqual(baseline.read_bytes(), original)
        self.args.action = 'restore'
        install.perform(self.args, self.home)
        self.assertEqual(self.values, {'cursor-theme': "'Original'", 'cursor-size': '24'})
        self.args.action = 'uninstall'
        install.perform(self.args, self.home)
        self.assertFalse((self.home / '.local/share/icons/IceGem-Violet-Static').exists())
        self.assertTrue(list((self.home / '.local/state/IceGem-Linux/removed').glob('*/IceGem-Violet-Static')))

    def test_refuse_unowned_directory(self):
        target = self.home / '.local/share/icons/IceGem-IceBlue-Animated'
        target.mkdir(parents=True)
        (target / 'user-file').write_text('preserve')
        with self.assertRaises(RuntimeError):
            install.perform(self.args, self.home)
        self.assertEqual((target / 'user-file').read_text(), 'preserve')

    def test_failed_apply_rolls_back(self):
        install.perform(self.args, self.home)
        previous = self.values.copy()
        self.args.color = 'Mint'
        def update(value):
            if value['cursor-theme'] == "'IceGem-Mint-Animated'":
                raise RuntimeError('simulated desktop rejection')
            self.values.update(value)
        with patch.object(install, 'set_values', side_effect=update):
            with self.assertRaises(RuntimeError):
                install.perform(self.args, self.home)
        self.assertEqual(previous, self.values)
        self.assertFalse((self.home / '.local/share/icons/IceGem-Mint-Animated').exists())
        self.assertFalse((self.home / '.icons/IceGem-Mint-Animated').is_symlink())

    def test_no_apply_all_colors(self):
        self.args.all = True
        self.args.no_apply = True
        install.perform(self.args, self.home)
        self.assertEqual(self.values['cursor-theme'], "'Original'")
        self.assertEqual(len(list((self.home / '.local/share/icons').glob('IceGem-*'))), 10)
        self.assertFalse((self.home / '.local/state/IceGem-Linux/before-icegem.json').exists())


if __name__ == '__main__':
    unittest.main()
