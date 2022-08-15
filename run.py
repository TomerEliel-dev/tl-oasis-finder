from flask import Flask
from tl_oasis_finder import tl_oasis_finder

if __name__ == '__main__':
    tl_oasis_finder.run(debug=False)