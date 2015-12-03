from app import app
from flask import Flask, jsonify,send_from_directory,request,redirect,url_for, render_template_string, Response, session
import sqlite3
from werkzeug import secure_filename
import os
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required
import flask_wtf as WTF
import shutil
from fpdf import FPDF


@app.route('/')
@app.route('/index')
def index():
	    return "Bookpad! A place to upload and edit your documents, Please login or register"


login_template = '''
<form action="{{ url_for('login') }}" method="POST" name="login_user_form">
    {{ form.csrf_token }}

    {{ form.email() }}
    {{ form.password() }}
    {{ form.submit() }}

</form>

'''

login_web_template = '''
<form action="{{ url_for('login_web') }}" method="POST" name="login_user_form">
    {{ form.csrf_token }}

    {{ form.email() }}
    {{ form.password() }}
    {{ form.submit() }}

</form>

'''


register_template = '''
<form action="{{ url_for('register') }}" method="POST" name="register_user_form">
    {{ form.csrf_token }}

    {{ form.email() }}
    {{ form.password() }}
    {{ form.submit() }}

</form>

'''

list_template = '''
<form action="{{ url_for('list_files') }}" method="POST" name="list_user_form">
    {{ form.csrf_token }}

    {{ form.email() }}
    {{ form.password() }}
    {{ form.submit() }}

</form>

'''

upload_template = '''
<form action="{{ url_for('upload_file') }}" method="POST" name="upload_user_form">
    {{ form.csrf_token }}

    {{ form.email() }}
    {{ form.password() }}
    {{ form.submit() }}

</form>

'''


class LoginForm(WTF.Form):
    email = StringField('Email', validators=[Required()]) 
    password = PasswordField('Password', validators=[Required()]) 
    submit = SubmitField('Submit')

class RegisterForm(WTF.Form):
    email = StringField('Email', validators=[Required()])
    password = StringField('Password', validators=[Required()]) 
    submit = SubmitField('Submit')


class ListForm(WTF.Form):
    email = StringField('Email', validators=[Required()])
    password = StringField('Password', validators=[Required()]) 
    submit = SubmitField('Submit')


class UploadForm(WTF.Form):
    email = StringField('Email', validators=[Required()])
    password = StringField('Password', validators=[Required()]) 
    submit = SubmitField('Submit')

def Valid(username, password) :
	conn = sqlite3.connect('user.db')
	x = username
	y = password
	cmd = 'SELECT username, password from USER where username = ' + "'" + x + "'" + ' AND password = ' + "'" + y + "'" + ';'
	cursor = conn.execute(cmd)
	for row in cursor :
		return True
	return False



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm() # instantiate the form class
    if request.method == 'POST': # if the request method is POST
	username = request.values['email']
	password = request.values['password']
	print username, password
	if Valid(username, password) :
		session['log_in'] = username
		return redirect(url_for('list'))
	else :
		return "Invalid username, password"
    return render_template_string(login_template, form=form)


