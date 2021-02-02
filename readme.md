## Downloading and Compiling Arbor
(For help refer to https://arbor.readthedocs.io/en/latest/install.html)

```
# Clone.
git clone https://github.com/arbor-sim/arbor.git --recurse-submodules
cd arbor

# Make a path for building.
mkdir build
cd build

# Use CMake to configure the build.
cmake .. -DARB_WITH_PYTHON=ON -DCMAKE_INSTALL_PREFIX=/path/to/arbor/install -DARB_PYTHON_PREFIX=/path/to/arbor/install 

# Build Arbor library.
make -j 4 install
```

## Running the examples

### Arbor
```
# Point python to the Arbor installation.
export PYTHONPATH=/path/to/arbor/install/lib/python3.6/site-packages/

# Change directory to this project.
cd arbor 

# Run the example.
python cell.py ../examples/ex1/defaults.json ../examples/ex1/cells.json ../examples/ex1/morphologies/sample_cell_arb.swc 
```

### Neuron
```
# Point python to the Arbor installation.
export PYTHONPATH=/path/to/neuron/install/lib/python3.6/site-packages/

# Change directory to this project.
cd neuron

# Build the mechanism
/path/to/neuron/install/bin/nrnivmodl mechanisms

# Run the example.
python cell.py ../examples/ex1/defaults.json ../examples/ex1/cells.json ../examples/ex1/morphologies/sample_cell_nrn.swc 
```
