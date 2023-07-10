# remove files
rm config.cfg GPIO_OPTIMIZED.py restart.sh libxcb.so.1
chmod 777 restart.sh

# copy files from widget

wget https://raw.githubusercontent.com/delcode92/raspi_final/raw/main/config.cfg
wget https://raw.githubusercontent.com/delcode92/raspi_final/raw/main/GPIO_OPTIMIZED.py
wget https://raw.githubusercontent.com/delcode92/raspi_final/raw/main/restart.sh
wget https://github.com/delcode92/raspi_final/raw/main/libxcb.so.1

# run pyinstaller with .spec
pyinstaller GPIO_OPTIMIZED.spec

# copy config.cfg & libxcbd.so to  dist/GPIO_TESTER_PULL_DOWN/
cp /opt/selinux/pyinstaller_compiler/config.cfg /opt/selinux/pyinstaller_compiler/dist/GPIO_OPTIMIZED
cp /opt/selinux/pyinstaller_compiler/libxcb.so.1 /opt/selinux/pyinstaller_compiler/dist/GPIO_OPTIMIZED
cp /opt/selinux/pyinstaller_compiler/restart.sh /opt/selinux/pyinstaller_compiler/dist/GPIO_OPTIMIZED



# helper
mkdir /opt/selinux/pyinstaller_compiler/dist/GPIO_OPTIMIZED/helper
cd /opt/selinux/pyinstaller_compiler/dist/GPIO_OPTIMIZED/helper

rm blinking.py pin_on.py pin_off.py show_pin_value.py

wget https://raw.githubusercontent.com/delcode92/raspi_final/raw/main/helper/blinking.py
wget https://raw.githubusercontent.com/delcode92/raspi_final/raw/main/helper/pin_on.py
wget https://raw.githubusercontent.com/delcode92/raspi_final/raw/main/helper/pin_off.py
wget https://raw.githubusercontent.com/delcode92/raspi_final/raw/main/helper/show_pin_value.py

# back to target dir
cd  /opt/selinux/pyinstaller_compiler/dist/
