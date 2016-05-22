import random
import argparse


PERMENANT_TORMENT = 5
CHARMED = 1

class D10(object):
    def __init__(self):
        self.roll = random.randint(1,10)

    @property
    def botch(self):
        return self.roll == 1

    def success(self, diff):
        return self.roll >= diff

    def torment(self, diff, pTorment):
        return self.success(diff) and self.roll < pTorment


class Roll(object):
    def __init__(self, poolSize, diff, pTorment, charmed=0):
        self.poolSize = poolSize
        self.diff = diff
        self.pTorment = pTorment
        self.charmed = charmed
        self.dice = []
        for i in range(self.poolSize):
            self.dice.append(D10())


    @property
    def sortedDice(self):
        return sorted([x.roll for x in self.dice], reverse=True)


    def successes(self, diff=None):
        if not diff:
            diff = self.diff
        total = 0
        for die in self.dice:
            if die.success(diff):
                total += 1
        return total

    def torment(self, diff=None, pTorment=None):
        if not pTorment:
            pTorment = self.pTorment
        if not diff:
            diff = self.diff
        total = 0
        for die in self.dice:
            if die.torment(diff, pTorment):
                total += 1
        return total

    @property
    def botches(self):
        total = 0
        for die in self.dice:
            if die.botch:
                total += 1
        return total

    def netSuccesses(self, diff=None):
        return self.successes(diff) - max(0, (self.botches - self.charmed))

    def isBotchRoll(self, diff=None):
         return self.successes(diff) <= 0 and self.botches > self.charmed
         # return self.netSuccesses(diff) < 0 and self.botches > self.charmed

    def isTormentRoll(self, diff=None, pTorment=None):
        if self.netSuccesses(diff) > 0:
            return self.torment(diff, pTorment) > self.netSuccesses(diff)/2
        else:
            return False

class RollSim(object):
    def __init__(self, poolSize, diff, pTorment, charmed=0, iterations=10000):
        self.poolSize = poolSize
        self.diff = diff
        self.pTorment = pTorment
        self.charmed = charmed
        self._iterations = iterations
        self.successes = [0 for x in range(self.poolSize + 1)]
        self.failures = 0
        self.botches = 0
        self.torment = 0

        self.sim()

    @property
    def successPercent(self):
        return list(map(self._percent, self.successes[1:]))

    @property
    def failurePercent(self):
        return self._percent(self.failures)

    @property
    def botchPercent(self):
        return self._percent(self.botches)

    @property
    def tormentPercent(self):
        return self._percent(self.torment)

    @property
    def expectedSuccesses(self):
        return sum([y/float(self._iterations)*x for x,y in enumerate(self.successes)])

    def sim(self):
        for _ in range(self._iterations):
            roll = Roll(self.poolSize, self.diff, self.pTorment, self.charmed)
            if roll.netSuccesses() <= 0:
                self.failures += 1
                if roll.isBotchRoll():
                    self.botches += 1
            else:
                self.successes[roll.netSuccesses()] += 1
                if roll.isTormentRoll():
                    self.torment += 1

    def _percent(self, catCount):
        return catCount/(self._iterations/100)

class SimCache(dict):

    def getSim(self, pool, diff, torment, charmed, iterations=10000):
        try:
            return self[(pool, diff, torment, charmed, iterations)]
        except KeyError:
            simObj = RollSim(pool, diff, torment, charmed, iterations)
            self[(pool, diff, torment, charmed, iterations)] = simObj
            return simObj

