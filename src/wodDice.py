"""
Module to roll and calculate the probability for dice pools in
White Wolf's Demon: The Fallen.
"""

import random


class D10(object):
    """
    Single roll of a single D10.
    """
    def __init__(self):
        self.roll = random.randint(1,10)

    @property
    def botch(self):
        """@returns: bool -- the roll is a botch"""
        return self.roll == 1

    def success(self, diff):
        """@returns: bool -- the roll is a success"""
        return self.roll >= diff

    def torment(self, diff, pTorment):
        """@returns: bool -- the roll is a tormented success"""
        return self.success(diff) and self.roll < pTorment


class Roll(object):
    """
    A single roll of a dice pool.
    """
    def __init__(self, poolSize, diff, pTorment, charmed=0):
        """
        Roll of a dicepool.
        @param poolSize: int -- size of pool to roll
        @param diff: int -- difficulty of the roll
        @param pTorment: int -- permanent torment. If more than half of
                    successses are below this number the roll is tormented.
        @param charmed: int -- level of charmed existence; I don't know
                    a way to get more than one, but just in case.
        """
        self.poolSize = poolSize
        self.diff = diff
        self.pTorment = pTorment
        self.charmed = charmed
        self.dice = []
        for _ in range(self.poolSize):
            self.dice.append(D10())


    @property
    def sortedDice(self):
        """
        Sort the dice from high to low.

        @return: sorted list of D10 objects.
        """
        return sorted([x.roll for x in self.dice], reverse=True)


    def successes(self, diff=None):
        """
        Number of successes without considering botches.

        @diff: int: difficulty of the roll.

        @return: int -- Total number of successful D10s.
        """
        if not diff:
            diff = self.diff
        total = 0
        for die in self.dice:
            if die.success(diff):
                total += 1
        return total

    def torment(self, diff=None, pTorment=None):
        """
        Number of tormented successes.

        @diff: int -- difficulty of the roll.
        @pTorment: int -- permanent torment.

        @return: int -- Total number of tormented D10s.
        """
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
        """
        Number of botches.

        @return: int -- Total number of botched D10s.
        """
        total = 0
        for die in self.dice:
            if die.botch:
                total += 1
        return total

    def netSuccesses(self, diff=None):
        """
        Number of successes when considering botches.

        @diff: int: difficulty of the roll.

        @return: int -- Total number of successful D10s minus
                    total number of botches.  Botches is adjusted
                    by level of charm if any.
        """
        return self.successes(diff) - max(0, (self.botches - self.charmed))

    def isBotchRoll(self, diff=None):
        """
        Whether the roll as a hole is botched (No successes and at least
                one more botched die than  levels of charmed).

        @diff: int: difficulty of the roll.

        @return: bool -- True if the roll is botched.
        """
        return self.successes(diff) <= 0 and self.botches > self.charmed

    def isTormentRoll(self, diff=None, pTorment=None):
        """
        Whether the roll as a hole is tormented (Successful and more
            tormented dice than untormented successes.  botches
            remove from untormented successes first).

        @diff: int: difficulty of the roll.
        @pTorment: int -- permanent torment.

        @return: bool -- True if the roll is tormented.
        """
        if self.netSuccesses(diff) > 0:
            return self.torment(diff, pTorment) > self.netSuccesses(diff)/2
        else:
            return False


class PoolCalc(object):
    """
    calculate probabilities of the dice pool.
    """
    BOTCH = 0
    FAIL = 1
    TORMENT = 2
    SUCCESS = 3

    def __init__(self, pool, diff, torment, charmed):
        """
        @param poolSize: int -- size of pool to roll
        @param diff: int -- difficulty of the roll
        @param pTorment: int -- permanent torment. If more than half of
                    successses are below this number the roll is tormented.
        @param charmed: int -- level of charmed existence; I don't know
                    a way to get more than one, but just in case.
        """
        self.pool =pool
        self.diff = diff
        self.torment = torment
        self.charmed = charmed
        self.tier = {(0,0,0,0): 1.0}  # See populate()

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
        """
        Iteratively calculate the probability of each die.
        This builds a quasi tree that collapses any effectively
        identical branches.  Thus a branch that rolled a botch
        and then a success is merged with a branch that rolled a
        success and then a botch.

        The leaf nodes are stored as the self tier dict.

        The key is a four element tuple:

            (numBotches, numFailures, numTorments, numSuccesses)

        While botches and torments are respectively failures and
        successes, for the purpose of the key all categories are
        mutually exclusive.

        The value is the probability of that outcome.
        """
        for _ in range(self.pool):
            newTier = {}
            for key, baseProb in self.tier.items():
                for branch in range(4):
                    newProb = baseProb * self.pDict[branch]
                    if newProb == 0.0:
                        continue
                    newKey = list(key[:])  # make a mutable copy of the key
                    newKey[branch] += 1
                    newKey = tuple(newKey) # make it hashable again
                    newTier[newKey] = newTier.get(newKey, 0.0) + newProb
            self.tier = newTier
            # print(self.tier)

    def isBotch(self, key):
        """
        Check if the key is a botched roll.

        @param key: tuple -- The key to check to see if it is a botched roll.

        @returns: bool -- Returns true if the key represent  a
                botched roll.
        """
        return key[self.BOTCH] > self.charmed and key[self.SUCCESS] == 0

    def isTorment(self, key, netBotches):
        """
        Check if the key is a tormented roll.

        @param key: tuple -- The key to check to see if it is a tormented roll.

        @returns: bool -- Returns true if the key represent  a
                tormented roll.
        """
        return (key[self.SUCCESS] - netBotches) < key[self.TORMENT] and \
                (key[self.SUCCESS] - netBotches) + key[self.TORMENT] > 0

    def summary(self):
        """
        Iterate over all the the outcomes in the dice pool and
        calculate probabilities of botch, torment, failure, success
        levels.

        @returns: dict -- calculated probabilities.
        """
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


