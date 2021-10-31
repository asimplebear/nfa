#!/usr/bin/python3

from parser import resolve_to_nfa

instructions = '''
When prompted enter a regular expression using \
letters from "01abcdefghijklmnopqrstuvwxyz" with \
operators "*" for kleene closure, "|" for union and \
juxtaposition for concatenation.  Then when prompted \
for a word enter a word and see if the word is in the \
language of the regular expression.  Type '!' to break \
out of any prompt.
'''

print(instructions)

while __name__ == "__main__":

    regex = input('regex: ')
    if regex == '!':
        break

    try:
        machine = resolve_to_nfa(regex)
    except AssertionError as e:
        print(e)
        continue

    print('\n{} is the same as {}\n'.\
            format(regex, machine.regex))
    print('an nfa for {} is:'.format(regex))
    machine.display()
    machine.nfa_to_dfa()
    machine.renumber_dfa()
    print('\na dfa for {} is:'.format(regex))
    machine.display()

    while True:
        word = input('word: ')
        if word == '!': break
        if machine.run(word):
            x = 'accepted'
        else:
            x = 'rejected'
        print("'{}' {} {}".format(regex, x, word))
