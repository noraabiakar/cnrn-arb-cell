from neuron import h
import numpy as np
import time as cookie
import pylab as plt
import pickle
import json
import sys
import copy
import json_reader as loader

h.load_file("stdrun.hoc")
h.load_file('import3d.hoc')

with open(sys.argv[1]) as json_file:
    defaults = json.load(json_file)

with open(sys.argv[2]) as json_file:
    cells = json.load(json_file)

default_file = sys.argv[1]
cell_file    = sys.argv[2]

# Class to create cell from swc
swc = sys.argv[3]
class cell():
  def __init__(self, fname):
    self.fname = fname
    self.load_morphology()
  def load_morphology(self):
    cell = h.Import3d_SWC_read()
    cell.input(self.fname)
    i3d = h.Import3d_GUI(cell, 0)
    i3d.instantiate(self)
  def __str__(self):
    return 'Cell'

# Creat cell and region map
c = cell(swc)

# Create region map
region_map = {"all" : c.all}
if (hasattr(c, "soma")): 
  region_map["soma"] = c.soma
if (hasattr(c, "dend")): 
  region_map["dend"] = c.dend
if (hasattr(c, "apic")): 
  region_map["apic"] = c.apic
if (hasattr(c, "axon")): 
  region_map["axon"] = c.axon

# load parameters
local_param_dict = loader.load_param_dict(default_file, cell_file)
local_ion_dict   = loader.load_ion_dict(default_file, cell_file)
method_dict      = loader.load_method_dict(default_file, cell_file)
mechanism_dict   = loader.load_mechanism_dict(cell_file)

# Paint region mechanisms
for mech_desc in mechanism_dict: 
  region = mech_desc["region"]
  mech   = mech_desc["mechanism"]
  params = mech_desc["parameters"]

  translated_params = {}
  for p in params: 
    translated_params[p + "_" + mech] = params[p]
    
  for sec in region_map[region]:
    sec.insert(mech) 
    for p in translated_params: 
      setattr(sec, p, translated_params[p])

# Set region properties
region_map.pop("all")
for region in region_map: 
  for sec in region_map[region]:
    sec.cm = local_param_dict[region]["cm"]
    print(sec, "cm", sec.cm)
    sec.Ra = local_param_dict[region]["Ra"]
    print(sec, "Ra", sec.Ra)
    for ion in local_ion_dict[region]:
      iconc = ion+"i"
      econc = ion+"o"
      revpot = "e"+ion
      if hasattr(sec, iconc):
        setattr(sec, iconc, local_ion_dict[region][ion]["iconc"])
        print(sec, ion, "iconc", getattr(sec, iconc))
      if hasattr(sec, econc):
        setattr(sec, econc, local_ion_dict[region][ion]["econc"])
        print(sec, ion, "econc", getattr(sec, econc))
      if hasattr(sec, revpot):
        setattr(sec, revpot, local_ion_dict[region][ion]["revpot"])
        print(sec, ion, "revpot", getattr(sec, revpot))
  print()

# Set ion methods 
for ion in method_dict:
  ion_name = ion + "_ion"
  if method_dict[ion] == "nernst":
    h.ion_style(ion_name, 3, 2, 1, 1, 1)
  elif method_dict[ion] == "constant":
    h.ion_style(ion_name, 3, 2, 0, 0, 1)
  else: 
     raise Exception("Only allowed ion methods are \"nernst\" and \"constant\"")

# Set nseg
for sec in c.all: 
  n = int(sec.L//0.5)
  print(n)
  sec.nseg = n

# Set model properties after checking consistency
global_vm = local_param_dict["all"]["Vm"]
global_temp = local_param_dict["all"]["celsius"]

for region in local_param_dict:
  if local_param_dict[region]["Vm"] != global_vm: 
     raise Exception("Neuron doesn't allow inconsistent initial membrane voltage across different regions of a cell")
  if local_param_dict[region]["celsius"] != global_temp: 
     raise Exception("Neuron doesn't allow inconsistent temperatures across different regions of a cell")

h.v_init = global_vm
h.celsius = global_vm

# Setup stims
stim = h.IClamp(0.5, c.soma[0])
stim.delay = 0
stim.dur = 3 
stim.amp = 3.5

################################
# Setting up vectors to record #
################################
v = h.Vector()
v.record(c.soma[0](0.5)._ref_v)

t = h.Vector()
t.record(h._ref_t)

#########################
# Setting up simulation #
#########################
h.secondorder = 0

h.t = 0
h.tstop = 20
h.dt = 0.025 

h.steps_per_ms = 1/h.dt

##################
# Run simulation #
##################
h.stdinit()
print(h.dt)

print("running simulation")
ST = cookie.time()
h.run()
ET = cookie.time()-ST
print("Finished in %f seconds" % ET)

fig, ax = plt.subplots()
ax.plot(t, v)

ax.set(xlabel='time (ms)', ylabel='voltage (mV)', title='swc morphology demo')
plt.xlim(0,h.tstop)
# plt.ylim(-80,80)
ax.grid()

plot_to_file=False
if plot_to_file:
    fig.savefig("voltages.png", dpi=300)
else:
    plt.show()