@app.route('/web/login', methods=['GET', 'POST'])
def login_web():
    form = LoginForm() # instantiate the form class
    if request.method == 'POST': # if the request method is POST
	username = request.values['email']
	password = request.values['password']
	print username, password
	if Valid(username, password) :
		session['log_in'] = username
		return redirect(url_for('list'))
	else :
		return "Invalid username, password"
    return render_template_string(login_web_template, form=form)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def Insert(username, password) :
	conn = sqlite3.connect('user.db')
	cmd = 'INSERT INTO USER (username, password) VALUES ( '
	cmd += "'" + username + "'" + ', '
	cmd += "'" + password + "'" + ')'
	conn.execute(cmd);
	conn.commit()
	conn.close()


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm() # instantiate the form class
    if request.method == 'POST': # if the request method is POST
	username = request.values['email']
	password = request.values['password']
	Insert(username, password)
	return 'Registration done!' + ' Username : ' + username + ' Password : ' + password
    return render_template_string(register_template, form=form)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['txt', 'pdf'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def Insert_File(filename, username) :
	#print filename, username
	conn = sqlite3.connect('user.db')
	cmd = 'INSERT INTO FILE (filename, username) VALUES ( '
	cmd += "'" + filename + "'" + ', '
	cmd += "'" + username + "'" + ')'
	#print cmd
	conn.execute(cmd);
	conn.commit()
	conn.close()


@app.route('/web/upload', methods=['GET', 'POST'])
def upload():
    if 'log_in' not in session.keys() :
	return redirect(url_for('index'))
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            username = session['log_in']
	    Insert_File(filename, username)
            return redirect(url_for('uploaded',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST': 
		username = request.values['email']
		password = request.values['password']
	        #file = request.files['file']
		fname = request.values['file']
		fname = str(fname)
		src = fname
		fname = fname.split('/')[-1]
		dest = os.path.join(app.config['UPLOAD_FOLDER'], fname)

		shutil.copy2(src, dest)
		Insert_File(fname, username)	
		return "Uploaded file successfully"	
	return '''
	    <!doctype html>
	    <title>Upload new File</title>
	    <h1>Upload new File</h1>
	    <form action="" method=post enctype=multipart/form-data>
		<input type=text name=email>
		<input type=text name=password>
	      	<input type=text name=file>
		 <input type=submit value=Submit>
	    </form>
	    '''


import gc

@app.route('/web/uploaded/<filename>')
def uploaded(filename):
	if 'log_in' not in session.keys() :
		return redirect(url_for('index'))
	username = session['log_in']
	conn = sqlite3.connect('user.db')
	cmd = 'SELECT filename, username from FILE where username = ' + "'" + username + "'" + ' AND filename = ' + "'" + filename + "'"
	cursor = conn.execute(cmd)
	fl = False
	for row in cursor :
		fl = True
	if not fl :
		return redirect(url_for('index'))

	response = send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
	response.headers.extend({
		'Cache-Control': 'no-cache'
	    })

	return response

@app.route('/web/list', methods=['GET', 'POST'])
def list() :
	if 'log_in' not in session.keys() :
		return redirect(url_for('index'))
	username = session['log_in']
	
	conn = sqlite3.connect('user.db')
	cmd = 'SELECT filename from FILE where username = ' + "'" + username + "'"
	cursor = conn.execute(cmd)
	out = ''
	for row in cursor :
		out += '<li>'
		out += '<a href=/web/uploaded/'+row[0]+'>' +row[0] + '</a> '
		out += '</li>'
	conn.close()
	return out


@app.route('/list_files', methods=['GET', 'POST'])
def list_files() :
	"""	if 'log_in' not in session.keys() :
		return redirect(url_for('index'))
	username = session['log_in']
"""
	form = ListForm() # instantiate the form class
	if request.method == 'POST': # if the request method is POST
		username = request.values['email']
		password = request.values['password']
		if Valid(username, password) :
			conn = sqlite3.connect('user.db')
			cmd = 'SELECT filename from FILE where username = ' + "'" + username + "'"
			cursor = conn.execute(cmd)
			out = ''
			for row in cursor :
				out += row[0] + '<br />'
			conn.close()
			return out
		else :
			return "Invalid Username or Password"
	return render_template_string(list_template, form=form)

@app.route('/view/<fname>', methods=['GET', 'POST'])
def view_api(fname, pages=None):
	if request.method == 'POST': 
		username = request.values['email']
		password = request.values['password']
	        #file = request.files['file']
		fname = str(fname)
		src = fname
		conn = sqlite3.connect('user.db')
		cmd = 'SELECT filename, username from FILE where username = ' + "'" + username + "'" + ' AND filename = ' + "'" + fname + "'"
		cursor = conn.execute(cmd)
		fl = False
		for row in cursor :
			fl = True
		if not fl :
			return redirect(url_for('index'))
	
		#f = send_from_directory(app.config['UPLOAD_FOLDER'],fname)
		fname = os.path.join(app.config['UPLOAD_FOLDER'], fname)
	
		exten = fname.split('.')[1]
		print exten
		if exten != 'pdf' :
			f = open(fname, 'rb').read()
			return f
		if not pages:
		    pagenums = set()
		else:
		    pagenums = set(pages)

		output = StringIO()
		manager = PDFResourceManager()
		converter = TextConverter(manager, output, laparams=LAParams())
		interpreter = PDFPageInterpreter(manager, converter)

		infile = file(fname, 'rb')
		for page in PDFPage.get_pages(infile, pagenums):
		    interpreter.process_page(page)
		infile.close()
		converter.close()
		text = output.getvalue()
		output.close
		return text 
	return '''
	    <!doctype html>
	    <title>Upload new File</title>
	    <h1>Upload new File</h1>
	    <form action="" method=post enctype=multipart/form-data>
		<input type=text name=email>
		<input type=text name=password>
	      	<input type=text name=file>
		 <input type=submit value=Submit>
	    </form>'''



@app.route('/web/view/<fname>')
def view(fname, pages=None):
	if 'log_in' not in session.keys() :
		return redirect(url_for('index'))
	username = session['log_in']

	conn = sqlite3.connect('user.db')
	cmd = 'SELECT filename, username from FILE where username = ' + "'" + username + "'" + ' AND filename = ' + "'" + fname + "'"
	cursor = conn.execute(cmd)
	fl = False
	for row in cursor :
		fl = True
	if not fl :
		return redirect(url_for('index'))
	
	#f = send_from_directory(app.config['UPLOAD_FOLDER'],fname)
	fname = os.path.join(app.config['UPLOAD_FOLDER'], fname)
	exten = fname.split('.')[1]
	if exten != 'pdf' :
		f = open(fname, 'rb').read()
		return f
	if not pages:
	    pagenums = set()
	else:
	    pagenums = set(pages)

	output = StringIO()
	manager = PDFResourceManager()
	converter = TextConverter(manager, output, laparams=LAParams())
	interpreter = PDFPageInterpreter(manager, converter)

	infile = file(fname, 'rb')
	for page in PDFPage.get_pages(infile, pagenums):
	    interpreter.process_page(page)
	infile.close()
	converter.close()
	text = output.getvalue()
	output.close
	return text 

@app.route('/web/edit/<fname>')
def edit_file(fname, pages=None):
	if 'log_in' not in session.keys() :
		return redirect(url_for('index'))
	#f = send_from_directory(app.config['UPLOAD_FOLDER'],fname)
	filename = fname
	fname = os.path.join(app.config['UPLOAD_FOLDER'], fname)
	exten = fname.split('.')[1]
	print exten
	if exten != 'pdf' :
		f = open(fname, 'rb').read()
		text = f
	else :
		if not pages:
		    pagenums = set()
		else:
		    pagenums = set(pages)

		output = StringIO()
		manager = PDFResourceManager()
		converter = TextConverter(manager, output, laparams=LAParams())
		interpreter = PDFPageInterpreter(manager, converter)

		infile = file(fname, 'rb')
		for page in PDFPage.get_pages(infile, pagenums):
		    interpreter.process_page(page)
		infile.close()
		converter.close()
		text = output.getvalue()
		output.close
	print filename
	return '<!doctype html><title>Edit File</title><h1>Upload new File</h1><form action="/save" method=post><p><textarea name="contents" rows=30 cols = 150 autofocus>' + text +'</textarea><br /><input type=hidden name=filename value=' + str(filename) + '> <input type=submit value=Upload></form></html>'

@app.route('/save', methods=['GET', 'POST'])
def save_file():
	filename = request.values['filename']
	contents = request.values['contents']
	fname = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	backup_path = os.path.join(app.config['BACKUP_FOLDER'], filename)
	shutil.copy2(fname, backup_path)
	exten = fname.split('.')[1]
	if exten != 'pdf' :
		f = open(fname, 'w')
		f.write(contents)
		f.close()
	else:
		pdf=FPDF('P', 'mm',(500,400))
		pdf.add_page()
		pdf.set_font('Courier','B',16)
		for line in contents.split("\n"):
			pdf.cell(40,10,line)
			pdf.ln(h='')
		pdf.output(fname,'F')
	return redirect(url_for('list'))


def Delete(fname, uname) :
	conn = sqlite3.connect('user.db')
	cmd = 'DELETE FROM FILE WHERE '
	cmd += 'filename = ' + "'" + fname + "'" + ' AND '
	cmd += 'username = ' + "'" + uname + "'"
	print cmd
	conn.execute(cmd);
	conn.commit()
	conn.close()

def Update(oldfname, newfname, uname) :
	conn = sqlite3.connect('user.db')
	cmd = 'UPDATE FILE SET filename = ' + "'" + newfname + "'" + 'WHERE '
	cmd += 'filename = ' + "'" + oldfname + "'" + ' AND '
	cmd += 'username = ' + "'" + uname + "'"
	print cmd
	conn.execute(cmd);
	conn.commit()
	conn.close()

@app.route('/web/delete/<fname>', methods = ['GET', 'POST'])
def delete_file(fname):
	if 'log_in' not in session.keys() :
		return redirect(url_for('index'))
	username = session['log_in']
	conn = sqlite3.connect('user.db')
	cmd = 'SELECT filename, username from FILE where username = ' + "'" + username + "'" + ' AND filename = ' + "'" + fname + "'"
	cursor = conn.execute(cmd)
	fl = False
	for row in cursor :
		fl = True
	if not fl :
		return redirect(url_for('index'))
	Delete(fname, username)
	fname = os.path.join(app.config['UPLOAD_FOLDER'], fname)
	print fname
	os.remove(fname)
	return redirect(url_for('list'))

@app.route('/delete/<fname>', methods = ['GET', 'POST'])
def delete_file_rest(fname):
	form = ListForm() # instantiate the form class
	if request.method == 'POST': # if the request method is POST
		username = request.values['email']
		password = request.values['password']
		if Valid(username, password) :
			conn = sqlite3.connect('user.db')
			cmd = 'SELECT filename, username from FILE where username = ' + "'" + username + "'" + ' AND filename = ' + "'" + fname + "'"
			cursor = conn.execute(cmd)
			fl = False
			for row in cursor :
				fl = True
			if not fl :
				return redirect(url_for('index'))
			Delete(fname, username)
			fname = os.path.join(app.config['UPLOAD_FOLDER'], fname)
			print fname
			os.remove(fname)
			return redirect(url_for('list'))

		else :
			return "Invalid Username or Password"
	return render_template_string(list_template, form=form)	

#this function restores previous version from backup
@app.route('/web/restore/<fname>', methods = ['GET', 'POST'])
def restore_file(fname):
	if 'log_in' not in session.keys() :
		return redirect(url_for('index'))
	username = session['log_in']
	conn = sqlite3.connect('user.db')
	cmd = 'SELECT filename, username from FILE where username = ' + "'" + username + "'" + ' AND filename = ' + "'" + fname + "'"
	cursor = conn.execute(cmd)
	fl = False
	for row in cursor :
		fl = True
	if not fl :
		return redirect(url_for('index'))
	
	dest = os.path.join(app.config['UPLOAD_FOLDER'], fname)
	src = os.path.join(app.config['BACKUP_FOLDER'], fname)
	shutil.move(src,dest)
	return redirect(url_for('list'))

@app.route('/restore/<fname>', methods = ['GET', 'POST'])
def restore_file_rest(fname):
	form = ListForm() # instantiate the form class
	if request.method == 'POST': # if the request method is POST
		username = request.values['email']
		password = request.values['password']
		if Valid(username, password) :
			conn = sqlite3.connect('user.db')
			cmd = 'SELECT filename, username from FILE where username = ' + "'" + username + "'" + ' AND filename = ' + "'" + fname + "'"
			cursor = conn.execute(cmd)
			fl = False
			for row in cursor :
				fl = True
			if not fl :
				return redirect(url_for('index'))
			dest = os.path.join(app.config['UPLOAD_FOLDER'], fname)
			src = os.path.join(app.config['BACKUP_FOLDER'], fname)
			shutil.move(src,dest)
			return redirect(url_for('list'))

		else :
			return "Invalid Username or Password"
	return render_template_string(list_template, form=form)	


@app.route('/web/rename/<oldfname>/<newfname>', methods = ['GET', 'POST'])
def rename_file(oldfname,newfname):
	if 'log_in' not in session.keys() :
		return redirect(url_for('index'))
	username = session['log_in']
	conn = sqlite3.connect('user.db')
	cmd = 'SELECT filename, username from FILE where username = ' + "'" + username + "'" + ' AND filename = ' + "'" + oldfname + "'"
	cursor = conn.execute(cmd)
	fl = False
	for row in cursor :
		fl = True
	if not fl :
		return redirect(url_for('index'))
	Update(oldfname, newfname, username)
	src = os.path.join(app.config['UPLOAD_FOLDER'], oldfname)
	dest = os.path.join(app.config['UPLOAD_FOLDER'], newfname)
	shutil.move(src,dest)
	print "yo"
	return redirect(url_for('list'))

@app.route('/rename/<oldfname>/<newfname>', methods = ['GET', 'POST'])
def rename_file_rest(oldfname,newfname):
	form = ListForm() # instantiate the form class
	if request.method == 'POST': # if the request method is POST
		username = request.values['email']
		password = request.values['password']
		if Valid(username, password) :
			conn = sqlite3.connect('user.db')
			cmd = 'SELECT filename, username from FILE where username = ' + "'" + username + "'" + ' AND filename = ' + "'" + oldfname + "'"
			cursor = conn.execute(cmd)
			fl = False
			for row in cursor :
				fl = True
			if not fl :
				return redirect(url_for('index'))
			Update(oldfname, newfname, username)
			src = os.path.join(app.config['UPLOAD_FOLDER'], oldfname)
			dest = os.path.join(app.config['UPLOAD_FOLDER'], newfname)
			shutil.move(src,dest)
			return redirect(url_for('list'))

		else :
			return "Invalid Username or Password"
	return render_template_string(list_template, form=form)	

