#!/usr/bin/env python

"""
Flask request routing.
"""

import flask
from flask import Flask
import os

import wodDice

app = Flask(__name__, static_url_path='')
app.debug = True
app.config.from_object('config')

@app.route('/')
def index():
    """ Return the main html page. """
    return app.send_static_file('index.html')

@app.route('/api/roll/<int:diff>/<int:pool>/')
@app.route('/api/roll/<int:diff>/<int:pool>/<int:torment>/')
@app.route('/api/roll/<int:diff>/<int:pool>/<int:torment>/<int:charmed>/')
def roll(diff, pool, torment=5, charmed=0):
    """
    api call to get a single roll of a dice pool.
    """
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

@app.route('/api/calc/<int:diff>/<int:pool>/')
@app.route('/api/calc/<int:diff>/<int:pool>/<int:torment>/')
@app.route('/api/calc/<int:diff>/<int:pool>/<int:torment>/<int:charmed>/')
def calc(diff, pool, torment=5, charmed=1):
    """
    api call to get the probabilities of a dice pool.
    """
    root = wodDice.PoolCalc(pool, diff, torment, charmed)
    s = root.summary()
    result = {
        'pool': pool,
        'diff': diff,
        'torment': torment,
        'charmed': charmed,
        'FailuresPercent': s['totalFail'],
        'BotchesPercent': s['botch'],
        'TormentPercent': s['torment'],
        'Percent': s['success'][1:],
        'expectedSuccesses': s['expectedSuccesses'],
    }
    return flask.json.jsonify(result)

@app.route('/api/enhance/<int:diff>/<int:pool>/<int:tool>/')
@app.route('/api/enhance/<int:diff>/<int:pool>/<int:tool>/<int:charmed>/')
def enhance(diff, pool, tool, charmed=1):
    """
    api call that finds the most advantagous use of Forge 1 evocation
    for each viable success level using the rules from the players guide.
    """
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
            # s = wodDice.RollSim(pool+enhTool, enhDiff, torment, charmed)
            node = wodDice.PoolCalc(pool+enhTool, enhDiff, torment, charmed)
            s = node.summary()
            last.append({'diff': enhDiff,
                        'pool': pool,
                        'tool': enhTool,
                        'charmed': charmed,
                        'torment': torment,
                        'reqSuccesses': successes,
                        'successes': s['expectedSuccesses']})
        if not last:
            break
        else:
            last = sorted(last, key=lambda a: a['successes'], reverse=True)
            enh.append(last)
    return flask.json.jsonify({'results': enh})


# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
