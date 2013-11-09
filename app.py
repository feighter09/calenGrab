from flask import Flask, render_template
import controllers

app = Flask(__name__, template_folder='views')
app.register_blueprint(controllers.main)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)