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
from datetime import time, datetime, timedelta
from os.path import expanduser
from os import makedirs

try:
    makedirs(expanduser('~/.esmuc_aules'))

except OSError:
    pass

context = daemon.DaemonContext(
    working_directory=expanduser('~/.esmuc_aules'),
    umask=002
)

with context:
    while True:
        with open('.asimut_login') as login_credentials:
            user = login_credentials.readline().rstrip('\n')
            password = login_credentials.readline().rstrip('\n')

        now_time = datetime.today()
        future_time = datetime(now_time.year, now_time.month, now_time.day, 6, 28)
        if now_time.hour > 6 or (now_time.hour == 6 and now_time.minute >= 30):
            future_time += timedelta(days=1)
        sleep((future_time-now_time).total_seconds())

        session = AsimutSession()
        session.login(user, password)

        fire_time = datetime(future_time.year, future_time.month, future_time.day,
                                                                        6, 29, 45)
        sleep((fire_time-future_time).total_seconds())

        book_date = future_time + timedelta(days=1)
        date = "%i/%i/%i" % (book_date.day, book_date.month, book_date.year)
        room = 'C117'
        starttime = '08:00'
        endtime = '08:30'
        description = ''
        response = {'class' : '', 'text' : 'NO success'}
        success_response = 'message-success'
        attempts = 0

        while (response['class'] != success_response or
               time.today().minute < 31):
            response = session.book_room(room, date, starttime,
                                                endtime, description)
            attempts += 1

        with open('.cron_booking.log', 'a'):
            booking_log.write("%s - room: %s, from %s to %s. [%s]\n" % (date,
                                                                        room,
                                                                        starttime,
                                                                        endtime,
                                                                        description))
            booking_log.write("\t-- %s in %i attempts.\n\n" % (response['text'],
                                                               attempts))


