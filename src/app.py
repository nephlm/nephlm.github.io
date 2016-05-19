import flask
from flask import Flask, render_template, request
# from flask.ext.sqlalchemy import SQLAlchemy
# import logging
# from logging import Formatter, FileHandler
# from forms import *
import os

import wodDice

app = Flask(__name__, static_url_path='')
app.debug = True
app.config.from_object('config')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/roll/<int:diff>/<int:pool>/')
@app.route('/api/roll/<int:diff>/<int:pool>/<int:torment>/')
@app.route('/api/roll/<int:diff>/<int:pool>/<int:torment>/<int:charmed>/')
def roll(diff, pool, torment=5, charmed=0):
    r = wodDice.Roll(pool , diff, torment, charmed)
    result = {
        'pool': pool,
        'diff': diff,
        'torment': torment,
        'charmed': charmed,
        'rolls': r.sortedDice,
        'successes': r.successes(),
        'botches': r.botches,
        'torments': r.torment(),
        'netSuccesses': r.netSuccesses(),
        'botchRoll': r.isBotchRoll(),
        'tormentRoll': r.isTormentRoll()
    }
    return flask.json.jsonify(result)

@app.route('/api/sim/<int:diff>/<int:pool>/')
@app.route('/api/sim/<int:diff>/<int:pool>/<int:torment>/')
@app.route('/api/sim/<int:diff>/<int:pool>/<int:torment>/<int:charmed>/')
def sim(diff, pool, torment=5, charmed=1):
    s = wodDice.RollSim(pool, diff, torment, charmed)
    result = {
        'pool': pool,
        'diff': diff,
        'torment': torment,
        'charmed': charmed,
        'Failures': s.failures,
        'Botches': s.botches,
        'Torment': s.torment,
        'FailuresPercent': s.failurePercent,
        'BotchesPercent': s.botchPercent,
        'TormentPercent': s.tormentPercent,
        'Successes':s.successes[1:],
        'Percent': s.successPercent,
        'expectedSuccesses': s.expectedSuccesses,
    }
    return flask.json.jsonify(result)

@app.route('/api/enhance/<int:diff>/<int:pool>/<int:tool>/')
@app.route('/api/enhance/<int:diff>/<int:pool>/<int:tool>/<int:charmed>/')
def enhance(diff, pool, tool, charmed=1):
    torment =0
    enh = []
    last = []
    successes = 0
    while successes == 0 or last:
        successes += 1
        last = []
        for i in range(successes+1):
            enhDiff = diff - i
            enhTool = tool + (successes-i)
            if (enhTool > tool*2) or (enhDiff < 3):
                continue
            s = wodDice.RollSim(pool+enhTool, enhDiff, torment, charmed)
            last.append({'diff': enhDiff,
                        'pool': pool,
                        'tool': enhTool,
                        'charmed': charmed,
                        'torment': torment,
                        'reqSuccesses': successes,
                        'successes': s.expectedSuccesses})
        if not last:
            break
        else:
            last = sorted(last, key=lambda a: a['successes'], reverse=True)
            enh.append(last)
    return flask.json.jsonify({'results': enh})





# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('errors/404.html'), 404


# # Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
