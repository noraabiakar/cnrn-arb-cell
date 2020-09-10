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

# Read json files and generate local params

# Default parameter dictionary
param_dict = {"celsius": defaults["celsius"],
              "Vm"     : defaults["Vm"],
              "Ra"     : defaults["Ra"],
              "cm"     : defaults["cm"]*100}

# Default ion_dictionary
ion_dict = {}
for ion in {"ca", "na", "k"}:
  ion_dict[ion] = {"iconc"  : defaults["ions"][ion]["internal-concentration"],
                   "econc"  : defaults["ions"][ion]["external-concentration"],
                   "revpot" : defaults["ions"][ion]["reversal-potential"]}

# Override defaults 
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

# Local param dictionary, intialized with the defaults
local_param_dict = {"soma": copy.deepcopy(param_dict), 
                    "dend": copy.deepcopy(param_dict), 
                    "axon": copy.deepcopy(param_dict), 
                    "apic": copy.deepcopy(param_dict), 
                    "all" : copy.deepcopy(param_dict)} 

# Local ion dictionary, intialized with the defaults 
local_ion_dict   = {"soma": copy.deepcopy(ion_dict), 
                    "dend": copy.deepcopy(ion_dict), 
                    "axon": copy.deepcopy(ion_dict), 
                    "apic": copy.deepcopy(ion_dict), 
                    "all" : copy.deepcopy(ion_dict)} 

# Override locals
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

# Creat cell and rehion map
c = cell(swc)
region_map = {"soma": c.soma, 
              "dend": c.dend,
              "axon": c.axon,
              "apic": c.apic, 
              "all" : c.all}

# Set region properties
for region in region_map: 
  for sec in region_map[region]:
    sec.cm = local_param_dict[region]["cm"]
    sec.Ra = local_param_dict[region]["Ra"]
    for ion in local_ion_dict[region]:
      iconc = ion+"i"
      econc = ion+"o"
      revpot = "e"+ion
      if hasattr(sec, iconc):
        setattr(sec, iconc, local_ion_dict[region][ion]["iconc"])
      if hasattr(sec, econc):
        setattr(sec, econc, local_ion_dict[region][ion]["econc"])
      if hasattr(sec, revpot):
        setattr(sec, revpot, local_ion_dict[region][ion]["revpot"])

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

# Paint region mechanisms
for mech_desc in cells["mechanisms"]: 
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
