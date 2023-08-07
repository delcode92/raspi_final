#!/bin/bash
# yesnobox.sh - An inputbox demon shell script
OUTPUT="/tmp/input.txt"

# create empty file
>$OUTPUT

# Purpose - say hello to user 
#  $1 -> name (set default to 'anonymous person')
function sayhello(){
	local n=${@-"anonymous person"}
	#display it
	dialog --title "Hello" --clear --msgbox "Hello ${n}, let us be friends!" 10 41
}

function writeToSpec(){
spec_str=$(cat << EOF
# -*- mode: python ; coding: utf-8 -*-\n

block_cipher = None\n


a = Analysis(\n
    ['GPIO_OPTIMIZED.py'],\n
    pathex=[],\n
    binaries=[],\n
    datas=[],\n
    hiddenimports=['$1', '$2'],
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

# cleanup  - add a trap that will remove $OUTPUT
# if any of the signals - SIGHUP SIGINT SIGTERM it received.
trap "rm $OUTPUT; exit" SIGHUP SIGINT SIGTERM

# show an inputbox
dialog --title "Inputbox - To take input from you" \
--backtitle "Linux Shell Script Tutorial Example" \
--inputbox "Enter your name " 8 60 2>$OUTPUT

# get response
respose=$?

# get data stored in $OUPUT using input redirection
# echo $(<$OUTPUT)
name=$(<$OUTPUT)

# make a decsion 
case $respose in
  0) 
  	# sayhello ${name}
	writeToSpec $name "file_name_2"
  	;;
  1) 
  	echo "Cancel pressed." 
  	;;
  255) 
   echo "[ESC] key pressed."
esac

# remove $OUTPUT file
rm $OUTPUT