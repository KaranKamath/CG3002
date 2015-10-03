#!/bin/bash

function log {
    echo $1 >> /home/pi/logs/tweet_ip.log
}

function tweet {
    consumer_key=3r8XaB3DrVihMoCjqbvAcu6xZ
    consumer_secret=QYjJ6ezrFDwU2UcHCrLUvQvnbZc6NQcWZiPP0yq1A57xXc5Edp
    oauth_token=3535282152-vdd0chrSNOYI61xHa3oC62rxwrnZvWUIhZJCy0t
    oauth_secret=yOgsiiYXPIKHTEvcsy98u9MdXld28yDAfaN8layJa3xdE

    timestamp=`date +%s`
    nonce=`date +%s%T555555555 | openssl base64 | sed -e s'/[+=/]//g'`
    signature_base_string="POST&https%3A%2F%2Fapi.twitter.com%2F1.1%2Fstatuses%2Fupdate.json&oauth_consumer_key%3D${consumer_key}%26oauth_nonce%3D${nonce}%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D${timestamp}%26oauth_token%3D${oauth_token}%26oauth_version%3D1.0%26status%3DMy%2520IP%2520Address%2520is%2520${1}%2520%2523${timestamp}"
    signature_key="${consumer_secret}&${oauth_secret}"
    oauth_signature=`echo -n ${signature_base_string} | openssl dgst -sha1 -hmac ${signature_key} -binary | openssl base64 | sed -e s'/+/%2B/' -e s'/\//%2F/' -e s'/=/%3D/'`
    header="Authorization: OAuth oauth_consumer_key=\"${consumer_key}\", oauth_nonce=\"${nonce}\", oauth_signature=\"${oauth_signature}\", oauth_signature_method=\"HMAC-SHA1\", oauth_timestamp=\"${timestamp}\", oauth_token=\"${oauth_token}\", oauth_version=\"1.0\""

    response=`curl -s 'https://api.twitter.com/1.1/statuses/update.json' --data "status=My+IP+Address+is+${1}+%23${timestamp}" --header "${header}"`
    log "$response"
}

while true;
do
    ip=$(echo $(hostname -I) | awk '{print $NF}')

    echo "$ip" > /home/pi/.ip.tmp
    cmp --silent "/home/pi/.ip.tmp" "/home/pi/.ip"
    cmp_result=$?

    if [ $cmp_result -eq 0 ]; then
        log "No change in IP"
        rm -f /home/pi/.ip.tmp
    else
        rm -f /home/pi/.ip
        mv /home/pi/.ip.tmp /home/pi/.ip
        tweet $ip
    fi
    sleep 2;
done