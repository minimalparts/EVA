import random
import numpy as np

class Entity(object):

    def __init__(self, name, species, features):
        self.name = name
        self.species = species
        self.features = features

class Situation(object):

    def __init__(self, ID, entities):
        self.ID = ID
        self.entities = entities

class World(object):

    def __init__(self, situations):
        self.situations = situations

def check_incompatibilities(animal,feature):
  incompatible = False
  colours = ["is_black", "is_blue", "is_brown", "is_emerald", "is_grey", "is_indigo", "is_red", "is_yellow", "is_silvery"]
  if feature in colours and any(c in animal.features for c in colours):
    incompatible = True
  return incompatible

def sample_animal(name,animals):
  animal = random.choice(animals.keys())
  x = Entity(name,animal,[])
  
  for k,v in animals[animal].items():
     has_feature = np.random.binomial(1,v)
     if has_feature == 1 and not check_incompatibilities(x,k):
       x.features.append(k)

  #print x.name, x.species, x.features
  return x


def sample_situation(ID, animal_entities):
  s = Situation(ID, []) 
  n = random.randint(1,10)
  sampled_animals = random.sample(animal_entities, n)
  for animal in sampled_animals:
    s.entities.append(animal)
  return s
