from bottle import route, template, request, redirect
import modeli

@route('/prijava')
def prijava_get():
    return template('prijava')  # To dodaš kasneje

@route('/prijava', method='POST')
def prijava_post():
    uporabnisko_ime = request.forms.get('uporabnisko_ime')
    uporabnik = modeli.prijava(uporabnisko_ime)
    if uporabnik:
        # Shrani sejo
        redirect(f'/izberi_dirkalisce/{uporabnisko_ime}')
    else:
        return "Uporabnik ne obstaja!"

@route('/izberi_dirkalisce/<uporabnisko_ime>')
def izberi_dirkalisce(uporabnisko_ime):
    dirkalisca = modeli.seznam_dirkalisca()
    return template('izberi_dirkalisce', uporabnisko_ime=uporabnisko_ime, dirkalisca=dirkalisca)