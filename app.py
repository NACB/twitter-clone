########################################
# flask/db setup
########################################

from flask import Flask, render_template, request, make_response
from werkzeug.utils import redirect
app = Flask(__name__)

# sqlite3 is built in python3, no need to pip3 install
import sqlite3

# process command line arguments
import argparse
parser = argparse.ArgumentParser(description='Create a database for the twitter project')
parser.add_argument('--db_file', default='twitter_clone.db')
args, _ = parser.parse_known_args()

# markdown and sanitizing stuff
import bleach
import markdown_compiler

########################################
# helper functions
########################################

def print_debug_info():
    '''
    Print information stored in GET/POST/Cookie variables to the terminal.
    '''
    # request is different from request*s*

    # these variables are set by the information after the ? in the URL;
    # args = arguments; the information after the ? is called the query arguments;
    # these variables are just for 1 webpage
    print("request.args.get('username')=",request.args.get('username'))
    print("request.args.get('password')=",request.args.get('password'))

    # this information comes from a POST form,
    # the methods for the route must include 'POST';
    # these variables are just for 1 webpage
    print("request.form.get('username')=",request.form.get('username'))
    print("request.form.get('password')=",request.form.get('password'))

    # these variables pass between different webpages;
    # these are "persistent"; the other variables are "effemeral"
    print("request.cookies.get('username')=",request.cookies.get('username'))
    print("request.cookies.get('password')=",request.cookies.get('password'))


def is_valid_login(con, username, password):
    '''
    Return True if the given username/password is a valid login;
    otherwise return False.
    '''


    sql = """
    SELECT username,password
    FROM users
    WHERE username=?  
      AND password=?;
    """
    # ? means we don't know the value, but it'll come later
    cur = con.cursor()
    parameters = [username, password]
    cur.execute(sql, parameters) # this is where we specify what the ? are equal to
    rows = cur.fetchall()
    
    # if the total number of rows returned is 0,
    # then no username/password combo was not found
    if len(list(rows))==0:
        return False

    # if the total number of rows returned is > 0,
    # then the username/password combo was found
    else:
        return True

def is_available_username(con, username):
    sql = """
    SELECT username
    FROM users
    WHERE username=?;
    """
    cur = con.cursor()
    parameters = [username]
    cur.execute(sql, parameters)
    rows = cur.fetchall()
    if len(list(rows))==0:
        return True
    else:
        return False

def add_user(con, username, password):
    sql = """
    INSERT INTO users (username, password) values (?, ?);
    """
    cur = con.cursor()
    paramaters = [username, password]
    cur.execute(sql, paramaters)
    con.commit()

def get_id(con, username):
    sql = """
    SELECT id FROM users WHERE username = ?;
    """
    cur = con.cursor()
    cur.execute(sql, [username])
    return str(cur.fetchall()[0][0])
    #return str(rows[0])

def add_post(con, user_id, message_contents):
    #bleaching
    message_contents_clean = bleach.clean(message_contents)
    message_contents_complete = bleach.linkify(message_contents_clean)
    sql = """
    INSERT INTO messages (sender_id, message) values (?,?);
    """
    message_contents_final = markdown_compiler.convert_file(message_contents_complete, add_css=False)
    cur = con.cursor()
    #paramaters = [user_id, message_contents]
    cur.execute(sql, (user_id, message_contents_final))
    con.commit()


def changepassword(con, form_password_n, userid):

    print ('user=', userid)
    sql="""
    UPDATE users SET password=? WHERE id=?;
    """
    cur = con.cursor()
    paramaters = [form_password_n, userid]
    cur.execute(sql, paramaters)
    con.commit()

def delete_user(con, user_id):
    sql="""
    DELETE FROM users WHERE id=?
    """
    cur = con.cursor()
    cur.execute(sql, [user_id])
    con.commit()

