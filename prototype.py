#!/usr/bin/env python
# coding=utf-8

# Python prototipe for an Android app to automatize login and room
# reservation of the Escola Superior de Musica de Catalunya - Asimut
# system.
#
# Copyright 2013 Arnau Orriols. All Rights Reserved.

import requests
from sys import argv

class AsimutSession (object):

    LOGIN_URL = "https://esmuc.asimut.net/public/login.php"

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


    def login(self, user, password):

        payload = {'authenticate-useraccount' : user,
                   'authenticate-password' : password}

        self.requests_session = requests.session()
        self.requests_session.cookies = \
        requests.cookies.cookiejar_from_dict({'asimut-width' : '640'})
        print self.requests_session.post(self.LOGIN_URL, data=payload).content


if __name__ == "__main__":
    
    if len(argv) == 3:
        AsimutSession().login(argv[1], argv[2])
    else:
        print "\nUsage: '$ python prototype.py <username> <password>'\n"
        print AsimutSession().LOCATIONS_ID
