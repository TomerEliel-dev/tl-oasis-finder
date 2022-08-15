from subprocess import CREATE_NEW_CONSOLE
from flask import Flask, render_template, request

tl_oasis_finder = Flask(__name__)

@tl_oasis_finder.route("/",methods = ['GET'])
def index(name="Tomer"):
    return render_template('index.html', name=name)

@tl_oasis_finder.route('/search', methods=['GET'])
def search():
    return render_template('search.html', name = request.args.get('name'))

