import json
import copy

def load_param_dict(default_file, cell_file):
  with open(default_file) as json_file:
      defaults = json.load(json_file)
  with open(cell_file) as json_file:
      cells = json.load(json_file)

  # Default parameter dictionary
  param_dict = {"celsius": defaults["celsius"],
                "Vm"     : defaults["Vm"],
                "Ra"     : defaults["Ra"],
                "cm"     : defaults["cm"]*100}

  # Override defaults 
  if "celsius" in  cells["global"]: 
    param_dict["celsius"] = cells["global"]["celsius"]
  
  if "Vm" in cells["global"]:
    param_dict["Vm"] = cells["global"]["Vm"]
  
  if "Ra" in cells["global"]:
    param_dict["Ra"] = cells["global"]["Ra"]
  
  if "cm" in cells["global"]:
    param_dict["cm"] = cells["global"]["cm"]*100

  # Local param dictionary, intialized with the defaults
  local_param_dict = {"soma": copy.deepcopy(param_dict), 
                      "dend": copy.deepcopy(param_dict), 
                      "axon": copy.deepcopy(param_dict), 
                      "apic": copy.deepcopy(param_dict), 
                      "all" : copy.deepcopy(param_dict)} 

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

  return local_param_dict
 

def load_ion_dict(default_file, cell_file):
  with open(default_file) as json_file:
      defaults = json.load(json_file)
  with open(cell_file) as json_file:
      cells = json.load(json_file)

  # Default ion_dictionary
  ion_dict = {}
  for ion in {"ca", "na", "k"}:
    ion_dict[ion] = {"iconc"  : defaults["ions"][ion]["internal-concentration"],
                     "econc"  : defaults["ions"][ion]["external-concentration"],
                     "revpot" : defaults["ions"][ion]["reversal-potential"]}

  # Override defaults 
  if "ions" in cells["global"]:
     for ion in {"ca", "na", "k"}:
       if ion in cells["global"]["ions"]:
         if "internal-concentration" in cells["global"]["ions"][ion]:
           ion_dict[ion]["iconc"] = cells["global"]["ions"][ion]["internal-concentration"]
         if "external-concentration" in cells["global"]["ions"][ion]:
           ion_dict[ion]["econc"] = cells["global"]["ions"][ion]["external-concentration"]
         if "reversal-potential" in cells["global"]["ions"][ion]:
           ion_dict[ion]["revpot"] = cells["global"]["ions"][ion]["reversal-potential"]
  
  # Local ion dictionary, intialized with the defaults 
  local_ion_dict   = {"soma": copy.deepcopy(ion_dict), 
                      "dend": copy.deepcopy(ion_dict), 
                      "axon": copy.deepcopy(ion_dict), 
                      "apic": copy.deepcopy(ion_dict), 
                      "all" : copy.deepcopy(ion_dict)} 

  # Override locals
  for local_dict in cells["local"]:
    region = local_dict["region"]
    if "ions" in local_dict: 
       for ion in {"ca", "na", "k"}:
         if ion in local_dict["ions"]:
           if "internal-concentration" in local_dict["ions"][ion]:
             local_ion_dict[region][ion]["iconc"] = local_dict["ions"][ion]["internal-concentration"]
           if "external-concentration" in local_dict["ions"][ion]:
             local_ion_dict[region][ion]["econc"] = local_dict["ions"][ion]["external-concentration"]
           if "reversal-potential" in local_dict["ions"][ion]:
             local_ion_dict[region][ion]["revpot"] = local_dict["ions"][ion]["reversal-potential"]
  
  return local_ion_dict


def load_method_dict(default_file, cell_file):
  with open(default_file) as json_file:
      defaults = json.load(json_file)
  with open(cell_file) as json_file:
      cells = json.load(json_file)

  # Ion revpot methods
  method_dict = {"ca" : defaults["ions"]["ca"]["method"],
                 "na" : defaults["ions"]["na"]["method"],
                 "k"  : defaults["ions"]["k"]["method"]}
  
  if "ions" in cells["global"]:
     for ion in {"ca", "na", "k"}:
       if ion in cells["global"]["ions"]:
         if "method" in cells["global"]["ions"][ion]:
           method_dict[ion] = cells["global"]["ions"][ion]["method"]

  return method_dict


def load_mechanism_dict(cell_file):
  with open(cell_file) as json_file:
      cells = json.load(json_file)

  return cells["mechanisms"]
