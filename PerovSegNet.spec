# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PerovSegNet desktop application.
This ensures all necessary files and dependencies are included.
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

block_cipher = None

# Collect all application files
app_datas = [
    ('app', 'app'),  # Include entire app directory
]

# Collect Streamlit metadata - THIS IS CRITICAL!
# copy_metadata includes the .dist-info directory that importlib.metadata needs
app_datas += copy_metadata('streamlit')
app_datas += copy_metadata('altair')
app_datas += copy_metadata('pandas')
app_datas += copy_metadata('numpy')
app_datas += copy_metadata('pillow')
app_datas += copy_metadata('packaging')

# Collect Streamlit data files
streamlit_datas = collect_data_files('streamlit', include_py_files=True)
altair_datas = collect_data_files('altair')
app_datas.extend(streamlit_datas)
app_datas.extend(altair_datas)

# Collect all Streamlit submodules
streamlit_imports = collect_submodules('streamlit')

# Hidden imports that PyInstaller might miss
hiddenimports = [
    # App modules
    'app.config',
    'app.processing',
    'app.processing.security',
    'app.processing.image_processor',
    'app.processing.model',
    'app.ui',
    'app.ui.components',
    # Streamlit dependencies
    'streamlit.web.cli',
    'streamlit.web.bootstrap',
] + streamlit_imports

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=app_datas,
    hiddenimports=hiddenimports,
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
    name='PerovSegNet',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False to hide console window (change after testing)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.icns',  # Uncomment and provide icon file if available
)
