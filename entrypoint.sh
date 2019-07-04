#!/usr/bin/env bash

start(){
    echo "--> INFO: server..."

    python /var/www/src/app.py server
}

case $1 in

run)
    shift 1
    start $@
;;

*)
   >&2 echo "---> INFO: running: '$1'."
;;

esac