# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/magic_qc/cli.py'],
    pathex=[],
    binaries=[],
    datas=[('/opt/dev/etd/magic_qc/.venv/lib/python3.12/site-packages/cv2/data', 'cv2/data'), ('src/magic_qc/management/config/facial/quality_standards_v2.json', 'magic_qc/management/config/facial')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='magic_qc',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
