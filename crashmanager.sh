#!/bin/bash
# Marco V, March 27th 2009, Version 1.000.00
#

RANDOM=$$
UPPER_LIMIT=16
SUCCESS=0
FAIL=255

# Invalid user selection
invalid_choice()
{
ERRMSG="Invalid Menu Number... Please Try Again"
}

show_menu()
{
#clear
echo -e "\t\t\tCrash Scenario Manager"
echo -e "\t\t\t----------------------"
echo 
echo -e "\t\tChoose one of the following crash scenario:"
echo 
echo -e "\t\t\tLoss of a control file:\t\t\t\t\t[ 1]"
echo -e "\t\t\tLoss of all control files:\t\t\t\t[ 2]"
echo -e "\t\t\tLoss of a redo log file group member:\t\t\t[ 3]"
echo -e "\t\t\tLoss of a redo log file group:\t\t\t\t[ 4]"
echo -e "\t\t\tLoss of a non-system datafile:\t\t\t\t[ 5]"
echo -e "\t\t\tLoss of a temporary datafile:\t\t\t\t[ 6]"
echo -e "\t\t\tLoss of a SYSTEM datafile:\t\t\t\t[ 7]"
echo -e "\t\t\tLoss of an UNDO datafile:\t\t\t\t[ 8]"
echo -e "\t\t\tLoss of a Read-Only tablespace:\t\t\t\t[ 9]"
echo -e "\t\t\tLoss of an Index tablespace:\t\t\t\t[10]"
echo -e "\t\t\tLoss of all indexes in USERS tablespace:\t\t[11]"
echo -e "\t\t\tLoss of a non-system tablespace:\t\t\t[12]"
echo -e "\t\t\tLoss of a temporary tablespace:\t\t\t\t[13]"
echo -e "\t\t\tLoss of a SYSTEM tablespace:\t\t\t\t[14]"
echo -e "\t\t\tLoss of an UNDO tablespace:\t\t\t\t[15]"
echo -e "\t\t\tLoss of the password file:\t\t\t\t[16]"
echo -e "\t\t\tLoss of all datafiles:\t\t\t\t\t[17]"
echo -e "\t\t\tLoss of redo log member of a multiplexed group:\t\t[18]"
echo -e "\t\t\tLoss of all redo log members of an INACTIVE group:\t[19]"
echo -e "\t\t\tLoss of all redo log members of an ACTIVE group:\t[20]"
echo -e "\t\t\tLoss of all redo log members of CURRENT group:\t\t[21]"
echo 
echo -e "\t\t\tPerform a random crash scenario:\t\t\t[99]"
echo 
echo -e "\t\t\tExit:\t\t\t\t\t\t\t[ 0]"
echo 
echo $ERRMSG
echo 
echo -n "Enter the value number associated with the crash scenario you want to reproduce: "
}

exec_menu()
{
                # Execute one of the functions based
                # on the number entered by the user.
                case "$1" in
                        "1"  ) menu_id_01 ;;
                        "2"  ) menu_id_02 ;;
                        "3"  ) menu_id_03 ;;
                        "4"  ) menu_id_04 ;;
                        "5"  ) menu_id_05 ;;
                        "6"  ) menu_id_06 ;;
                        "7"  ) menu_id_07 ;;
                        "8"  ) menu_id_08 ;;
                        "9"  ) menu_id_09 ;;
                        "10" ) menu_id_10 ;;
                        "11" ) menu_id_11 ;;
                        "12" ) menu_id_12 ;;
                        "13" ) menu_id_13 ;;
                        "14" ) menu_id_14 ;;
                        "15" ) menu_id_15 ;;
                        "16" ) menu_id_16 ;;
                        "0" ) break ;;
                         *  ) invalid_choice ;;
                esac

}

kill_instance()
{
	smon_pid=$(ps -ef | grep smon | grep -v grep | awk '{print $2}')
	kill -9 "$smon_pid"
}

get_random_number()
{
RANDOM_NUMBER=$(( $RANDOM % $UPPER_LIMIT + 1 ))
return "$RANDOM_NUMBER"
}

