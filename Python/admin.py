from bottle import route, template, request, redirect
import modeli

@route('/admin')
def admin_index():
    dirke = modeli.seznam_dirk()
    return template('admin_index', dirke=dirke)

@route('/admin/dodaj_rezultat/<id_dirke>')
def dodaj_rezultat_get(id_dirke):
    uporabniki = modeli.seznam_uporabnikov()  # To dodaš v `modeli.py`
    return template('dodaj_rezultat', id_dirke=id_dirke, uporabniki=uporabniki)

@route('/admin/dodaj_rezultat/<id_dirke>', method='POST')
def dodaj_rezultat_post(id_dirke):
    uporabnisko_ime = request.forms.get('uporabnisko_ime')
    uvrstitev = int(request.forms.get('uvrstitev'))
    tocke = int(request.forms.get('tocke'))
    
    modeli.dodaj_rezultat(id_dirke, uporabnisko_ime, uvrstitev, tocke)
    redirect('/admin')