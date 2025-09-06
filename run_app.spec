# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import copy_metadata, collect_data_files
block_cipher = None

app_datas = [
    ('app.py', '.'),
    ('download_data.py', '.'),
    ('process_data.py', '.')
]

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=copy_metadata('streamlit') + collect_data_files('streamlit')+ app_datas,
    hiddenimports=['streamlit.runtime.scriptrunner.magic_funcs'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Dota2AnalyticsHub',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
