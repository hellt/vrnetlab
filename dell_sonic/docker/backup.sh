#!/bin/bash

DEFAULT_USER="admin"
DEFAULT_PASSWORD="admin"
REMOTE_FILE="/etc/sonic/config_db.json"
TMP_FILE="/tmp/${REMOTE_FILE##*/}"
BACKUP_FILE="/config/${REMOTE_FILE##*/}"

handle_args() {
    # Parse options
    while getopts 'u:p:' OPTION; do
        case "$OPTION" in
            u)
            user="$OPTARG"
            ;;
            p)
            password="$OPTARG"
            ;;
            ?)
            usage
            exit 1
            ;;
        esac
    done
    shift "$(($OPTIND -1))"

    # Assign defaults if options weren't provided
    if [ -z "$user" ] ; then
        user=$DEFAULT_USER
    fi
    if [ -z "$password" ] ; then
        password=$DEFAULT_PASSWORD
    fi

    SSH_CMD="sshpass -p $password ssh -o LogLevel=ERROR -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
    SCP_CMD="sshpass -p $password scp -o LogLevel=ERROR -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
    HOST="$user@127.0.0.1"

    # Parse commands
    case $1 in

    backup)
        backup
        ;;

    restore)
        restore
        ;;

    *)
        usage
        ;;
    esac
}

usage() {
	echo "Usage: $(basename $0) [-u USERNAME] [-p PASSWORD] COMMAND"
    echo "Options:"
    echo "  -u USERNAME    VM SSH username (default: $DEFAULT_USER)"
    echo "  -p PASSWORD    VM SSH password (default: $DEFAULT_PASSWORD)"
    echo
    echo "Commands:"
    echo "  backup         Backup VM $REMOTE_FILE directory to $BACKUP_FILE"
    echo "  restore        Restore VM $REMOTE_FILE directory from $BACKUP_FILE"
	exit 0;
}

backup() {
    echo "Retrieveing the config from the VM..."
    # copy the original config to the tmp location and set permissions to 777
    # and then copy out the file from the temp location
    $SSH_CMD $HOST "sudo cp $REMOTE_FILE $TMP_FILE && sudo chmod 777 $TMP_FILE" && \
    $SCP_CMD $HOST:$TMP_FILE $BACKUP_FILE
}

restore() {
    if [ -f "$BACKUP_FILE" ]; then
        echo "Copying startup config file to the VM..."

        $SCP_CMD $BACKUP_FILE $HOST:$TMP_FILE && $SSH_CMD $HOST "sudo cp $TMP_FILE $REMOTE_FILE && sudo config reload -y"
    else
        echo "$BACKUP_FILE not found. Nothing to push to the VM."
    fi
}

handle_args "$@"
