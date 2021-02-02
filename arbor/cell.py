import arbor
import json
import json_to_arb 
import seaborn
import pandas
import sys

with open(sys.argv[1]) as json_file:
    defaults_json = json.load(json_file) 
with open(sys.argv[2]) as json_file:
    decor_json = json.load(json_file) 
swc_file      = sys.argv[3]

morpho   = arbor.load_swc_arbor(swc_file)
defaults = json_to_arb.load(defaults_json)
decor    = json_to_arb.load(decor_json)

# Define the regions and locsets in the model.
defs = {'soma': '(tag 1)',  # soma has tag 1 in swc files.
        'axon': '(tag 2)',  # axon has tag 2 in swc files.
        'dend': '(tag 3)',  # dendrites have tag 3 in swc files.
        'apic': '(tag 4)',  # dendrites have tag 3 in swc files.
        'all' : '(all)',    # all the cell
        'root': '(root)',   # the start of the soma in this morphology is at the root of the cell.
        'mid_soma': '(location 0 0.5)'
        } # end of the axon.
labels = arbor.label_dict(defs)


# Place current clamp and spike detector.
decor.place('"mid_soma"', arbor.iclamp(0, 3, current=3.5))
decor.place('"root"', arbor.spike_detector(-10))

# Select a fine discritization for apt comparison with neuron.
decor.discretization(arbor.cv_policy_max_extent(0.5))

# Create cable_cell from morphology, label_dict and decor.
cell = arbor.cable_cell(morpho, labels, decor)

# Make single cell model.
m = arbor.single_cell_model(cell)

# Set the model default parameters
m.properties = defaults

# Extend the default catalogue
m.catalogue.extend(arbor.bbp_catalogue(), "")

# Attach voltage probes that sample at 50 kHz.
m.probe('voltage', where='"mid_soma"', frequency=50000)

# Simulate the cell for 20 ms.
tfinal=20
m.run(tfinal)

# Print spike times.
if len(m.spikes)>0:
    print('{} spikes:'.format(len(m.spikes)))
    for s in m.spikes:
        print('  {:7.4f}'.format(s))
else:
    print('no spikes')

# Plot the recorded voltages over time.
print("Plotting results ...")
df_list = []
for t in m.traces:
    df_list.append(pandas.DataFrame({'t/ms': t.time, 'U/mV': t.value, 'Location': str(t.location), "Variable": t.variable}))

df = pandas.concat(df_list)

seaborn.relplot(data=df, kind="line", x="t/ms", y="U/mV",hue="Location",col="Variable",ci=None).savefig('single_cell_arb.svg')
