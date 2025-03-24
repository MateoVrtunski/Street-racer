from bottle import run, static_file
import uporabnik
import admin

@bottle.route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')

if __name__ == "__main__":
    run(host='0.0.0.0', port=8080, debug=True, reloader=True)