class Root(object):
    BOTCH = 0
    FAIL = 1
    TORMENT = 2
    SUCCESS = 3
    def __init__(self, pool, diff, torment, charmed):
        self.pool =pool
        self.diff = diff
        self.torment = torment
        self.charmed = charmed
        self.tier = {(0,0,0,0): 1.0}

        self.pBotch = .1
        self.pFail = (diff -2) * .1
        self.pTorment = max(0, (torment - diff) * .1)
        self.pSuccess = (1 + (10 - max(torment, diff))) * .1
        self.children = []
        self.pDict = {
            self.BOTCH: self.pBotch,
            self.FAIL: self.pFail,
            self.TORMENT: self.pTorment,
            self.SUCCESS: self.pSuccess,
        }

        self.populate()

    def populate(self):
        for x in range(self.pool):
            newTier = {}
            for key, baseProb in self.tier.items():
                for branch in range(4):
                    newProb = baseProb * self.pDict[branch]
                    if newProb == 0.0:
                        continue
                    newKey = list(key[:])
                    newKey[branch] += 1
                    newKey = tuple(newKey)
                    newTier[newKey] = newTier.get(newKey, 0.0) + newProb
            self.tier = newTier
            # print(self.tier)

    def isBotch(self, key):
        return key[self.BOTCH] > self.charmed and key[self.SUCCESS] == 0

    def isTorment(self, key, netBotches):
        # print('goodNetSuccess: {}'.format(outcome['success'] - netBotches))
        return (key[self.SUCCESS] - netBotches) < key[self.TORMENT] and \
                (key[self.SUCCESS] - netBotches) + key[self.TORMENT] > 0

    def summary(self):
        keys = self.tier.keys()
        botchProb = 0
        tormentProb = 0
        successes = []
        for key in keys:
            # print(key)
            netBotches = max(0, key[self.BOTCH] - self.charmed)
            # print('isTorment: {}'.format(self.isTorment(outcome, netBotches)))
            netSuccesses = max(0,key[self.TORMENT] + key[self.SUCCESS] - netBotches)
            if self.isBotch(key):
                botchProb += self.tier[key]
            if self.isTorment(key, netBotches) and netSuccesses > 0:
                tormentProb += self.tier[key]
            try:
                successes[netSuccesses] += self.tier[key]
            except IndexError:
                successes.extend([0 for _ in range(netSuccesses - len(successes))])
                successes.append(self.tier[key])
        return {
            'botch': botchProb,
            'torment': tormentProb,
            'success': successes,
            'totalFail': botchProb + successes[0],
            'totalSuccess': sum(successes[1:]),
            'expectedSuccesses': sum([i*n for i,n in enumerate(successes)]),
            'charmed': self.charmed,
            'diff': self.diff,
            'pool': self.pool,
            'tormentVal': self.torment,
        }




class Node(object):

    def __init__(self, pool, diff, torment, charmed, path=None):
        self.pool =pool
        self.diff = diff
        self.torment = torment
        self.charmed = charmed
        self.pBotch = .1
        self.pFail = (diff -2) * .1
        self.pTorment = max(0, (torment - diff) * .1)
        self.pSuccess = (1 + (10 - max(torment, diff))) * .1
        if path is None:
            self.path = []
        else:
            self.path = path
        self.children = []
        self.pDict = {
            'botch': self.pBotch,
            'failure': self.pFail,
            'torment': self.pTorment,
            'success': self.pSuccess,
        }
        self.baseBotches = len([x for x in self.path if x=='botch'])
        self.baseFailures = len([x for x in self.path if x=='failure'])
        self.baseTorments = len([x for x in self.path if x=='torment'])
        self.baseSuccesses = len([x for x in self.path if x=='success'])
        self.populate()

    def populate(self):
        if not self.children and self.pool > 1:
            for step in ['botch', 'failure', 'torment', 'success']:
                self.children.append(Node(self.pool-1, self.diff, self.torment,
                                            self.charmed, self.path + [step]))
            for child in self.children:
                child.populate()

    def pathProb(self):
        prob = 1
        for step in self.path:
            prob *= self.pDict[step]
        return prob

    def isLeaf(self):
        return not self.children

    @staticmethod
    def match(step, val):
        return 1 if step==val else 0

    def summary(self):
        if self.isLeaf():
            # print('leaf- {}'.format(self.path))
            paths = []
            for step in ['botch', 'failure', 'torment', 'success']:
                if self.pathProb() * self.pDict[step] > 0.00001:
                    paths.append({
                        'botch': self.baseBotches + self.match(step, 'botch'),
                        'failure': self.baseFailures + self.match(step, 'failure'),
                        'torment': self.baseTorments + self.match(step, 'torment'),
                        'success': self.baseSuccesses + self.match(step, 'success'),
                        'prob': self.pathProb() * self.pDict[step]
                    })
                # print(paths[-1])
            return paths
        else:
            # print('graph- {}'.format(self.path))
            outcomes = []
            for child in self.children:
                outcomes = outcomes + child.summary()
            return outcomes

    def isBotch(self, outcome):
        return outcome['botch'] > self.charmed and outcome['success'] == 0

    def isTorment(self, outcome, netBotches):
        # print('goodNetSuccess: {}'.format(outcome['success'] - netBotches))
        return (outcome['success'] - netBotches) < outcome['torment'] and \
                (outcome['success'] - netBotches) + outcome['torment'] > 0

    def rootSummary(self):
        outcomes = self.summary()
        botchProb = 0
        tormentProb = 0
        successes = []
        for outcome in outcomes:
            # print(outcome)
            netBotches = max(0, outcome['botch'] - self.charmed)
            # print('isTorment: {}'.format(self.isTorment(outcome, netBotches)))
            netSuccesses = outcome['torment'] + outcome['success'] - netBotches
            if self.isBotch(outcome):
                botchProb += outcome['prob']
            if self.isTorment(outcome, netBotches) and netSuccesses > 0:
                tormentProb += outcome['prob']
            try:
                successes[netSuccesses] += outcome['prob']
            except IndexError:
                successes.extend([0 for _ in range(netSuccesses - len(successes))])
                successes.append(outcome['prob'])
        return {
            'botch': botchProb,
            'torment': tormentProb,
            'success': successes,
            'totalFail': botchProb + successes[0],
            'totalSuccess': sum(successes[1:]),
            'expectedSuccesses': sum([i*n for i,n in enumerate(successes)]),
            'charmed': self.charmed,
            'diff': self.diff,
            'pool': self.pool,
            'tormentVal': self.torment,
        }











