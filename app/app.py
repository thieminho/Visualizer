#from plugins import one, two

import importlib
PLUGIN_NAME = "plugins.two"  #zamiast tego znajdowanie modułów z folderu plugins

plugin_module = importlib.import_module(PLUGIN_NAME, ".")

print(plugin_module)

plugin = plugin_module.Plugin("hello", key=1)
result = plugin.execute(7,2)
print(result)

#print(one)
#print(two)
#one.Plugin("hello world", key=123)+