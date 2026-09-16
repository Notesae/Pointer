"""Per-user Zorin/GNOME installer. No root, no shell-evaluated backups."""
from pathlib import Path
import argparse
import datetime
import fcntl
import json
import os
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
COLORS = ('IceBlue', 'Violet', 'RosePink', 'Mint', 'Amber')
NAMES = tuple(f'IceGem-{c}-{m}' for c in COLORS for m in ('Animated', 'Static'))
OWNER = 'IceGem-Linux-v1'
SCHEMA = 'org.gnome.desktop.interface'


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.PIPE).strip()


def settings():
    if not shutil.which('gsettings'):
        raise RuntimeError('找不到 gsettings；请在 Zorin 图形桌面的终端运行，或加 --no-apply 仅安装。')
    result = {}
    for key in ('cursor-theme', 'cursor-size'):
        if run('gsettings', 'writable', SCHEMA, key) != 'true':
            raise RuntimeError(f'{key} 不可写；请使用当前桌面用户，不要 sudo。')
        result[key] = run('gsettings', 'get', SCHEMA, key)
    return result


def set_values(values):
    for key in ('cursor-theme', 'cursor-size'):
        run('gsettings', 'set', SCHEMA, key, values[key])
    actual = {k: run('gsettings', 'get', SCHEMA, k) for k in values}
    if actual != values:
        raise RuntimeError('gsettings 回读不一致，配置可能被桌面策略覆盖。')


def color_arg(value):
    key = value.lower().replace('-', '')
    for color in COLORS:
        if color.lower() == key:
            return color
    raise argparse.ArgumentTypeError('颜色可选：' + ', '.join(COLORS))


def safe_base(value, home):
    path = Path(value)
    if not path.is_absolute() or not path.resolve().is_relative_to(home.resolve()) or path.resolve() == home.resolve():
        raise RuntimeError('为避免误操作，XDG 用户目录必须为用户主目录内的绝对路径。')
    return path


def owned(path):
    marker = path / '.icegem-linux'
    return path.is_dir() and not path.is_symlink() and marker.is_file() and not marker.is_symlink() and marker.read_text().strip() == OWNER


def backup_values(path, values):
    if not path.exists():
        # Exclusive creation preserves the very first backup across color changes.
        with path.open('x', encoding='utf-8') as handle:
            json.dump({'owner': OWNER, 'settings': values}, handle, indent=2)


def read_backup(path):
    data = json.loads(path.read_text())
    values = data.get('settings', {})
    if data.get('owner') != OWNER or set(values) != {'cursor-theme', 'cursor-size'} or not all(isinstance(v, str) for v in values.values()):
        raise RuntimeError('备份格式不正确，未执行恢复。')
    return values