# Remove files pointed from the array of file location
# starting from 0 to n (argument passed to the function)
remove_files() 
{
	ii=0
	file_renamed=$(date +%Y%m%d_%H%M%S).bck
	while ((ii < "$1"))
	do
		echo "mv ${ARRAY_OF_FILES[ii]} ${ARRAY_OF_FILES[ii]}.$file_renamed"
		mv "${ARRAY_OF_FILES[ii]}" "${ARRAY_OF_FILES[ii]}.$file_renamed"
		((ii = ii + 1))
	done
	return "$SUCCESS"
}

# Read content of tmp file
read_files()
{
	ii=0
	file_exist "$1"
	if [ "$?" -eq "$SUCCESS" ]
	then
		# Testing for presence of a second arg (how many lines do you want to read)
		if [ "$#" -eq "2" ]
		then
			# Reading exactly n lines of the file
	 		for filename in `seq $2`
			do
				read filename
				if [[ ! -z "$filename" && "$filename" != '' ]]
				then
					ARRAY_OF_FILES[$ii]=$filename
					((ii = ii + 1))
				fi
			done < "$1"
		else
			# Reading all lines of the file
			while read filename
			do
				if [[ ! -z "$filename" && "$filename" != '' ]]
				then
					ARRAY_OF_FILES[$ii]=$filename
					((ii = ii + 1))
				fi
			done < $1
		fi
	else
		return "$FAIL"
	fi
	return "$SUCCESS"
}

# Checking existence of tmp file
file_exist()
{
	if [[ -e "$1" ]]
	then
		return "$SUCCESS"
	fi
	return "$FAIL"
}

# Counts how many lines are present in the file
count_files()
{
	file_exist "$1"
	if [ "$?" -eq "$SUCCESS" ]
	then
		# Checking for Oracle errors (0 match found, 1 match not found) 
		# ORA-01034: ORACLE not available for example
		grep -q ORA- "$1"
		return_val=$?
		if [ "$return_val" -ne "$SUCCESS" ]
		then
			return $(echo $(wc -l < "$1"))
		fi
	fi
	return "$FAIL"
}



query_controlfiles()
{
$ORACLE_HOME/bin/sqlplus -s / as sysdba << EOF > /tmp/controlfile.tmp
set serveroutput on
set lines 180
set pages 1000
set feedback off
set echo off
set ver off
col name format a150

DECLARE
BEGIN
    FOR rec IN (select name from v\$controlfile)
    LOOP
        dbms_output.put_line(rec.name);
    END LOOP;
END;
/

set echo on
set feed on
set ver on
exit;
EOF
}

query_ns_datafiles()
{
$ORACLE_HOME/bin/sqlplus -s / as sysdba << EOF > /tmp/non_system_datafile.tmp
set serveroutput on
set lines 180
set pages 1000
set feedback off
set echo off
set ver off
col FILE_NAME format a150
col TABLESPACE_NAME format a30

DECLARE
BEGIN
    FOR rec IN (select FILE_NAME from dba_data_files where TABLESPACE_NAME='USERS' order by FILE_ID)
    LOOP
        dbms_output.put_line(rec.FILE_NAME);
    END LOOP;
END;
/

set echo on
set feed on
set ver on
exit;
EOF
}

query_temp_datafiles()
{
$ORACLE_HOME/bin/sqlplus -s / as sysdba << EOF > /tmp/temporary_datafile.tmp
set serveroutput on
set lines 180
set pages 1000
set feedback off
set echo off
set ver off
col FILE_NAME format a150
col TABLESPACE_NAME format a30

DECLARE
BEGIN
    FOR rec IN (select file_name 
		from dba_users, dba_temp_files 
		where tablespace_name = temporary_tablespace 
		and username = 'SYS')
    LOOP
        dbms_output.put_line(rec.FILE_NAME);
    END LOOP;
END;
/

set echo on
set feed on
set ver on
exit;
EOF
}

