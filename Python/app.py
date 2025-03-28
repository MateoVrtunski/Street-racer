from bottle import Bottle, run, static_file, request, redirect, template
import os
from uporabnik import prijava_uporabnika, registracija_uporabnika, dobimo_avte
from dostop import ustvari_povezavo

app = Bottle()

# Get the absolute path to the HTML directory
current_dir = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.abspath(os.path.join(current_dir, '..', 'HTML'))

# Serve static files
@app.route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root=HTML_DIR)

# Main routes
@app.route('/')
def index():
    return static_file('index.html', root=HTML_DIR)

# Serve HTML files
@app.route('/<filename:re:.*\\.html>')
def serve_html(filename):
    return static_file(filename, root=HTML_DIR)

# User login route
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

# User registration rout
@app.route('/register', method='POST')
def register_page():
    cars = dobimo_avte()  # Use the function from uporabnik.py
    return cars
def register():
    # Get all form data
    username = request.forms.get('username')
    password = request.forms.get('password')
    ime = request.forms.get('ime')
    priimek = request.forms.get('priimek')
    avto_id = request.forms.get('avto')
    
    # Process registration
    conn, cur = ustvari_povezavo()
    try:
        success = registracija_uporabnika(cur, conn, username, ime, priimek, password, avto_id)
        if success:
            return '''
                <script>
                    alert('Registracija uspešna!');
                    window.location.href = '/login_uporabnika.html';
                </script>
            '''
        else:
            return '''
                <script>
                    alert('Registracija ni uspela!');
                    window.location.href = '/register_uporabnika.html';
                </script>
            '''
    finally:
        cur.close()
        conn.close()


    
# Run the app
if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True, reloader=True)