#This is the real real world.

import sys
sys.path.append("../")
import random
from utils import read_dataset
import numpy as np

class Thing(object):
    '''A thing has an ID (a string variable), a kind (a string) and
    some information about which attributes it has, and in which scenes
    it occurs.'''
    def __init__(self, ID, attributes):
        self.ID = ID
        self.attributes = attributes
        self.scenes = []

class Scene(object):
    '''A scene has an ID and involves a number of things.'''
    def __init__(self, ID):
        self.ID = ID
        self.things = []
            

class World(object):
    '''The following are utility functions to generate a world.'''
    
    def check_incompatibilities(self,thing,attribute):
        incompatible = False
        colours = ["is_black", "is_blue", "is_brown", "is_emerald", "is_grey", "is_indigo", "is_red", "is_yellow", "is_silvery"]
        if attribute in colours and any(c in thing.attributes for c in colours):
            incompatible = True
        return incompatible


    def sample_thing(self,ID,kinds):
        kind = random.choice(kinds.keys())
        x = Thing(ID,[kind])
        for k,v in kinds[kind].items():
            has_attribute = np.random.binomial(1,v)
            if has_attribute == 1 and not self.check_incompatibilities(x,k[:-2]):
                x.attributes.append(k)
        return x
    
    def sample_scene(self,ID, things):
        s = Scene(ID) 
        n = random.randint(1,min(10,len(things)))
        sampled_things = random.sample(things, n)
        for thing in sampled_things:
            s.things.append(thing.ID)
        return s

    '''A world is a set of things and scenes.'''
    def __init__(self, probability_file, num_entities, num_scenes):
        self.things = []
        self.scenes = []

        '''Record probability data to generate the world'''
        kinds, vocabulary = read_dataset(probability_file)

        '''Produce all instances in this world.'''
        for n in range(num_entities):
            x = self.sample_thing("x"+str(n),kinds)
            self.things.append(x)

        '''Produce all scenes for this world.'''
        for n in range(num_scenes):
            s = self.sample_scene("S"+str(n),self.things)
            for thing in self.things:
                thing.scenes.append(s.ID)
            self.scenes.append(s)

        '''Record world'''
        world_file=open("./data/world.txt",'w')
        for e in self.things:
            for a in e.attributes:
                for s in e.scenes:
                    world_file.write(e.ID+","+a+","+s+"\n")
        world_file.close()


