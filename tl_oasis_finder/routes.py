from tl_oasis_finder import tl_oasis_finder
from flask import render_template, request

@tl_oasis_finder.route("/",methods = ['GET'])
def index(name="Tomer"):
    return render_template('index.html', name=name)

@tl_oasis_finder.route('/search', methods=['GET'])
def search():
    return render_template('search.html', name = request.args.get('name'))

