import json
import zipfile

PATH_OBJ = 'test.objects.json.zip'
PATH_ATT = 'test.attributes.json.zip'
PATH_REL = 'test.relationships.json.zip'

def clean_string(s):
    s = s.replace(' ','|')
    while s[-1] == '|':
        s = s[:-1]
    while s[0] == '|':
        s = s[1:]
    return s.lower()

def extract_objects(filepath):
    all_objects = {}
    situations = {}
    zfile = zipfile.ZipFile(filepath)
    for finfo in zfile.infolist():
        ifile = zfile.open(finfo)
        data = json.loads(ifile.read().decode('utf-8'))
        for image in data:
            im_id = image['image_id']
            situations[im_id] = []
            for obj in image['objects']:
                objects = obj['synsets']
                objects_id = obj['object_id']
                for obj in objects:
                    #print('%s(%s)' %(obj,objects_id))
                    pair = (obj,objects_id)
                    situations[im_id].append(pair)
                    all_objects[objects_id] = objects
    return all_objects, situations

def extract_attributes(filepath):
    attributes = {}
    zfile = zipfile.ZipFile(filepath)
    for finfo in zfile.infolist():
        ifile = zfile.open(finfo)
        data = json.loads(ifile.read().decode('utf-8'))
        for image in data:
            for attr in image['attributes']:
                objects_id = attr['object_id']
                try:
                    atts = [attr['attribute']]
                except:
                    try:
                        atts = attr['attributes']
                    except:
                        atts = []
                if len(atts) != 0:
                    for att in atts:
                        if len(att) > 0:
                            #print('%s(%s)' %(att,objects_id))
                            att = clean_string(att)
                            if objects_id in attributes:
                                attributes[objects_id].append(att)
                            else:
                                attributes[objects_id] = [att]
    return attributes

def extract_rels(filepath):
    args1 = {}
    args2 = {}
    zfile = zipfile.ZipFile(filepath)
    for finfo in zfile.infolist():
        ifile = zfile.open(finfo)
        data = json.loads(ifile.read().decode('utf-8'))
        for rels in data:
            for rel in rels['relationships']:
                if len(rel['predicate']) > 0:
                    pred = clean_string(rel['predicate'])
                else:
                    continue
                try:
                    subj = rel['subject']['object_id']
                except:
                    subj = '-'
                try:
                    obj = rel['object']['object_id']
                except:
                    obj = '-'
                if subj in args1:
                    args1[subj].append((pred,obj))
                else:
                    args1[subj] = [(pred,obj)]
                if obj in args2:
                    args2[obj].append((pred,subj))
                else:
                    args2[obj] = [(pred,subj)]
              
    return args1,args2


all_objects, situations = extract_objects(PATH_OBJ)
all_attributes = extract_attributes(PATH_ATT)
args1,args2 = extract_rels(PATH_REL)

for situation, objects in situations.items():
    print('<situation id=%s>' %situation)
    for o,i in objects:
        print('    <entity id=%s>' %i)
        print('        %s(%s)' %(o,i))
        if i in all_attributes:
            for a in all_attributes[i]:
                print('        %s(%s)' %(a,i))
        if i in args1 and i in all_objects:
            for pred,obj in args1[i]:
                if obj in all_objects:
                    print('        %s(%s,%s)' %(pred,i,obj))
                    #print('        %s(%s,%s)' %(pred,all_objects[i],all_objects[obj]))
        if i in args2 and i in all_objects:
            for pred,sub in args2[i]:
                if sub in all_objects:
                    print('        %s(%s,%s)' %(pred,sub,i))
                    #print('        %s(%s,%s)' %(pred,all_objects[sub],all_objects[i]))
        print('    </entity>')
    print('</situation>')
