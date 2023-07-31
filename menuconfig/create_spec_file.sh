#!/bin/bash

DIALOG_CANCEL=1
DIALOG_ESC=255
HEIGHT=0
WIDTH=0

display_result() {
  dialog --title "$1" \
    --no-collapse \
    --msgbox "$result" 0 0
}

while true; do
  exec 3>&1
  selection=$(dialog \
    --backtitle "System Information" \
    --title "Menu" \
    --clear \
    --cancel-label "Exit" \
    --menu "Please select:" $HEIGHT $WIDTH 4 \
    "1" "buildroot" \
    "2" "compile python" \
    "3" "Display Home Space Utilization" \
    2>&1 1>&3)
  exit_status=$?
  echo "data " $exit_status
  exec 3>&-
  case $exit_status in
    $DIALOG_CANCEL)
      clear
      echo "Program terminated."
      exit
      ;;
    $DIALOG_ESC)
      clear
      echo "Program aborted." >&2
      exit 1
      ;;
  esac
  case $selection in
    1 )
      # result=$(echo "masuk bro")
      # result=$(ls -l)
      # display_result "Buildroot setup"
      selection=$(dialog \
        --backtitle "another" \
        --title "another Menu" \
        --clear \
        --cancel-label "Exit" \
        --menu "Please select:" $HEIGHT $WIDTH 4 \
        "1" "xyz" \
        "2" "abc" \
        "3" "Display Home Space Utilization" \
        2>&1 1>&3)
      ;;
    2 )
      result=$(df -h)
      display_result "Disk Space"
      ;;
    3 )
      if [[ $(id -u) -eq 0 ]]; then
        result=$(du -sh /home/* 2> /dev/null)
        display_result "Home Space Utilization (All Users)"
      else
        result=$(du -sh $HOME 2> /dev/null)
        display_result "Home Space Utilization ($USER)"
      fi
      ;;
  esac
done
