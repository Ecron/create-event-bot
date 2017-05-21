# -*- coding: utf-8 -*-

import time
from modules import inline
from datetime import datetime

from parsedatetime import parsedatetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardHide
from telegram.ext import CommandHandler, MessageHandler, Filters
from validators import url, ValidationFailure

from store import TinyDBStore

from config import params, chats, allowed_users, other_users

FIELDS = [
    {
        'name': 'name',
        'message': '\u0031\u20E3 Envia\'m el *nom de l\'excursió*.\n\nPer a cancel·lar el procés, envia /cancel.',
        'required': True
    },
    {
        'name': 'description',
        'message': '\u0032\u20E3 Envia\'m una *descripció breu* de l\'excursió.\n\nPots enviar /omet per a deixar el camp en blanc o /cancel per a cancel·lar la creació de l\'excursió.',
        'required': False
    },
    {
        'name': 'type',
        'message': '\u0033\u20E3 Especifia el *tipus de ruta* que aneu a fer: senderisme, bicicleta, etc.\n\nPer a cancel·lar el procés, envia /cancel',
        'required': True
    },
    {
        'name': 'duration',
        'message': '\u0034\u20E3 Envia\'m ara la duració mitja de l\'excursió: 1 hora, 5 hores, etc.\n\nPots enviar /omet per a deixar el camp en blanc o /cancel per a cancel·lar la creació de l\'excursió.',
        'required': False
    },
    {
        'name': 'difficulty',
        'message': '\u0035\u20E3 Quina dificultat té la ruta: Difícil, moderada, fàcil?\n\nPots enviar /omet per a deixar el camp en blanc o /cancel per a cancel·lar la creació de l\'excursió.',
        'required': False
    },
    {
        'name': 'month',
        'message': '\u0036\u20E3 Ara m\'hauràs d\'enviar la *data i hora* d\'eixida de l\'excursió.\n\n\U0001F5D3 En primer lloc selecciona el *mes*:',
        'required': True
    },
    {
        'name': 'day',
        'message': '\U0001F5D3 En segon lloc, hauràs de seleccionar el *dia*:',
        'required': True
    },
    {
        'name': 'year',
        'message': '\U0001F5D3 Selecciona l\'*any*:',
        'required': True
    },
    {
        'name': 'hour',
        'message': '\U0001F570 Selecciona l\'*hora*:',
        'required': True
    },
    {
        'name': 'minute',
        'message': '\U0001F570 I per a acabar, selecciona el *minut* d\'entre els quatre quarts o escriu qualsevol número entre 0 i 59:',
        'required': True
    },
    {
        'name': 'date',
        'message': 'Comprova que la data és correcta (seguint l\'ordre *mes/dia/any hora:minut*) i si és així toca el botó per a guardar-la.\n\nPer a cancel·lar el procés, envia /cancel.',
        'required': True
    },
    {
        'name': 'place',
        'message': '\u0036\u20E3 Envia\'m el *punt de trobada* on iniciareu l\'excursió. Pot ser el *nom* d\'un carrer, una plaça, etc. o una *ubicació* enviada des del 📎 > Ubicació.\n\nPots enviar /omet per a deixar el camp en blanc o /cancel per a cancel·lar la creació de l\'excursió.',
        'required': False
    },
    {
        'name': 'parking',
        'message': '\u0037\u20E3 Si per a l\'excursió és menester agafar el cotxe, envia\'m el *lloc a on l\'aparcareu*, que serà el punt d\'eixida de l\'excursió. Pot ser el *nom* d\'un carrer, una plaça, etc. o una *ubicació* enviada des del 📎 > Ubicació.\n\nPots enviar /omet per a deixar el camp en blanc o /cancel per a cancel·lar la creació de l\'excursió.',
        'required': False
    },
    {
        'name': 'route',
        'message': '\u0038\u20E3 Envia\'m l\'*URL del mapa amb el GPX de la ruta*. Ací també pots enviar l\'URL d\'una pàgina de _Wikiloc_, per exemple.\n\nPots enviar /omet per a deixar el camp en blanc o /cancel per a cancel·lar el procés de creació de l\'excursió.',
        'required': False
    },
]


