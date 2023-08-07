#!/bin/sh

#define parameters which are passed in.
LIB1=$1
LIB2=$2

#define the template.
# cat  << EOF
# This is my template.
# Port is $PORT
# Domain is $DOMAIN
# EOF
function gen(){
spec_str=$(cat << EOF
# -*- mode: python ; coding: utf-8 -*-\n

block_cipher = None\n


a = Analysis(\n
    ['GPIO_OPTIMIZED.py'],\n
    pathex=[],\n
    binaries=[],\n
    datas=[],\n
    hiddenimports=['$LIB1', '$LIB2'],
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
    [],
    exclude_binaries=True,
    name='GPIO_SERVICE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GPIO_OPTIMIZED',
)
EOF)

echo $spec_str > result.spec
echo "selesai ..."

}

echo "before ..."
gen
echo "after ..."

