from flask import Flask, url_for, session, flash, render_template, request, send_file, redirect
from functools import wraps
from Data import data, domains_reader, Utils
from os.path import exists
app = Flask(__name__)
app.secret_key = 'Datsent'
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('login'))
    return wrap
@app.route('/')
def check_sours():
    if exists(Utils.DB_FILE):
        return redirect(url_for('data_web'))
    else:
        return redirect(url_for('signup'))
@app.route('/data')
@login_required
def data_web():
    file = data.load_db_into_list()
    return render_template('index.html', SCORES=file)


@app.route('/data', methods=['POST'])
@login_required
def data_web_post():
    new_domain = request.form.get('shortcode')
    data.add_new_domain(new_domain)
    file = data.load_db_into_list()
    return render_template('index.html', SCORES=file)


@app.route('/refresh')

def refreshed():
    domains_reader.main()
    # file = data.load_db_into_list()
    return redirect(url_for('data_web'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['name'] != data.load_user_into_list()[0][0] or request.form['password'] != data.load_user_into_list()[0][1]:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            return redirect(url_for('data_web'))
    return render_template('login.html')
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        data.add_user([request.form.get('name'), request.form.get('password')])
        return redirect(url_for('data_web'))

    return render_template('signup.html')



'''@app.route('/signup', methods=['POST'])
def signup_post():
    data.add_user([request.form.get('name'), request.form.get('password')])
    return redirect('login')'''



@app.route('/download')
def download_file():
    path = "domains.csv"

    return send_file(path, as_attachment=True)




if __name__ == '__main__':
    app.run('0.0.0.0',port=5000, debug=True)