def parse_fields(field, value):
    if field == 'month':
        if value == 'Gener' or value == 'Febrer' or value == 'Març' or value == 'Abril' or value == 'Maig' or value == 'Juny' or value == 'Juliol' or value == 'Agost' or value == 'Setembre' or value == 'Octubre' or value == 'Novembre' or value == 'Desembre':  
             return value
        elif value == 'gener' or value == 'febrer' or value == 'març' or value == 'abril' or value == 'maig' or value == 'juny' or value == 'juliol' or value == 'agost' or value == 'setembre' or value == 'octubre' or value == 'novembre' or value == 'desembre':
             valuecap = value.capitalize()  
             return valuecap
        else:
             error = 'error'
             return error
    if field == 'day':
        try:
             value2 = int(value)
        except:
             error = 'error'
             return error
        if value2 >= 1 and value2 <= 31:
             return value
        else:
             error = 'error'
             return error
    if field == 'year':
        actualdate = datetime.now()
        actualyear = int(actualdate.year)
        try:
             value2 = int(value)
        except:
             error = 'error'
             return error
        if value2 >= actualyear and value2 <= actualyear + 3:
             return value
        else:
             error = 'error'
             return error
    if field == 'hour':
        try:
             value2 = int(value)
        except:
             error = 'error'
             return error
        if value2 >= 0 and value2 <= 23:
             return value
        else:
             error = 'error'
             return error
    if field == 'minute':
        try:
             value2 = int(value)
        except:
             error = 'error'
             return error
        if value2 >= 0 and value2 <= 59:
             return value
        else:
             error = 'error'
             return error
    if field == 'date':
        if value.find('/') == 2 and value.find('/', 3) == 5 and value.find(':') == 13:
             cal = parsedatetime.Calendar()
             time_struct, parse_status = cal.parse(value)
             timestamp = time.mktime(datetime(*time_struct[:6]).timetuple())
             return str(int(timestamp))
        else:
             error = 'error'
             return error

    if field == 'route':
        try:
             assert url(value)
             return value
        except:
             error = 'error'
             return error

    if field == 'type':
        if value != "Senderisme" and value != "Bicicleta" and value != "Nocturna":
             error = 'error'
             return error
        else:
             return value

    return value


def help_command(bot, update):
    if str(chat_id) == chats['group']:
        bot.sendMessage(update.message.chat_id, text="Sóc el robot *Rutes guapes* i la meua funció és organitzar les excursions que es faran en aquest grup: establir la data, els punts de trobada, la ruta, la durada, etc. Podeu enviar les ordres següents si voleu informació extra:\n\n\\ruta: Envie el missatge de la pròxima ruta.\n\\llista: Envie la llista d'excursions que haveu fet.\nSi se vos acudeix cap altra funcionalitat que estiga bé, digueu-ho i l'@Artur mirarà d'incorporar-la 😉.", parse_mode="Markdown")
    else:
        bot.sendMessage(update.message.chat_id, text='Aquest bot és privat i només alguns usuaris poden crear esdeveniments per a excursions. Si quan envies /start reps un missatge amb el teu \U0001F194, això vol dir que no tens permisos.')

class CommandsModule(object):
    def __init__(self):
        self.handlers = [
            CommandHandler('start', self.start_command, pass_args=True),
            CommandHandler('omet', self.skip_command),
	    CommandHandler('cancel', self.cancel_command),
#            CommandHandler('invite', self.invite_channel),
            CommandHandler('ruta', self.get_route_command),
            CommandHandler('llista', self.get_list_command),
            CommandHandler('elimina', self.delete_command),
            CommandHandler('raw', self.get_raw_command),
            CommandHandler('users', self.get_users_command),
            CommandHandler('help', help_command),
            MessageHandler([Filters.text], self.message),
            MessageHandler([Filters.location], self.message_location)
        ]
        self.store = TinyDBStore()

    def start_command(self, bot, update, args):
        user_id = str(update.message.from_user.id)
        chat_id = update.message.chat_id
        user_f = update.message.from_user.first_name
        user_u = update.message.from_user.username