def delete_messages(con, user_id):
    sql="""
    DELETE FROM messages WHERE sender_id=?
    """
    cur = con.cursor()
    cur.execute(sql, [user_id])
    con.commit()

########################################
# custom routes
########################################

@app.route('/')     
def root():
    con = sqlite3.connect(args.db_file)
    print_debug_info()

    # modify the behavior of this route depending on whether the user is logged in

    username = request.cookies.get('username')
    password = request.cookies.get('password')
    is_logged_in = is_valid_login(con, username, password)
    redirected = request.cookies.get('created')
    messages = []

    cur_messages = con.cursor()
    cur_messages.execute('select sender_id, message, created_at from messages order by created_at DESC')
    for message_row in cur_messages.fetchall():
        cur_users = con.cursor()
        cur_users.execute('select username, age from users where id=' +str(message_row[0])+';')
        for user_row in cur_users.fetchall():
            pass

        messages.append({
            'message' : message_row[1],
            'created_at' : message_row[2],
            'username' : user_row[0],
            'sender_id' : message_row[0]
        })

    
    return render_template('root.html', is_logged_in=is_logged_in, messages=messages, successful_create=redirected)


@app.route('/login', methods=['GET','POST'])
def login():
    con = sqlite3.connect(args.db_file)
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    is_logged_in = is_valid_login(con, username, password)
    print_debug_info()

    # the basic idea:
    # we will get the information from the POST request;
    # if it's correct, set some cookies;
    # we can always check using cookies to determine whether someone is logged in or not
    form_username = request.form.get('username')
    form_password = request.form.get('password')
    print('form_username=', form_username)
    print('form_password=', form_password)

    if form_username is not None:
        if form_username != '':
            has_clicked_form = True
        else:
            has_clicked_form = False
    else: 
        has_clicked_form = False
    #has_clicked_form = form_username is not '' or None
    print('has_clicked_form=', has_clicked_form)

    if has_clicked_form:
        login_info_correct = is_valid_login(con, form_username, form_password)
        if login_info_correct:
            # if someone has clicked on the form;
            # and the form information is correct;
            # then we should set the cookies
            response = make_response(render_template('login.html', successful_login=True, is_logged_in=True))
            response.set_cookie('username', form_username)
            response.set_cookie('password', form_password)
            return response

        else:
            # if someone has clicked on the form;
            # and the form information is wrong;
            # then we should display an error
            return render_template('login.html', display_error=True, is_logged_in=is_logged_in)

    else:
        # if someone has not clicked on the form;
        # do nothing special
        return render_template('login.html', is_logged_in=is_logged_in)
    

@app.route('/logout')     
def logout():
    print_debug_info()
    #return render_template('logout.html')
    response = make_response(render_template('logout.html'))
    response.set_cookie('username', '', expires=0)
    response.set_cookie('password', '', expires=0)
    response.set_cookie('created', '', expires=0)
    return response
    

@app.route('/create_message', methods=['GET','POST'])     
def create_message():
    con = sqlite3.connect(args.db_file)
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    is_logged_in = is_valid_login(con, username, password)
  
    message_contents = request.form.get('post')

    has_clicked_form = message_contents is not None

    if message_contents is not None:
        if message_contents != '':
            has_clicked_form = True
        else:
            has_clicked_form = False
    else: 
        has_clicked_form = False

    print('has_clicked_form=', has_clicked_form)
    print_debug_info()
    print('message_contents_after_click=', message_contents)

    if has_clicked_form:
        user_id = get_id(con, username)
        add_post(con, user_id, message_contents)
        return render_template('create_message.html', is_logged_in=is_logged_in, posting_complete=True)
    else:
        return render_template('create_message.html', is_logged_in=is_logged_in)


    

