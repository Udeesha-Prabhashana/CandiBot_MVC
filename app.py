from flask import Flask
from config import Config
from controllers import file_controller, question_controller, result_controller

app = Flask(__name__, template_folder='views')
app.config.from_object(Config)

# Register Blueprints
app.register_blueprint(file_controller.bp)
app.register_blueprint(question_controller.bp)
app.register_blueprint(result_controller.bp)

if __name__ == '__main__':
    app.run(debug=True)
