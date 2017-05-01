# IdealWords
[![Code Quality][quality-image]][quality-url]


This repo will contain code to generate mini-worlds and simulate some speakers
experiencing a number of situations in those worlds, and talking about them.

This is work in progress! Current project status is to be found below.

### Current status

Run with

python ./mk_world.py

The program will:

*    create a world
*    create situations in that world
*    sample situations that speaker S1 has experienced
*    make speaker S1 utter some simple sentences about those situations
*    make speaker S2 listen
*    make speaker S2 perform a mapping between things they have heard and things they know, as expressed in vector form.

WARNING: at this time (May 1st, 2017), the mapping (linear regression) is bugged!

[quality-image]:https://img.shields.io/codeclimate/github/minimalparts/IdealWords.svg?style=flat-square
[quality-url]:https://codeclimate.com/github/minimalparts/IdealWords