query_sys_datafiles()
{
$ORACLE_HOME/bin/sqlplus -s / as sysdba << EOF > /tmp/system_datafile.tmp
set serveroutput on
set lines 180
set pages 1000
set feedback off
set echo off
set ver off
col FILE_NAME format a150

DECLARE
BEGIN
    FOR rec IN (select FILE_NAME from dba_data_files where TABLESPACE_NAME='SYSTEM' order by FILE_ID)
    LOOP
        dbms_output.put_line(rec.FILE_NAME);
    END LOOP;
END;
/

set echo on
set feed on
set ver on
exit;
EOF
}

query_undo_datafiles()
{
$ORACLE_HOME/bin/sqlplus -s / as sysdba << EOF > /tmp/undo_datafile.tmp
set serveroutput on
set lines 180
set pages 1000
set feedback off
set echo off
set ver off
col FILE_NAME format a150

DECLARE
BEGIN
    --FOR rec IN (select FILE_NAME from dba_data_files where TABLESPACE_NAME='UNDOTBS1' order by FILE_ID)
    FOR rec IN (select FILE_NAME from dba_data_files a, dba_tablespaces b where b.STATUS = 'ONLINE' and b.CONTENTS = 'UNDO' and a.TABLESPACE_NAME = b.TABLESPACE_NAME order by FILE_ID)
    LOOP
        dbms_output.put_line(rec.FILE_NAME);
    END LOOP;
END;
/

set echo on
set feed on
set ver on
exit;
EOF
}

query_readonly_tablespace()
{
$ORACLE_HOME/bin/sqlplus -s / as sysdba << EOF > /tmp/readonly_tablespace.tmp
set serveroutput on
set lines 180
set pages 1000
set feedback off
set echo off
set ver off
col FILE_NAME format a150

DECLARE
BEGIN
    FOR rec IN (select file_name from dba_data_files a, dba_tablespaces b where b.STATUS = 'READ ONLY' and b.TABLESPACE_NAME = a.TABLESPACE_NAME order by FILE_ID)
    LOOP
        dbms_output.put_line(rec.FILE_NAME);
    END LOOP;
END;
/

set echo on
set feed on
set ver on
exit;
EOF
}

