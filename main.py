from string import Template
from io import StringIO
import argparse


# Initializing messages
wrong_msg = 'Wrong. The right answer is'
correct_msg = 'Correct!'
actions = ['add', 'remove', 'import', 'export', 'ask', 'exit', 'log', 'hardest card', 'reset stats']
init_msg = 'Input the action ({}):'.format(', '.join(actions))
card_added = Template('The pair ("$term":"$definition") has been added.')
which_card = 'Which card?\n'
msg01 = f'Input the number of cards:\n'
msg02 = Template('The term for card #$n:\n')
msg03 = Template('The term "$term" already exists. Try again:')
msg04 = Template('The definition for card #$n:\n')
msg05 = Template('The definition "$definition" already exists. Try again:')
msg06 = Template('$count cards have been loaded.')
msg07 = Template('$count cards have been saved.')
msg08 = 'File not found.'
msg09 = 'How many times to ask?\n'
msg10 = 'The card has been removed.'
msg11 = 'File name:'
msg12 = 'The log has been saved.'
msg13 = Template('The hardest card is "$card". You have $n errors answering it')
msg14 = 'The hardest cards are'
msg15 = 'Card statistics have been reset.'
msg16 = 'There are no cards with errors.'
msg17 = Template('Can\'t remove "$card": there is no such card.')
msg18 = 'File name:\n'
msg19 = Template('Print the definition of "$term"\n')
msg20 = Template(f'Wrong. The right answer is $definition, but your definition is correct for $term.')

# Logging and argument initialization
log_file = StringIO()
parser = argparse.ArgumentParser(description='This is a flashcard program.')
parser.add_argument('--import_from', default=None)
parser.add_argument('--export_to', default=None)
args = parser.parse_args()