#        if len(args) == 0:
        if str(chat_id) == chats['group']:
            bot.sendMessage(chat_id, parse_mode='Markdown',
                            text="Bon dia! Envieu /ruta si voleu recordar quina és la pròxima ruta. Si voleu crear-ne una, envieu-me un missatge en privat 😉")
        else:
            if str(user_id) in allowed_users.values():
                self.store.new_draft(user_id)
                bot.sendMessage(update.message.chat_id,parse_mode='Markdown',
                            text="Crearem un esdeveniment per a una excursió.\n\n\u0031\u20E3 El primer que has de fer és enviar-me el *nom de l\'excursió*.\n\nSi no vols continuar amb el procés, envia /cancel.",
                            reply_markup=ReplyKeyboardHide()
		)
            else:
                f_name = update.message.from_user.first_name
                bot.sendMessage(update.message.chat_id,
                            text= str(f_name) + ", no tens permís per a crear excursions \U0001F622.\nSi vols obtindre permisos, parla amb l'administrador (necessitaràs el teu identificador d'usuari.\n\U0001F194 = " + str(user_id) + ").")
                bot.sendMessage(chat_id = allowed_users['admin'],
                            text = "L'usuari " + user_f + " (@" + user_u + ", " + user_id + ") ha enviat l'ordre /start."
                ) 
