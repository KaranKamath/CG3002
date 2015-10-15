#! /bin/sh
### BEGIN INIT INFO
# Provides:          navi
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: NAVI service
### END INIT INFO

DESC="NAVI service"
NAME=navi
DAEMON=/home/pi/cg3002/navigator.py
DAEMON_ARGS=""
PIDFILE=/var/run/$NAME.pid
SCRIPTNAME=/etc/init.d/$NAME
DAEMON_USER=pi

# Load the VERBOSE setting and other rcS variables
. /lib/init/vars.sh

# Define LSB log_* functions.
# Depend on lsb-base (>= 3.2-14) to ensure that this file is present
# and status_of_proc is working.
. /lib/lsb/init-functions

#
# Function that starts the daemon/service
#
do_start()
{
    log_daemon_msg "Starting system $NAME daemon"
    start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --startas $DAEMON -- $DAEMON_ARGS
    log_end_msg $?
}

#
# Function that stops the daemon/service
#
do_stop()
{
    log_daemon_msg "Stopping system $NAME daemon"
    start-stop-daemon --stop --pidfile $PIDFILE --retry 10
    log_end_msg $?
}


case "$1" in
  start|stop)
    do_${1}
    ;;

  restart)
    do_stop
    do_start
    ;;

  status)
    status_of_proc "$NAME" "$DAEMON" && exit 0 || exit $?
    ;;

  *)
    echo "Usage: $SCRIPTNAME {start|stop|status|restart}" >&2
    exit 3
    ;;
esac
exit 0