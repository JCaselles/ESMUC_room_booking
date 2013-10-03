#!/usr/bin/env python
# coding=utf-8
#
# Daemon script for prototype.py, to simulate the functionality of an
# Android service.
#
# Author: Arnau Orriols

from prototype import AsimutSession
import daemon
from time import sleep
from datetime import datetime, timedelta
from os.path import expanduser
from os import makedirs
from sys import argv

try:
    makedirs(expanduser('~/.esmuc_aules'))

except OSError:
    pass

context = daemon.DaemonContext(
    working_directory=expanduser('~/.esmuc_aules'),
    umask=002
)

std_ioe = open (expanduser('~/.esmuc_aules/.daemon_io.log'), 'w')

context.stdout = std_ioe
context.stderr = std_ioe

room = argv[1]
date = argv[2]
starttime = argv[3]
endtime = argv[4]
description = argv[5]

with context:
    with open('.asimut_login') as login_credentials:
        user = login_credentials.readline().rstrip('\n')
        password = login_credentials.readline().rstrip('\n')

    book_time = datetime(int(date[-4:]), int(date[3:5]), int(date[:2]),
                                            int(endtime[:2]), int(endtime[-2:]))
    book_time -= timedelta(days=1, hours=2)

    login_time = book_time - timedelta(minutes=2)
    sleep((login_time-datetime.now()).total_seconds())

    """ Perform login 2 minutes before booking """
    session = AsimutSession()
    session.login(user, password)

    fire_time = book_time - timedelta(seconds=15)
    sleep((fire_time-datetime.now()).total_seconds())

    """ Start requesting the server 45 seconds before booking opens """
    response = {'class' : '', 'text' : 'NO success'}
    success_response = 'message-success'
    attempts = 0

    while (response['class'] != success_response and
           datetime.today() < (book_time + timedelta(seconds=15))):
        response = session.book_room(room, date, starttime,
                                            endtime, description)
        attempts += 1
        print response
        print attempts

    """ Register the booking results """
    with open('.cron_booking.log', 'a') as booking_log:
        booking_log.write("-" * 10)
        booking_log.write("\n%s - room: %s, from %s to %s. [%s]\n"
                          % (date, room, starttime, endtime, description))
        booking_log.write("\t-- %s in %i attempts.\n\n" % (response['text'],
                                                           attempts))
        booking_log.write("Current books:\n")
        booked_list = session.fetch_booked_list()
        for book in booked_list:
            booking_log.write("\t- %s at %s\n" % (book['room'], book['time']))

        response = session.cancel_book(session.get_last_book_id())
        if response['class'] == success_response:
            booking_log.write('\nTest book has been successfuly canceled\n')
        booking_log.write('-' * 10)
        booking_log.write('\n' * 2)

