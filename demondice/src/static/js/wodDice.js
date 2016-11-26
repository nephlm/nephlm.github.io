

function getRandom(min, max) {
    return min + Math.floor(Math.random() * (max - min + 1));
}


function D10(){
    this.roll = getRandom(1,10);
    this.botch = (this.roll == 1);

    this.success = function(diff) {
        return this.roll >= diff;
    };

    this.torment = function(diff, pTorment) {
        return this.success(diff) && this.roll < pTorment;
    };
};

function Roll(pollSize, diff, pTorment, charmed){
    this.pollSize = pollSize;
    this.diff = diff;
    this.pTorment = pTorment;
    this.charmed = typeof charmed !== 'undefined' ? charmed : 0;
    this.dice = [];
    for (i=0; i < this.pollSize; i++) {
        this.dice.push(new D10());
    }

    this.sortedDice = function() {

        var rolls = this.dice.map(function(d) {return d.roll})
        rolls.sort(function(a,b) {return b-a;})
        return rolls
    };

    this.successes = function(diff) {
        diff = typeof diff !== 'undefined' ? diff : this.diff;
        succ = 0;
        this.dice.forEach(function(d) {
            if (d.roll >= diff) succ++;
        });
        return succ;
    };

    this.torment = function(diff, pTorment) {
        diff = typeof diff !== 'undefined' ? diff : this.diff;
        pTorment = typeof pTorment !== 'undefined' ? pTorment : this.pTorment;
        tCount = 0;
        this.dice.forEach(function(d) {
            if (d.torment(diff, pTorment)) {
                tCount++;
            }
        });
        return tCount;
    };

    this.botches = function () {
        bCount = 0;
        this.dice.forEach(function(d) {
            if (d.botch) { bCount++;};
        });
        return bCount;
    };

    this.netSuccesses = function(diff) {
        diff = typeof diff !== 'undefined' ? diff : this.diff;
        return this.successes(diff) - (Math.max(0, (this.botches() - this.charmed)));

    };

    this.isBotchRoll = function(diff) {
        diff = typeof diff !== 'undefined' ? diff : this.diff;
        return (this.successes(diff) <= 0) && (this.botches() > this.charmed);
    }

    this.isTormentRoll = function(diff, pTorment) {
        diff = typeof diff !== 'undefined' ? diff : this.diff;
        pTorment = typeof pTorment !== 'undefined' ? pTorment : this.pTorment;
        if (this.netSuccesses(diff) <= 0) {
            return false;
        } else {
            return this.torment(diff, pTorment) > (this.netSuccesses(diff)/2)
        }
    }
};

hash = function(tuple) {
    return tuple.join(',')
}

unhash = function(st) {
    return st.split(',').map(function(i) {return parseInt(i, 10)})
}


function PoolCalc(pool, diff, torment, charmed) {
    this.BOTCH = 0;
    this.FAIL = 1;
    this.TORMENT = 2;
    this.SUCCESS = 3;
    this.PROB = 4;

    this.pool = pool;
    this.diff = diff;
    this.torment = torment;
    this.charmed = charmed;

    this.tier = {};
    this.tier[hash([0,0,0,0])] = 1.0;

    this.pDict = [];
        this.pDict[this.BOTCH] = 0.1;
        this.pDict[this.FAIL] = (diff-2)*.1;
        this.pDict[this.TORMENT] = Math.max(0, ((torment-diff) * .1));
        this.pDict[this.SUCCESS] = (1 + (10 - Math.max(torment, diff))) * .1;

    this.populate = function() {
        for(var i=0;i<this.pool;i++){
            var newTier = {};
            for (var stKey in this.tier) {
                var key = unhash(stKey);
                var baseProb = this.tier[stKey];
                for (branch=0; branch<4; branch++) {
                    var newProb = baseProb * this.pDict[branch];
                    if (newProb != 0.0) {
                        var newKey = key.slice();
                        newKey[branch] = key[branch] + 1;
                        var tierProb = newTier[hash(newKey)] || 0.0;
                        newTier[hash(newKey)] = newProb + tierProb;
                    };
                };
            };
            //console.log(newTier)
            this.tier = newTier;
        }
    };

    this.isBotch = function(key) {
        return (key[this.BOTCH] > this.charmed) && ((key[this.SUCCESS] + key[this.TORMENT]) == 0)
    };

    this.isTorment = function(key, netBotches) {
        return ((key[this.SUCCESS] - netBotches) < key[this.TORMENT]) &&
                (((key[this.SUCCESS] - netBotches) + key[this.TORMENT]) > 0)
    };

    this.summary = function() {
        var botchProb = 0.0;
        var tormentProb = 0.0;
        var successes = [];
        var expectedSuccesses = 0.0;
        for (var stKey in this.tier) {
            var key = unhash(stKey)
            var prob = this.tier[stKey]
            var netBotches = Math.max(0, key[this.BOTCH] - this.charmed)
            var netSuccesses = Math.max(0,key[this.TORMENT] + key[this.SUCCESS] - netBotches)
            if (this.isBotch(key)) {
                botchProb += this.tier[stKey]
                //console.log([this.tier[stKey], botchProb])
            }
            if (this.isTorment(key, netBotches) && netSuccesses > 0) {
                tormentProb += prob
            }
            successes[netSuccesses] = (successes[netSuccesses] || 0.0) + prob
            }
        for (var i=0; i < successes.length; i++) {
            expectedSuccesses += (i*successes[i])
        }
        return {
            'botch': botchProb,
            'torment': tormentProb,
            'success': successes,
            'totalFail': successes[0],
            'totalSuccess': successes.slice(1).reduce(function(a,b) {return a+b}, 0),
            'expectedSuccesses': expectedSuccesses,
            'charmed': this.charmed,
            'diff': this.diff,
            'pool': this.pool,
            'tormentVal': this.torment,
        }
    }
}


