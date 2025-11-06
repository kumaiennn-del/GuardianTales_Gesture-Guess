# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Gesture&Guess.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('bg.jpg', '.'),
        ('button.wav', '.'),
        ('gameover.wav', '.'),
        ('gamestart.wav', '.'),
        ('getpoint.wav', '.'),
        ('losepoint.wav', '.'),
        ('HYPixel11pxU-2.ttf', '.'),
        ('topics.json', '.'),
        ('pictures/*', 'pictures'),
        ('Gesture&Guess.ico', '.')
    ],
    hiddenimports=[],
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
    name='GestureGuessGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为 True 可显示控制台窗口（调试用）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Gesture&Guess.ico',
)