def roll(dicePool, diff):

    r = Roll(dicePool, diff, PERMENANT_TORMENT, CHARMED)
    print(r.sortedDice)
    print('Successes: %s' % r.successes())
    print('Botches: %s' % r.botches)
    print('Torment: %s' % r.torment())
    print('NetSuccesses: %s' % r.netSuccesses())
    if r.isBotchRoll():
        print('BOTCH!')
    elif r.isTormentRoll():
        print('TORMENT!')

def sim(dicePool, diff):
    sim = RollSim(dicePool, diff, PERMENANT_TORMENT, CHARMED)
    print('Failures: %s - %s%%' % (sim.failures, sim.failurePercent))
    print('Botches: %s - %s%%' % (sim.botches, sim.botchPercent))
    print('Torment: %s - %s%%' % (sim.torment, sim.tormentPercent))
    print('Successes: %s' % str(sim.successes[1:]))
    print('Percent: %s' % ['%s%%' % x for x in sim.successPercent])

    print(sim.expectedSuccesses)

def enhance(dicePool, diff, enhanceNum, maxAddDice=None):
    if maxAddDice is None:
        maxAddDice = dicePool
    maxDicePool = dicePool + maxAddDice
    torment = PERMENANT_TORMENT

    for elvl in range(enhanceNum):
        print('\nEnhance Level: %s' % (elvl +1))
        if diff <= 2 and dicePool < maxDicePool:
            c1 = RollSim(dicePool+1, diff, torment)
            print('dicePool=%s; diff=%s: %s' % (c1.poolSize, c1.diff, c1.expectedSuccesses))
            dicePool +=1
            continue
        elif diff > 2 and dicePool >= maxDicePool:
            c2 = RollSim(dicePool, diff-1, torment)
            print('dicePool=%s; diff=%s: %s' % (c2.poolSize, c2.diff, c2.expectedSuccesses))
            diff -= 1
            continue
        elif diff > 2 and dicePool < maxDicePool:
            c1 = RollSim(dicePool+1, diff, torment)
            print('dicePool=%s; diff=%s: %s' % (c1.poolSize, c1.diff, c1.expectedSuccesses))
            c2 = RollSim(dicePool, diff-1, torment)
            print('dicePool=%s; diff=%s: %s' % (c2.poolSize, c2.diff, c2.expectedSuccesses))
            if c1.expectedSuccesses > c2.expectedSuccesses:
                dicePool += 1
            else:
                diff -= 1
        else:
            print('Max Enhance')
            break


def parseCLI():
    parser = argparse.ArgumentParser()
    parser.add_argument('dice', type=int,
                        help="Number of dice to roll.")
    parser.add_argument('--sim', '-s', action='store_true',
                       help='Monte Carlo roll simulation')
    parser.add_argument('--diff', '-d', type=int, default=6,
                       help='Difficulty of the roll')
    parser.add_argument('--enhance', '-e', type=int, default=None,
                       help='Find optimal enhance plan.')
    return parser.parse_args()


if __name__ == '__main__':
    args = parseCLI()
    dicePool = args.dice
    diff = args.diff
    if args.sim:
        sim(dicePool, diff)
    elif args.enhance:
        enhance(dicePool, diff, args.enhance)
    else:
        roll(dicePool, diff)


