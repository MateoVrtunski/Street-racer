from bottle import Bottle, run, static_file, request, redirect, TEMPLATE_PATH, template, url
import os
from Python.uporabnik import prijava_uporabnika, registracija_uporabnika, dobimo_avte, spremeni_avto, spremeni_geslo, pridobi_profil, prijavi_na_dirko, moje_dirke, odjava_dirke, kdojekdo
from beaker.middleware import SessionMiddleware
from Python.admin import poglej_championship, pridobi_rezultate_dirk, prijava_admina, prikazi_trenutno_dirko, pridobi_profil_admina, spremeni_geslo_admina, dodaj_admina, mozne_dirke, doloci_rezultate, prijavljeni_na_dirko
from functools import wraps

app = Bottle()

SERVER_PORT = int(os.environ.get('BOTTLE_PORT', 8080))
RELOADER = os.environ.get('BOTTLE_RELOADER', True)

#to nam omogoča, da aplikacija opredeljuje posameznika
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': True,
    'session.auto': True,
    'session.data_dir': './data'
}
TEMPLATE_PATH.insert(0, os.path.join(os.getcwd(), "views"))

from bottle import request, redirect

def safe_redirect(path):
    """
    Return a correct redirect path depending on the environment (local or Binder/JupyterHub).
    """
    jupyter_prefix = request.environ.get('JUPYTERHUB_SERVICE_PREFIX')

    if jupyter_prefix:
        return redirect(f"{jupyter_prefix}proxy/8080/{path}")
    else:
        return redirect(f"{path}")
    
@app.route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root="views/static")

@app.route('/<filename>.html')
def serve_template(filename):
    return template(filename, error=None, success=None)

# glavna stran
@app.route('/')
def index():
    jupyter_prefix = request.environ.get('JUPYTERHUB_SERVICE_PREFIX')

    if jupyter_prefix:
        return template('index')
    else:
        return template('index2')

# prijava admina
@app.route('/login_admina', method='POST')
def logina():
    session = request.environ['beaker.session']
    username = request.forms.get('username').strip()
    password = request.forms.get('password').strip()
    
    if prijava_admina(username, password):
        session['username'] = username  
        session.save()
        return safe_redirect('meni_admina.html')
    else:
        return '''
            <script>
                alert('Napačno uporabniško ime ali geslo!');
                window.location.href = 'login_admina.html';
            </script>
        '''
# prijava uporabnika
@app.route('/login_uporabnika', method='POST')
def loginu():
    session = request.environ['beaker.session']
    username = request.forms.get('username').strip()
    password = request.forms.get('password').strip()
    
    if prijava_uporabnika(username, password):
        session['username'] = username  
        session.save()
        return safe_redirect("meni_uporabnika.html")
    else:
        return '''
            <script>
                alert('Napačno uporabniško ime ali geslo!');
                window.location.href = 'login_uporabnika.html';
            </script>
        '''

# registracija uporabnika 
@app.route('/register_uporabnika.html')
def register_page():
    cars = dobimo_avte()  
    return template('register_uporabnika', cars=cars, error=None, success=None)

