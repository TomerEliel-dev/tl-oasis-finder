from time import sleep
from tl_oasis_finder import tl_oasis_finder, api
from flask import render_template, request, jsonify

@tl_oasis_finder.route("/",methods = ['GET'])
def index(name="Tomer"):
    return render_template('index.html', name=name)

@tl_oasis_finder.route('/search', methods=['GET'])
def search():
    return render_template('search.html', name = request.args.get('name'))

@tl_oasis_finder.route('/map', methods=['GET'])
def map(map="Empty"):      
    map = api.handleGetMapFilesAndProcess(request.args.get('base_url'),request.args.get('usr'),request.args.get('passw'))
    return render_template('map.html', map = jsonify(map))

@tl_oasis_finder.route('/loading', methods=['GET'])
def loading(timeLeft = '70'):
    # return render_template('loading.html', timeLeft = timeLeft)
    map = api.handleGetMapFilesAndProcess(request.args.get('base_url'),request.args.get('usr'),request.args.get('passw'))
    return render_template('map.html', map = jsonify(map))

@tl_oasis_finder.route('/getprogress', methods=['POST'])
def returnProgress():
    return None
