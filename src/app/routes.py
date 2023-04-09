from flask import Blueprint, render_template, request

# Create a blueprint for routes
bp = Blueprint('routes', __name__)


# Define routes and handlers
@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Do something with the uploaded file
        pass

# ...
