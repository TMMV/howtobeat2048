from lib.logic import up,right,down,left
import random

POSSIBLE_MOVES = [up, right, down, left]

def find_pattern(sequence):
    for i in range(1,int(len(sequence)/2)+1):
        base = sequence[:i]
        fit = len(sequence)/len(base)
        if not fit.is_integer():
            continue
        else:
            fit = int(fit)
        base_sequence = base*fit
        if base_sequence == sequence:
            return base
    return []

def rotate_sequence(seq, times):
    tmp = []
    for move in seq:
        new_index = (POSSIBLE_MOVES.index(move) + times) % len(POSSIBLE_MOVES)
        shifted_move = POSSIBLE_MOVES[new_index]
        tmp.append(shifted_move)
    return tmp

def flip_x(seq):
    tmp = list(seq)
    for index, move in enumerate(tmp):
        if move in [right,left]:
            tmp[index] = move
        else:
            if move == up:
                tmp[index] = down
            else:
                tmp[index] = up
    return tmp

def flip_y(seq):
    tmp = list(seq)
    for index, move in enumerate(tmp):
        if move in [up,down]:
            tmp[index] = move
        else:
            if move == right:
                tmp[index] = left
            else:
                tmp[index] = right
    return tmp

def mutation_swap(seq):
    idx = range(len(seq))
    i1, i2 = random.sample(idx, 2)
    seq[i1], seq[i2] = seq[i2], seq[i1]

def mutation_mutate(seq):
    index = random.randint(0,len(seq)-1)
    to_replace = seq[index]
    seq[index] = random.choice([x for x in POSSIBLE_MOVES if x != to_replace])

def mutation_insertion(seq):
    index = random.randint(0,len(seq))
    to_insert = random.choice(POSSIBLE_MOVES)
    seq.insert(index, to_insert)

def mutation_deletion(seq):
    index = random.randint(0,len(seq)-1)
    seq.pop(index)

from lib.logic import up,right,down,left

