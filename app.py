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

            #agregar el mensaje a la base de datos
            agregar_mensajes_log(json.dumps(messages))

            if tipo == "interactive":
                    tipo_interactivo = messages["interactive"]["type"]

                    if tipo_interactivo == "button_reply":
                        text = messages["interactive"]["button_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)
                    
                    elif tipo_interactivo == "list_reply":
                        text = messages["interactive"]["list_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)
            
            if "text" in messages:
              text = messages["text"]["body"]
              numero = messages["from"]

              enviar_mensajes_whatsapp(text, numero)

              #agregar el texto del mensaje a la base de datos

              agregar_mensajes_log(json.dumps(text))

        return jsonify({'message': 'EVENT_RECEIVED'})
   
   except Exception as e:
        return jsonify({'message': 'EVENT_RECEIVED'})
   
def enviar_mensajes_whatsapp(texto, number):
  texto = texto.lower()
  w_token = "EAAtwn97dOL0BQzqXSmjNzpkUWfp09FD3wTtrA3H58z4gRke4S36me3cQ804eiZCHlnHclvWD5ixG1EvZAxv1ZBFcCZAcLLZAByIhJ6uZApgkGwu9Jex9XyWXrkHqmmfBZAaRUPVV68ql6djDiaI8i8Ju1SJXHADlJZAT7BqW4ZCgGNuf23PODoIDGxKD8ajThjNLWpoLMzHRuyiC7UjTQg9liRKmgHsKgZABgZCZAiX6zfOZB4HEPgFiUTOxAZC3QZAtxzRkZB7oBLGnyHcgzY74qd34H6Mk3qkZD"

  if "gulupa" in texto:
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
      #41.32064229530019, -72.85969102024134 coordenadas academy
      data = {
          "messaging_product": "whatsapp",
          "to": number,
          "type": "location",
          "location": {
              "latitude": "41.32064229530019",
              "longitude": "-72.85969102024134",
              "name": "Academy Dsigns",
              "address": "836 Foxon Rd, East Haven, CT 06513, United States"
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
  elif "boton" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type":"button",
                "body": {
                    "text": "¿Confirmas tu registro?"
                },
                "footer": {
                    "text": "Selecciona una de las opciones"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply":{
                                "id":"btnsi",
                                "title":"Si"
                            }
                        },{
                            "type": "reply",
                            "reply":{
                                "id":"btnno",
                                "title":"No"
                            }
                        },{
                            "type": "reply",
                            "reply":{
                                "id":"btntalvez",
                                "title":"Tal Vez"
                            }
                        }
                    ]
                }
            }
        }
  elif "btnenglish" in texto:
        data ={
            "messaging_product": "whatsapp",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type" : "list",
                "body": {
                    "text": "Welcome to Academy Dsigns, visit our Web academyd-signs.com for more information"
                },
                "footer": {
                    "text": "Select an option to help you"
                },
                "action":{
                    "button":"Options",
                    "sections":[
                        {
                            "title":"Our Services",
                            "rows":[
                                {
                                    "id":"btnsigns_eng",
                                    "title" : "Signs and Signages",
                                    "description": "We offer a variety of signs and signages for your business."
                                },
                                {
                                    "id":"btnwrap_eng",
                                    "title" : "Vehicle Wraps",
                                    "description": "We offer a variety of vehicle wraps for your business."
                                },
                                {
                                    "id":"btnfoodtruck_eng",
                                    "title" : "Food Truck",
                                    "description": "We offer a variety of food truck build-outs and wraps."
                                }
                            ]
                        },{
                            "title":"Contact Us",
                            "rows":[
                                {
                                    "id":"btnaddress_eng",
                                    "title" : "Address",
                                    "description": "You can visit our local."
                                },
                                {
                                    "id":"btnelse_eng",
                                    "title" : "Other",
                                    "description": "Ask a human"
                                }
                            ]
                        }
                    ]
                }
            }
        }
  elif "btnspanish" in texto:
        data ={
            "messaging_product": "whatsapp",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type" : "list",
                "body": {
                    "text": "Bienvenido a Academy Dsigns, visita nuestra página academyd-signs.com para más información"
                },
                "footer": {
                    "text": "Selecciona una opción para ayudarte"
                },
                "action":{
                    "button":"Opciones",
                    "sections":[
                        {
                            "title":"Nuestros Servicios",
                            "rows":[
                                {
                                    "id":"btnsigns_spa",
                                    "title" : "Signs and Signages",
                                    "description": "We offer a variety of signs and signages for your business."
                                },
                                {
                                    "id":"btnwrap_eng",
                                    "title" : "Vehicle Wraps",
                                    "description": "We offer a variety of vehicle wraps for your business."
                                },
                                {
                                    "id":"btnfoodtruck_eng",
                                    "title" : "Food Truck",
                                    "description": "We offer a variety of food truck build-outs and wraps."
                                }
                            ]
                        },{
                            "title":"Contact Us",
                            "rows":[
                                {
                                    "id":"btnaddress_eng",
                                    "title" : "Address",
                                    "description": "You can visit our local."
                                },
                                {
                                    "id":"btnelse_eng",
                                    "title" : "Other",
                                    "description": "Ask a human"
                                }
                            ]
                        }
                    ]
                }
            }
        }
  elif "lista" in texto:
        data ={
            "messaging_product": "whatsapp",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type" : "list",
                "body": {
                    "text": "Selecciona Alguna Opción"
                },
                "footer": {
                    "text": "Selecciona una de las opciones para poder ayudarte"
                },
                "action":{
                    "button":"Ver Opciones",
                    "sections":[
                        {
                            "title":"Compra y Venta",
                            "rows":[
                                {
                                    "id":"btncompra",
                                    "title" : "Comprar",
                                    "description": "Compra los mejores articulos de tecnologia"
                                },
                                {
                                    "id":"btnvender",
                                    "title" : "Vender",
                                    "description": "Vende lo que ya no estes usando"
                                }
                            ]
                        },{
                            "title":"Distribución y Entrega",
                            "rows":[
                                {
                                    "id":"btndireccion",
                                    "title" : "Local",
                                    "description": "Puedes visitar nuestro local."
                                },
                                {
                                    "id":"btnentrega",
                                    "title" : "Entrega",
                                    "description": "La entrega se realiza todos los dias."
                                }
                            ]
                        }
                    ]
                }
            }
        }  
  elif "btnsigns_eng" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Your business deserves to stand out. Let our expert sign services create eye-catching signage that grabs attention and drives results. Tell us about your project and we'll bring your vision to life."
            }
        } 
  elif "btnsigns_spa" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Tu negocio merece destacar. Deja que nuestros expertos en señalización creen letreros llamativos que atraigan la atención e impulsen resultados. Cuéntanos sobre tu proyecto y le daremos vida a tu visión."
            }
        } 
  elif "btnwrap_eng" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Transform your vehicle into a moving billboard with our premium wrapping services. From bold colors to custom designs, we deliver stunning wraps that protect your paint and make a statement. Let's create something unforgettable. Tell us about your project and we'll bring your vision to life."
            }
        }
  elif "btnwrap_spa" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Transforma tu vehículo en una valla publicitaria móvil con nuestros servicios de wrapping premium. Desde colores vibrantes hasta diseños personalizados, ofrecemos wraps impresionantes que protegen tu pintura y marcan la diferencia. Creemos algo inolvidable. Cuéntanos sobre tu proyecto y le daremos vida a tu visión."
            }
        } 
  elif "btnfoodtruck_eng" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "For over 7 years, we have been setting the standard in custom food truck builds and commercial kitchen installations. We don't just build trucks; we launch businesses. Tell us about your project and we'll bring your vision to life."
            }
        }
  elif "btnfoodtruck_spa" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Por más de 7 años, hemos establecido el estándar en la construcción de food trucks personalizados e instalaciones de cocinas comerciales. No solo construimos camiones; lanzamos negocios. Cuéntanos sobre tu proyecto y le daremos vida a tu visión."
            }
        } 
  elif "btnaddress_eng" in texto:
        data = {
          "messaging_product": "whatsapp",
          "to": number,
          "type": "location",
          "location": {
              "latitude": "41.32064229530019",
              "longitude": "-72.85969102024134",
              "name": "Academy Dsigns",
              "address": "836 Foxon Rd, East Haven, CT 06513, United States"
          }
      } 
  elif "btnaddress_spa" in texto:
        data = {
          "messaging_product": "whatsapp",
          "to": number,
          "type": "location",
          "location": {
              "latitude": "41.32064229530019",
              "longitude": "-72.85969102024134",
              "name": "Academy Dsigns",
              "address": "836 Foxon Rd, East Haven, CT 06513, United States"
          }
      } 
  elif "btnelse_eng" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Hello, thank you for contacting Academy Dsigns. A human agent will contact you as soon as possible."
            }
        } 
  elif "btnelse_spa" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Hola, gracias por contactar a Academy Dsigns. ¿En qué puedo ayudarte?"
            }
        } 
  else:
        data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "interactive",
                "interactive":{
                    "type":"button",
                    "body": {
                        "text": "Academy Dsigns"
                    },
                    "footer": {
                        "text": "Language / Idioma"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply":{
                                    "id":"btnenglish",
                                    "title":"English"
                                }
                            },{
                                "type": "reply",
                                "reply":{
                                    "id":"btnspanish",
                                    "title":"Español"
                                }
                            }
                        ]
                    }
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