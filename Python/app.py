from bottle import Bottle, run, static_file, request, redirect, TEMPLATE_PATH, template
import os
from uporabnik import prijava_uporabnika, registracija_uporabnika, dobimo_avte, spremeni_avto, spremeni_geslo, pridobi_profil, prijavi_na_dirko
from dostop import ustvari_povezavo
from beaker.middleware import SessionMiddleware
from admin import poglej_championship, pridobi_rezultate_dirk, prijava_admina, prikazi_trenutno_dirko, pridobi_profil_admina, spremeni_geslo_admina

app = Bottle()

# Nastavimo pravilno pot do `views` mapo
TEMPLATE_PATH.insert(0, os.path.join(os.getcwd(), "HTML/views"))
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': True,
    'session.auto': True,
    'session.data_dir': './data'
}

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


@app.route('/login_admina', method='POST')
def login():
    session = request.environ['beaker.session']
    username = request.forms.get('username').strip()
    password = request.forms.get('password').strip()
    
    if prijava_admina(username, password):
        session['username'] = username  # Shrani uporabnika v sejo
        session.save()
        return redirect('/meni_admina.html')
    else:
        return '''
            <script>
                alert('Napačno uporabniško ime ali geslo!');
                window.location.href = '/login_admina.html';
            </script>
        '''

# 🔑 **Prijava uporabnika**
@app.route('/login_uporabnika', method='POST')
def login():
    session = request.environ['beaker.session']
    username = request.forms.get('username').strip()
    password = request.forms.get('password').strip()
    
    if prijava_uporabnika(username, password):
        session['username'] = username  # Shrani uporabnika v sejo
        session.save()
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
    session = request.environ['beaker.session']
    cars = dobimo_avte()
    username = request.forms.get("username")
    ime = request.forms.get("ime")
    priimek = request.forms.get("priimek")
    password = request.forms.get("password")
    avto_id = request.forms.get("avto")
    
    result = registracija_uporabnika(username, ime, priimek, password, avto_id)
    
    if result == 1:
        return '''
            <script>
                alert('Uporabniško ime že obstaja!');
                window.location.href = '/register_uporabnika.html';
            </script>
        '''
    elif result == 2:
        session['username'] = username  # Shrani uporabnika v sejo
        session.save()
        return '''
            <script>
                alert('Registracija uspešna!');
                window.location.href = '/meni_uporabnika.html';
            </script>
        '''
    else:
        return '''
            <script>
                alert('Napaka pri registraciji!');
                window.location.href = '/register_uporabnika.html';
            </script>
        '''
    
@app.route('/meni_uporabnika.html')
def meni_uporabnika():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')  # Privzeto 'Uporabnik', če ni shranjenega imena
    return template('meni_uporabnika', username=username)

@app.route('/meni_admina.html')
def meni_uporabnika():
    session = request.environ['beaker.session']
    username = session.get('username', 'Admin')  # Privzeto 'Uporabnik', če ni shranjenega imena
    return template('meni_admina', username=username)

@app.route('/championship.html')
def championship_page():
    championship_data = poglej_championship()  # Dobimo podatke
    return template('championship', championship=championship_data)

@app.route('/poglej_prijave.html')
def poglej_dirke():
    trenutne, koncane = prikazi_trenutno_dirko()  # Dobimo podatke
    return template('poglej_prijave', trenutne=trenutne, koncane = koncane)

@app.route('/rezultati_dirk.html')
def rezultati_dirk_page():
    dirka_podatki = pridobi_rezultate_dirk()  # Dobimo podatke iz baze
    return template('rezultati_dirk', dirke=dirka_podatki)

@app.route('/profil_uporabnika.html')
def profil_uporabnika():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')
    if not username:
        return redirect('/login_uporabnika.html')

    profil_podatki = pridobi_profil(username)
    avtomobili = dobimo_avte()

    return template('profil_uporabnika', profil=profil_podatki, avtomobili=avtomobili)


@app.route('/spremeni_geslo_uporabnika', method="POST")
def posodobi_geslo():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')

    novo_geslo = request.forms.get("novo_geslo")

    if spremeni_geslo(username, novo_geslo):
        return '''
            <script>
                alert("Geslo uspešno spremenjeno!");
                window.location.href = "/profil_uporabnika.html";
            </script>
        '''
    else:
        return '''
            <script>
                alert("Napaka pri spreminjanju gesla!");
                window.location.href = "/profil_uporabnika.html";
            </script>
        '''


@app.route('/spremeni_avto', method="POST")
def posodobi_avto():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')
    avto_id = request.forms.get("avto")

    if spremeni_avto(username, avto_id):
        return '''
            <script>
                alert("Avto uspešno spremenjen!");
                window.location.href = "/profil_uporabnika.html";
            </script>
        '''
    else:
        return '''
            <script>
                alert("Napaka pri spreminjanju avta!");
                window.location.href = "/profil_uporabnika.html";
            </script>
        '''


@app.route('/profil_admina.html')
def profil_uporabnika():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')
    if not username:
        return redirect('/login_admina.html')

    profil_podatki = pridobi_profil_admina(username)


    return template('profil_admina', profil=profil_podatki)


@app.route('/spremeni_geslo_admina', method="POST")
def posodobi_geslo():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')

    novo_geslo = request.forms.get("novo_geslo")

    if spremeni_geslo_admina(username, novo_geslo):
        return '''
            <script>
                alert("Geslo uspešno spremenjeno!");
                window.location.href = "/profil_admina.html";
            </script>
        '''
    else:
        return '''
            <script>
                alert("Napaka pri spreminjanju gesla!");
                window.location.href = "/profil_admina.html";
            </script>
        '''

@app.route('/prijava_na_dirko.html')
def prijava_dirka():

    trenutne, koncane = prikazi_trenutno_dirko()  # Dobimo podatke
    return template('prijava_na_dirko', trenutne=trenutne, koncane = koncane)

@app.route('/prijava_dirka', method="POST")
def obdelaj_prijavo_dirke():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')
    
    id_dirke = request.forms.get("id_dirke")

    rezultat = prijavi_na_dirko(username, id_dirke)

    return f'''
        <script>
            alert("{rezultat}");
            window.location.href = "/prijava_na_dirko.html";
        </script>
    '''

    
app = SessionMiddleware(app, session_opts)

# 🚀 **Zagon Bottle strežnika**
if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True, reloader=True)
