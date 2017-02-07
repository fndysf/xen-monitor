#!/usr/bin/python
#encoding=utf-8
from xml.dom.minidom import Document
import myutils
import pprint, sys, time
import XenAPI
from conf import *

def help():
    print "Usage:"
    print sys.argv[0], " "
    print sys.argv[0], " --host-name [host] "
    print sys.argv[0], " --vm-name [vm]"

def getChildByName(parent,name):
    for node in parent.childNodes:
        if node.nodeName==name:
           return node
    return None

def simplify_pbd(odoc,pbds,ndoc,parent):
    for pbd in pbds.childNodes:
        l1=pbd.firstChild
        if len(l1.childNodes)==0:
            continue
        node=l1.firstChild
        element=ndoc.createElement('PBD')
        parent.appendChild(element)
        content=ndoc.createTextNode(myutils.toString(node.firstChild.nodeValue))
        element.appendChild(content)

def simplify_pif(odoc,pifs,ndoc,parent):
    for pif in pifs.childNodes:
        l1=pif.childNodes
        element=ndoc.createElement('Network')
        parent.appendChild(element)
        for node in l1:
            if node.nodeName=='network':
                element.setAttribute('name',node.getAttribute('name'))
                for subnode in node.childNodes:
                    child=ndoc.createElement(subnode.nodeName)
                    element.appendChild(child)
                    content=ndoc.createTextNode(myutils.toString(subnode.firstChild.nodeValue))
                    child.appendChild(content)
            else:
                child = ndoc.createElement(node.nodeName)
                element.appendChild(child)
                content = ndoc.createTextNode(myutils.toString(node.firstChild.nodeValue))
                child.appendChild(content)

def simplify_vm(odoc,vms,ndoc,parent):
    for vm in vms.childNodes:
        nvm=ndoc.createElement('VM')
        content=ndoc.createTextNode(vm.getAttribute('name'))
        nvm.appendChild(content)
        parent.appendChild(nvm)

def simplify_vm2network(odoc,vms,ndoc,parent):
    for vm in vms.childNodes:
        vifs=getChildByName(vm,'VIFs')
        if vifs==None:
            return
        nvm=ndoc.createElement('VM')
        nvm.setAttribute('name',vm.getAttribute('name'))
        parent.appendChild(nvm)
        for vif in vifs.childNodes:
            nw=ndoc.createElement('network')
            nvm.appendChild(nw)
            subnw=getChildByName(vif,'network')
            nw.setAttribute('name',subnw.getAttribute('name'))
            bridge=getChildByName(subnw,'bridge')
            bd=ndoc.createElement('bridge')
            content=ndoc.createTextNode(bridge.firstChild.nodeValue)
            bd.appendChild(content)
            nw.appendChild(bd)
            mac=getChildByName(vif,'MAC')
            element=ndoc.createElement('MAC')
            element.appendChild(ndoc.createTextNode(mac.firstChild.nodeValue))
            nw.appendChild(element)

def simplify_host(odoc,host,ndoc):
    nhost=ndoc.createElement('Host')
    ndoc.appendChild(nhost)
    nhost.setAttribute('name',host.getAttribute('name'))
    storage=ndoc.createElement('Host2Storage')
    nhost.appendChild(storage)
    network=ndoc.createElement('Host2Network')
    nhost.appendChild(network)
    vmnode=ndoc.createElement('Host2VM')
    nhost.appendChild(vmnode)
    v2n=ndoc.createElement('VM2Network')
    nhost.appendChild(v2n)
    pbds=None
    pifs=None
    vms=None
    for child in host.childNodes:
        if child.nodeName=='PBDs':
            pbds=child
        elif child.nodeName=='PIFs':
            pifs=child
        elif child.nodeName=='resident_VMs':
            vms=child
    simplify_pbd(odoc,pbds,ndoc,storage)
    simplify_pif(odoc, pifs, ndoc, network)
    simplify_vm(odoc, vms, ndoc, vmnode)
    simplify_vm2network(odoc, vms, ndoc, v2n)
def simplify(odoc,ndoc):
    for host in odoc.getElementsByTagName('Host'):
        simplify_host(odoc,host,ndoc)
if __name__ == "__main__":
    if not(len(sys.argv) == 1) and not(len(sys.argv) == 3):
        help()
        sys.exit(q)
    
    session = XenAPI.Session(URL)
    session.xenapi.login_with_password(USERNAME, PASSWORD)
    doc=Document();
    allhost=doc.createElement('Hosts')
    doc.appendChild(allhost)
    hosts=session.xenapi.host.get_all()
    for host in hosts:
      myutils.create(doc,allhost,'Host',host,session)
    session.xenapi.session.logout()
    ndoc=Document()
    simplify(doc,ndoc)
    file = open('host1.xml','w')
    file.write(doc.toprettyxml(indent = '  '))
    file.close()
