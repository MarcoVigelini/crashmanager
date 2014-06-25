# Shell script to install PySide (the Python Qt bindings project) and other tools on Oracle Linux 6.5
# to successfully run Crashmanager
# 22/06/2014, Marco Vigelini
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi
if [ "`echo ${PWD} | grep crashmanager | wc -l`" == "1" ]; then
   echo "This script must be run outside a crashmanager directory" 1>&2
   echo "Copy this file (install_pyside_sandbox.sh) under the /root directory and then run it again as root" 1>&2
   exit 1
fi
ps -ef|grep PackageKit | grep -v grep | awk '{print $2}' | xargs kill -9
if rpm -q --quiet git ; then 
  echo "git already installed"
else
  yum install -y git
fi
# Adding the Extra Packages for Enterprise Linux (EPEL) repository
cd /tmp
wget http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
rpm -ivh epel-release-6-8.noarch.rpm
# Installing PySide from yum
yum install -y python-pyside
# Building PySide sandbox from source code
cd /u01/oracle
sudo -u oracle git clone https://github.com/PySide/BuildScripts
cd /u01/oracle/BuildScripts/
sudo -u oracle git submodule init
sudo -u oracle git submodule update
sed -i -e 's/install/install -y/' /u01/oracle/BuildScripts/dependencies.fedora.sh
./dependencies.fedora.sh 
# Credit for below patch is to: Afterthought Software Ltd
# Original patch is described here: http://afterthoughtsoftware.com/posts/PySide-on-Centos-6.3
# I've simply modified it using the echo command and few backslash characters
echo "diff --git a/build_and_install b/build_and_install
index 2beb51a..e04f7a3 100755
--- a/build_and_install
+++ b/build_and_install
@@ -51,6 +51,7 @@ for d in \"\${dirs[@]}\" ; do
         cmake .. -DCMAKE_INSTALL_PREFIX=\$PYSIDESANDBOXPATH \\
                  -DCMAKE_BUILD_TYPE=\$BUILD_TYPE \\
                  -DENABLE_ICECC=0 \\
+                 -DQT_PHONON_INCLUDE_DIR=/usr/include/phonon \\
                  \$PYSIDE_BS_CMAKE_FLAGS \\
             && make -j4 && make install || exit 1
     ) || exit 1" > /u01/oracle/BuildScripts/centos-pyside.patch
chown oracle.oracle /u01/oracle/BuildScripts/centos-pyside.patch
cd /u01/oracle/BuildScripts/
sudo -u oracle patch -p1 < /u01/oracle/BuildScripts/centos-pyside.patch
cd /u01/oracle/BuildScripts/
sudo -u oracle ./build_and_install
# Env settings 
echo "export PYSIDESANDBOXPATH=/u01/oracle/pkg/pyside-sandbox" > /u01/oracle/set_pyside_sandbox_env.sh
echo "export PATH=$PYSIDESANDBOXPATH/bin:$PATH" >> /u01/oracle/set_pyside_sandbox_env.sh
echo "export PYTHONPATH=$PYSIDESANDBOXPATH/lib64/python2.6/site-packages:$PYTHONPATH" >> /u01/oracle/set_pyside_sandbox_env.sh
echo "export LD_LIBRARY_PATH=/u01/app/oracle/product/12.1.0/dbhome_1/lib:$PYSIDESANDBOXPATH/lib:$LD_LIBRARY_PATH" >> /u01/oracle/set_pyside_sandbox_env.sh
echo "export PKG_CONFIG_PATH=$PYSIDESANDBOXPATH/lib/pkgconfig:$PKG_CONFIG_PATH" >> /u01/oracle/set_pyside_sandbox_env.sh
echo "export DYLD_LIBRARY_PATH=$PYSIDESANDBOXPATH/lib:$DYLD_LIBRARY_PATH" >> /u01/oracle/set_pyside_sandbox_env.sh
echo "export ORACLE_HOME=/u01/app/oracle/product/12.1.0/dbhome_1" >> /u01/oracle/set_pyside_sandbox_env.sh
chown oracle.oracle /u01/oracle/set_pyside_sandbox_env.sh
# Loading env settings
source /u01/oracle/set_pyside_sandbox_env.sh
ps -ef|grep PackageKit | grep -v grep | awk '{print $2}' | xargs kill -9
cd /tmp
wget http://dl.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm
rpm -ivh epel-release-6-8.noarch.rpm
# Installing Pip (Python Package Index, a tool for installing and managing Python packages)
yum -y install python-pip
# Installing cx_Oracle, Python extension module that enables access to Oracle databases
pip install cx_Oracle
if [ -d "/u01/oracle/crashmanager" ]; then
  rm -rf /u01/oracle/crashmanager
fi
cd /u01/oracle
# Getting crashmanager git repository
sudo -u oracle git clone https://github.com/MarcoVigelini/crashmanager
echo "source /u01/oracle/set_pyside_sandbox_env.sh" >> /u01/oracle/.bash_profile
