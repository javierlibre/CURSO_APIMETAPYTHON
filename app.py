from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# modelo de la tabla log
class Log(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
  texto = db.Column(db.TEXT)

#crear la tabla si no existe
with app.app_context():
  db.create_all()

#función para ordenar los mensajes por fecha y hora
def ordenar_por_fecha_y_hora(registros):
  return sorted(registros, key=lambda x: x.fecha_y_hora, reverse=True)

@app.route('/')
def index():
  # Obtener los registros de la base de datos
  registros = Log.query.all()
  registros_ordenados = ordenar_por_fecha_y_hora(registros)
  return render_template('index.html', registros=registros_ordenados)

mensajes_log = []

#función para agregar mensajes y guardarlos en la base de datos
def agregar_mensajes_log(texto):
  if isinstance(texto, dict):
    texto = json.dumps(texto)
  mensajes_log.append(texto)

  #guardar el mensaje en la base de datos
  nuevo_registro = Log(texto=texto)
  db.session.add(nuevo_registro)
  db.session.commit()


#Token de verificación para la configuración del webhook
TOKEN_ANDERCODE = 'ANDERCODE'

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
  if request.method == 'GET':
    challenge = verificar_token(request)
    return challenge
  elif request.method == 'POST':
    response = recibir_mensajes(request)
    return response
  
def verificar_token(req):
  token = req.args.get('hub.verify_token')
  challenge = req.args.get('hub.challenge')
  if challenge and token == TOKEN_ANDERCODE:
    return challenge
  else:
    return jsonify({'error': 'Token de verificación incorrecto'}), 401
  

def recibir_mensajes(req):
   try:
        req = request.get_json()
        entry =req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']

        if objeto_mensaje:
          messages = objeto_mensaje[0]
          if "type" in messages:
            tipo = messages["type"]

            if tipo == "interactive":
              return 0
            
            if "text" in messages:
              text = messages["text"]["body"]
              numero = messages["from"]

              enviar_mensajes_whatsapp(text, numero)

        return jsonify({'message': 'EVENT_RECEIVED'})
   
   except Exception as e:
        return jsonify({'message': 'EVENT_RECEIVED'})
   
def enviar_mensajes_whatsapp(texto, number):
  texto = texto.lower()
  w_token = "EAAtwn97dOL0BQkgC9bkbdbqiQV7tj1B7iaeZBpaJyPvFHdvjXl8Ol6GIzmmeJ9TZBZBeUvn2yIXHWpPK40rk4JXqWcsYjmPC4GpZA9jWIKWgYo6NZA7BCZBlyLKENOj76EFIwgEPuGqk2ottZAEks5sbFdCzmIVOE9ZAtiSyPTKasCpmn3rqxsjsbaZCBQElV1ZBAd7ZCOpZC901gqpqPmSPtvn6K4cQaark5yINRNOU2qyFZBPkwPl1B4dNlYpzvUl8ifDLv1lnT1pNjiRJ88OfaKHRdowZDZD"

  if "hola" in texto:
    data = {
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": number,
      "type": "text",
      "text" : {
        "preview_url": False,
        "body": "🚀 Hola, ¿Cómo estás? Bienvenido."
      }
    }

  elif "1" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
            }
        }
  elif "2" in texto:
      data = {
          "messaging_product": "whatsapp",
          "to": number,
          "type": "location",
          "location": {
              "latitude": "-12.067158831865067",
              "longitude": "-77.03377940839486",
              "name": "Estadio Nacional del Perú",
              "address": "Cercado de Lima"
          }
      }
  elif "3" in texto:
      data={
          "messaging_product": "whatsapp",
          "recipient_type": "individual",
          "to": number,
          "type": "document",
          "document": {
                  "link": "https://www.turnerlibros.com/wp-content/uploads/2021/02/ejemplo.pdf",
                  "caption": "Temario del Curso #001"
              }
          }
  elif "4" in texto:
      data={
          "messaging_product": "whatsapp",
          "recipient_type": "individual",
          "to": number,
          "type": "audio",
          "audio": {
              "link": "https://filesamples.com/samples/audio/mp3/sample1.mp3"
          }
      }
  elif "5" in texto:
      data = {
          "messaging_product": "whatsapp",
          "to": number,
          "text": {
              "preview_url": True,
              "body": "Introduccion al curso! https://youtu.be/6ULOE2tGlBM"
          }
      }
  elif "6" in texto:
      data = {
          "messaging_product": "whatsapp",
          "recipient_type": "individual",
          "to": number,
          "type": "text",
          "text": {
              "preview_url": False,
              "body": "🤝 En breve me pondre en contacto contigo. 🤓"
          }
      }
  elif "7" in texto:
      data = {
          "messaging_product": "whatsapp",
          "recipient_type": "individual",
          "to": number,
          "type": "text",
          "text": {
              "preview_url": False,
              "body": "📅 Horario de Atención : Lunes a Viernes. \n🕜 Horario : 9:00 am a 5:00 pm 🤓"
          }
      }
  elif "0" in texto:
      data = {
          "messaging_product": "whatsapp",
          "recipient_type": "individual",
          "to": number,
          "type": "text",
          "text": {
              "preview_url": False,
              "body": "🚀 Hola, visita mi web anderson-bastidas.com para más información.\n \n📌Por favor, ingresa un número #️⃣ para recibir información.\n \n1️⃣. Información del Curso. ❔\n2️⃣. Ubicación del local. 📍\n3️⃣. Enviar temario en PDF. 📄\n4️⃣. Audio explicando curso. 🎧\n5️⃣. Video de Introducción. ⏯️\n6️⃣. Hablar con AnderCode. 🙋‍♂️\n7️⃣. Horario de Atención. 🕜 \n0️⃣. Regresar al Menú. 🕜"
          }
      }
  else:
    data = {
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": number,
      "type": "text",
      "text" : {
        "preview_url": False,
        "body": "🚀 Hola, visita mi web anderson-bastidas.com para más información.\n \n📌Por favor, ingresa un número #️⃣ para recibir información.\n \n1️⃣. Información del Curso. ❔\n2️⃣. Ubicación del local. 📍\n3️⃣. Enviar temario en PDF. 📄\n4️⃣. Audio explicando curso. 🎧\n5️⃣. Video de Introducción. ⏯️\n6️⃣. Hablar con AnderCode. 🙋‍♂️\n7️⃣. Horario de Atención. 🕜 \n0️⃣. Regresar al Menú. 🕜"
      }
    }

  data = json.dumps(data)

  headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + w_token
  }

  connection = http.client.HTTPSConnection("graph.facebook.com")
  try:
    connection.request("POST", "/v22.0/979289148595438/messages", data, headers)
    response = connection.getresponse()
    print(response.status, response.reason)
  except Exception as e:
    agregar_mensajes_log(json.dumps(e))

  finally:
    connection.close()


if __name__ == '__main__':
  #app.run(debug=True)
  app.run(host='0.0.0.0', port=80, debug=True)