query_spfile()
{
ls -gGl /home/oracle/app/oracle/product/11.2.0/dbhome_2/dbs/*ora |awk '{print $7}' > /tmp/spfile.tmp
}

query_all_datafiles()
{
$ORACLE_HOME/bin/sqlplus -s / as sysdba << EOF > /tmp/all_datafile.tmp
set serveroutput on
set lines 180
set pages 1000
set feedback off
set echo off
set ver off
col FILE_NAME format a150
col TABLESPACE_NAME format a30

DECLARE
BEGIN
    FOR rec IN (select FILE_NAME from dba_data_files order by FILE_ID)
    LOOP
        dbms_output.put_line(rec.FILE_NAME);
    END LOOP;
END;
/

set echo on
set feed on
set ver on
exit;
EOF
}

query_redo_member()
{
$ORACLE_HOME/bin/sqlplus -s / as sysdba << EOF > /tmp/redo_member.tmp
set serveroutput on
set lines 180
set pages 1000
set feedback off
set echo off
set ver off
col member format a150

DECLARE
BEGIN
    FOR rec IN (select member 
		    from  v\$log a, v\$logfile b
		    where a.group# = b.group#
		    and a.status = 'CURRENT')
    LOOP
        dbms_output.put_line(rec.member);
    END LOOP;
END;
/

set echo on
set feed on
set ver on
exit;
EOF
}

query_inactive_group()
{
$ORACLE_HOME/bin/sqlplus -s / as sysdba << EOF > /tmp/inactive_group.tmp
set serveroutput on
set lines 180
set pages 1000
set feedback off
set echo off
set ver off
col member format a150

DECLARE
BEGIN
    FOR rec IN (select member 
		    from  v\$log a, v\$logfile b
		    where a.group# = b.group#
		    and a.status = 'INACTIVE'
		    order by b.group#, member)
    LOOP
        dbms_output.put_line(rec.member);
    END LOOP;
END;
/

set echo on
set feed on
set ver on
exit;
EOF
}

query_active_group()
{
$ORACLE_HOME/bin/sqlplus -s / as sysdba << EOF > /tmp/active_group.tmp
set serveroutput on
set lines 180
set pages 1000
set feedback off
set echo off
set ver off
col member format a150

DECLARE
BEGIN
    execute immediate 'alter system switch logfile';
    FOR rec IN (select member 
		    from  v\$log a, v\$logfile b
		    where a.group# = b.group#
		    and a.status = 'ACTIVE'
		    order by b.group#, member)
    LOOP
        dbms_output.put_line(rec.member);
    END LOOP;
END;
/

set echo on
set feed on
set ver on
exit;
EOF
}

query_current_group()
{
$ORACLE_HOME/bin/sqlplus -s / as sysdba << EOF > /tmp/current_group.tmp
set serveroutput on
set lines 180
set pages 1000
set feedback off
set echo off
set ver off
col member format a150

DECLARE
BEGIN
    FOR rec IN (select member 
		    from  v\$log a, v\$logfile b
		    where a.group# = b.group#
		    and a.status = 'CURRENT'
		    order by b.group#, member)
    LOOP
        dbms_output.put_line(rec.member);
    END LOOP;
END;
/

set echo on
set feed on
set ver on
exit;
EOF
}

files_to_tmp()
{
	case "$1" in
		"CONTROLFILES"     ) query_controlfiles ;;
		"NONSYSTEMDATA"    ) query_ns_datafiles ;;
		"TEMPORARYDATA"    ) query_temp_datafiles ;;
		"SYSTEMDATA"       ) query_sys_datafiles ;;
		"UNDODATA"         ) query_undo_datafiles ;;
		"READONLYTBS"      ) query_readonly_tablespace ;;
		"NONSYSTEMTBS"     ) query_ns_datafiles ;;
		"TEMPORARYTBS"     ) query_temp_datafiles ;;
		"SYSTEMTBS"        ) query_sys_datafiles ;;
		"UNDOTBS"          ) query_undo_datafiles ;;
		"SPFILE"           ) query_spfile ;;
		"ALLDATA"          ) query_all_datafiles ;;
		"REDOMEMBER"       ) query_redo_member ;;
		"INACTIVEGROUP"    ) query_inactive_group ;;
		"ACTIVEGROUP"      ) query_active_group ;;
		"CURRENTGROUP"     ) query_current_group ;;
	esac
}

# Menu 1 selected: LOSS OF A CONTROL FILE
menu_id_01()
{
	# Read from database the control file's location
	# redirecting the output to a tmp file
	files_to_tmp "CONTROLFILES"

        # Counting the number of control files found
	count_files "/tmp/controlfile.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -le "1" ]
	then
		ERRMSG="Can not proceed. Your database has just one control file. Select menu 2 if you want to perform a loss of all control files."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your control files. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/controlfile.tmp" "1"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove one file
                remove_files "1"

	fi

	kill_instance
	exit 0
}

# Menu 2 selected: LOSS OF ALL CONTROL FILES
menu_id_02()
{
	# Read from database the control file's location
	# redirecting the output to a tmp file
	files_to_tmp "CONTROLFILES"

        # Counting the number of control files found
	count_files "/tmp/controlfile.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -le "1" ]
	then
		ERRMSG="Not able to find information on your control files. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read all the lines of the file
                read_files "/tmp/controlfile.tmp"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove all files
                remove_files "${#ARRAY_OF_FILES[*]}"
	fi

	kill_instance
	exit 0
}

# Menu 3 selected: LOSS OF A REDO LOG FILE GROUP MEMBER
menu_id_03()
{
	# Read from database the redo log file group member's location
	# redirecting the output to a tmp file
	files_to_tmp "LOGFILES"

        # Counting the number of redo log file group member files found
	count_files "/tmp/logfile.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -le "1" ]
	then
		ERRMSG="Can not proceed. Your database has just one redo log file group member file. Select menu 4 if you want to perform a loss of all redo log file group member files."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your redo log file group member files. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/logfile.tmp" "1"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove one file
                remove_files "1"
	fi

	kill_instance
	exit 0
}

# Menu 4 selected: LOSS OF A REDO LOG FILE GROUP
menu_id_04()
{
	# Read from database the redo log file group member's location
	# redirecting the output to a tmp file
	files_to_tmp "LOGGROUP"

        # Counting the number of redo log file group member files found
	count_files "/tmp/log_groupfiles.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -le "1" ]
	then
		ERRMSG="Not able to find information on your redo log file group member files. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read all the lines of the file
                read_files "/tmp/log_groupfiles.tmp"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove all files
                remove_files "${#ARRAY_OF_FILES[*]}"
	fi

	kill_instance
	exit 0
}

# Menu 5 selected: LOSS OF A NON-SYSTEM DATAFILE
menu_id_05()
{
	# Read from database the non-system datafile's location
	# redirecting the output to a tmp file
	files_to_tmp "NONSYSTEMDATA"

        # Counting the number of non-system datafile found
	count_files "/tmp/non_system_datafile.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -le "1" ]
	then
		ERRMSG="Can not proceed. Your database has just one non-system datafile. Select menu 12 if you want to perform a loss of all non-system datafiles of USERS tablespace."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your non-system datafile. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/non_system_datafile.tmp" "1"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove one file
                remove_files "1"
	fi

	kill_instance
	exit 0

}

# Menu 6 selected: LOSS OF A TEMPORARY DATAFILE
menu_id_06()
{
	# Read from database the temporary datafile's location
	# redirecting the output to a tmp file
	files_to_tmp "TEMPORARYDATA"

        # Counting the number of temporary datafile found
	count_files "/tmp/temporary_datafile.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -le "1" ]
	then
		ERRMSG="Can not proceed. Your database has just one temporary datafile. Select menu 13 if you want to perform a loss of all temporary datafiles of temporary tablespace."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your temporary datafile. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/temporary_datafile.tmp" "1"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove one file
                remove_files "1"
	fi

	kill_instance
	exit 0
}

# Menu 7 selected: LOSS OF A SYSTEM DATAFILE
menu_id_07()
{
	# Read from database the system datafile's location
	# redirecting the output to a tmp file
	files_to_tmp "SYSTEMDATA"

        # Counting the number of system datafile found
	count_files "/tmp/system_datafile.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -le "1" ]
	then
		ERRMSG="Can not proceed. Your database has just one system datafile. Select menu 14 if you want to perform a loss of all system datafiles of SYSTEM tablespace."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your system datafile. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/system_datafile.tmp" "1"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove one file
                remove_files "1"
	fi

	kill_instance
	exit 0
}

# Menu 8 selected: LOSS OF A UNDO DATAFILE
menu_id_08()
{
	# Read from database the undo datafile's location
	# redirecting the output to a tmp file
	files_to_tmp "UNDODATA"

        # Counting the number of undo datafile found
	count_files "/tmp/undo_datafile.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -le "1" ]
	then
		ERRMSG="Can not proceed. Your database has just one undo datafile. Select menu 14 if you want to perform a loss of all datafiles of UNDO tablespace."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your undo datafile. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/undo_datafile.tmp" "1"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove one file
                remove_files "1"
	fi

	kill_instance
	exit 0
}

# Menu 9 selected: LOSS OF A READ-ONLY TABLESPACE
menu_id_09()
{
	# Read from database the read-only datafile's location
	# redirecting the output to a tmp file
	files_to_tmp "READONLYTBS"

        # Counting the number of read-only datafile found
	count_files "/tmp/readonly_tablespace.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your read-only datafile. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read all the lines of the file
                read_files "/tmp/readonly_tablespace.tmp"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove all files
                remove_files "${#ARRAY_OF_FILES[*]}"
	fi

	kill_instance
	exit 0
}

# Menu 10 selected: LOSS OF AN INDEX TABLESPACE
menu_id_10()
{
ERRMSG="MENU 10 TO BE IMPLEMENTED."
return "$SUCCESS"
}

# Menu 11 selected: LOSS OF ALL INDEXES IN USERS TABLESPACE
menu_id_11()
{
ERRMSG="MENU 11 TO BE IMPLEMENTED."
return "$SUCCESS"
}

# Menu 12 selected: LOSS OF A NON-SYSTEM TABLESPACE
menu_id_12()
{
	# Read from database the non-system datafile's location
	# redirecting the output to a tmp file
	files_to_tmp "NONSYSTEMTBS"

        # Counting the number of non-system datafile found
	count_files "/tmp/non_system_datafile.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your non-system tablespace. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/non_system_datafile.tmp" "1"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove all files
                remove_files "${#ARRAY_OF_FILES[*]}"
	fi

	kill_instance
	exit 0
}

# Menu 13 selected: LOSS OF A TEMPORARY TABLESPACE
menu_id_13()
{
	# Read from database the temporary datafile's location
	# redirecting the output to a tmp file
	files_to_tmp "TEMPORARYTBS"

        # Counting the number of temporary datafile found
	count_files "/tmp/temporary_datafile.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your temporary tablespace. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/temporary_datafile.tmp" "1"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove all files
                remove_files "${#ARRAY_OF_FILES[*]}"
	fi

	kill_instance
	exit 0
}

# Menu 14 selected: LOSS OF A SYSTEM TABLESPACE
menu_id_14()
{
	# Read from database the system datafile's location
	# redirecting the output to a tmp file
	files_to_tmp "SYSTEMTBS"

        # Counting the number of system datafile found
	count_files "/tmp/system_datafile.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your system tablespace. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/system_datafile.tmp" "1"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove all files
                remove_files "${#ARRAY_OF_FILES[*]}"
	fi

	kill_instance
	exit 0
}

# Menu 15 selected: LOSS OF AN UNDO TABLESPACE
menu_id_15()
{
	# Read from database the undo datafile's location
	# redirecting the output to a tmp file
	files_to_tmp "UNDOTBS"

        # Counting the number of undo datafile found
	count_files "/tmp/undo_datafile.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your undo tablespace. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/undo_datafile.tmp" "1"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove all files
                remove_files "${#ARRAY_OF_FILES[*]}"
	fi

	kill_instance
	exit 0
}

# Menu 16 selected: LOSS OF THE PASSWORD FILE
menu_id_16()
{
	# Read from database the spfile's location
	# redirecting the output to a tmp file
	files_to_tmp "SPFILE"

        # Counting the number of spfile found
	count_files "/tmp/spfile.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your spfile. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/spfile.tmp"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove all files
                remove_files "${#ARRAY_OF_FILES[*]}"
	fi

	kill_instance
	exit 0
}

# Menu 17 selected: LOSS OF ALL DATAFILES
menu_id_17()
{
	# Read from database the datafiles's location
	# redirecting the output to a tmp file
	files_to_tmp "ALLDATA"

        # Counting the number of spfile found
	count_files "/tmp/all_datafile.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your datafiles. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/all_datafile.tmp"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove all files
                remove_files "${#ARRAY_OF_FILES[*]}"
	fi

	kill_instance
	exit 0
}

# Menu 18 selected: LOSS OF REDO LOG MEMBER OF A MULTIPLEXED GROUP
menu_id_18()
{
	# Read from database the redo logfile's location
	# redirecting the output to a tmp file
	files_to_tmp "REDOMEMBER"

        # Counting the number of redo logfile found
	count_files "/tmp/redo_member.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -le "1" ]
	then
		ERRMSG="Can not proceed. Your database has just one redo logfile member for group. Select menu 19, 20 or 21 if you want to perform a loss of all redo logfiles."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your redo logfile. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/redo_member.tmp"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove one file
                remove_files "1"
	fi

	kill_instance
	exit 0
}

# Menu 19 selected: LOSS OF ALL REDO LOG MEMBERS OF AN INACTIVE GROUP
menu_id_19()
{
	# Read from database the redo logfile's location
	# redirecting the output to a tmp file
	files_to_tmp "INACTIVEGROUP"

        # Counting the number of redo logfile found
	count_files "/tmp/inactive_group.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty. Perhaps you don't have any INACTIVE group."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your redo logfile. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/inactive_group.tmp"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove all files
                remove_files "${#ARRAY_OF_FILES[*]}"
	fi

	kill_instance
	exit 0
}

# Menu 20 selected: LOSS OF ALL REDO LOG MEMBERS OF AN ACTIVE GROUP
menu_id_20()
{
	# Read from database the redo logfile's location
	# redirecting the output to a tmp file
	files_to_tmp "ACTIVEGROUP"

        # Counting the number of redo logfile found
	count_files "/tmp/active_group.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty. Perhaps you don't have any ACTIVE group."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your redo logfile. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/active_group.tmp"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove all files
                remove_files "${#ARRAY_OF_FILES[*]}"
	fi

	kill_instance
	exit 0
}

# Menu 21 selected: LOSS OF ALL REDO LOG MEMBERS OF CURRENT GROUP
menu_id_21()
{
	# Read from database the redo logfile's location
	# redirecting the output to a tmp file
	files_to_tmp "CURRENTGROUP"

        # Counting the number of redo logfile found
	count_files "/tmp/current_group.tmp"
	return_val=$?
	if [ "$return_val" -eq "0" ]
	then
		ERRMSG="Can not proceed. Temporary file is empty."
		return "$SUCCESS"
	elif [ "$return_val" -eq "$FAIL" ]
	then
		ERRMSG="Not able to find information on your redo logfile. Be sure your database is up and running."
		return "$SUCCESS"
	else
		# Read just the first line of the file
                read_files "/tmp/current_group.tmp"
		return_val=$?
		if [ "$return_val" -eq "$FAIL" ]
		then
			ERRMSG="Can not proceed. Program was not able to locate temporary files."
			return "$SUCCESS"
		fi

		# Remove all files
                remove_files "${#ARRAY_OF_FILES[*]}"
	fi

	kill_instance
	exit 0
}

# Menu 99 selected: PERFORM A RANDOM CRASH SCENARIO
menu_id_99()
{
get_random_number
MENU=$?
exec_menu $MENU
#return "$SUCCESS"
}

#------------------------------------------------------
# Main
#------------------------------------------------------
# Up to this point there are variables and functions.
# The program starts running here.

#checks to see if user is root

#if [ "$(whoami)" != "oracle" ]
if [ "$(whoami)" != "oracle" ]
	then
	  echo "Error: You ARE NOT oracle user!!!!!"
	  exit 1
else
	while true
	do
		# Display the menu.
		show_menu

		# Read the number of menu entered by the user.
		read menu_number

		# Clear any error message.
		ERRMSG=""

		# Execute one of the functions based
		# on the number entered by the user.
		case "$menu_number" in
			"1"  ) menu_id_01 ;;
			"2"  ) menu_id_02 ;;
			"3"  ) menu_id_03 ;;
			"4"  ) menu_id_04 ;;
			"5"  ) menu_id_05 ;;
			"6"  ) menu_id_06 ;;
			"7"  ) menu_id_07 ;;
			"8"  ) menu_id_08 ;;
			"9"  ) menu_id_09 ;;
			"10" ) menu_id_10 ;;
			"11" ) menu_id_11 ;;
			"12" ) menu_id_12 ;;
			"13" ) menu_id_13 ;;
			"14" ) menu_id_14 ;;
			"15" ) menu_id_15 ;;
			"16" ) menu_id_16 ;;
			"17" ) menu_id_17 ;;
			"18" ) menu_id_18 ;;
			"19" ) menu_id_19 ;;
			"20" ) menu_id_20 ;;
			"21" ) menu_id_21 ;;
			"22" ) menu_id_22 ;;
			"99" ) menu_id_99 ;;
			"0" ) break ;;
			 *  ) invalid_choice ;;
		esac
	done
fi

