#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peewee import *
from application import Uzanto, Tu, db

db.connect()

Tu.delete().execute()

db.close()