@app.route('/create_user', methods=['GET','POST'])     
def create_user():
    con = sqlite3.connect(args.db_file)
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    request.cookies.get('created')
    is_logged_in = is_valid_login(con, username, password)

    form_username = request.form.get('c_username')
    form_password1 = request.form.get('password1')
    form_password2 = request.form.get('password2')
    print('form_username=', form_username)
    print('form_password=', form_password1)
    print('form_password2=', form_password2)

    if form_username is not None:
        if form_username != '':
            has_clicked_form = True
        else:
            has_clicked_form = False
    else: 
        has_clicked_form = False
    print('has_clicked_form=', has_clicked_form)

    if has_clicked_form:
        if str(form_password1) != str(form_password2):
            return render_template('create_user.html', bad_password = True, is_logged_in=is_logged_in)
        else:
            create_info_correct = is_available_username(con, form_username)
            if create_info_correct == True:
                add_user(con, form_username, form_password1)
                response = make_response(redirect('http://127.0.0.1:5000/'))
                response.set_cookie('username', form_username)
                response.set_cookie('password', form_password1)
                response.set_cookie('created', '42', max_age=15)
                return (response)
            if create_info_correct == False:
                return render_template('create_user.html', bad_username = True, is_logged_in=is_logged_in)
    else:
        return render_template('create_user.html', is_logged_in=is_logged_in)


    print_debug_info()

@app.route('/account_info', methods=['GET','POST'])     
def account_info():
    con = sqlite3.connect(args.db_file)
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    is_logged_in = is_valid_login(con, username, password)
    return render_template('account_info.html', is_logged_in=is_logged_in)

@app.route('/delete', methods=['GET','POST'])     
def delete():
    con = sqlite3.connect(args.db_file)
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    is_logged_in = is_valid_login(con, username, password)

    delete_conf = request.form.get('delete_statement')
    if str(delete_conf) == 'i am lame and done with this site':
        user_id=get_id(con, username)
        #print ('conf_statement= True')
        delete_messages(con, user_id)
        delete_user(con, user_id)
        #return render_template('delete.html', is_logged_in=False, deleted = True)
        response = make_response(render_template('delete.html', is_logged_in=False, deleted = True))
        response.set_cookie('username', '', expires=0)
        response.set_cookie('password', '', expires=0)
        response.set_cookie('created', '', expires=0)
        return (response)
    elif str(delete_conf) == '':
        return render_template('delete.html', is_logged_in=is_logged_in)  
    elif str(delete_conf) != 'i am lame and done with this site' or '':
        return render_template('delete.html', is_logged_in=is_logged_in)
    else:
        return render_template('delete.html', is_logged_in=is_logged_in)


@app.route('/changepass', methods=['GET','POST'])     
def changepass():
    con = sqlite3.connect(args.db_file)
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    is_logged_in = is_valid_login(con, username, password)
    #return render_template('changepass.html', is_logged_in=is_logged_in)

    form_password_o = request.form.get('password_o')
    form_password_n = request.form.get('password_n')
    form_password_n2 = request.form.get('password_n2')
    print('form_username=', form_password_o)
    print('form_password=', form_password_n)
    print('form_password2=', form_password_n2)

    if form_password_o and form_password_n is not None:
        if form_password_o and form_password_n != '':
            has_clicked_form = True
        else:
            has_clicked_form = False
    else: 
        has_clicked_form = False
    print('has_clicked_form=', has_clicked_form)

    if has_clicked_form:
        if str(form_password_n) != str(form_password_n2):
            return render_template('changepass.html', bad_password = True, is_logged_in=is_logged_in)
        else:
            if form_password_o != password:
                return render_template('changepass.html', wrong_password=True, is_logged_in=is_logged_in)
            else:
                userid=get_id(con, username)
                changepassword(con, form_password_n, userid)
                response = make_response(render_template('changepass.html', is_logged_in=is_logged_in, change=True))
                response.set_cookie('username', username)
                response.set_cookie('password', form_password_n)
                return (response)
    else:
        return render_template('changepass.html', is_logged_in=is_logged_in)


########################################
# boilerplate
########################################

if __name__=='__main__':
    app.run()