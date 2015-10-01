'''
Created on 30 Sep 2015

@author: tobydobbs
'''

import random

#===============================================================================
# Population: A group of individuals
#===============================================================================
class Population:
    
    def __init__(self):
        self.members = []
        self.popSize = 0
        
    def addMember(self, individual):
        self.popSize += 1
        self.members.append(Individual(individual, self.popSize))
        
    def genRandomMember(self):
        genome = ""
        bins = [0, 1]
        i = 0
        while i < 8:
            genome += str(random.choice(bins))
            i += 1
        self.popSize += 1
        self.members.append(Individual(genome, self.popSize))
        
    def genRanPop(self, size):
        while size > 0:
            self.genRandomMember()
            size = size - 1
        self.updatePop()
        
    def updatePop(self):
        self.sbf(0, len(self.members) - 1) # sort the list by rank in descending order
        self.assignRanks() # assign ranks to each item
        self.assignProbs() # assign probabilities for crossover 
        
    def printPop(self):
        print ("The current population contains:\n" + str(self.members)
               + "\nThe ranks amount to: " + str(self.F)
               + "\nThe number of items in the array is: " + str(len(self.members))
               + "\nThe mean fitness value is: " + str(self.meanFitness()) + "\n")
        
    #===========================================================================
    # sbf: used to sort the members of the population by fitness, therefore providing rank
    # the first element in the list will be the fittest and therefore the top rank (which is 0 in this case)
    #===========================================================================
    def sbf(self, lo, hi):
        if lo < hi:
            p = self.partition(lo, hi)
            self.sbf(lo, p - 1)
            self.sbf(p + 1, hi)

    def partition(self, lo, hi):
        wall = lo
        pivot = hi
        for i in range(lo, hi):
            if self.members[i].fitness < self.members[pivot].fitness:
                self.swap(wall, i)
                wall += 1 # move the wall up one space
        self.swap(wall, hi)
        return wall  

    def swap(self, i, j):
        temp = self.members[i]
        self.members[i] = self.members[j]
        self.members[j] = temp
        
    def assignRanks(self):
        self.F = 0
        for i in range(len(self.members)):
            self.members[i].assignRank(i+1)
            self.F += self.members[i].rank
            
    def assignProbs(self):
        for i in range(len(self.members)):
            if i == 0:
                self.members[i].assignProb(self.F);
            else:
                self.members[i].assignProb(self.F, self.members[i-1]);
    
    def meanFitness(self):
        totalFitness = 0
        for m in self.members:
            totalFitness += m.fitness
        return float(totalFitness) / len(self.members)
                
        
#===============================================================================
# Individual: A genome that exists as part of a population of prospective solutions
#===============================================================================
class Individual:
    
    def __init__(self, genome, idNo = 0):
        self.genome = genome
        self.evalFitness()
        self.id = idNo 
        self.rank, self.prob = None, None
        
    def evalFitness(self):
        self.fitness = int(self.genome, 2)
        
    def getFitness(self):
        print "Fitness of individual " + str(self.id) + ": " + str(self.fitness)
        
    def assignRank(self, rank):
        self.rank = rank
        
    def assignProb(self, divisor, prev = None):
        if prev != None:
            self.prob = prev.prob + float(self.rank) / divisor
        else:
            self.prob = float(self.rank) / divisor
        
    def mutate(self):
        randex = random.randint(0,7)
        toMutate = list(self.genome)
        if toMutate[randex] == "0":
            toMutate[randex] = "1"
        else:
            toMutate[randex] = "0"
        self.genome = "".join(toMutate)
        self.evalFitness()
        
    def __repr__(self):
        return ("{ id: " + str(self.id) 
                + ", genome: " + str(self.genome) 
                + ", fitness: " + str(self.fitness) 
                + ", rank: " + str(self.rank)
                + ", prob: " + str(self.prob) + " }")
        
def breed(pop):
    parents = []
    limit = (len(pop.members) - 1) * 2
    for i in range(limit):
        parents.append(rouletteSelect(pop.members))
        
    pairs = []
    i = 0
    while i < (limit - 1):
        parent1 = random.choice(parents)
        parent2 = random.choice(parents)
        pairs.append((parent1, parent2))
        i += 2
        
    children = vary(pairs) # get the mutated children of the parents
    chindividuals = [] # apologies for this terrible, terrible name
    for child in children:
        chindividuals.append(Individual(child))     
    
    return nextGen(pop, chindividuals)

#===============================================================================
# nextGen: Breed next generation, keep the best of previous
#===============================================================================
def nextGen(current, new):
    nex = Population()
    strongest = current.members[len(current.members) - 1]
    # print "strongest: " + str(strongest.genome)
    nex.addMember(strongest.genome)
    for n in new:
        nex.addMember(n.genome)
    return nex
    
def vary(breeders):
    children = []
    for pair in breeders:
        parent1 = list(pair[0].genome)
        parent2 = list(pair[1].genome)
        child = []
        xover = random.randint(0, len(parent1) - 1)
        for i in range(xover):
            child.append(parent1[i])
        for i in range(xover, len(parent1)):
            child.append(parent2[i])
        children.append(mutate(child))
    return children
    
#===============================================================================
# mutate: swap mutation by selecting two distinct genes and simply swapping their places
#===============================================================================
def mutate(child):
    i = random.randint(0, len(child) - 1)
    j = random.randint(0, len(child) - 1)
    while j == i:
        j = random.randint(0, len(child) - 1)
    monster = list(child) # November spawned a monster
    temp = monster[i]
    monster[i] = monster[j]
    monster[j] = temp
    return "".join(monster)
    
#===============================================================================
# returns the randomly selected value
#===============================================================================
def rouletteSelect(members):
    weight_sum = 0
    for i in range(len(members)):
        weight_sum += members[i].prob
    value = random.random() * weight_sum
    for i in range(len(members)):
        value = value - members[i].prob
        if value <= 0:
            return members[i]
    return members[len(members) - 1]
    
CB = Population()
CB.genRanPop(100) # Generate a random population of individuals and evaluate their fitnesses, they are ranked auto
CB.printPop()

i = 0
while i < 100:
    new = breed(CB)
    new.updatePop()
    if i % 10 == 0:
        new.printPop()
    i += 1
new.printPop()

        
