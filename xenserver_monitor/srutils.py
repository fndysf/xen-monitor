#!/usr/bin/python
#encoding=utf-8
import conf

def get_record(session,key,value):
    if not (isinstance(value,(str,unicode))) or not ('OpaqueRef' in value):
        return value
    if value=='OpaqueRef:NULL':
        return 'Null'
    if 'VM' in key:
        return session.xenapi.VM.get_record(value)
    elif 'PIF' in key:
        return session.xenapi.PIF.get_record(value)
    elif 'VIF' in key:
        return session.xenapi.VIF.get_record(value)
    elif 'PBD' in key:
        return session.xenapi.PBD.get_record(value)
    elif 'VBD' in key:
        return session.xenapi.VBD.get_record(value)
    elif 'SR' in key:
        return session.xenapi.SR.get_record(value)
    elif 'network' in key:
        return session.xenapi.network.get_record(value)
    elif 'VDI' in key:
        return session.xenapi.VDI.get_record(value)
    else:
        return session.xenapi.host.get_record(value)

def toString(value):
    if not isinstance(value,(str,unicode)):
        value=str(value)
    return value.encode('utf-8')

def create(doc,xmlparent,key,value,session):
    if not value:
        return
    attribute_map={'Host':['host_name','PIFs','PBDs','resident_VMs'],
                   'resident_VM':['power_state','is_control_domain','VIFs','VBDs','memory_static_min','memory_static_max','memory_dyanmic_min','memory_dynamic_max','memory_target'],
                   'VIF':['MAC','network','ipv4_allowed'],
                   'VBD':['device','mode','type','bootable','unpluggable','VDI'],
                   'PIF':['IP','ip_configuration','gateway','DNS','MAC','device','network'],
                   'PBD':['device_config'],
                   'network':['bridge','name_description'],
                   'VDI':['location'],
                   'SR':['type','PBDs','PIFs'],
                   'device_config':['location'],
                   'VIFs':[],
                   'PIFs':[],
                   'VBDs':[],
                   'PBDs':[],
                   'SRs':[],
                   'VDIs':[],
                   'networks':[]
                   }
    element = doc.createElement(key)
    xmlparent.appendChild(element)
    value=get_record(session,key,value)
    if isinstance(value,(list,tuple,set)):
        singlekey = key[0:len(key)-1]
        for v in value:
            create(doc,element,singlekey,v,session)
    elif isinstance(value,dict):
        if 'name_label' in value.keys():
            element.setAttribute('name',value.get('name_label'))
        for e in value.keys():
            #if e in attribute_map.get(key):
            current=create(doc,element,e,value.get(e),session)
    else:
        value=toString(value)
        content=doc.createTextNode(value)
        element.appendChild(content)
    return element
