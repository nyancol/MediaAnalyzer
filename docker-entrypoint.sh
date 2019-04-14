#!/bin/sh

case $1 in
    publishers)
        shift
        publisher_select $@
        ;;
    pull)
        shift
        pull_tweets $@
        ;;
    process)
        shift
        process_tweets $@
        ;;
    store)
        shift
        store_records $@
        ;;
    *)
        exit 1
        ;;
esac
