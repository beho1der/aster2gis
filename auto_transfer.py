#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import string
import datetime
import sys
from pyagi.pyagi import AGI

# Класс с параметрами для соединения с БД
class cdrbase:
	DBHOST = "localhost"
	DBUSER = "voip"
	DBPASS = "voip2voip"
	DBNAME = "asterisk"


	def db_init(self):
		""" Функция соединения с БД """
		connect = MySQLdb.connect(db=self.DBNAME, host=self.DBHOST, user=self.DBUSER, passwd=self.DBPASS, use_unicode=True, charset="utf8")
		connect.set_character_set('utf8')
		return connect 

	def cdr(self,num): 
		""" Функция поиска по cdr базе в asterisk """
		d = datetime.date.today()
		date_start = d.strftime("%Y-%m-%d %H:%M:%S")
		date_end = d.strftime("%Y-%m-%d 23:59:59")	
		cursor = self.db_init().cursor()
		cursor.execute("""SELECT src FROM cdr WHERE calldate>=(%s) AND calldate<=(%s) AND dst=(%s)  ORDER BY calldate DESC  LIMIT 1""",( date_start, date_end, num))
		if cursor.fetchone() != None:
			for row in cursor:
			    x = row[0] 
		else:
			    x='none' 
		self.db_init().close()		
		return x
			

if __name__ == '__main__':
	agi = AGI()
	number = agi.env["agi_callerid"]
	arr = cdrbase()
	subnumber = 'SIP/' + arr.cdr(number).encode('utf8')
	agi.set_variable('subnumber', subnumber)
	sys.exit(0)

