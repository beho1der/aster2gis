#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import string
import datetime
import sys
import urllib
import simplejson
import lxml.html
import  random
from pyagi.pyagi import AGI

# Класс с параметрами для соединения с БД в которой лежит cdr от Asterisk
class cdrbase:
	DBHOST = "localhost"
	DBUSER = "voip"
	DBPASS = "voip2voip"
	DBNAME = "asterisk"
	PHONE_PREFIX = "351"

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
		if (num[0:3] == self.PHONE_PREFIX):      # Нужно если городские номера отправляются к VOIP провайдеру без кода города,иначе закоментировать
				num = num[3:]
				num9 = '9' + num
				cursor.execute("""SELECT src FROM cdr WHERE calldate>=(%s) AND calldate<=(%s) AND (dst=(%s) OR dst=(%s))   ORDER BY calldate DESC  LIMIT 1""",( date_start, date_end, num, num9))
		else: 
				num = '8' + num
				num9 = '9' + num
				cursor.execute("""SELECT src FROM cdr WHERE calldate>=(%s) AND calldate<=(%s) AND (dst=(%s) OR dst=(%s))   ORDER BY calldate DESC  LIMIT 1""",( date_start, date_end, num, num9))
		if cursor.fetchone() != None:
			for row in cursor:
			    x = row[0] 
		else: x='none' 
		self.db_init().close()		
		return x