class Flashcards:
    """
    The generic flashcards root class.
    """
    def __init__(self):
        self.dict = {}
        self.tries = {}

    @staticmethod
    def logger(msg, out=True):
        """

        :param msg: The message to log (input or output)
        :param out: Bool, defaults to True. If False, the message is treated as input from the user
        :return: Nothing by default, the msg if out = False
        """
        if not out:
            log_file.write(f'> {msg}\n')
            return
        log_file.write(f'{msg}\n')
        return msg

    def check_term(self, term):
        """

        :param term: The term to check if it exists in the active dictionary
        :return: True/False
        """
        if term in self.dict:
            return True
        else:
            return False

    def check_def(self, definition):
        """

        :param definition: The definition to check if it exists in the active dictionary
        :return: True/False
        """
        if definition in self.dict.values():
            return True
        else:
            return False

    def reverse_dict(self):
        """

        :return: The active dictionary, reversed
        """
        rdict = {value: key for key, value in self.dict.items()}
        return rdict

    def add_cards(self, no_of_cards=None, term=None, definition=None, hardness=0):
        """

        :param no_of_cards: int: How many cards to add
        :param term: If provided, along with its definition, they will be added
        :param definition: If provided, along with its definition, they will be added
        :param hardness: The number of failed attempts
        :return: True if successful
        """
        n = 0
        # Checks if term: definition pair was provided
        if term is not None and definition is not None:
            self.dict[term] = definition
            self.tries[term] = int(hardness)
            print(self.logger(card_added.substitute(term=term, definition=definition)))
            n += 1
            if no_of_cards is not None:
                if no_of_cards <= n:
                    return True
            else:
                return True

        # Checks if no_of_cards was provided
        if no_of_cards is None:
            no_of_cards = int(input(self.logger(msg01)))
            self.logger(no_of_cards, out=False)

        # Asks for term: definition 'no_of_cards' times
        for p in range(n + 1, int(no_of_cards) + 1):
            term = input(self.logger(msg02.substitute(n=p)))
            self.logger(term, out=False)
            while self.check_term(term):
                print(self.logger(msg03.substitute(term=term)))
                term = input()
                self.logger(term, out=False)
            definition = input(self.logger(msg04.substitute(n=p)))
            self.logger(definition, out=False)
            while self.check_def(definition):
                print(self.logger(msg05.substitute(definition=definition)))
                definition = input()
                self.logger(definition, out=False)
            self.dict[term] = definition
            self.tries[term] = 0
            print(self.logger(card_added.substitute(term=term, definition=definition)))
        return True

    def remove_card(self, rcard=None):
        """

        :param rcard: Card to be removed, defaults to None
        :return: Nothing
        """
        if rcard is None:
            rcard = input(self.logger(which_card))
            self.logger(rcard, out=False)
        if self.check_term(rcard):
            del self.dict[rcard]
            del self.tries[rcard]
            print(self.logger(msg10))
        else:
            print(self.logger(msg17.substitute(card=rcard)))

    def import_cards(self, fname=None):
        """

        :param fname: The file name to import cards from.
        :return: A message with how many cards were added, or an error if the file was not found
        """
        if fname is None:
            fname = input(self.logger(msg18))
            self.logger(fname, out=False)
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                for count, line in enumerate(f):
                    term, definition, hardness = line.rstrip('\n').split(', ')
                    self.add_cards(term=term, definition=definition, hardness=hardness)
            return msg06.substitute(count=count + 1)
        except OSError:
            return msg08

    def export_cards(self, fname=None):
        """

        :param fname: The file name to export cards to. It will overwrite without asking.
        :return: A message with how many cards were exported or False if an error occured.
        """
        if fname is None:
            fname = input(self.logger(msg18))
            self.logger(fname, out=False)
        try:
            with open(fname, 'w', encoding='utf-8') as f:
                for key, value, _key_h, hardness in zip(self.dict.keys(), self.dict.values(), self.tries.keys(),
                                                        self.tries.values()):
                    f.write(key + ', ' + value + ', ' + str(hardness) + '\n')
            return msg07.substitute(count=str(len(self.dict)))
        except ValueError:
            return False

    def hardest(self):
        """

        :return: The card(s) with the most failed attempts, or an error message if none found.
        """
        try:
            max_hardness = max([value for value in self.tries.values()])
            if max_hardness == 0:
                return msg16
        except ValueError:
            return msg16
        hardest_terms = []
        for key, value in self.tries.items():
            if value == max_hardness:
                hardest_terms.append(key)
        if len(hardest_terms) > 1:
            return '{} {}'.format(msg14, *hardest_terms, sep=' ')
        else:
            return msg13.substitute(card=hardest_terms[0], n=max_hardness)

    def play(self, n=None):
        """

        :param n: How many questions to be asked. Will repeat if not enough cards.
        :return: Nothing
        """
        if n is None:
            n = int(len(self.dict))
        rdict = self.reverse_dict()
        counter = 0
        while counter <= n:
            for term, definition in self.dict.items():
                answer = input(self.logger(msg19.substitute(term=term)))
                self.logger(answer, out=False)
                if answer == definition:
                    print(self.logger(correct_msg))
                elif answer in rdict:
                    self.tries[term] += 1
                    print(self.logger(msg20.substitute(definition=definition, term=rdict[answer])))
                else:
                    self.tries[term] += 1
                    print(self.logger(f'{wrong_msg} "{definition}".'))
                counter += 1
                if counter == n:
                    return
        return

    def log(self):
        """
        Will ask for a file name and export all cards on dict to that file.
        :return: Nothing
        """
        fname = input(self.logger(msg11))
        self.logger(fname, out=False)
        with open(fname, 'w', encoding='utf-8') as fn:
            print(log_file.getvalue(), file=fn)
        print(self.logger(msg12))

    def reset_stats(self):
        """
        Will reset all stats (failed attempts) to 0
        :return: A message
        """
        for key in self.tries.keys():
            self.tries[key] = 0
        return self.logger(msg15)

    def start(self):
        if args.import_from is not None:
            print(self.logger(self.import_cards(fname=args.import_from)))
        while True:
            print(self.logger(init_msg))
            action = input()
            self.logger(action, out=False)
            if action not in actions:
                continue
            elif action == 'add':
                self.add_cards(no_of_cards=1)
            elif action == 'remove':
                self.remove_card()
            elif action == 'import':
                print(self.logger(self.import_cards()))
            elif action == 'export':
                print(self.logger(self.export_cards()))
            elif action == 'ask':
                n = int(input(msg09))
                self.logger(n, out=False)
                self.play(n=n)
            elif action == 'log':
                self.log()
            elif action == 'hardest card':
                print(self.logger(self.hardest()))
            elif action == 'reset stats':
                print(self.reset_stats())
            elif action == 'exit':
                if args.export_to is not None:
                    print(self.logger(self.export_cards(args.export_to)))
                print(self.logger('Bye bye!'))
                break


set01 = Flashcards()
set01.start()
