#!/bin/sh

case $1 in
    publishers)
        shift
        publisher_select --queue-ip $RABBITMQ_SERVICE_HOST $@
        ;;
    pull)
        shift
        pull_tweets --queue-ip $RABBITMQ_SERVICE_HOST $@
        ;;
    process)
        shift
        process_tweets --queue-ip $RABBITMQ_SERVICE_HOST $@
        ;;
    store)
        shift
        store_records --queue-ip $RABBITMQ_SERVICE_HOST $@
        ;;
    *)
        exit 1
        ;;
esac