@app.route('/register_uporabnika', method="POST")
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
                window.location.href = 'register_uporabnika.html';
            </script>
        '''
    elif result == 2:
        session['username'] = username  # Shrani uporabnika v sejo
        session.save()
        return '''
            <script>
                alert('Registracija uspešna!');
                window.location.href = 'meni_uporabnika.html';
            </script>
        '''
    else:
        return '''
            <script>
                alert('Napaka pri registraciji!');
                window.location.href = 'register_uporabnika.html';
            </script>
        '''
    
@app.route('/meni_uporabnika.html')
def meni_uporabnika():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')  # Privzeto 'Uporabnik', če ni shranjenega imena
    return template('meni_uporabnika', username=username)

@app.route('/meni_admina.html')
def meni_admina():
    session = request.environ['beaker.session']
    username = session.get('username', 'Admin')  # Privzeto 'Uporabnik', če ni shranjenega imena
    return template('meni_admina', username=username)

@app.route('/championship.html')
def championship_page():
    session = request.environ['beaker.session']
    username = session.get('username')
    back_link = kdojekdo(username)
    championship_data = poglej_championship()  # Dobimo podatke
    return template('championship', championship=championship_data, back_link=back_link)

@app.route('/poglej_prijave.html')
def poglej_dirke():
    session = request.environ['beaker.session']
    username = session.get('username')
    back_link = kdojekdo(username)
    trenutne, koncane = prikazi_trenutno_dirko()  # Dobimo podatke
    return template('poglej_prijave', trenutne=trenutne, koncane = koncane, back_link=back_link)

@app.route('/rezultati_dirk.html')
def rezultati_dirk_page():
    session = request.environ['beaker.session']
    username = session.get('username')
    back_link = kdojekdo(username)
    dirka_podatki = pridobi_rezultate_dirk()  # Dobimo podatke iz baze
    return template('rezultati_dirk', dirke=dirka_podatki, back_link=back_link)

@app.route('/profil_uporabnika.html')
def profil_uporabnika():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')
    if not username:
        return safe_redirect("login_uporabnika.html")

    profil_podatki = pridobi_profil(username)
    avtomobili = dobimo_avte()
    moje = moje_dirke(username)

    return template('profil_uporabnika', profil=profil_podatki, avtomobili=avtomobili, moje = moje)


@app.route('/spremeni_geslo_uporabnika', method="POST")
def posodobi_geslou():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')

    novo_geslo = request.forms.get("novo_geslo")

    if spremeni_geslo(username, novo_geslo):
        return '''
            <script>
                alert("Geslo uspešno spremenjeno!");
                window.location.href = "profil_uporabnika.html";
            </script>
        '''
    else:
        return '''
            <script>
                alert("Napaka pri spreminjanju gesla!");
                window.location.href = "profil_uporabnika.html";
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
                window.location.href = "profil_uporabnika.html";
            </script>
        '''
    else:
        return '''
            <script>
                alert("Napaka pri spreminjanju avta!");
                window.location.href = "profil_uporabnika.html";
            </script>
        '''


@app.route('/profil_admina.html')
def profil_adminaa():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')
    if not username:
        return safe_redirect('login_admina.html')

    profil_podatki = pridobi_profil_admina(username)


    return template('profil_admina', profil=profil_podatki)


@app.route('/spremeni_geslo_admina', method="POST")
def posodobi_gesloa():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')

    novo_geslo = request.forms.get("novo_geslo")

    if spremeni_geslo_admina(username, novo_geslo):
        return '''
            <script>
                alert("Geslo uspešno spremenjeno!");
                window.location.href = "profil_admina.html";
            </script>
        '''
    else:
        return '''
            <script>
                alert("Napaka pri spreminjanju gesla!");
                window.location.href = "profil_admina.html";
            </script>
        '''

@app.route('/prijava_na_dirko.html')
def prijava_dirka():
    trenutne, koncane = prikazi_trenutno_dirko() 
    return template('prijava_na_dirko', trenutne=trenutne, koncane = koncane)

@app.route('/prijava_na_dirko', method="POST")
def obdelaj_prijavo_dirke():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')
    
    id_dirke = request.forms.get("id_dirke")

    rezultat = prijavi_na_dirko(username, id_dirke)

    return f'''
        <script>
            alert("{rezultat}");
            window.location.href = "prijava_na_dirko.html";
        </script>
    '''

@app.route('/odjava_na_dirko.html')
def odjava_dirka():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')
    moje = moje_dirke(username) 
    return template('odjava_na_dirko', moje = moje)

@app.route('/odjava_dirka', method="POST")
def obdelaj_odjavo_dirke():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')
    
    id_dirke = request.forms.get("id_dirke")

    rezultat = odjava_dirke(username, id_dirke)

    return f'''
        <script>
            alert("{rezultat}");
            window.location.href = "odjava_na_dirko.html";
        </script>
    '''

@app.route('/dodaj_admina', method="POST")
def dodaj():
    session = request.environ['beaker.session']
    username = session.get('username', 'Uporabnik')
    
    admin = request.forms.get("username")

    rezultat = dodaj_admina(admin)

    return f'''
        <script>
            alert("{rezultat}");
            window.location.href = "dodaj_admina.html";
        </script>
    '''

@app.route('/doloci_rezultate.html')
def doloci():
    dirke = mozne_dirke()  
    return template('doloci_rezultate', dirke=dirke)

@app.route('/izberi_dirko', method="POST")
def izberi():
    session = request.environ['beaker.session']
    dirka = request.forms.get("dirka")

    session['dirka'] = dirka 
    session.save()

    return safe_redirect("shrani_rezultate.html")

@app.route('/shrani_rezultate.html')
def prijava_dirka():
    session = request.environ['beaker.session']
    dirke = session.get('dirka')  
    id_dirke = dirke[0]
    prijavljeni = prijavljeni_na_dirko(id_dirke)

    return template('shrani_rezultate', dirke=dirke, prijavljeni = prijavljeni)

@app.route('/shrani_rezultate', method="POST")
def shrani_rezultate():
    session = request.environ['beaker.session']
    dirke = session.get('dirka')
    id_dirke = dirke[0]

    rezultat_seznam = request.forms.getall("rezultat[]") 

    rezultat = doloci_rezultate(id_dirke, rezultat_seznam)
    
    return f'''
        <script>
            alert("{rezultat}");
            window.location.href = "meni_admina.html";
        </script>
    '''
    

app = SessionMiddleware(app, session_opts)


run(app, host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)
