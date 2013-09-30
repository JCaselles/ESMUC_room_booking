#!/usr/bin/env python
# coding=utf-8

# Python prototipe for an Android app to automatize login and room
# reservation of the Escola Superior de Musica de Catalunya - Asimut
# system.
#
# Copyright 2013 Arnau Orriols. All Rights Reserved.

import requests
from sys import argv, exit

class AsimutSession (object):

    BASE_URL = "https://esmuc.asimut.net/public/"
    SERVER_CALLS = {'login' : 'login.php',
                    'book' : 'async-event-save.php',
                    'cancel' : 'async-event-cancel.php',
                    'fetch events' : 'async_fetchevents.php'
    }

    LOCATIONGROUPS_ID = {'cabina' : '6',
                          'instrument individual' : '5',
                          'cambra' : '4',
                          'col·lectiva' : '3',
                          'aules de concert' : '12',
                          'improvisació' : '13',
                          'pianistes' : '11',
                          'musica antiga' : '9',
                          'jazz i mm' : '7',
                          'percussió' : '10',
                          'audiovisuals' : '14',
                          'informàtica' : '15',
                          'aules especifiques' : '18'}

    LOCATIONS_ID = {str(grupid) : {} for grupid in
    LOCATIONGROUPS_ID.itervalues()}

    LOCATIONS_ID[LOCATIONGROUPS_ID['pianistes']].update({
        "A%i" %room : str(ref) for room, ref
                               in zip(range(339, 344), range(73, 78))
    })
    LOCATIONS_ID[LOCATIONGROUPS_ID['cabina']].update({
        "C%i" %room : str(ref) for room, ref
                               in zip(range(102, 119), range(94, 111))
    })
    LOCATIONS_ID[LOCATIONGROUPS_ID['instrument individual']].update({
        "A%i" %room : str(ref) for room, ref
                               in zip(range(119, 121), range(19, 21))
    })
    LOCATIONS_ID[LOCATIONGROUPS_ID['instrument individual']].update({
        "A125" : "26", "A126" : "25"})
    LOCATIONS_ID[LOCATIONGROUPS_ID['instrument individual']].update({
        "A%i" %room : str(ref) for room, ref
                               in zip(range(301, 337), range(35, 71))
                               if room not in range(304, 322)
    })
    LOCATIONS_ID[LOCATIONGROUPS_ID['cambra']].update({
        "A%i" %room : str(ref) for room, ref
                              in zip(range(304, 339), range(38, 73))
                              if (room not in range(308, 314) and
                                  room not in range(316, 318) and
                                  room not in range(319, 337)
                              )
    })

    own_book_ids = []


    def login(self, user, password):

        payload = {'authenticate-useraccount' : user,
                   'authenticate-password' : password}
        url = "%s%s" % (self.BASE_URL, self.SERVER_CALLS['login'])

        self.requests_session = requests.session()
        self.requests_session.cookies = \
        requests.cookies.cookiejar_from_dict({'asimut-width' : '640'})
        self.requests_session.post(url, data=payload).content


    def book_room(self, room, date, starttime, endtime, description=''):

        room_id = self.find_room_id_by_name(room)
        roomgroup = self.find_roomgroup_by_room_id(room_id)

        payload = {'event-id' : '0',
                   'location-id' : room_id,
                   'date' : date,
                   'starttime' : starttime,
                   'endtime' : endtime,
                   'location' : room,
                   'description' : description
        }

        url = "%s%s" % (self.BASE_URL, self.SERVER_CALLS['book'])
        self.requests_session.post(url, data=payload)
        # This is not save
        self.own_book_ids.append(self.get_last_booking_id(date, roomgroup))
        return self.own_book_ids[-1]

    def get_last_booking_id(self, date, roomgroup_id):

        url = "%s%s" % (self.BASE_URL, self.SERVER_CALLS['fetch events'])
        date = "-".join(reversed(date.split('/')))
        payload = {'starttime' : date,
                   'endtime' : date,
                   'locationgroup' : "-%s" % roomgroup_id
        }

        response = self.requests_session.get(url, params=payload).json()
        book_ids = [book[0] for book in response]
        return sorted(book_ids)[-1]


    def cancel_last_book(self, last_book_id):

        payload = {'id' : last_book_id}
        url = "%s%s" % (self.BASE_URL, self.SERVER_CALLS['cancel'])

        response = None
        while not response:
            response = self.requests_session.get(url, params=payload).json()
            payload['id'] = str(int(payload['id'])-1)
        self.own_book_ids.pop()
        return response

    def find_room_id_by_name(self, room_name):

        for room_group in self.LOCATIONGROUPS_ID.itervalues():
            if room_name in self.LOCATIONS_ID[room_group].keys():
                return self.LOCATIONS_ID[room_group][room_name]

        exit("Room doesn't exist")

    def find_roomgroup_by_room_id(self, room_id):

        for room_group in self.LOCATIONGROUPS_ID.itervalues():
            if room_id in self.LOCATIONS_ID[room_group].values():
                return room_group
        exit("Error")

if __name__ == "__main__":

    if len(argv) == 8:
        Session = AsimutSession()
        Session.login(argv[1], argv[2])
        book_id = Session.book_room(argv[3], argv[4],
                                    argv[5], argv[6],
                                    argv[7]
        )
        print Session.cancel_last_book(book_id)
    else:
        print "\nUsage: '$ python prototype.py <username> <password> " \
              "<room(ex:'A340')> <day(ex:'1/10/2013')> " \
              "<start_time (ex:'21:00')> <end_time(ex:'21:30')> " \
              "<description>"
