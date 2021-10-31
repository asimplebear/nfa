from machines import Automaton as A
import pdb

#kleene star, union and concatenation
operators = '*|.'
letters = '01abcdefghijklmnopqrstuvwxyz'

bad_char_error = '''
The char {{}} is neither letter, operator \
nor parenthesis.  Letters come from {} and \
operators are "*" (kleene star), "|" (union) \
and no char for concatenation.
'''.format(letters)



#these symbols can open/close
#a complete expression
opening = letters + '('
closing = letters + ')*'


def tokenizer(st):

    #did the last token end a
    #complete expression?
    completed = False
    for t in st:
        #juxtaposition of complete
        #expressions is construed
        #as concatenation
        if completed and t in opening:
            yield '.'
        #did this token end a
        #complete expression?
        completed = t in closing
        yield t


def shuntyard(tokens):

    #output and operator stacks
    outstack, opstack = [], []

    for token in tokens:

        #letters always go to output stack
        if token in letters:
            outstack.append(token)

        #open parens go to operator stack
        #to await next matching close paren
        #between is a complete expression
        #and will pop off as such
        elif token == '(':
            opstack.append(token)

        #close parens means everything on
        #operator stack above the matching
        #open parens is self contained
        #priority.  push to output stack
        #as if it were a single expression
        elif token == ')':
            while opstack[-1] != '(':
                outstack.append(opstack.pop())
            #get rid of original open paren
            opstack.pop()

        #kleene star is right unary highest
        #priority. send it directly to output
        #stack to bind with a completed
        #expression i.e a letter or
        #something in parens
        elif token == '*':
            outstack.append('*')

        #concatenation has higher priority
        #than union.  it does not have to
        #wait for anything to go from operator
        #stack to output stack
        elif token == '.':
            opstack.append(token)

        #union has lowest priority of anything
        #on the operator stack.
        elif token == '|':
            #so if the operator stack has
            #higher priority op (ie .) then
            #pop the operator stack to the output
            #until no . is there
            while opstack and opstack[-1] == '.':
                outstack.append(opstack.pop())
            #only then push the |
            opstack.append(token)

        else:
            assert False, bad_char_error.format(token)


    #empty operation stack into ouput stack
    while opstack:
        outstack.append(opstack.pop())

    return outstack


def resolve_to_nfa(regex):

    try:
        stack = shuntyard(tokenizer(regex))
    except IndexError:
        assert False, "shuntyard probably tried to pop empty stack"


    if not stack:
        return A()

    calcstack = []

    stack.reverse()

    while stack:

        item = stack.pop()

        if item in letters:
            mach = A.letter(item)
            calcstack.append(mach)

        elif item == '*':
            a = calcstack.pop()
            a.kleene()
            calcstack.append(a)

        elif item == '.':
            a, b = calcstack.pop(), calcstack.pop()
            b.concat(a)
            calcstack.append(b)

        elif item == '|':
            a, b = calcstack.pop(), calcstack.pop()
            b.union(a)
            calcstack.append(b)
        else:
            assert False,\
            "'{}' was found on output stack of shuntyard"\
                    .format(item)

    assert len(calcstack) == 1,\
            'problem: calcstack was {}'.format(calcstack)

    return calcstack.pop()

