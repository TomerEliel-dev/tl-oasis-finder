from flask import Flask, render_template, request


tl_oasis_finder = Flask(__name__)

from tl_oasis_finder import routes