crashmanager
============

This software simulates several crash scenarios on Oracle database: so you can test your backup strategy, your restore and recovery scripts, your RMAN skills and be more prepared when a real crash happens on your system.

To test your RMAN skills you first need to install the "Database App Development VM".
Follow the Setup instructions provided by Oracle at this link: http://www.oracle.com/technetwork/database/enterprise-edition/databaseappdev-vm-161299.html

Completed the setup, start the new virtual machine and when a terminal window appears execute the following commands, providing the root password (oracle):
su -
wget --no-check-certificate https://raw.githubusercontent.com/MarcoVigelini/crashmanager/master/install_pyside_sandbox.sh
chmod +x install_pyside_sandbox.sh

Run install_pyside_sandbox.sh file:
./install_pyside_sandbox.sh

When the script finishes to run (if I first shutdown the database it takes about 130 minutes to complete), execute from the terminal window:
su - oracle

Once logged in as oracle user issue:
python crashmanager/crashmanager.py

If your oracle user is missing some environment variables remember to load them using:
source /u01/oracle/set_pyside_sandbox_env.sh
