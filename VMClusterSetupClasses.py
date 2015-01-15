#Copyright (c) 2015 Microsoft Corp 

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from azure import *
from azure.servicemanagement import *
from azure.servicemanagement import ServiceManagementService

import requests

from requests import Request, Session, Response, certs, auth
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

cert_path = "C:\Python_Files\AzureCertificate.pem"
cert_key_path = "C:\Python_Files\AzureCertificateKey.pem"

class AzureHttpRequests(object):
    
    def get_role(subscription_id, cs_name,deployment_name,role_name):
        url = "https://management.core.windows.net/" + subscription_id + "/services/hostedservices/" + cs_name + "/deployments/" + deployment_name + "/roles/" + role_name
        req = Request(method="GET",url=url,headers={"x-ms-version":"2014-06-01","Content-Type":"plain/text"})
        req_prepped = req.prepare()
        res = Response()
        s = Session()
        res = s.send(req_prepped,cert=(cert_path,cert_key_path))
        f = open("C:\\Python_Files\\response_xml_requestid_getrole.txt","w")
        f.write(str(res.content))
        
    @staticmethod
    def get_request(url):
        req = Request(method="GET",url=url,headers={"x-ms-version":"2014-06-01","Content-Type":"plain/text"})
        req_prepped = req.prepare()
        res = Response()
        s = Session()
        res = s.send(req_prepped,cert=(cert_path,cert_key_path))
        f = open("C:\\Python_Files\\response_xml_requestid_status.txt","w")
        f.write(str(res.content))

    @staticmethod
    def post_request(url,config_file_path):
        config_file = open(config_file_path,"rb")
        print("Preparing to send request ...")
        #res = requests.Request("POST",url=url,headers={"x-ms-version":"2014-06-01","Content-Type":"text/plain"},files={"filename":config_file_path},cert="C:\Python_Files\AzureCertificate.pem")
      #  req = Request(method="POST",url=url,headers={"x-ms-version":"2014-06-01","Content-Type":"text/plain"}, files={"filename":config_file_path})
        req = Request(method="POST",url=url,headers={"x-ms-version":"2014-06-01","Content-Type":"application/xml"}, files={"filename":config_file_path})
     #   
        req_prepped = req.prepare()   
        s = Session()
        res = Response() 
        res = s.send(req_prepped, cert=(cert_path,cert_key_path))
       #https://management.core.windows.net/<subscriptionID/operations/<requestId>
        #print(str(res.headers['x-ms-requestid']))
        print(str(res.content))
        
        

