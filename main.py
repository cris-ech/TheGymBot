# -*- coding: utf-8 -*-

import telebot
import json
from config import API_TOKEN, USERS_FILE, IMG_DIR, AUX_DIR
from rutinas_list import rutinas_list
import matplotlib.pyplot as plt
import os
from random import choice
from time import gmtime, strftime

bot = telebot.TeleBot(API_TOKEN)

try:
    fich = open(USERS_FILE, "r")
    users = json.loads(fich.read())
    fich.close()
except IOError:
    users = {}


nextmarca = {}

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    if str(message.chat.id) not in users:
        users[str(message.chat.id)] = {}
        actualizar_fichero()
    bot.reply_to(message, """\
Bienvenido a Rutinas bot

Los comandos disponibles son:
/start - Inicia el bot
/help - Muestra este mensaje
/crearrutina - Crea tu rutina
/imc - Calcula tu IMC y registra tus datos
/grafica - Muestra gráficas sobre tus datos
/motivame - Muestra imágenes con frases motivantes
/nuevamarca - Añade una nueva marca
/mostrarmarcas - Muestra las marcas almacenadas
/dieta - Mostrar sugerencias de dietas
/reset - Reinicia los datos
/creditos - Mostrar los créditos
""")

@bot.message_handler(commands=['crearrutina'])
def send_inicio(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Principiante', 'Intermedio', 'Avanzado')
    bot.send_message(message.chat.id, "Selecciona tu nivel:", reply_markup=markup)
    bot.register_next_step_handler(message, objetivo_msg)

def objetivo_msg(message):
    if message.text == 'Principiante':
        users[str(message.chat.id)]['lvl'] = 0
    elif message.text == 'Intermedio':
        users[str(message.chat.id)]['lvl'] = 1
    elif message.text == 'Avanzado':
        users[str(message.chat.id)]['lvl'] = 2
    else:
        bot.register_next_step_handler(message, objetivo_msg)
        return

    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Ganar masa muscular', 'Perder peso', 'Ganar fuerza')
    bot.send_message(message.chat.id, '¿Cual es tu objetivo?', reply_markup=markup)
    bot.register_next_step_handler(message, tipoDeRutina)

def tipoDeRutina(message):
    if message.text == 'Ganar masa muscular':
        users[str(message.chat.id)]['obj'] = 0
    elif message.text == 'Perder peso':
        users[str(message.chat.id)]['obj'] = 1
    elif message.text == 'Ganar fuerza':
        users[str(message.chat.id)]['obj'] = 2
    else:
        bot.register_next_step_handler(message, RecibeTipoDeRutina)
        return

    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    #markup.add('Full Body', 'Torso-Pierna', 'Weider', 'Tiron-Empujon')
    if '0' in rutinas_list[users[str(message.chat.id)]['lvl']][users[str(message.chat.id)]['obj']]:
        markup.add('Full Body')
    if '1' in rutinas_list[users[str(message.chat.id)]['lvl']][users[str(message.chat.id)]['obj']]:
        markup.add('Torso-Pierna')
    if '2' in rutinas_list[users[str(message.chat.id)]['lvl']][users[str(message.chat.id)]['obj']]:
        markup.add('Weider')
    if '3' in rutinas_list[users[str(message.chat.id)]['lvl']][users[str(message.chat.id)]['obj']]:
        markup.add('Tiron-Empujon')
    bot.send_message(message.chat.id, '¿Que tipo de rutina prefieres?', reply_markup=markup)
    bot.register_next_step_handler(message, RecibeTipoDeRutina)
    
def RecibeTipoDeRutina(message):
    if message.text == 'Full Body':
        users[str(message.chat.id)]['tipo'] = 0
    elif message.text == 'Torso-Pierna':
        users[str(message.chat.id)]['tipo'] = 1
    elif message.text == 'Weider':
        users[str(message.chat.id)]['tipo'] = 2
    elif message.text == 'Tiron-Empujon':
        users[str(message.chat.id)]['tipo'] = 3
    else:
        bot.register_next_step_handler(message, RecibeTipoDeRutina)
        return

    actualizar_fichero()

    bot.send_message(message.chat.id, rutinas_list[users[str(message.chat.id)]['lvl']][users[str(message.chat.id)]['obj']][str(users[str(message.chat.id)]['tipo'])])

@bot.message_handler(commands=['imc'])
def imc1(message):
    bot.send_message(message.chat.id, "Introduce tu altura en cm")
    bot.register_next_step_handler(message, imc2)

def imc2(message):
    if 'altura' not in users[str(message.chat.id)] :
        users[str(message.chat.id)]['altura'] = []
    try:
        users[str(message.chat.id)]['altura'].append(int(message.text))
    except ValueError:
        bot.register_next_step_handler(message, imc2)
        return
    bot.send_message(message.chat.id, "Introduce tu peso en kg")
    bot.register_next_step_handler(message, calcularimc)

def calcularimc(message):
    if 'peso' not in users[str(message.chat.id)] :
        users[str(message.chat.id)]['peso'] = []
    try:
        users[str(message.chat.id)]['peso'].append(int(message.text))
    except ValueError:
        bot.register_next_step_handler(message, calcularimc)
        return
    imc = round(users[str(message.chat.id)]['peso'][-1] / pow(float(users[str(message.chat.id)]['altura'][-1])/100, 2), 2)
    if 'imc' not in users[str(message.chat.id)] :
        users[str(message.chat.id)]['imc'] = []
    users[str(message.chat.id)]['imc'].append(imc)
    bot.send_message(message.chat.id, "Tu índice de masa corporal es {}".format(imc))
    actualizar_fichero()
    if imc < 16:
        bot.send_message(message.chat.id, "Infrapeso: Delgadez Severa")
    elif imc < 17:
        bot.send_message(message.chat.id, "Infrapeso: Delgadez moderada")
    elif imc < 18.5:
        bot.send_message(message.chat.id, "Infrapeso: Delgadez aceptable")
    elif imc < 25:
        bot.send_message(message.chat.id, "Peso Normal")
    elif imc < 30:
        bot.send_message(message.chat.id, "Sobrepeso")
    elif imc < 35:
        bot.send_message(message.chat.id, "Obeso: Tipo I")
    elif imc < 40:
        bot.send_message(message.chat.id, "Obeso: Tipo II")
    else:
        bot.send_message(message.chat.id, "Obeso: Tipo III")
    photo = open(AUX_DIR + 'indice.png', 'r')
    bot.send_photo(message.chat.id, photo)
    

@bot.message_handler(commands=['grafica'])
def grafica1(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Peso', 'Altura', 'IMC')
    bot.send_message(message.chat.id, "¿Que gráfica quieres crear?", reply_markup=markup)
    bot.register_next_step_handler(message, grafica2)

def grafica2(message):
    if message.text == 'Peso':
        if 'peso' not in users[str(message.chat.id)]:
            bot.send_message(message.chat.id, "No hay datos")
            return
        datos = users[str(message.chat.id)]['peso']
    elif message.text == 'Altura':
        if 'altura' not in users[str(message.chat.id)]:
            bot.send_message(message.chat.id, "No hay datos")
            return
        datos = users[str(message.chat.id)]['altura']
    elif message.text == 'IMC':
        if 'imc' not in users[str(message.chat.id)]:
            bot.send_message(message.chat.id, "No hay datos")
            return
        datos = users[str(message.chat.id)]['imc']
    else:
        bot.register_next_step_handler(message, grafica2)
        return
    
    x = range(1, len(datos)+1)
    x[0] = str(x[0])
    plt.plot(x ,datos)
    plt.savefig('img.png')
    plt.clf()
    photo = open('img.png', 'rb')
    bot.send_photo(message.chat.id, photo)

def actualizar_fichero():
    fw = open(USERS_FILE, "w")
    fw.write(json.dumps(users))
    fw.close()

@bot.message_handler(commands=['motivame'])
def motivame(message):
    lista = os.listdir(IMG_DIR)
    img = open(IMG_DIR + choice(lista), "rb")
    bot.send_photo(message.chat.id, img)

@bot.message_handler(commands=['nuevamarca'])
def marcas(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Press banca', 'Sentadilla', 'Peso muerto')
    bot.send_message(message.chat.id, "¿Que marca quieres registrar?", reply_markup=markup)
    bot.register_next_step_handler(message, marcas2)

def marcas2(message):
    if message.text == 'Press banca':
        nextmarca[str(message.chat.id)] = 'Press banca'
    elif message.text == 'Sentadilla':
        nextmarca[str(message.chat.id)] = 'Sentadilla'
    elif message.text == 'Peso muerto':
        nextmarca[str(message.chat.id)] = 'Peso muerto'
    else:
        bot.register_next_step_handler(message, marcas2)
        return
    bot.send_message(message.chat.id, "Introduce la marca en kg")
    bot.register_next_step_handler(message, marcas3)

def marcas3(message):
    if nextmarca[str(message.chat.id)] not in users[str(message.chat.id)]:
        users[str(message.chat.id)][nextmarca[str(message.chat.id)]] = []
    users[str(message.chat.id)][nextmarca[str(message.chat.id)]].append((strftime("%d/%m/%Y", gmtime()), int(message.text)))
    bot.send_message(message.chat.id, "Marca guardada")
    actualizar_fichero()

@bot.message_handler(commands=['mostrarmarcas'])
def mostrarmarcas(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Press banca', 'Sentadilla', 'Peso muerto')
    bot.send_message(message.chat.id, "¿Que marcas quieres mostrar?", reply_markup=markup)
    bot.register_next_step_handler(message, mostrarmarcas2)

def mostrarmarcas2(message):
    if message.text != 'Press banca' and message.text != 'Sentadilla' and message.text != 'Peso muerto':
        bot.register_next_step_handler(message, mostrarmarcas2)
        return
    if message.text not in users[str(message.chat.id)]:
        bot.send_message(message.chat.id, "No tienes marcas para {}".format(message.text))
        return
    cadena = ""
    for m in users[str(message.chat.id)][message.text]:
        cadena = cadena + "{} - {} kg\n".format(m[0], m[1])
    bot.send_message(message.chat.id, cadena)

@bot.message_handler(commands=['sorpresa'])
def sorpresa(message):
    im1 = open(AUX_DIR + "1.jpeg")
    im2 = open(AUX_DIR + "2.jpeg")
    bot.send_photo(message.chat.id, im1)
    bot.send_photo(message.chat.id, im2)

@bot.message_handler(commands=['dieta'])
def dieta(message):
    im = open(AUX_DIR + "dieta.jpeg")
    bot.send_photo(message.chat.id, im)

@bot.message_handler(commands=['creditos'])
def creditos(message):
    bot.reply_to(message, """\
Bot realizado para el Hackatón 2018 del Aula de Software Libre de la Universidad de Córdoba.
Cristian Ruz
Andrés Salinas
Álvaro Herrero
""")

@bot.message_handler(commands=['reset'])
def reset(message):
    users[str(message.chat.id)] = {}
    actualizar_fichero()
    bot.send_message(message.chat.id, "Se han reiniciado los datos")

bot.polling()