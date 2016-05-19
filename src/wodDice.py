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
         return self.netSuccesses(diff) <= 0 and self.botches > self.charmed

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