# Класс с параметрами для соединения с БД voip
class calloutrec:
	DBHOST = "localhost"
	DBUSER = "voip"
	DBPASS = "voip2voip"
	DBNAME = "voip"
	GISKEY = "key"
	
	def db_init(self):
		""" Функция соединения с БД """
		connect = MySQLdb.connect(db=self.DBNAME, host=self.DBHOST, user=self.DBUSER, passwd=self.DBPASS, use_unicode=True, charset="utf8")
		connect.set_character_set('utf8')
		return connect 

	def rosfirm(self,num): 
		""" Функция парсинга ответа от www.rosfirm.ru,получения названия контрагента возвращает список вида ['Название контрагента','Префиск организации' ] """
		headers = {'User-Agent' : 'Mozilla/19.0 (compatible; MSIE 7.0; Windows NT 6.0)'}
		# ссылка для получения названия организации
		list = []
		page = urllib.urlopen("http://www.rosfirm.ru/catalog?show_list=1&se=1&field_keywords=&field_search_type=&field_phone="+num +"&field_director=&srubrik=&rubrik_id=&sel_rubrik_path=&save_rubrik_flag=1&search=1&reset_reset=1", None, headers) 
		doc = lxml.html.fromstring(page.read())
		txt = doc.xpath('//div[@class="goodsDescription"]/h3/a/text()')
		if len(txt) == 0:
			return list
		# Преобразуем массив в строку
		x = ''.join(txt[0]).encode("utf-8").strip()
		if x.find(',') == -1:
			begin = x.find('(')
			end = x.find(')')	
			srez = x[begin + 1:end]
			if srez.find('"') > 0:
				y = srez.split(' ')[0].replace('компания ','').replace('Компания ','').replace('"','').strip() # Название Организации
				z = srez[srez.find('"') + 1:srez.rfind('"')] # Префикс организации (ЗАО,ООО..)
				list.append(y) #вынести в отдельную функцию!
				list.append(z)
				return list
			y = srez.split(' ')[0].replace('компания ','').replace('Компания ','').replace('"','').strip() # Название Организации
			z = srez.split(' ')[1].strip() # Префикс организации (ЗАО,ООО..)
			list.append(y)
			list.append(z)
			return list
		y = x.split(',')[-1].strip() # Название Организации
		z = x.split(',')[-2].replace('компания ','').replace('Компания ','').replace('"','').strip() # Префикс организации (ЗАО,ООО..)
		list.append(y)
		list.append(z)
		return list

	def togis(self,num):
		""" Запрос названия организациия из базы 2gis """
		list = []
		dic_city = {39022: 'Абакан', 8182: 'Архангельск', 8512: 'Астрахань', 3852: 'Барнаул', 4722: 'Белгород', 3854: 'Бийск', 4162: 'Благовещенск', 3953: 'Братск', 4832: 'Брянск', 8162: 'Великий Новгород', 4232: 'Владивосток', 4922: 'Владимир', 8442: 'Волгоград', 8172: 'Вологда', 4732: 'Воронеж', 38822: 'Горный Алтай', 343: 'Екатеринбург', 493: 'Иваново', 3412: 'Ижевск', 3952: 'Иркутск', 8362: 'Йошкар-Ола', 843: 'Казань', 4012: 'Калининград', 4842: 'Калуга', 3842: 'Кемерово', 8332: 'Киров', 4942: 'Кострома', 861: 'Краснодар', 3912: 'Красноярск', 3522: 'Курган', 4712: 'Курск', 4742: 'Липецк', 3519: 'Магнитогорск', 8552: 'Набережные Челны', 3466: 'Нижневартовск', 8312: 'Нижний Новгород', 3435: 'Нижний Тагил', 3843: 'Новокузнецк', 8617: 'Новороссийск', 3812: 'Омск', 3532: 'Оренбург', 8412: 'Пенза', 3422: 'Пермь', 863: 'Ростов на Дону', 4912: 'Рязань', 846: 'Самара', 812: 'Санкт-Петербург', 8452: 'Саратов', 4812: 'Смоленск', 8622: 'Сочи', 8652: 'Ставрополь', 4725: 'Старый Оскол', 3473: 'Стерлитамак', 3462: 'Сургут', 8212: 'Сыктывкар', 4822: 'Тверь', 8482: 'Тольяти', 3822: 'Томск', 4872: 'Тула', 3452: 'Тюмень', 3012: 'Улан-Удэ', 8422: 'Ульяновск', 3472: 'Уфа', 4212: 'Хабаровск', 351: 'Челябинск', 3022: 'Чита', 4112: 'Якутск', 4852: 'Ярославль', 499: 'Москва', 495: 'Москва', 3513: 'Миасс'}
		if int(num[0:5]) in dic_city:
			city=dic_city[int(num[0:5])]
			num=int(num[5:])
		else: 
			if int(num[0:4]) in dic_city:
				city=dic_city[int(num[0:4])]
				num=int(num[4:])
			else:
				if int(num[0:3]) in dic_city:
					city=dic_city[int(num[0:3])]
					num=int(num[3:])
				else:return list
	    	query_url = ("http://catalog.api.2gis.ru/search?what={0}&version=1.3&where=%s&pagesize=5&key=%s&lang=ru").format(num)% (city, self.GISKEY)  
		result = simplejson.load(urllib.urlopen(query_url))
		if result.has_key('result'):
			x = result['result'][0]['name'].strip()
			y = result['result'][0]['name'].split(',')
			if len(y) > 3:
				y = x.split(',')[0].strip() # название организации	
				z = x.split(',')[1].strip() # префикс организации
				h = x.split(',')[2].strip() # описание организации
				list.append(y) 
				list.append(z)
				list.append(h)
			else: 	
				y = x.split(',')[0].strip()
				h = x.split(',')[1].strip()
				list.append(h) 
				list.append(y)		
		return list

	def togis_write(self,num,z): 
		""" Функция записи ответа от rosfirm """
		dt = datetime.date.today()
		cursor = self.db_init().cursor()
		y = self.togis(num)
		if (z == 1) and (len(y) == 0):
			return num
		if z == 1:
		        cursor.execute("""UPDATE name SET organization = %s, date = %s WHERE number = %s""",(y[1], dt, int(num)))
			return y[1]
		if len(y) == 0:
			cursor.execute("""INSERT INTO name(organization, number, date, source, prefix) values(%s,%s,%s,%s,%s)""",('none', int(num), dt, 0,'none'))
			x = 'none'
		else:						
			cursor.execute("""INSERT INTO name(organization, number, date, source, prefix) values(%s,%s,%s,%s,%s)""",(y[1], int(num), dt, 0, y[0]))	
			x = y[1] # маркер не пустого значения
		return x

	def rosfirm_write(self,num,z): 
		""" Функция записи ответа от rosfirm """
		dt = datetime.date.today()
		cursor = self.db_init().cursor()
		y = self.rosfirm(num)
		if (z == 1) and (len(y) == 0):
			return num
		if z == 1:
		        cursor.execute("""UPDATE name SET organization = %s, date = %s WHERE number = %s""",(y[1], dt, int(num)))
			return y[1]
		if len(y) == 0:
			cursor.execute("""INSERT INTO name(organization, number, date, source, prefix) values(%s,%s,%s,%s,%s)""",('none', int(num), dt, 1,'none'))
		else:						
			cursor.execute("""INSERT INTO name(organization, number, date, source, prefix) values(%s,%s,%s,%s,%s)""",(y[1], int(num), dt, 1, y[0]))
			x = y[1]
		return x	

	def main(self,num):
		""" Основная Функия """
		# Соединение с базой и получение название контагента
		cursor = self.db_init().cursor()
		cursor.execute("""SELECT organization,date,source,prefix FROM name WHERE number=%s  LIMIT 1""", int(num,))
		if cursor.fetchone() != None:
			for row in cursor:
			    x = row[0] 
			    y = row[1]
			    z = row[2]
			    h = row[3]
			y = datetime.date.today() - y
			if (x == 'none') and (y < datetime.timedelta(days=60)): # Проверяем номер в базе, чтобы постоянно не кидать запросы к web
				self.db_init().close()
				return num
			if (y > datetime.timedelta(days=60)) and (z == 1) and (x != 'none'): # Проверяем что дата не устарела для rosfirm
				 x = self.rosfirm_write(num,1) # Запрос на обновление информации
			if (y > datetime.timedelta(days=60)) and (z == 0) and (x != 'none'): # Проверяем что дата не устарела для 2GIS
				 x = self.write_togis(num,1)
		else:
			x = self.togis_write(num,0)  # Записи в базу,определение номера через 2gis!
			if (x == 'none'): x = self.rosfirm_write(num,1)  # Записи в базу,определение номера через rosfirm!
			if (x == 'none'): x = num # Возвращаем номер чтобы не приходило значение none
		self.db_init().close()
		if 'h' in locals(): c = h + " " + '"' + x + '"'
		else: return x
		if len(c) > 15: x = x
		else: x = c
		return x  # Возвращаем наименование организации и префикс,но не более 15 символов для yealink T22

if __name__ == '__main__':
	agi = AGI()
	number = agi.env["agi_callerid"]
	app = calloutrec()
	arr = cdrbase()
	name = app.main(number).encode('utf8')
	subnumber = 'SIP/' + arr.cdr(number).encode('utf8')
	agi.set_variable('calleridname', name)
	agi.set_variable('subnumber', subnumber)	
	sys.exit(0)

