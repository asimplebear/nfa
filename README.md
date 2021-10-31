# nfa
main.py prompts for a gegular expression using lower case letters and 0 and 1 for letters and * for kleene closure and | for union and just juxtapostion for concatenation.  It uses shuntyard algorithm to parse it and then makes an nfa for that regular expression and uses power set construction to convert to a dfa that can then run on words to either accept or reject.
