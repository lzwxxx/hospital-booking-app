from flask import request, redirect, abort, url_for
from os import environ

# Import app instance from main file
from __main__ import app

@app.route('/callback')
def callback():
    try:
        code = request.args.get('code')
        # state sent in format: ""page_<PAGETYPE:add|history>__guid_<GUID>"
        state = request.args.get('state')
        vars = state.split('__')
        vars = [var.split('_') for var in vars]
        print(vars)
        if vars[0][1] == 'add':
            dest = 'index'
            return redirect(url_for(dest,code=code))
        elif vars[0][1] == 'history':
            guid = vars[1][1]
            dest = 'view_appointment_history'
            return redirect(url_for(dest,guid=guid,code=code))

        return {state},400
    except:
        abort(404)