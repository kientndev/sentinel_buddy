# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['sentinel_buddy_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'groq',
        'groq._client',
        'groq._base_client',
        'groq._types',
        'groq._utils',
        'groq.resources',
        'pyautogui',
        'pystray',
        'PIL',
        'PIL._tkinter_finder',
    ],
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
    name='SentinelBuddy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed mode - no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
