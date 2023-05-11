from flask import Flask, request, render_template
from flask import send_from_directory

# Initialise app instance for route import 
app = Flask(__name__)

# Static assets endpoint
@app.route('/assets/<path:path>')
def fetch_asset(path):
    return send_from_directory('assets', path)

# DECLARE ROUTES IN routes/<page name>.py 
# THEN IMPORT ROUTES PY FILES HERE

from routes import callback
from routes import register_booking
from routes import view_appointment_history
from routes import edit_appointment
# END IMPORT ROUTES


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001,debug=True)