roll = function(diff, pool, torment, charmed) {
    r = new Roll(pool, diff, torment, charmed);
    return {
        'pool': pool,
        'diff': diff,
        'torment': torment,
        'charmed': charmed,
        'rolls': r.sortedDice(),
        'successes': r.successes(),
        'botches': r.botches(),
        'torments': r.torment(),
        'netSuccesses': r.netSuccesses(),
        'botchRoll': r.isBotchRoll(),
        'tormentRoll': r.isTormentRoll()
    }
}

calc = function(pool, diff, torment, charmed) {
    root = new PoolCalc(pool, diff, torment, charmed)
    root.populate()
    //console.log(root)
    s = root.summary()
    //console.log(s)
    return {
        'pool': pool,
        'diff': diff,
        'torment': torment,
        'charmed': charmed,
        'FailuresPercent': s['totalFail'],
        'BotchesPercent': s['botch'],
        'TormentPercent': s['torment'],
        'Percent': s['success'].splice(1),
        'expectedSuccesses': s['expectedSuccesses'],
    }
}

enhance = function(diff, pool, tool, charmed) {
    var torment = 0;
    var enh = [];
    var last = [];
    var successes = 0;
    while (successes == 0 || last.length > 0) {
        successes++;
        last = [];
        for(var i=0; i < successes+1; i++) {
            var enhDiff = diff - i;
            var enhTool = tool + (successes - i);
            if ((enhTool > tool*2) || (enhDiff < 3)) {
                continue;
            }
            node = new PoolCalc(pool+enhTool, enhDiff, torment, charmed);
            node.populate();
            s = node.summary();
            var val = {
                'diff': enhDiff,
                'pool': pool,
                'tool': enhTool,
                'charmed': charmed,
                'torment': torment,
                'reqSuccesses': successes,
                'successes': s['expectedSuccesses']
            };
            last.push(val);
        }
        if (last.length == 0) {
            break;
        } else {
            last.sort(function(a,b) {return b['successes']-a['successes']});
            enh.push(last);
        }
    }
    return enh;
}

/*console.log(enhance(6,3,3,1));
e = enhance(6,3,3,1);
for (x in e) {
    console.log(e[x]);
}
*/
//console.log(calc(5,6,5,1))

/*rollD = new Roll(8, 10, 8, 0);

console.log(rollD);
console.log(rollD.dice[0]);
console.log('=======')
rollD.sortedDice().forEach(function(i) {
    console.log(i);
})
console.log('succ (' + rollD.diff + '): ' + rollD.successes())
console.log('torm (' + rollD.pTorment + '): ' + rollD.torment())
console.log('botch: ' + rollD.botches())
console.log('netsucc: ' + rollD.netSuccesses())
console.log('isBotch: ' + rollD.isBotchRoll())
console.log('=======')

calc = new PoolCalc(5,4,6,1);
calc.populate()
console.log(calc);
console.log(calc.tier)
console.log(calc.summary())*/

// d10 = new D10();
// console.log(d10);
// console.log('succ10: ' + d10.success(10));
// console.log('succ1: ' + d10.success(1));
// console.log('torment 1/9: ' + d10.torment(1, 9));
// console.log('torment 10/3: ' + d10.torment(10, 3));
