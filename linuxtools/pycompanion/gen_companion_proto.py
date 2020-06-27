from __future__ import print_function
import sys

# Sort by class name to make diffing simpler
sort_output = True
sort_wirefields = True

gen_dummy_fields = True
gen_dummies_max_tag = 80
gen_dummies_class_names = ['BlackCoral', 'Companion']

base_package = 'co.glassio.blackcoral'

if len(sys.argv) > 1:
    base_path = sys.argv[1]
else:
    base_path = "../../src/out/sources/co/glassio/blackcoral"

def parse_wirefield_info(l):
    is_required = 'REQUIRED' in l
    parts = [v.strip() for v in l.split('(')[1].split(')')[0].split(',')]
    parts = [[z.strip() for z in v.split('=')] for v in parts]
    assert all([len(x) == 2 for x in parts])
    parts = { k : v for k, v in parts }
    parts['adapter'] = parts['adapter'][1:-1]
    is_def = False
    if 'com.squareup.wire.ProtoAdapter' in parts['adapter']:
        ftype = ('base', parts['adapter'].split('#')[1])
    elif 'co.glassio.blackcoral' in parts['adapter']:
        is_def = True
        if '$' in parts['adapter']:
            cname = parts['adapter'].split('$')[1].split('#')[0]
            ftype = ('nest', cname)
        else:
            cname = parts['adapter'].split('#')[0]
            assert cname.startswith(base_package + '.')
            cname = cname[(len(base_package)+1):]
            ftype = ('ext', cname)

    tag = parts['tag']
    for k in parts.keys():
        if k not in ['label', 'adapter', 'tag']:
            raise RuntimeError("Got unhandled proto field: " + k)

    if 'label' in parts:
        assert parts['label'] in ['WireField.Label.REPEATED', 'WireField.Label.REQUIRED']
    return {
            'type' : ftype,
            'repeated' : parts.get('label', '') == 'WireField.Label.REPEATED',
            'tag' : tag,
            'is_def' : is_def,
            'required' : is_required
        }

def process_file(fname, name_prefix=''):

    ilevel = 0
    next_is_wirefield = False
    in_enum = False


    stack = []


    fields = []
    enum_fields = []
    defs = []
    cur_field = None

    msg_name = None

    nopen = 0

    with open(fname) as fin:
        lines = [x.strip() for x in fin.readlines()]
        for l in lines:
            for x in l:
                if x == '{':
                    nopen += 1
                if x == '}':
                    nopen -= 1

            if stack and nopen < stack[-1][0]:

                sub_defs = defs[:]
                sub_fields = fields[:]

                defs = stack[-1][4]
                fields = stack[-1][3]
                assert not enum_fields
                assert not cur_field
                assert not in_enum
                assert not next_is_wirefield

                defs.append((stack[-1][1], stack[-1][2], sub_fields, sub_defs))
                stack.pop()

            elif next_is_wirefield:
                #print("    ", l)
                if l != '@Deprecated':
                    assert (l[-1] == ';')
                    ttype = l[:-1].split(' ')[-2]
                    name = l[:-1].split(' ')[-1]

                    fields.append({ 'name' : name, 'ttype' : ttype, 'info' : cur_field })
                    next_is_wirefield = False
                    cur_field = None
            elif in_enum:
                #print("     ", l)
                assert l[-1] in [',', ';']
                val_name = l.split('(')[0]
                val_val = l[:-1].split('(')[1].split(')')[0]
                enum_fields.append((val_name, val_val))
                if l.endswith(';'):
                    defs.append((in_enum, 'enum', tuple(enum_fields), []))
                    enum_fields = []
                    in_enum = None

            else:
                if l.startswith('public final class '):
                    parts = l.split()
                    assert parts[4] == 'extends'
                    assert msg_name is None
                    msg_name = parts[3]
                elif l.startswith('public static final class ') and 'extends Message<' in l:
                    name = l.split()[4]
                    stack.append((nopen, name, 'message', fields, defs))
                    fields = []
                    defs = []

                    assert not enum_fields
                    assert not cur_field
                    assert not in_enum
                    assert not next_is_wirefield

                    #print("Found msg class: ", msg_name) #l)
                #elif l.startswith('public static final class '):
                #and 'extends Mes:
                #    print
                elif l.startswith('public enum ') and 'implements WireEnum' in l:
                    assert(len(l.split()) == 6)
                    name = l.split()[2]
                    in_enum = name
                elif l.startswith('@WireField'):
                    cur_field = parse_wirefield_info(l)
                    next_is_wirefield = True

                # msg def

    #print("Msg: ", msg_name)
    #print("FIELDS: ")
    #for f in fields:
    #    print("    ", f)
    #print("DEFS: ")
    #for d in defs:
    #    print("    ", d)

    return (msg_name, 'message', fields, defs)
