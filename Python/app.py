from bottle import Bottle, run, static_file, request, redirect, TEMPLATE_PATH, template
import os
from uporabnik import prijava_uporabnika, registracija_uporabnika, dobimo_avte
from dostop import ustvari_povezavo

app = Bottle()

# Nastavimo pravilno pot do `views` mapo
TEMPLATE_PATH.insert(0, os.path.join(os.getcwd(), "HTML/views"))

# Serve static files (CSS, JS, images)
@app.route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root="HTML/views/static")

# 🔥 **Pravilno serviranje HTML datotek z `template()`**
@app.route('/<filename>.html')
def serve_template(filename):
    return template(filename, error=None, success=None)

# 🏠 **Glavna stran**
@app.route('/')
def index():
    return template('index')

# 🔑 **Prijava uporabnika**
@app.route('/login', method='POST')
def login():
    username = request.forms.get('username').strip()
    password = request.forms.get('password').strip()
    
    if prijava_uporabnika(username, password):
        return redirect('/meni_uporabnika.html')
    else:
        return '''
            <script>
                alert('Napačno uporabniško ime ali geslo!');
                window.location.href = '/login_uporabnika.html';
            </script>
        '''
@app.route('/register_uporabnika.html')
def register_page():
    cars = dobimo_avte()  # Get cars from database
    return template('register_uporabnika', cars=cars, error=None, success=None)

# ✅ **Obdelava registracije**
@app.route('/register', method="POST")
def process_register():
    cars = dobimo_avte()
    username = request.forms.get("username")
    ime = request.forms.get("ime")
    priimek = request.forms.get("priimek")
    password = request.forms.get("password")
    avto_id = request.forms.get("avto")
    
    success = registracija_uporabnika(username, ime, priimek, password, avto_id)
    
    if success:
        return template("register_uporabnika", cars=cars, success="Registracija uspešna!", error=None)
    else:
        return template("register_uporabnika", cars=cars, error="Napaka pri registraciji!", success=None)


# 🚀 **Zagon Bottle strežnika**
if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True, reloader=True)
