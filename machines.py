import pdb

class Automaton:

    def __init__(self, states = [0],
                       letters = '',
                       trans = {},#(state,letter):[states]
                       start = 0,
                       accepts = [0],
                       regex = ''):

        self.states = states
        self.letters = letters
        self.trans = trans
        self.start = start
        self.accepts = accepts
        self.regex = regex

    def display(self):
        print('states: ', self.states)
        print('letters: ', self.letters)
        print('trans: ')
        t = list(self.trans.items())
        t.sort(key = lambda x: x[0][0]*100 + ord(x[0][1]))
        for i in t:
            print('{} ===> {}'.format(i[0], i[1]))
        print('start: ', self.start)
        print('accepts: ', self.accepts)
        print(self.regex)


    @classmethod
    def letter(cls, letter):


        d = {
             'states':   [0, 1],
             'letters':  letter,
             'trans':    {
                          (0, letter): [1]
                         },
             'start':    0,
             'accepts':   [1],
             'regex': letter,
            }
        return cls(**d)


    def kleene(self):

        start = 0
        letters = ''.join(set(self.letters+'@'))
        msize = len(self.states)
        accept = msize + 1
        states = list(range(msize+2))
        trans = {}
        for src, tar in self.trans.items():
            state, letter = src
            state += 1
            src = (state, letter)
            tar = [x+1 for x in tar]
            trans[src] = tar
        accepts = [accept]
        for ac in self.accepts:
            if not (ac+1, '@') in trans.keys():
                trans[(ac+1, '@')] = []
            trans[(ac+1, '@')].append(accept)
        if not (0, '@') in trans.keys():
            trans[(0, '@')] = []
        trans[(0, '@')].append(1)
        trans[(0, '@')].append(accept)
        trans[(0, '@')] = list(set(trans[0, '@']))
        trans[(0, '@')].sort()
        if not (msize, '@') in trans.keys():
            trans[(msize, '@')] = []
        trans[(msize, '@')].append(1)
        trans[(msize, '@')].append(accept)
        trans[(msize, '@')] = list(set(trans[msize, '@']))
        trans[(msize, '@')].sort()
        accepts = list(set(accepts))
        accepts.sort()

        self.states = states
        self.letters = letters
        self.trans = trans
        self.start = start
        self.accepts = accepts
        self.regex =\
                '({}*)'.format(self.regex)


    def concat(self, other):
        '''
        fix for multiple accepting states in other
        '''
        s_size,o_size = len(self.states),len(other.states)
        start = 0
        #fix for multiple acceptings in other
        accepts = [s_size+o_size-2]
        states = list(range(s_size+o_size-1))
        letters =\
            ''.join(set(self.letters+other.letters))

        #trans = m0['trans'] mutates the argument m0 :(
        trans = {x:y for x,y in self.trans.items()}

        _trans = {(a+s_size-1, b): [x+s_size-1 for x in c]\
                 for (a,b),c in other.trans.items()}

        trans.update(_trans)

        self.states = states
        self.letters = letters
        self.trans = trans
        self.start = start
        self.accepts = accepts
        self.regex =\
                '({}.{})'.format(self.regex, other.regex)


    def union(self, other):

        s_size,o_size = len(self.states),len(other.states)
        start = 0
        letters =\
            ''.join(set(self.letters+other.letters+'@'))
        states = list(range(s_size+o_size+2))
        accepts = [s_size + o_size + 1]
        trans = {}
        for src, tar in self.trans.items():
            state, letter = src
            state += 1
            src = (state, letter)
            trans[src] = [x+1 for x in tar]######
        for src, tar in other.trans.items():
            state, letter = src
            state += (s_size + 1)
            src = (state, letter)
            trans[src] = [x+s_size+1 for x in tar]
        trans[(0, '@')] = [1, s_size + 1]
        trans[(s_size, '@')] = accepts
        trans[(s_size + o_size), '@'] = accepts

        self.states = states
        self.letters = letters
        self.trans = trans
        self.start = start
        self.accepts = accepts
        self.regex =\
                '({}|{})'.format(self.regex, other.regex)



    def letter_closure_(self, state, letter):

        ret = set()
        if (state, letter) in self.trans.keys():
            ret = set(self.trans[(state, letter)])
        return frozenset(ret)



    def letter_closure(self, powstate, letter):

        ret = set()
        for state in powstate:
            ret = ret.union(self.letter_closure_(state,\
                                                 letter))
        return frozenset(ret)



    def ep_closure__(self, state, cum):
        #pdb.set_trace()
        cum = cum.union(set([state]))
        for (st, sym), tar in self.trans.items():
            if sym == '@' and st in cum:
                cum = cum.union(set(tar))
        return cum


    def ep_closure_(self, state):

        cum = set([state])
        comp = set()
        while comp != cum:
            l = cum.difference(comp)
            comp = cum
            for i in l:
                new = self.ep_closure__(i, cum)
                cum = cum.union(new)

        return cum


    def ep_closure(self, powstate):

        ret = set()
        for state in powstate:
            ret = ret.union(self.ep_closure_(state))

        return frozenset(ret)


    def closure(self, powstate, letter):

        symbclosure =\
                self.letter_closure(powstate, letter)
        return self.ep_closure(symbclosure)



    def dfa_states(self):

        start = self.ep_closure(set([0]))
        states = set([start])
        comp = set()
        while comp != states:
            comp = states
            for state in states:
                for symb in self.letters.replace('@',''):
                    newstate = self.closure(state, symb)
                    states = states.union([newstate])
        return frozenset(states)


    def dfa_trans(self):

        states = self.dfa_states()
        trans = {}
        for state in states:
            for symb in self.letters.replace('@', ''):
                tar = self.closure(state, symb)
                trans[(state, symb)] = tar
        return trans


    def nfa_to_dfa(self):


        states = self.dfa_states()
        letters = self.letters
        start = self.ep_closure(set([0]))
        trans = self.dfa_trans()
        accepts = []
        for state in states:
            if self.accepts[0] in state:
                accepts.append(state)

        powdfa = {
                  'states': states,
                  'letters': letters,
                  'trans': trans,
                  'start': start,
                  'accepts': accepts
                 }

        self.states = states
        self.letters = letters
        self.trans = trans
        self.start = start
        self.accepts = accepts


    def renumber_dfa(self):

        changer = {self.start: 0}

        dfas = self.states.difference(\
            frozenset([self.start]))

        z = zip(dfas, range(1, 1 + len(self.states)))
        changer.update(z)

        states = [changer[x] for x in self.states]
        states.sort()

        letters = list(self.letters.replace('@',''))
        letters.sort()
        letters = ''.join(letters)

        trans = { (changer[a], b) : changer[c] for\
                  (a, b), c in self.trans.items() }
        start = 0
        accepts = [changer[x] for x in self.accepts]

        #in case want to produce a new machine?
        ret =   {
                 'states': states,
                 'letters': letters,
                 'trans': trans,
                 'start': start,
                 'accepts': accepts
                }
        self.states = states
        self.letters = letters
        self.trans = trans
        self.start = start
        self.accepts = accepts


    def run(self, st):
        state = self.start
        for l in st:
            state = self.trans.get((state, l))
        return state in self.accepts


    def is_deterministic(self):
        if '@' in self.letters: return False
        return all(len(self.trans[_]) == 1\
                        for _ in self.trans.keys())