#        elif len(args) == 1 and args[0] == 'convida-al-canal':
#            self.invite_channel(bot, update)

    def message(self, bot, update):
        user_id = str(update.message.from_user.id)
        chat_id = update.message.chat_id
        text = update.message.text
        draft = self.store.get_draft(user_id)

        if draft:
            event = draft['event']
            current_field = draft['current_field']
            field = FIELDS[current_field]

            event[field['name']] = parse_fields(field['name'], text)
            if field['name'] == 'day' and event['day'] == 'error':
                  bot.sendMessage(
                  update.message.chat_id,
                  text="\u26A0\uFE0F No és un dia vàlid, assegura't que és un número entre 1 i 31 i torna a provar-ho."
                  )
                  current_field += 0
                  self.update_draft(bot, event, user_id, update, current_field)

            elif field['name'] == 'month' and event['month'] == 'error':
                  bot.sendMessage(
                  update.message.chat_id,
                  text="\u26A0\uFE0F No és un mes vàlid, escriu-lo amb lletres i en valencià i torna a provar-ho."
                  )
                  current_field += 0
                  self.update_draft(bot, event, user_id, update, current_field)

            elif field['name'] == 'year' and event['year'] == 'error':
                  actualdate = datetime.now()
                  actualyear = int(actualdate.year)
                  bot.sendMessage(
                  update.message.chat_id,
                  text="\u26A0\uFE0F No és un any vàlid, has d'escriure " + str(actualyear) + ", " + str(actualyear + 1) + ", " + str(actualyear + 2) + " o " + str(actualyear + 3) + " i tornar a provar-ho."
                  )
                  current_field += 0
                  self.update_draft(bot, event, user_id, update, current_field)

            elif field['name'] == 'hour' and event['hour'] == 'error':
                  bot.sendMessage(
                  update.message.chat_id,
                  text="\u26A0\uFE0F No és una hora vàlida, assegura't que és un número entre 0 i 23 i torna a provar-ho."
                  )
                  current_field += 0
                  self.update_draft(bot, event, user_id, update, current_field)

            elif field['name'] == 'minute' and event['minute'] == 'error':
                  bot.sendMessage(
                  update.message.chat_id,
                  text="\u26A0\uFE0F No és un minut vàlid, assegura't que és un número entre 0 i 59 i torna a provar-ho."
                  )
                  current_field += 0
                  self.update_draft(bot, event, user_id, update, current_field)

            elif field['name'] == 'date' and event['date'] == 'error':
                  bot.sendMessage(
                  update.message.chat_id,
                  text="\u26A0\uFE0F No és una data vàlida. Si la data és correcta, prem el botó, no escrigues cap text."
                  )
                  current_field += 0
                  self.update_draft(bot, event, user_id, update, current_field)

            elif field['name'] == 'route' and event['route'] == 'error':
                  bot.sendMessage(
                  update.message.chat_id,
                  text="\u26A0\uFE0F Sembla que l'URL que has enviat no és vàlid, comprova'l i torna a enviar-lo."
                  )
                  current_field += 0
                  self.update_draft(bot, event, user_id, update, current_field)

            elif field['name'] == 'type' and event['type'] == 'error':
                  bot.sendMessage(
                  update.message.chat_id,
                  text="\u26A0\uFE0F Eixe tipus de ruta no és vàlid, usa els botons per triar-ne un."
                  )
                  current_field += 0
                  self.update_draft(bot, event, user_id, update, current_field)

            else:
                  current_field += 1

                  self.update_draft(bot, event, user_id, update, current_field)

        else:
            if str(chat_id) != chats['group']: 
                bot.sendMessage(
                    update.message.chat_id,
                    text="\U0001F914 No entenc el que em vols dir, però sóc un robot \U0001F916 i funcione de manera molt senzilla:\n\n1. /start per a començar a crear una excursió nova\n2. /help per a saber un poc més sobre mi.",
                    reply_markup=ReplyKeyboardHide()
                )

    def message_location(self, bot, update):
        user_id = str(update.message.from_user.id)
        text = str(update.message.location.latitude) + "|" + str(update.message.location.longitude)
        draft = self.store.get_draft(user_id)

        if draft:
            event = draft['event']
            current_field = draft['current_field']
            field = FIELDS[current_field]

            if field['name'] == 'place' or field['name'] == 'parking':
                event[field['name']] = parse_fields(field['name'], text)

                current_field += 1

                self.update_draft(bot, event, user_id, update, current_field)
            else:
                bot.sendMessage(
                    update.message.chat_id,
                    text="\u26A0\uFE0F En aquest pas no pots enviar una ubicació. Torna a provar-ho seguint els passos que s'indiquen."
                    )
                current_field += 0
                self.update_draft(bot, event, user_id, update, current_field)
        else:
            bot.sendMessage(
            update.message.chat_id,
            text="\U0001F914 No sé a on para això, ni per què m'ho has enviat. Si vols fer alguna cosa útil:\n\n1. /start per a començar a crear una excursió nova\n2. /help per a saber un poc més sobre mi.",
            reply_markup=ReplyKeyboardHide()
            )

    def cancel_command(self, bot, update):
        user_id = str(update.message.from_user.id)
        chat_id = update.message.chat_id
        draft = self.store.get_draft(user_id)

        if str(chat_id) != chats['group']:
            if draft:
                self.store.remove_draft(user_id)
                bot.sendMessage(
                update.message.chat_id,
                text="\U0001F5D1 S'ha cancel·lat la creació de l'excursió.",
                reply_markup=ReplyKeyboardHide()
                )
            else:
                bot.sendMessage(
                update.message.chat_id,
                text="\u26A0\uFE0F No hi ha res a cancel·lar.\nAquesta ordre només funciona quan s'ha iniciat la creació d'una excursió.",
                reply_markup=ReplyKeyboardHide()
            )

    def skip_command(self, bot, update):
        user_id = str(update.message.from_user.id)
        chat_id = update.message.chat_id
        draft = self.store.get_draft(user_id)

        if str(chat_id) != chats['group']:
            if draft:
                current_field = draft['current_field']
                field = FIELDS[current_field]

                if field['required']:
                    bot.sendMessage(update.message.chat_id,parse_mode='Markdown',
                                    text="\u26A0\uFE0F Aquest camp és necessari.\n\n" + field['message'])
                else:
                    event = draft['event']
                    current_field += 1
                    self.update_draft(bot, event, user_id, update, current_field)

            else:
                bot.sendMessage(update.message.chat_id,
                                text="\u26A0\uFE0F Aquesta ordre només té sentit si s'està creant una excursió i es vol deixar en blanc un camp que no és necessari.")

    def get_route_command(self, bot, update):
        user = update.message.from_user.__dict__
        user_id = str(update.message.from_user.id)
        user_f = update.message.from_user.first_name
        user_u = update.message.from_user.username
        chat_id = update.message.chat_id
        esdevens = len(self.store.events_db)
        event = self.store.get_event(esdevens)

        if str(chat_id) == chats['group']:
            if esdevens > 1:
                bot.sendMessage(chat_id = update.message.chat_id,
                        text = inline.create_event_message(event, user),
                        reply_markup = InlineKeyboardMarkup(inline_keyboard = inline.create_keyboard(event, user)),
                        parse_mode = "MARKDOWN",
	                disable_web_page_preview = True
                )
            else:
                bot.sendMessage(chat_id = update.message.chat_id,
                        text = "Encara no s'ha programat cap excursió!",
                        parse_mode = "MARKDOWN"
                )
        else:
            bot.sendMessage(chat_id = update.message.chat_id,
                        text = "Aquesta ordre no es troba disponible als xats individuals.",
            )
            bot.sendMessage(chat_id = allowed_users['admin'],
                            text = "L'usuari " + user_f + " (@" + user_u + ", " + user_id + ") ha enviat l'ordre /ruta."
            )

    def get_list_command(self, bot, update):
        user_id = str(update.message.from_user.id)
        user_f = update.message.from_user.first_name
        user_u = update.message.from_user.username
        chat_id = update.message.chat_id
        message = "Ací teniu la llista de les pròximes excursions:\n\n"
        esdevens = len(self.store.events_db) + 1
        actualdate = datetime.now()

        if str(chat_id) == chats['group']:
            y = 1
            for x in range(2, esdevens):
                eventX = self.store.get_event(x)

                if eventX['month'] == 'Gener':
                     monthnum = 1
                elif eventX['month'] == 'Febrer':
                     monthnum = 2
                elif eventX['month'] == 'Març':
                     monthnum = 3
                elif eventX['month'] == 'Abril':
                     monthnum = 4
                elif eventX['month'] == 'Maig':
                     monthnum = 5
                elif eventX['month'] == 'Juny':
                     monthnum = 6
                elif eventX['month'] == 'Juliol':
                     monthnum = 7
                elif eventX['month'] == 'Agost':
                     monthnum = 8
                elif eventX['month'] == 'Setembre':
                     monthnum = 9
                elif eventX['month'] == 'Octubre':
                     monthnum = 10
                elif eventX['month'] == 'Novembre':
                     monthnum = 11
                else:
                     monthnum = 12

                if eventX == None:
                    message = message
                    y += 1
                elif int(eventX['year']) >= actualdate.year and monthnum > int(actualdate.month):
                    message += "_" + str(eventX.eid - y) + "_. *" + eventX['name'] + "* el " + inline.format_date(eventX['date']) + "\n"
                elif monthnum == int(actualdate.month) and int(eventX['day']) >= actualdate.day:
                    message += "_" + str(eventX.eid - y) + "_. *" + eventX['name'] + "* el " + inline.format_date(eventX['date']) + "\n"

            bot.sendMessage(chat_id = update.message.chat_id,
                        text = message,
                        parse_mode = "MARKDOWN"
            )
        else:
            bot.sendMessage(chat_id = update.message.chat_id,
                        text = "Aquesta ordre no es troba disponible als xats individuals.",
            )
            bot.sendMessage(chat_id = allowed_users['admin'],
                            text = "L'usuari " + user_f + " (@" + user_u + ", " + user_id + ") ha enviat l'ordre /llista."
            )
    def delete_command(self, bot, update):
        user_id = str(update.message.from_user.id)
        chat_id = update.message.chat_id
        user_f = update.message.from_user.first_name
        user_u = update.message.from_user.username

        if str(user_id) == allowed_users['admin']:
