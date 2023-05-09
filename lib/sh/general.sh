#!/bin/bash

# Shell script include library of commonly used functions and variables by
# Clintosaurous scripts.
#
#   . $SCRIPTNAME
#
# Variables:
#   PATH
#       Updated as needed.
#   PYTHONPATH
#       Updated as needed.

# Version: 1.0.1
# Last Updated: 2022-12-02


CLINTBIN=$CLINTHOME/home/bin
CLINTLIB=$CLINTHOME/home/lib
HOSTSDIR=$CLINTHOME/home/hosts
export HOSTLISTFILE=/etc/clintosaurous/host-list.txt

if [ -z `echo "$PYTHONPATH" | grep "$CLINTLIB/python"` ]; then
    export PYTHONPATH="$PYTHONPATH:$CLINTLIB/python"
fi

if [ -z `echo "$PATH" | grep "$CLINTBIN"` ]; then
    export PATH="$CLINTBIN:$PATH"
fi

if [ -z `echo "$PATH" | grep "$HOSTSDIR"` ]; then
    export PATH="$HOSTSDIR:$PATH"
fi


# Creates an error lock file that can be checked to suppress alerts.
error_lock_check ()
{

    LOCKFILE="/tmp/`basename $0`.lock"
    if [ -e $LOCKFILE ]; then
        echo 1
    else
        echo 0
    fi

}


# Creates an error lock file that can be checked to suppress alerts.
error_lock ()
{

    LOCKFILE="/tmp/`basename $0`.lock"
    echo `localtime` >> $LOCKFILE

}


# Deletes error lock file.
error_unlock ()
{

    LOCKFILE="/tmp/`basename $0`.lock"
    rm -f $LOCKFILE

}


home_net_check ()
{

    LINECNT=`resolvectl status | egrep '192\.168\.4\.1[012]|127\.0' | wc -l`
    if [ $LINECNT -lt 2 ]; then
        echo "Wrong DNS servers! Not running on home network!" >&2
        exit 1
    fi
    IPCNT=`ip address | grep '192\.168\.10\.' | wc -l`
    if [ $IPCNT -eq 0 ]; then
        echo "Wrong IP address! Not running on home network!" >&2
        exit 1
    fi

}


localtime ()
{

    echo `date +"%a %b %e %H:%M:%S %Y"`

}   # End function localtime


# This function takes the directory(s) supplied and verifies they exist and
#   attempts to create them if they do not.
verify_dir ()
{

    for DIR
    do
        if [ ! -e $DIR ] ; then create_dir $DIR ; fi
    done

}   # End function verify_dir
