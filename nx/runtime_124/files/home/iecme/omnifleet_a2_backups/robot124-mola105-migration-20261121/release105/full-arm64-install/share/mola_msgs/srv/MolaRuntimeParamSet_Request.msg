# This service requests changing one or more runtime configurable parameters of running mola::ExecutableBase modules.

# Request: a multiline string in YAML format with all parameters that need to be changed, in this format:
# ---
# module1:
#   var: value
# module2:
#   var: value
# ...
# ---
string parameters
