import numpy as np


# path to saved dictionary
fp = './mmodel_dictionary.npy'

# load the dictionary
d = np.load(fp).item()

# first level
print 'Top level is accessed by name of each tool: d.keys() ='
print d.keys()
print

# second level
print 'The next level is for each analysis tool (radon, pylint, metrix):'
print "e.g., d['DTK'].keys() =", d['DTK'].keys()
print 'NOTE: an entry will exist only if that tool was run:'
print "\tOpenMI has nothing (for some reason...): d['OpenMI'] =", d['OpenMI']
print "\tAiiDA only has radon: d['AiiDA'].keys() =", d['AiiDA'].keys()
print

# third level
print 'Each analysis tool has its own structure from here on out:'
print "\tRadon: has a key for each .py file and a total, e.g. d['DTK']['radon'].keys() =", d['DTK']['radon'].keys()
print "\t'total' contains d['DTK']['radon']['total'].keys() =", d['DTK']['radon']['total'].keys()
print "\tEach of the above keys should produce a value."
print
print "\tPyLint:  has a key for every .py file, e.g. d['DTK']['pylint'].keys() =", d['DTK']['pylint'].keys()
print "\t'conf.py' contains d['DTK']['pylint']['conf.py'].keys() =", d['DTK']['pylint']['conf.py'].keys()
print "\tPyLint is the trickiest as each of the above keys corresponds to a table, which has its own keys..."
print "\tI recommend just playing around a bit, e.g.:"
print "\t\td['DTK']['pylint']['conf.py']['regions'].keys() =", d['DTK']['pylint']['conf.py']['regions'].keys()
print "\t\td['DTK']['pylint']['conf.py']['regions']['function'].keys() =", d['DTK']['pylint']['conf.py']['regions']['function'].keys()
print "\t\td['DTK']['pylint']['conf.py']['regions']['function']['number'] =", d['DTK']['pylint']['conf.py']['regions']['function']['number']
print "\tWe had to go pretty deep to get that 0, but you get the idea."
print
print "\tMetrixPP: has a key for each parameter d['DTK']['metrix'].keys() ="
print '\t', d['DTK']['metrix'].keys()
print '\tEach of the above keys should contain values for "average" and "total".'
