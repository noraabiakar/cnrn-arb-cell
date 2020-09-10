# Test multiple synaptic activation of cell models

from neuron import h
import numpy as np
import time as cookie
import pylab as plt
import pickle
import json
import sys
import copy

h.load_file("stdrun.hoc")
h.load_file('import3d.hoc')

with open(sys.argv[1]) as json_file:
    defaults = json.load(json_file)

with open(sys.argv[2]) as json_file:
    cells = json.load(json_file)

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

param_dict = {"celsius": defaults["celsius"],
              "Vm"     : defaults["Vm"],
              "Ra"     : defaults["Ra"],
              "cm"     : defaults["cm"]*100}

ion_dict = {}
for ion in {"ca", "na", "k"}:
  ion_dict[ion] = {"iconc"  : defaults["ions"][ion]["internal-concentration"],
                   "econc"  : defaults["ions"][ion]["external-concentration"],
                   "revpot" : defaults["ions"][ion]["reversal-potential"]}

if "celsius" in  cells["global"]: 
  param_dict["celsius"] = cells["global"]["celsius"]

if "Vm" in cells["global"]:
  param_dict["Vm"] = cells["global"]["Vm"]

if "Ra" in cells["global"]:
  param_dict["Ra"] = cells["global"]["Ra"]

if "cm" in cells["global"]:
  param_dict["cm"] = cells["global"]["cm"]*100

if "ions" in cells["global"]:
   for ion in {"ca", "na", "k"}:
     if ion in cells["global"]["ions"]:
       if "internal-concentration" in cells["global"]["ions"][ion]:
         ion_dict[ion]["iconc"] = cells["global"]["ions"][ion]["internal-concentration"]
       if "external-concentration" in cells["global"]["ions"][ion]:
         ion_dict[ion]["econc"] = cells["global"]["ions"][ion]["external-concentration"]
       if "reversal-potential" in cells["global"]["ions"][ion]:
         ion_dict[ion]["revpot"] = cells["global"]["ions"][ion]["reversal-potential"]

local_param_dict = {"soma": copy.deepcopy(param_dict), 
                    "dend": copy.deepcopy(param_dict), 
                    "axon": copy.deepcopy(param_dict), 
                    "apic": copy.deepcopy(param_dict)} 

local_ion_dict   = {"soma": copy.deepcopy(ion_dict), 
                    "dend": copy.deepcopy(ion_dict), 
                    "axon": copy.deepcopy(ion_dict), 
                    "apic": copy.deepcopy(ion_dict)} 

for local_dict in cells["local"]:
  region = local_dict["region"]
  if "celsius" in local_dict:
    local_param_dict[region]["celsius"] = local_dict["celsius"]
  if "Vm" in local_dict: 
    local_param_dict[region]["Vm"]      = local_dict["Vm"]
  if "Ra" in local_dict:
    local_param_dict[region]["Ra"]      = local_dict["Ra"]
  if "cm" in local_dict:
    local_param_dict[region]["cm"]      = local_dict["cm"]*100
  if "ions" in local_dict: 
     for ion in {"ca", "na", "k"}:
       if ion in local_dict["ions"]:
         if "internal-concentration" in local_dict["ions"][ion]:
           local_ion_dict[region][ion]["iconc"] = local_dict["ions"][ion]["internal-concentration"]
         if "external-concentration" in local_dict["ions"][ion]:
           local_ion_dict[region][ion]["econc"] = local_dict["ions"][ion]["external-concentration"]
         if "reversal-potential" in local_dict["ions"][ion]:
           local_ion_dict[region][ion]["revpot"] = local_dict["ions"][ion]["reversal-potential"]

c = cell(swc)
print(c.soma)
print(c.dend)
print(c.apic)
print(c.axon)

#Create ball and stick model
soma      = h.Section(name='soma')
soma.L    = 11.65968
soma.diam = 11.65968
soma.nseg = 1

soma.Ra = 100
soma.cm = 1

dend      = h.Section(name='dend')
dend.L    = 200.0
dend.diam = 30
dend.nseg = 20

dend.Ra = 100
dend.cm = 1

dend.connect(soma(1))

# Paint regions

if in_param["soma_hh"] :
    soma.insert("hh")
    soma.ena = in_param["hh_ena"]
    soma.ek = in_param["hh_ek"]
    soma.gnabar_hh = in_param["hh_gnabar"]
    soma.gkbar_hh = in_param["hh_gkbar"]
    soma.gl_hh = in_param["hh_gl"]
else :
    soma.insert("pas")
    soma.e_pas = in_param["pas_e"]
    soma.g_pas = in_param["pas_g"]

if in_param["dend_hh"] :
    dend.insert("hh")
    dend.ena = in_param["hh_ena"]
    dend.ek = in_param["hh_ek"]
    dend.gnabar_hh = in_param["hh_gnabar"]
    dend.gkbar_hh = in_param["hh_gkbar"]
    dend.gl_hh = in_param["hh_gl"]
else :
    dend.insert("pas")
    dend.e_pas = in_param["pas_e"]
    dend.g_pas = in_param["pas_g"]

################################
# Setting up vectors to record #
################################
v = h.Vector()
v.record(soma(0.5)._ref_v)

t = h.Vector()
t.record(h._ref_t)

#########################
# Setting up simulation #
#########################
h.secondorder = 0

h.v_init = in_param["vinit"]
h.celsius = in_param["temp"]

h.t = 0
h.tstop = 200
h.dt = in_param["dt_neuron"]

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

########
# Plot #
########
output = open("voltages.json", "w")
output.write("{\n")
output.write("  \"cell\":\"ball and stick - neuron\",\n")
output.write("  \"data\": {\n")
output.write("    \"time\": [\n")

for i in range(len(t)-1):
    output.write("      ")
    output.write(str(t[i]))
    output.write(",\n")

output.write("      ")
output.write(str(t[-1]))
output.write("\n")

output.write("    ],\n")
output.write("    \"voltage\": [\n")

for i in range(len(v)-1):
    output.write("      ")
    output.write(str(v[i]))
    output.write(",\n")

output.write("      ")
output.write(str(v[-1]))
output.write("\n")

output.write("    ]\n")
output.write("  },\n")
output.write("  \"name\": \"neuron demo\",\n")
output.write("  \"units\": \"mv\"\n")
output.write("}\n")

output.close()
