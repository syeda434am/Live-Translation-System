# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('com/mhire/assets', 'com/mhire/assets'), ('com/mhire/config', 'com/mhire/config'), ('com/mhire/services', 'com/mhire/services'), ('com/mhire/utils', 'com/mhire/utils'), ('com/mhire/visuals', 'com/mhire/visuals'), ('.env', '.')],
    hiddenimports=['onnxruntime', 'websockets', 'numpy', 'tkinter', 'dotenv'],
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
    [],
    exclude_binaries=True,
    name='Live_Translator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Live_Translator',
)