def perform(args, home):
    data = safe_base(os.environ.get('XDG_DATA_HOME', str(home / '.local/share')), home)
    state = safe_base(os.environ.get('XDG_STATE_HOME', str(home / '.local/state')), home) / 'IceGem-Linux'
    icons, legacy = data / 'icons', home / '.icons'
    baseline = state / 'before-icegem.json'
    if legacy.is_symlink():
        raise RuntimeError('~/.icons 是符号链接。为避免修改未知位置，请按 README 手动安装。')
    state.mkdir(parents=True, exist_ok=True)
    with (state / 'install.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        current = settings() if not args.no_apply or args.action != 'install' else None
        if args.action in ('restore', 'uninstall'):
            if not baseline.is_file():
                raise RuntimeError('未找到首次安装前的备份。未修改系统。')
            original = read_backup(baseline)
            targets = []
            for name in NAMES:
                target, link = icons / name, legacy / name
                if target.exists() or target.is_symlink():
                    if not owned(target):
                        raise RuntimeError(f'目录并非本安装器所有，停止：{target}')
                    targets.append(target)
                if link.exists() or link.is_symlink():
                    if not link.is_symlink() or link.resolve() != target.resolve():
                        raise RuntimeError(f'兼容路径归属不符，停止：{link}')
            try:
                set_values(original)
            except Exception:
                set_values(current)
                raise
            if args.action == 'uninstall':
                archive = state / 'removed' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
                archive.mkdir(parents=True)
                for target in targets:
                    link = legacy / target.name
                    if link.is_symlink():
                        link.unlink()
                    shutil.move(str(target), archive / target.name)
                shutil.move(str(baseline), archive / baseline.name)
                print(f'已恢复原光标。主题文件已移至可恢复归档：{archive}')
            else:
                print('已恢复首次安装前的主题和大小，IceGem 文件仍保留。')
            return

        chosen = COLORS if args.all else (args.color,)
        names = [f'IceGem-{c}-{m}' for c in chosen for m in ('Animated', 'Static')]
        selected = f'IceGem-{args.color}-{args.mode.title()}'
        # Check every source and destination before altering installed themes.
        for name in names:
            source, target, link = HERE / 'themes' / name, icons / name, legacy / name
            if not owned(source) or not (source / 'cursors/left_ptr').is_file():
                raise RuntimeError(f'主题文件不完整：{source}。请先完整解压安装包。')
            for item in source.rglob('*'):
                if item.is_symlink() and not item.resolve().is_relative_to(source.resolve()):
                    raise RuntimeError('主题包含越界链接，停止。')
            if (target.exists() or target.is_symlink()) and not owned(target):
                raise RuntimeError(f'拒绝覆盖非本安装器的目录：{target}')
            if link.exists() or link.is_symlink():
                if not link.is_symlink() or link.resolve() != target.resolve():
                    raise RuntimeError(f'拒绝覆盖已有兼容目录：{link}')
        icons.mkdir(parents=True, exist_ok=True)
        legacy.mkdir(parents=True, exist_ok=True)
        archive = state / 'updates' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        archive.mkdir(parents=True)
        staged, installed, old, new_links = [], [], [], []
        if current is not None:
            backup_values(baseline, current)
        try:
            for name in names:
                stage = Path(tempfile.mkdtemp(prefix='.icegem-stage-', dir=icons))
                staged.append(stage)
                shutil.copytree(HERE / 'themes' / name, stage, dirs_exist_ok=True, symlinks=True)
                target, link = icons / name, legacy / name
                if target.exists():
                    previous = archive / name
                    shutil.move(str(target), previous)
                    old.append((previous, target))
                stage.rename(target)
                installed.append(target)
                if not link.is_symlink():
                    link.symlink_to(target, target_is_directory=True)
                    new_links.append(link)
            if current is not None:
                set_values({'cursor-theme': repr(selected), 'cursor-size': str(args.size)})
            print(f'已安装：{", ".join(names)}')
            if current is not None:
                print(f'已应用并回读确认：{selected}，{args.size}px。')
            else:
                print('仅安装文件，未改动桌面主题。')
            print('若部分窗口未更新，请完全重启该应用；必要时注销后重新登录。')
        except Exception:
            for link in new_links:
                if link.is_symlink():
                    link.unlink()
            for target in installed:
                if target.exists():
                    shutil.move(str(target), archive / ('failed-' + target.name))
            for previous, target in reversed(old):
                shutil.move(str(previous), target)
            if current is not None:
                try:
                    set_values(current)
                except Exception as error:
                    print(f'桌面配置回滚未成功，请手动恢复。备份：{baseline}；{error}')
            raise
        finally:
            for stage in staged:
                if stage.exists():
                    shutil.rmtree(stage)  # Only freshly-created temporary staging directories.


def main():
    parser = argparse.ArgumentParser(description='IceGem Linux / Zorin OS GNOME 光标安装器，无需 sudo')
    parser.add_argument('--color', type=color_arg, default='IceBlue')
    parser.add_argument('--mode', choices=('animated', 'static'), default='animated')
    parser.add_argument('--size', type=int, choices=(24, 32, 48, 64, 96), default=32)
    parser.add_argument('--all', action='store_true', help='安装全部五色，应用 --color 选中的颜色')
    parser.add_argument('--no-apply', action='store_true', help='仅安装文件，不修改桌面配置')
    parser.add_argument('--action', choices=('install', 'restore', 'uninstall'), default='install')
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.exit(1, '请用当前桌面用户运行，不要 sudo。\n')
    if args.no_apply and args.action != 'install':
        parser.error('--no-apply 只能用于安装')
    try:
        perform(args, Path.home())
    except (Exception, KeyboardInterrupt) as error:
        parser.exit(1, f'操作未完成：{error}\n')


if __name__ == '__main__':
    main()
