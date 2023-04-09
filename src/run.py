from flask import Flask
from app import routes

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(routes.bp)

# Other setup tasks, such as initializing databases, configuring extensions, etc.
# ...

if __name__ == '__main__':
    app.run(debug=True)