#env.msgs[name_prefix + d[0]] = (name_prefix + d[0], 'enum', d[1], [])

    #return (msg_name, fields, defs)


fn = "../../src/out/sources/co/glassio/blackcoral/HandshakeResponse.java"

class Env:
    def __init__(self):
        self.to_load = set()
        self.msgs = {}


env = {}

def process_class(name, env):
    pathname = None
    name_prefix = ''
    if '.' in name:
        name_prefix = '_'.join(name.split('.')[:-1]) + '_'
        pathname = base_path + '/' + '/'.join(name.split('.')) + '.java'
    else:
        pathname = base_path + '/' + name + '.java'

    #print("Processing: ", name, "/", pathname, " : ", name_prefix)

    msg_name, mtype, fields, defs = process_file(pathname)

    if not msg_name:
        # this is an enum?
        assert len(defs) == 1
        for d in defs:
            env.msgs[name_prefix + d[0]] = (name_prefix + d[0], d[1], d[2], [])
    else:
        assert msg_name
        for f in fields:
            if f['info']['type'][0] == 'ext':
                if not f['info']['type'][1] in env.msgs:
                    env.to_load.add(f['info']['type'][1])

        env.msgs[name_prefix + msg_name] = (name_prefix + msg_name, 'message', fields, defs)



def process_names(names, env=None):
    if not isinstance(names, list):
        names = [names]
    env = env or Env()
    for x in names:
        if not x in env.msgs:
            env.to_load.add(x)

    while env.to_load:
        elem = env.to_load.pop()
        process_class(elem, env)

    return env


def translate_type(f):
    if f[0] == 'base':
        return f[1].lower()
    else:
        return f[1].replace('.', '_')

def translate_label(f):
    if f['info']['repeated']:
        return 'repeated'
    elif f['info']['required']:
        return 'required'
    return 'optional'


def print_indented(x, indent=4, depth=0):
    if isinstance(x, list):
        for xi in x:
            if isinstance(xi, list):
                print_indented(xi, indent=indent, depth=depth+indent)
            else:
                print_indented(xi, indent=indent, depth=depth+indent)

    else:
        print(" "*depth + x)



def gen_one(msg, toplevel=True):
    name, mtype, fields, defs = msg
    out = []
    if mtype == 'enum':
        out.append('')
        out.append('enum %s {'%(name))
        prefix = '' if not toplevel else '%s_'%(name)
        out.append(['%s = %s;'%(prefix + a, b) for a, b in fields])
        out.append('}')
        out.append('')
    else:
        out.append('')
        out.append('message %s {'%(name))
        sfields = []
        ordered_fields = fields[:]
        if sort_wirefields:
            ordered_fields = sorted(ordered_fields, key=lambda x: int(x['info']['tag']))


        if gen_dummy_fields and name in gen_dummies_class_names:
            all_tags = [int(x['info']['tag']) for x in ordered_fields]
            missing = [z+1 for z in range(gen_dummies_max_tag) if z+1 not in all_tags]
            for z in missing:
                ordered_fields.append(dict(
                    info=dict(required=False, repeated=False, type=('ext', 'DummyEmpty'), tag=str(z), is_def=False),
                    name='dummy_%s'%z,
                ))

        if sort_wirefields:
            ordered_fields = sorted(ordered_fields, key=lambda x: int(x['info']['tag']))

        for f in ordered_fields:
            sfields.append('%s %s %s = %s;'%(
                translate_label(f),
                translate_type(f['info']['type']),
                f['name'],
                f['info']['tag']
            ))
        out.append(sfields)

        out.append('')
        dfields = []
        for d in defs:
            dfields.append(gen_one(d, toplevel=False)) #(d[0], 'enum', d[1], [])))
        out.append(dfields)
        out.append('}')
        out.append('')

    return out

def gen_proto_code(env):
    out = []
    items = list(env.msgs.items())
    if sort_output:
        items = sorted(items, key=lambda x: x[0])

    for m, msg in items:
        #env.msgs.items():
        out.append(gen_one(msg))

    return out


#env = process_names("BlackCoral")
env = process_names(["Companion", "BlackCoral"])

#print(env.msgs, env.to_load)
print("""
syntax = "proto2";

package focals;

message DummyEmpty {
}

""")
code = gen_proto_code(env)
print_indented(code)
# generate for class
#with open(sys.argv[1]







