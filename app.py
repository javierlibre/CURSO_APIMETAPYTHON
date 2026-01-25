from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

  prueba1 = Log(texto="Prueba 1")
  db.session.add(prueba1)
  db.session.commit()

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
def agregar_mensaje_log(texto):
  mensajes_log.append(texto)

  #guardar el mensaje en la base de datos
  nuevo_registro = Log(texto=texto)
  db.session.add(nuevo_registro)
  db.session.commit()

if __name__ == '__main__':
  #app.run(debug=True)
  app.run(host='0.0.0.0', port=80, debug=True)