class Strategy:
    def __init__(self, sequence, how_to_unstuck):
        self.tries = 0
        self.sequence = sequence
        self.stuck_sequence = how_to_unstuck
        self.current_index = 0
        self.stuck_index = 0
        self.is_stuck = False
        self.score = 0
        self.results = []

    def next(self):
        if self.tries == len(self.sequence):
            self.is_stuck = True
            self.stuck_index = 0

        self.tries += 1

        if self.is_stuck:
            return self.save_me_from_being_stuck()
        else:
            return self.normal_move()

    def normal_move(self):
        if self.current_index >= len(self.sequence) - 1:
            self.current_index = 0
        else:
            self.current_index += 1

        return self.sequence[self.current_index]

    def save_me_from_being_stuck(self):
        save_sequence = self.stuck_sequence
        if not save_sequence:
            random_sequence = [move for move in POSSIBLE_MOVES if move not in self.sequence]
            random.shuffle(random_sequence)
            save_sequence = random_sequence

        if self.stuck_index == len(save_sequence) - 1:
            self.stuck_index = 0
        else:
            self.stuck_index += 1
        return save_sequence[self.stuck_index]

    def is_valid(self):
        if not self.stuck_sequence: # random unstuck always works
            return True
        # otherwise we need to cover all possible moves
        return len(set(self.sequence + self.stuck_sequence)) == 4

    def successful_move(self):
        self.tries = 0
        self.is_stuck = False
        self.stuck_index = 0

    def compress(self):
        # find pattern and compress up,down,up,down = up,down
        cycle = find_pattern(self.sequence)
        if cycle:
            self.sequence = cycle
        # this won't happen for the stuck sequence since we are dealing with permutations on that one

        # up,down,left [down,left,right,up] = up,down,left [right]
        self.stuck_sequence = [move for move in self.stuck_sequence if move not in self.sequence]

        # up,down,left [right,right] = up,down,left [right]
        tmp_seq = []
        for move in self.stuck_sequence:
            if move not in tmp_seq:
                tmp_seq.append(move)
        self.stuck_sequence = tmp_seq

        # - [up,right,down,left] = up [right,down,left]
        if not self.sequence and self.stuck_sequence:
            self.sequence = [self.stuck_sequence[0]]
            self.stuck_sequence.pop(0)

    def store_results(self, results):
        self.results += results

    def compute_score(self):
        self.score = sum(self.results)/len(self.results)

    def set_parent_generation(self, generation):
        self.parent_generation = generation

    def mutate(self, max_sequence_size):
        before_mutation = Strategy(list(self.sequence),list(self.stuck_sequence))
        # chance of swap
        SEQUENCE_SWAP_CHANCE = 0.20
        STUCK_SWAP_CHANCE = 0.1
        # chance of mutate
        SEQUENCE_MUTATE_CHANCE = 0.20
        STUCK_MUTATE_CHANCE = 0.1
        # chance of insertion
        SEQUENCE_INSERTION_CHANCE = 0.10
        STUCK_INSERTION_CHANCE = 0.05
        # chance of deletion
        SEQUENCE_DELETION_CHANCE = 0.10
        STUCK_DELETION_CHANCE = 0.05

        mutation_tries = 0
        while self == before_mutation and mutation_tries < 100:
            mutated_self = Strategy(list(self.sequence),list(self.stuck_sequence))
            while len(mutated_self.sequence) > 1 and random.random() < SEQUENCE_SWAP_CHANCE:
                mutation_swap(mutated_self.sequence)
            while len(mutated_self.stuck_sequence) > 1 and random.random() < STUCK_SWAP_CHANCE:
                mutation_swap(mutated_self.stuck_sequence)

            while len(mutated_self.sequence) > 0 and random.random() < SEQUENCE_MUTATE_CHANCE:
                mutation_mutate(mutated_self.sequence)
            while len(mutated_self.stuck_sequence) > 0 and random.random() < STUCK_MUTATE_CHANCE:
                mutation_mutate(mutated_self.stuck_sequence)

            while len(mutated_self.sequence) < max_sequence_size and random.random() < SEQUENCE_INSERTION_CHANCE:
                mutation_insertion(mutated_self.sequence)
            while len(mutated_self.stuck_sequence) < max_sequence_size and random.random() < STUCK_INSERTION_CHANCE:
                mutation_insertion(mutated_self.stuck_sequence)

            while len(mutated_self.sequence) > 0 and random.random() < SEQUENCE_INSERTION_CHANCE:
                mutation_deletion(mutated_self.sequence)
            while len(mutated_self.stuck_sequence) > 0 and random.random() < STUCK_INSERTION_CHANCE:
                mutation_deletion(mutated_self.stuck_sequence)

            mutated_self.compress()

            if mutated_self.is_valid() :
                self.sequence = mutated_self.sequence
                self.stuck_sequence = mutated_self.stuck_sequence

            mutation_tries += 1


    def __eq__(self, other):
        # assumes isvalid and compress have been run beforehand
        if len(self.sequence) != len(other.sequence):
            return False

        if len(self.stuck_sequence) != len(other.stuck_sequence):
            return False

        is_same_sequence = False
        for rotation in range(0,4):  # rotation symmetry
            for do_flip_x in [False,True]:  # flip on x axis
                for do_flip_y in [False,True]:  # flip on y axis
                    new_sequence = rotate_sequence(other.sequence, rotation)
                    if do_flip_x:
                        new_sequence = flip_x(new_sequence)
                    if do_flip_y:
                        new_sequence = flip_y(new_sequence)

                    if new_sequence == self.sequence:
                        is_same_sequence = True
                        break

        is_same_stuck_sequence = False
        for do_flip_x in [False,True]:  # flip on x axis
            for do_flip_y in [False,True]:  # flip on y axis
                new_sequence = list(other.stuck_sequence)
                if do_flip_x:
                    new_sequence = flip_x(new_sequence)
                if do_flip_y:
                    new_sequence = flip_y(new_sequence)

                if new_sequence == self.stuck_sequence:
                    is_same_stuck_sequence = True
                    break

        if is_same_stuck_sequence and is_same_sequence:
            return True

        return False

    def __str__(self):
        def pretty_print_sequence(sequence):
            moves = []
            for move in sequence:
                if move == up:
                    moves.append('up')
                elif move == down:
                    moves.append('down')
                elif move == left:
                    moves.append('left')
                elif move == right:
                    moves.append('right')
            return ', '.join(moves)

        generation_text = ''
        if getattr(self, 'parent_generation', None) is not None:
            generation_text = ' [' + getattr(self, 'parent_generation') + ']'

        return pretty_print_sequence(self.sequence) + ' [' + \
                pretty_print_sequence(self.stuck_sequence) + '] (' + str(int(self.score)) + ')' \
                + generation_text
