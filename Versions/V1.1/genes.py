# ficher gérant le genome de l'otus

import random as rd

from lifeLimits import life_limits


# les quetres bases constituant l'adn de l'otus
bases = {"A": 0,
         "T": 1,
         "C": 2,
         "G": 3}

gene_size = 8


class Genome:

    def __init__(self, otus, parents=None):

        self.otus = otus

        self.gene_number = 12

        if parents is None:

            self.sequence = ""

            for j in range(self.gene_number):

                for i in range(gene_size):

                    self.sequence += rd.choice(list(bases.keys()))

        else:

            self.sequence = ""

            for i in range(self.gene_number):

                parentseq = [parents[0].genome.sequence[i*8:(i+1)*8], parents[1].genome.sequence[i*8:(i+1)*8]]

                self.sequence += rd.choice(parentseq)

            self.sequence = mutate(self.sequence, parents[0].genome.mutationrate)

        self.mutationrate = decrypt(self.sequence[88:96], life_limits["mutation rate"])


def mutate(seq, probability):
    newseq = list(seq)

    for i in range(len(seq)):
        if rd.random() < probability:

            newseq[i] = rd.choice(list(bases.keys()))

    newseq = "".join(newseq)

    return newseq


# fonction servant à convertir une séquence en valeur numérique
def decrypt(seq, limits):

    factor = len(bases) - 1

    value = 0
    for i in range(len(seq)):
        value += bases[seq[len(seq) - i - 1]] * factor ** i

    max_value = (factor**len(seq) - 1) * factor / 2

    return value/max_value * (limits[1]-limits[0]) + limits[0]