#            if len(args) == 0:
                esdevens = len(self.store.events_db)
                event = self.store.get_event(esdevens)

                self.store.remove_event(event)

                bot.sendMessage(update.message.chat_id,
                        text = "S'ha eliminat l'última excursió 👍.",
                        parse_mode = "Markdown",
                )
#            elif len(args) == 1:
#                esdevens = int(args[0]) + 1
#                event = self.store.get_event(str(esdevens))

#                self.store.remove_event(event)

#                bot.sendMessage(update.message.chat_id,
#                        text = "S'ha eliminat l'excursió número " + args[0] + ". *" + event['name'] + "👍.",
#                        parse_mode = "Markdown",
#                )
#            elif len(args) > 1:
#                bot.sendMessage(update.message.chat_id,
#                        text = "Només podeu enviar-li un argument a esta ordre."
#                )
         
        else:
            bot.sendMessage(
                update.message.chat_id,
                text="No tens permís per a realitzar aquesta acció."
            )
            bot.sendMessage(chat_id = allowed_users['admin'],
                            text = "L'usuari " + user_f + " (@" + user_u + ", " + user_id + ") ha enviat la comanda /delete."
            )

    def update_draft(self, bot, event, user_id, update, current_field):
        self.store.update_draft(user_id, event, current_field)

        if current_field <= len(FIELDS) - 1:

            if FIELDS[current_field]['name'] == 'type':
                bot.sendMessage(
                    update.message.chat_id,
                    parse_mode='Markdown',
                    text=FIELDS[current_field]['message'],
                    reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                              ['Senderisme','Bicicleta','Nocturna']
                         ],
                         one_time_keyboard=True,
                         resize_keyboard=True
                ))

            elif FIELDS[current_field]['name'] == 'month':
                bot.sendMessage(
                    update.message.chat_id,
                    parse_mode='Markdown',
                    text=FIELDS[current_field]['message'],
                    reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                              ['Gener','Febrer','Març'], ['Abril','Maig','Juny'],['Juliol','Agost','Setembre'],['Octubre','Novembre','Desembre']
                         ],
                         one_time_keyboard=True,
                         resize_keyboard=True
                ))

            elif FIELDS[current_field]['name'] == 'day' and event['month'] == 'Febrer':
                bot.sendMessage(
                    update.message.chat_id,
                    parse_mode='Markdown',
                    text=FIELDS[current_field]['message'],
                    reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                              ['01','02','03','04'],['05','06','07','08'],['09','10','11','12'],['13','14','15','16'],['17','18','19','20'],['21','22','23','24'],['25','26','27','28'],['29']
                         ],
                         one_time_keyboard=True,
                         resize_keyboard=True
                ))

            elif FIELDS[current_field]['name'] == 'day' and event['month'] == 'Abril':
                bot.sendMessage(
                    update.message.chat_id,
                    parse_mode='Markdown',
                    text=FIELDS[current_field]['message'],
                    reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                              ['01','02','03','04'],['05','06','07','08'],['09','10','11','12'],['13','14','15','16'],['17','18','19','20'],['21','22','23','24'],['25','26','27','28'],['29','30']
                         ],
                         one_time_keyboard=True,
                         resize_keyboard=True
                ))


            elif FIELDS[current_field]['name'] == 'day' and event['month'] == 'Juny':
                bot.sendMessage(
                    update.message.chat_id,
                    parse_mode='Markdown',
                    text=FIELDS[current_field]['message'],
                    reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                              ['01','02','03','04'],['05','06','07','08'],['09','10','11','12'],['13','14','15','16'],['17','18','19','20'],['21','22','23','24'],['25','26','27','28'],['29','30']
                         ],
                         one_time_keyboard=True,
                         resize_keyboard=True
                ))


            elif FIELDS[current_field]['name'] == 'day' and event['month'] == 'Setembre':
                bot.sendMessage(
                    update.message.chat_id,
                    parse_mode='Markdown',
                    text=FIELDS[current_field]['message'],
                    reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                              ['01','02','03','04'],['05','06','07','08'],['09','10','11','12'],['13','14','15','16'],['17','18','19','20'],['21','22','23','24'],['25','26','27','28'],['29','30']
                         ],
                         one_time_keyboard=True,
                         resize_keyboard=True
                ))


            elif FIELDS[current_field]['name'] == 'day' and event['month'] == 'Novembre':
                bot.sendMessage(
                    update.message.chat_id,
                    parse_mode='Markdown',
                    text=FIELDS[current_field]['message'],
                    reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                              ['01','02','03','04'],['05','06','07','08'],['09','10','11','12'],['13','14','15','16'],['17','18','19','20'],['21','22','23','24'],['25','26','27','28'],['29','30']
                         ],
                         one_time_keyboard=True,
                         resize_keyboard=True
                ))

            elif FIELDS[current_field]['name'] == 'day':
                bot.sendMessage(
                    update.message.chat_id,
                    parse_mode='Markdown',
                    text=FIELDS[current_field]['message'],
                    reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                              ['01','02','03','04'],['05','06','07','08'],['09','10','11','12'],['13','14','15','16'],['17','18','19','20'],['21','22','23','24'],['25','26','27','28'],['29','30','31']
                         ],
                         one_time_keyboard=True,
                         resize_keyboard=True
                ))

            elif FIELDS[current_field]['name'] == 'year':
                now = datetime.now()
                now2 = int(now.year)
                now3 = str(now2)
                next1 = str(now2 + 1)
                next2 = str(now2 + 2)
                next3 = str(now2 + 3)
                bot.sendMessage(
                    update.message.chat_id,
                    parse_mode='Markdown',
                    text=FIELDS[current_field]['message'],
                    reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                              [now3],[next1],[next2],[next3]
                         ],
                         one_time_keyboard=True,
                         resize_keyboard=True
                ))

            elif FIELDS[current_field]['name'] == 'hour':
                bot.sendMessage(
                    update.message.chat_id,
                    parse_mode='Markdown',
                    text=FIELDS[current_field]['message'],
                    reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                              ['06','07','08','09'],['10','11','12','13'],['14','15','16','17'],['18','19','20','21'],['22','23','00','01'],['02','03','04','05']
                         ],
                         one_time_keyboard=True,
                         resize_keyboard=True
                ))

            elif FIELDS[current_field]['name'] == 'minute':
                bot.sendMessage(
                    update.message.chat_id,
                    parse_mode='Markdown',
                    text=FIELDS[current_field]['message'],
                    reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                              ['00','15'],['30','45']
                         ],
                         one_time_keyboard=True,
                         resize_keyboard=True
                ))

            elif FIELDS[current_field]['name'] == 'date':
                 day = event['day']
                 year = event['year']
                 hour = event['hour']
                 minute = event['minute']
                 if event['month'] == 'Gener':
                      monthnum = '01'
                 elif event['month'] == 'Febrer':
                      monthnum = '02'
                 elif event['month'] == 'Març':
                      monthnum = '03'
                 elif event['month'] == 'Abril':
                      monthnum = '04'
                 elif event['month'] == 'Maig':
                      monthnum = '05'
                 elif event['month'] == 'Juny':
                      monthnum = '06'
                 elif event['month'] == 'Juliol':
                      monthnum = '07'
                 elif event['month'] == 'Agost':
                      monthnum = '08'
                 elif event['month'] == 'Setembre':
                      monthnum = '09'
                 elif event['month'] == 'Octubre':
                      monthnum = '10'
                 elif event['month'] == 'Novembre':
                      monthnum = '11'
                 else:
                      monthnum = '12'
                 newdate = monthnum + "/" + day + "/" + year + " " + hour + ":" + minute
                 bot.sendMessage(
                    update.message.chat_id,
                    parse_mode='Markdown',
                    text=FIELDS[current_field]['message'],
                    reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                              [newdate]
                         ],
                         one_time_keyboard=True,
                         resize_keyboard=True
                ))

            elif FIELDS[current_field]['name'] != 'month' or FIELDS[current_field]['name'] != 'day' or FIELDS[current_field]['name'] != 'year' or FIELDS[current_field]['name'] != 'hour' or FIELDS[current_field]['name'] != 'minute' or FIELDS[current_field]['name'] != 'date':
                bot.sendMessage(
                    update.message.chat_id,
                    parse_mode='Markdown',
                    text=FIELDS[current_field]['message'],
                    reply_markup=ReplyKeyboardHide()
                )
        else:
            event['user_id'] = user_id
            self.create_event(bot, update, event)

    def create_event(self, bot, update, event):
        self.store.insert_event(event)
        self.store.remove_draft(update.message.from_user.id)

        keyboard = [[InlineKeyboardButton(text="Envia l'excursió", callback_data='enviagrup_' + str(event['id']))], []]
