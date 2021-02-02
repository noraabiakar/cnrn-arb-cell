import json
import copy
import arbor as arb

def __make_dicts(jfile):
  params = {
  "temperature-K": None, 
  "init-membrane-potential": None,
  "axial-resistivity": None,
  "membrane-capacitance": None,
  }
  ions = {}
  for ion in {"ca", "na", "k"}:
    ions[ion] = {
       "init-int-concentration" : None, 
       "init-ext-concentration" : None, 
       "init-reversal-potential" : None, 
    }
  methods = {}

  if "temperature-K" in  jfile: 
    params["temperature-K"] = jfile["temperature-K"]
  if "init-membrane-potential" in jfile:
    params["init-membrane-potential"] = jfile["init-membrane-potential"]
  if "axial-resistivity" in jfile:
    params["axial-resistivity"] = jfile["axial-resistivity"]
  if "membrane-capacitance" in jfile:
    params["membrane-capacitance"] = jfile["membrane-capacitance"]
  if "ions" in jfile:
    jions = jfile["ions"]
    for ion_name in jions:
      if "init-int-concentration" in jions[ion_name]:
        ions[ion_name]["init-int-concentration"] = jions[ion_name]["init-int-concentration"]
      if "init-ext-concentration" in jions[ion_name]:
        ions[ion_name]["init-ext-concentration"] = jions[ion_name]["init-ext-concentration"]
      if "init-reversal-potential" in jions[ion_name]:
        ions[ion_name]["init-reversal-potential"] = jions[ion_name]["init-reversal-potential"]
      if "reversal-potential-method" in jions[ion_name] and jions[ion_name]["reversal-potential-method"] != "constant":
        methods[ion_name] = arb.mechanism(jions[ion_name]["reversal-potential-method"])

  return params, ions, methods

def load(jfile):
  if "type" not in jfile: 
    raise Exception("JSON file must contain \"type\" field")

  if "data" not in jfile: 
    raise Exception("JSON file must contain \"data\" field")

  if jfile["type"] == "default-parameters":
    props = arb.cable_global_properties()

    params, ions, methods = __make_dicts(jfile["data"])  
    props.set_property(tempK = params["temperature-K"])
    props.set_property(Vm = params["init-membrane-potential"])
    props.set_property(rL = params["axial-resistivity"])
    props.set_property(cm = params["membrane-capacitance"])
    for ion_name in ions: 
      props.set_ion(ion = ion_name, int_con = ions[ion_name]["init-int-concentration"])
      props.set_ion(ion = ion_name, ext_con = ions[ion_name]["init-ext-concentration"])
      props.set_ion(ion = ion_name, rev_pot = ions[ion_name]["init-reversal-potential"])
    for ion_name in methods: 
      props.set_ion(ion = ion_name, method = methods[ion_name])

    return props
      
  elif jfile["type"] == "decor": 
    decor_json = jfile["data"]
    decor = arb.decor()

    if "global" in decor_json:
      params, ions, methods = __make_dicts(decor_json["global"])  
      decor.set_property(tempK = params["temperature-K"])
      decor.set_property(Vm = params["init-membrane-potential"])
      decor.set_property(rL = params["axial-resistivity"])
      decor.set_property(cm = params["membrane-capacitance"])
      for ion_name in ions: 
        decor.set_ion(ion = ion_name, int_con = ions[ion_name]["init-int-concentration"])
        decor.set_ion(ion = ion_name, ext_con = ions[ion_name]["init-ext-concentration"])
        decor.set_ion(ion = ion_name, rev_pot = ions[ion_name]["init-reversal-potential"])
      for ion_name in methods: 
        decor.set_ion(ion = ion_name, method = methods[ion_name])

    if "local" in decor_json:
      loc_json_list = decor_json["local"]

      for loc_json in loc_json_list:  
        if "region" not in loc_json: 
          raise Exception("cell local description must contain \"region\" field")
  
        reg = "\"" +  loc_json["region"] + "\""

        params, ions, methods = __make_dicts(loc_json)  
        decor.paint(region = reg, tempK = params["temperature-K"])
        decor.paint(region = reg, Vm = params["init-membrane-potential"])
        decor.paint(region = reg, rL = params["axial-resistivity"])
        decor.paint(region = reg, cm = params["membrane-capacitance"])
        for ion in ions: 
          decor.paint(region = reg, ion_name = ion, int_con = ions[ion]["init-int-concentration"])
          decor.paint(region = reg, ion_name = ion, ext_con = ions[ion]["init-ext-concentration"])
          decor.paint(region = reg, ion_name = ion, rev_pot = ions[ion]["init-reversal-potential"])

    if "mechanisms" in decor_json:
      mech_json_list = decor_json["mechanisms"]

      for mech_json in mech_json_list:  
        if "region" not in mech_json: 
          raise Exception("cell mechanism description must contain \"region\" field")
        if "mechanism" not in mech_json: 
          raise Exception("cell mechanism description must contain \"mechanism\" field")

        reg = "\"" + mech_json["region"] + "\""
        mech = mech_json["mechanism"]
 
        mech_desc = arb.mechanism(mech)
        if "parameters" in mech_json:
          params = mech_json["parameters"]
          for param_name in params:
            mech_desc.set(param_name, params[param_name])

        decor.paint(region=reg, mechanism=mech_desc) 
 
    return decor
  
  else: 
    raise Exception("Unsupported \"type\" ", jfile["type"])
