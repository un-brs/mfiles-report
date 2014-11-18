import re
import shelve
from collections import defaultdict
from jinja2 import Environment, PackageLoader, FileSystemLoader

LATEX_SUBS = (
    (re.compile(r'\\'), r'\\textbackslash'),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
)

def escape_tex(value):
    newval = value
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
    return newval

def show_classes(all_classes):
	def _show_classes(value):
		ret = ""
		if value == all_classes:
			return "In all classes"
		elif len(value) > (len(all_classes) / 2):
			ret  = "In all classes except: "
			value = all_classes - value
		return ret + ', '.join(sorted(value))
	return _show_classes

def show_vaults(vaults):
	if len(vaults) == 3:
		return "In all vaults"
	return ", ".join(sorted(vaults))

texenv = Environment(loader=FileSystemLoader('templates'))
texenv.block_start_string = '((*'
texenv.block_end_string = '*))'
texenv.variable_start_string = '((('
texenv.variable_end_string = ')))'
texenv.comment_start_string = '((='
texenv.comment_end_string = '=))'
texenv.filters['escape_tex'] = escape_tex

def get_attributes(vaults):
	attrs = {}
	for vault in vaults:
		vault_name = vault["name"]
		for kls in vault["classes"]:
			kls_name = kls["name"]
			for attr in kls["attributes"]:
				name, dtype = attr["name"], attr["type"]
				val = attrs.get(name, None)
				if not val:
					val = {}
					val["types"] = set([dtype])
					val["vaults"]  = set([vault_name])
					val["classes"] = set([kls_name])
				else:
					val["types"].add(dtype)
					val["vaults"].add(vault_name)
					val["classes"].add(kls_name)
				attrs[name] = val
	return attrs

def generate_table(attrs, env):
	env.filters['show_classes'] = show_classes(attrs["Name or title"]["classes"])
	env.filters['show_vaults'] = show_vaults
	tmpl = env.get_template("table.tex")
	print(tmpl.render(attrs=attrs))

def main():
	db = shelve.open("vaults")
	attrs = get_attributes(db["vaults"])
	generate_table(attrs, texenv)

if __name__ == '__main__':
	main()

# print(tmpl.render())
# db = shelve.open("vaults")

