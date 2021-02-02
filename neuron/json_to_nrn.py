import json
import copy

def load_param_dict(defaults, decor):
  # Default parameter dictionary
  param_dict = {"temperature-C"          : defaults["temperature-K"] - 273.15,
                "init-membrane-potential": defaults["init-membrane-potential"],
                "axial-resistivity"      : defaults["axial-resistivity"],
                "membrane-capacitance"   : defaults["membrane-capacitance"]*100}

  # Override defaults 
  if "temperature-K" in  decor["global"]: 
    param_dict["temperature-K"] = decor["global"]["temperature-K"] - 273.15
  
  if "init-membrane-potential" in decor["global"]:
    param_dict["init-membrane-potential"] = decor["global"]["init-membrane-potential"]
  
  if "axial-resistivity" in decor["global"]:
    param_dict["axial-resistivity"] = decor["global"]["axial-resistivity"]
  
  if "membrane-capacitance" in decor["global"]:
    param_dict["membrane-capacitance"] = decor["global"]["membrane-capacitance"]*100

  # Local param dictionary, intialized with the defaults
  local_param_dict = {"soma": copy.deepcopy(param_dict), 
                      "dend": copy.deepcopy(param_dict), 
                      "axon": copy.deepcopy(param_dict), 
                      "apic": copy.deepcopy(param_dict), 
                      "all" : copy.deepcopy(param_dict)} 

  # Override locals
  for local_dict in decor["local"]:
    region = local_dict["region"]
    if "temperature-K" in local_dict:
      local_param_dict[region]["temperature-K"] = local_dict["temperature-K"] - 273.15
    if "init-membrane-potential" in local_dict: 
      local_param_dict[region]["init-membrane-potential"] = local_dict["init-membrane-potential"]
    if "axial-resistivity" in local_dict:
      local_param_dict[region]["axial-resistivity"] = local_dict["axial-resistivity"]
    if "membrane-capacitance" in local_dict:
      local_param_dict[region]["membrane-capacitance"] = local_dict["membrane-capacitance"]*100

  return local_param_dict
 

def load_ion_dict(defaults, decor):
  # Default ion_dictionary
  ion_dict = {}
  for ion in {"ca", "na", "k"}:
    ion_dict[ion] = {"iconc"  : defaults["ions"][ion]["init-int-concentration"],
                     "econc"  : defaults["ions"][ion]["init-ext-concentration"],
                     "revpot" : defaults["ions"][ion]["init-reversal-potential"]}

  # Override defaults 
  if "ions" in decor["global"]:
     for ion in {"ca", "na", "k"}:
       if ion in decor["global"]["ions"]:
         if "init-int-concentration" in decor["global"]["ions"][ion]:
           ion_dict[ion]["iconc"] = decor["global"]["ions"][ion]["init-int-concentration"]
         if "init-ext-concentration" in decor["global"]["ions"][ion]:
           ion_dict[ion]["econc"] = decor["global"]["ions"][ion]["init-ext-concentration"]
         if "init-reversal-potential" in decor["global"]["ions"][ion]:
           ion_dict[ion]["revpot"] = decor["global"]["ions"][ion]["init-reversal-potential"]
  
  # Local ion dictionary, intialized with the defaults 
  local_ion_dict   = {"soma": copy.deepcopy(ion_dict), 
                      "dend": copy.deepcopy(ion_dict), 
                      "axon": copy.deepcopy(ion_dict), 
                      "apic": copy.deepcopy(ion_dict), 
                      "all" : copy.deepcopy(ion_dict)} 

  # Override locals
  for local_dict in decor["local"]:
    region = local_dict["region"]
    if "ions" in local_dict: 
       for ion in {"ca", "na", "k"}:
         if ion in local_dict["ions"]:
           if "init-int-concentration" in local_dict["ions"][ion]:
             local_ion_dict[region][ion]["iconc"] = local_dict["ions"][ion]["init-int-concentration"]
           if "init-ext-concentration" in local_dict["ions"][ion]:
             local_ion_dict[region][ion]["econc"] = local_dict["ions"][ion]["init-ext-concentration"]
           if "init-reversal-potential" in local_dict["ions"][ion]:
             local_ion_dict[region][ion]["revpot"] = local_dict["ions"][ion]["init-reversal-potential"]
  
  return local_ion_dict


def load_method_dict(defaults, decor):
  # Ion revpot methods
  method_dict = {"ca" : defaults["ions"]["ca"]["reversal-potential-method"],
                 "na" : defaults["ions"]["na"]["reversal-potential-method"],
                 "k"  : defaults["ions"]["k"]["reversal-potential-method"]}
  
  if "ions" in decor["global"]:
     for ion in {"ca", "na", "k"}:
       if ion in decor["global"]["ions"]:
         if "reversal-potential-method" in decor["global"]["ions"][ion]:
           method_dict[ion] = decor["global"]["ions"][ion]["reversal-potential-method"]

  return method_dict


def load_mechanism_dict(decor):
  return decor["mechanisms"]
