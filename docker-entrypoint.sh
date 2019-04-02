#!/bin/bash

case $1 in
    publishers)
        publisher_select
        ;;
    pull)
        pull_tweets
        ;;
    process)
        process_tweets
        ;;
    store)
        store_records
        ;;
    *)
      exit 1
      ;;
esac