#switch_inline_query=event['name'])], []]
        bot.sendMessage(
            update.message.chat_id,
            text="S'ha creat l'excursió *" + event['name'] + "* 👍",
            parse_mode = "Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )

#    def invite_channel(self, bot, update):
#        user_id = update.message.from_user.id
#        user_f = update.message.from_user.first_name
#        user_ln = update.message.from_user.last_name
#        user_u = update.message.from_user.username
#        if user_ln != "" and user_u != "":
#           user_d= user_f + " " + user_ln + "* (podeu contactar-hi amb @" + user_u + ")"
#        elif user_ln == "" and user_u != "":
#           user_d= user_f + "* (podeu contactar-hi amb @" + user_u + ")" 
#        elif user_ln != "" and user_u == "":
#           user_d= user_f + " " + user_ln + "*"
#        elif user_ln == "" and user_u == "":
#           user_d= user_f + "*"
#        if str(user_id) in other_users.values():
#            keyboard = [[InlineKeyboardButton(text="\u2709\uFE0F Convida al canal", switch_inline_query="Convideu al canal")], []]
#            bot.sendMessage(
#                update.message.chat_id,
#                text="Visca! Teniu permisos per a convidar gent al canal privat *CELP familiar*.\n\nPer convidar a algú al canal primer premeu el botó _Convida al canal_, i a continuació seleccioneu l'usuari a qui voleu convidar. Llavors haureu de prémer la capseta amb el rètol *«Convideu al canal»*",
#                parse_mode='Markdown',
#                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
#            )
#            bot.sendMessage(
#                chat_id= allowed_users['admin'],
#                text="\U0001F6A6 L'usuari *" +user_d+ " ha volgut convidar a algú al canal, i té permisos.",
#                parse_mode='Markdown'
#            )
#        else:
#            bot.sendMessage(
#                update.message.chat_id,
#                text="No teniu permisos per convidar gent al canal privat *CELP familiar*.",
#                parse_mode='Markdown'
#            )
#            bot.sendMessage(
#                chat_id= allowed_users['admin'],
#                text="\u26A0\uFE0F\n\U0001F6A6 L'usuari *" +user_d+ " ha volgut convidar a algú al canal i no té permisos.\nPer donar-li permisos, el seu \U0001F194: " + str(user_id) + ".",
#                parse_mode='Markdown'
#            )

    def get_users_command(self, bot, update):
        user_id = str(update.message.from_user.id)
        user_f = update.message.from_user.first_name
        user_u = update.message.from_user.username

        if str(user_id) == allowed_users['admin']:
            u_list = other_users.keys()
            u_list2=sorted(u_list)
            list_u= "T\'envie el llistat d'*usuaris amb permisos* per a convidar al canal:\n"
            for u in u_list2:
               list_u += "- " + u + "\n"
            bot.sendMessage(
                update.message.chat_id,
                text= list_u,
                parse_mode='Markdown'
            )
        else:
            bot.sendMessage(
                update.message.chat_id,
                text="No tens permís per a realitzar aquesta acció.",
                parse_mode='Markdown'
            )
            bot.sendMessage(chat_id = allowed_users['admin'],
                            text = "L'usuari " + user_f + " (@" + user_u + ", " + user_id + ") ha enviat la comanda /users."
            )

    def get_raw_command(self, bot, update):
        user_id = str(update.message.from_user.id)
        user_f = update.message.from_user.first_name
        user_u = update.message.from_user.username

        if user_id == allowed_users['admin']:
            bot.sendMessage(
                update.message.chat_id,
                text="T\'envie els fitxers amb les *dades en cru*:",
                parse_mode='Markdown'
            )
            events_file= open('events.json', 'rb')
            bot.sendDocument(update.message.chat_id,
                             document=events_file)
            drafts_file= open('event_drafts.json', 'rb')
            bot.sendDocument(update.message.chat_id,
                             document=drafts_file)
#            invites_file= open('invites.csv', 'rb')
#            bot.sendDocument(update.message.chat_id,
#                             document=invites_file)
        else:
            bot.sendMessage(
                update.message.chat_id,
                text="No tens permís per a realitzar aquesta acció.",
                parse_mode='Markdown'
            )
            bot.sendMessage(chat_id = allowed_users['admin'],
                            text = "L'usuari " + user_f + " (@" + user_u + ", " + user_id + ") ha enviat la comanda /raw."
            )

    def get_handlers(self):
        return self.handlers