class XmlSerializerVMCluster(object):
    @staticmethod
    def create_vm_config_xml(deployment_name,deployment_slot,deployment_label,vm_details,resource_ext_det,end_point_det,vnet_det,config_abs_file_path):
        xml = "<?xml version='1.0' encoding='utf-8'?><Deployment xmlns='http://schemas.microsoft.com/windowsazure' xmlns:i='http://www.w3.org/2001/XMLSchema-instance'>"
        xml += "<Name>" + deployment_name+"</Name>"
        xml += "<DeploymentSlot>" + deployment_slot + "</DeploymentSlot>"
        xml+= "<Label>" + deployment_label + "</Label>"
        xml+="<RoleList>"
        if len(vm_details) >0:
            for i in range(len(vm_details)):
                xml+="<Role>"
                xml+="<RoleName>" + vm_details[i]["vm_name"]+"</RoleName>"
                xml+="<RoleType>PersistentVMRole</RoleType>"
                xml+="<ConfigurationSets>"
                xml+="<ConfigurationSet i:type='LinuxProvisioningConfigurationSet'>"
                xml+="<ConfigurationSetType>LinuxProvisioningConfiguration</ConfigurationSetType>"
                xml+="<HostName>" + vm_details[i]["host_name"] + "</HostName>"
                xml+="<UserName>" + vm_details[i]["vm_user_name"] + "</UserName>"
                xml+="<UserPassword>" + vm_details[i]["vm_password"] +"</UserPassword>"
                xml+="<DisableSshPasswordAuthentication>false</DisableSshPasswordAuthentication>"
                xml+="</ConfigurationSet>"
                xml+="<ConfigurationSet>"
                xml+="<ConfigurationSetType>NetworkConfiguration</ConfigurationSetType>"
                xml+="<InputEndpoints>"
                if(len(end_point_det))>0:
                    for j in range(len(end_point_det)):
                        xml+="<InputEndpoint>"
                        xml+="<LocalPort>" + str(end_point_det[j]["local_port_no"])+"</LocalPort>"
                        xml+="<Name>"+ end_point_det[j]["name"]+"</Name>"
                        xml+="<Port>"+ str(end_point_det[j]["port"])+"</Port>"
                        xml+="<Protocol>"+ end_point_det[j]["protocol"]+"</Protocol>"
                        xml+="</InputEndpoint>"

                xml+="</InputEndpoints>"
                xml+="<SubnetNames>"
                xml+="<SubnetName>" + vnet_det["vnet_subnet"]+"</SubnetName>"
                xml+="</SubnetNames>" 
                xml+="</ConfigurationSet>"  
                xml+="</ConfigurationSets>"   
                
                if (len(resource_ext_det))>0:
                    xml+="<ResourceExtensionReferences>"
                    for k in range(len(resource_ext_det)):
                        xml+="<ResourceExtensionReference>"
                        xml+="<ReferenceName>" + resource_ext_det[k]["res_ext_ref_name"] + "</ReferenceName>"
                        xml+="<Publisher>" + resource_ext_det[k]["res_ext_publisher"]+"</Publisher>"
                        xml+="<Name>" + resource_ext_det[k]["res_ext_name"]+"</Name>"
                        xml+="<Version>"+ resource_ext_det[k]["res_ext_version"] +"</Version>"
                        xml+="</ResourceExtensionReference>"
                    xml+="</ResourceExtensionReferences>"
                xml+="<VMImageName>"+ vm_details[i]["vm_img_name"]+"</VMImageName>"
                xml+="<RoleSize>"+ vm_details[i]["vm_size"]+"</RoleSize>"
                xml+="<ProvisionGuestAgent>true</ProvisionGuestAgent>"
                xml+="</Role>"
        xml+="</RoleList>"
        if len(vnet_det["vnet_name"])>0:
            xml+="<VirtualNetworkName>" + vnet_det["vnet_name"] +"</VirtualNetworkName>"
        dns = vnet_det["vnet_dns"]
        if len(dns)>0:
            xml+= "<Dns>"
            xml+="<DnsServers>"
            for l in range(len(dns)):
                xml+="<DnsServer>"
                xml+="<Name>"+ dns[l]["name"]+"</Name>"
                xml+="<Address>"+ dns[l]["IP_address"]+"</Address>"
                xml+="</DnsServer>"
            xml+="</DnsServers>"
            xml+="</Dns>"
        
        xml+="</Deployment>"

        complete_file_path = config_abs_file_path + "VM_Config_File.xml"
        f = open(complete_file_path,"w")
        f.write(xml)
        yes = f.close()
        return complete_file_path   

    @staticmethod
    def create_vnet_config_xml(vnet_name,location,dns,addr_space,subnet,config_abs_file_path):
        # Body of the function
        
        xml = "<?xml version='1.0' encoding='utf-8'?><NetworkConfiguration xmlns:xsd='http://www.w3.org/2001/XMLSchema' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns='http://schemas.microsoft.com/ServiceHosting/2011/07/NetworkConfiguration'>"
        xml += "<VirtualNetworkConfiguration><Dns><DnsServers>"
        for i in range(len(dns)):
            v_dns = dns[i]
            xml += "<DnsServer name ='" + v_dns["name"] +"' IPAddress='"+ v_dns["IP_address"] + "'/>"
        xml += "</DnsServers></Dns>"
        xml += "<VirtualNetworkSites><VirtualNetworkSite name='" + vnet_name + "' Location='" + location +"'><AddressSpace><AddressPrefix>"+addr_space+"</AddressPrefix></AddressSpace>"
        xml += "<Subnets><Subnet name='" + subnet["name"] + "'><AddressPrefix>" + subnet["addr"] +"</AddressPrefix></Subnet></Subnets> </VirtualNetworkSite></VirtualNetworkSites>"  
        xml += "</VirtualNetworkConfiguration></NetworkConfiguration>"        
        complete_file_path = config_abs_file_path + "Vnet_Config_File.xml"
        f = open(complete_file_path,"w")
        f.write(xml)
        yes = f.close()
        return complete_file_path   
        #where to save the file
   
 
   
