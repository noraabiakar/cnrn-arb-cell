import arbor
import sys
import matplotlib.pyplot as plt

defaults_file = sys.argv[1]
cells_file    = sys.argv[2]
swc_file      = sys.argv[3]

tree         = arbor.load_swc(swc_file)
defaults     = arbor.load_cell_default_parameters(defaults_file)
globals      = arbor.load_cell_global_parameters(cells_file)
locals       = arbor.load_cell_local_parameter_map(cells_file)
region_mechs = arbor.load_cell_mechanism_map(cells_file)

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

# Combine morphology with region and locset definitions to make a cable cell.
cell = arbor.cable_cell(tree, labels)

cell.apply_default_parameters(defaults)
cell.overwrite_default_parameters(globals)
cell.overwrite_local_parameters(locals)
cell.write_dynamics(region_mechs)

cell.place('mid_soma', arbor.iclamp(0, 3, current=3.5))
cell.place('root', arbor.spike_detector(-10))

# Have one compartment between each sample point.
cell.compartments_length(0.5)

# Make single cell model.
m = arbor.single_cell_model(cell)
m.properties.catalogue.extend(arbor.bbp_catalogue(), "")

# Attach voltage probes that sample at 50 kHz.
m.probe('voltage', where='root',  frequency=50000)
m.probe('voltage', where='mid_soma', frequency=50000)

# Simulate the cell for 15 ms.
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
fig, ax = plt.subplots()
for t in m.traces:
    ax.plot(t.time, t.value)
    # for v in t.value:
    #     print(v)

legend_labels = ['{}: {}'.format(s.variable, s.location) for s in m.traces]
ax.legend(legend_labels)
ax.set(xlabel='time (ms)', ylabel='voltage (mV)', title='swc morphology demo')
plt.xlim(0,tfinal)
ax.grid()

plot_to_file=False
if plot_to_file:
    fig.savefig("voltages.png", dpi=300)
else:
    plt.show()

