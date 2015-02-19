#Copyright (c) 2015 Microsoft Corp 

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from azure import *
from azure.servicemanagement import *
import VMClusterSetupClasses
from VMClusterSetupClasses import XmlSerializerVMCluster, AzureHttpRequests
from collections import namedtuple
import json
import base64
from _io import open
from builtins import bytes
from azure import _encode_base64
from azure import _Base64String
from requests import Response
import time
from time import sleep
#from __builtin__ import bytes
#import paramiko
#from paramiko import SSHClient
#from paramiko.client import AutoAddPolicy


# Constant variables
subscription_id = "5c78935e-b33b-4b89-b627-b32fd08408f5"
certificate_path = "CURRENT_USER\\my\\AzureCertificate"
storage_location_name = ""
vnet_name = "mysqlvnetsg"
cs_name = "mysqlchefsg"
vnet_location = ""
svc = ServiceManagementService(subscription_id, certificate_path)     
isStorageAccCreated = False
isHostedServiceCreated = False
vm_image_name="debian-77-disk"

config_file_path = "C:\\Python_Files\\"


def Create_StorageAccount():
    storage_acc_name = ""    
    storage_replication = ""
    storage_location_name = ""
    #Standard_LRS, Standard_ZRS, Standard_GRS, Standard_RAGRS
    if storage_acc_name == "":
        storage_acc_name = str(input("Enter a storage account name. Storage account names must be between 3 and 24 characters in length and use numbers and lower-case letters only... "))
        isBoolStorageAccountNameUnique = False
        while isBoolStorageAccountNameUnique == False:
            res = svc.check_storage_account_name_availability(storage_acc_name)
            if res.result  == True:
                isBoolStorageAccountNameUnique = True
                if len(storage_location_name) <= 0: 
                    storage_location_name = str(input("Enter storage location... "))
                if len(storage_replication) <= 0:
                    storage_replication = str(input("Enter replication factor (Standard_LRS, Standard_ZRS, Standard_GRS, Standard_RAGRS)... "))
                    isBoolStorageReplicationValid = False
                    while isBoolStorageReplicationValid == False:
                        if storage_replication != "Standard_LRS" and storage_replication != "Standard_ZRS" and storage_replication != "Standard_GRS" and storage_replication != "Standard_RAGRS":
                            storage_replication = str(input("Invalid entry: Please re-enter replication factor (Standard_LRS, Standard_ZRS, Standard_GRS, Standard_RAGRS), press E if you want to exit"))
                            if storage_replication == "E" or storage_replication == "e":
                                isStorageAccCreated = False
                                break
                        else:
                            isBoolStorageReplicationValid = True
                if isBoolStorageReplicationValid == True:
                    svc.create_storage_account(storage_acc_name,storage_acc_name,storage_acc_name,None,storage_location_name,True,None)
                    isStorageAccCreated = True
            else:
                storage_acc_name = str(input("The storage account name entered is already in use, please re-enter another one, press E to exit.."))                            
                if storage_acc_name == "E" or storage_acc_name == "e":
                    isStorageAccCreated = False
                    break
        if isStorageAccCreated == True:
            print("Storage account..." + storage_acc_name + " has been created")
        else:
            print("Storage account could be created")

    return True

def Create_HostedService():
   
    cs_label = ""
    cs_description = ""
    cs_location = ""
    isHostedCSNameUnique = False
    
    if len(storage_location_name) > 0 and isStorageAccCreated == True:
        cs_location = storage_location_name
    if len(cs_name) <= 0:
        cs_name = str(input("Enter hosted service name. This name is the DNS prefix name and can be used to access the hosted service"))
        while isHostedCSNameUnique == False:            
            res_cs_Name = svc.check_hosted_service_name_availability(cs_name)
            if res_cs_Name.result == True:
                isHostedCSNameUnique = True
                if len(cs_label) <= 0:
                    cs_label = str(input("Enter hosted service label"))
                if len(cs_description) <= 0:
                    cs_description = str(input("Enter hosted service description"))
                if len(cs_location) <= 0:
                    cs_location = str(input("Enter hosted service location"))
                svc.create_hosted_service(cs_name, cs_label,cs_description,cs_location)
                isHostedServiceCreated = True
                
            else:    
                print(res_cs_Name.body)
                cs_name = str(input("The host service name entered is already in use, please another one or press E to exit"))
                if cs_name == "E" or cs_name == "e":
                    isHostedServiceCreated = False
                    break
    if isHostedServiceCreated == True:
        print("Hosted service... " + cs_name + " created")  
    else:
        print("Hosted service could not be created")
def Create_VNet():
    # Creating VNet
    input_option = str(input("Do you have a Vnet configured? Y for Yes, N for No..."))
    if input_option == "Y" or input_option == "y":
        vnet_name = str(input("Please enter vnet name..."))  
    else:
        # creating a vnet from existing file?
        is_vnet_file = str(input("Do you have a pre-created vnet configuration xml file? please enter Y for Yes, N for No..."))        
        if is_vnet_file == "Y" or is_vnet_file == "y":
            vnet_file = str(input("Please enter the complete/absolute file path..."))
            file_created_path = vnet_file
            vnet_rest_api_path = "https://management.core.windows.net/" + subscription_id + "/services/networking/media"
            AzureHttpRequests.create_vnet(vnet_rest_api_path,file_created_path)
        else:
            # Input from JSon - Version 2
            print("Requesting all parameters...")
            vnet_name = str(input("Please enter a vnet name you wish to create..."))
            if len(storage_location_name) <= 0:
                vnet_location = str(input("Please enter location you wish to create the vnet in..."))
            else:
                vnet_location = storage_location_name             
            
            ### check vnet name availability .... version 2
            is_dns = str(input("Do you have dns servers to create? Please enter Y for Yes and N for No.... "))
            is_more_dns = True
            dns = []
            while is_more_dns == True:
                dns_inp = str(input("Enter dns server name, IPAddress seperated by ','ex: (www.abc.com,111.23.45.66), or press E after entering all dns entries ..."))
                if dns_inp != "E" and dns_inp != "e":
                    dns_val = dns_inp.split(",")
                    if len(dns_val) == 2:
                        dns_name = dns_val[0]
                        dns_addr = dns_val[1]
                        # check if IP Address is valid - Version 2
                        dns.append({"name":dns_name,"IP_address":dns_addr})                                                
                else:
                    is_more_dns = False
                    break
            ### Version 2 : Local network site inputs
            ### Entering Address Space
            ### Entering Virtual network subnet entries
            ## Defaulting address space and subnet values (for version 1)
            addr_space = "10.0.0.0/8"
            subnet_det = {"name":"Subnet-1","addr":"10.0.0.0/11"}
            if len(config_file_path) <=0:
                config_file_path = str(input("Please enter the configuration save file path..."))
            file_created_path = XmlSerializerVMCluster.create_vnet_config_xml(vnet_name,vnet_location,dns,addr_space,subnet_det,config_file_path)
            vnet_rest_api_path = "https://management.core.windows.net/" + subscription_id + "/services/networking/media"
            AzureHttpRequests.post_request(vnet_rest_api_path,file_created_path)

def Get_Res_Ext_List():
    chef_server_url = "<Chef server url>"
    validation_client_name = "<validation client name>"
    run_list = "role[percona]"
    ## for multiple cook books and receipes:   run_list = "recipe[cookbook1::recipe1],role[test_role1],recipe[cookbook2::recipe2],role[test_role2]"
    ##Note- update following path with your local
    validation_key_file_path = "<validation.pem file path>"

    res_ext_ref = []
    res = ResourceExtensionReference()
    res.reference_name="LinuxChefClient"
    res.name = "LinuxChefClient"
    res.publisher = "Chef.Bootstrap.WindowsAzure"
    res.version = "11.16"
    res.label = "LinuxChefClient"

    # Sets the public configuration for extension
    res_chef_client_rb = ResourceExtensionParameterValue()
    res_chef_client_rb.key = "PublicParams"
    pub_config = {}
    pub_config['client_rb'] = "chef_server_url \t %s\nvalidation_client_name\t%s" % (json.dumps(chef_server_url), json.dumps(validation_client_name))
    pub_config['runlist'] = json.dumps(run_list)
    res_chef_client_rb.value = _encode_base64(json.dumps(pub_config))
    res_chef_client_rb.type = "Public"

    # Sets the Private configuration for extension
    res_chef_client_validation = ResourceExtensionParameterValue()
    res_chef_client_validation.key = "PrivateParams"
    validation_key_file = open(validation_key_file_path, "r+")
    pri_config = {}
    pri_config['validation_key'] = validation_key_file.read()
    res_chef_client_validation.value = _encode_base64(json.dumps(pri_config))
    res_chef_client_validation.type = "Private"

    res.resource_extension_parameter_values.resource_extension_parameter_values.append(res_chef_client_rb)
    res.resource_extension_parameter_values.resource_extension_parameter_values.append(res_chef_client_validation)

    res_ext_ref.append(res)
    return res_ext_ref 

def Create_Virtual_Machine_Single(cs_name,deployment_name,label,role_name,system_config=None,os_hd=None,role_size="Small",resource_ext_refs=None,vnet_name=None,provision_guest_agent="true",network_config=None,add_role=False,vm_number=" "):
    # Creates a single VM based on parameters passed
    if add_role == False:
        result = svc.create_virtual_machine_deployment(service_name=cs_name,
        deployment_name=deployment_name,        
        deployment_slot='production',
        label=cs_name,
        role_name=role_name,
        system_config=system_config,
        os_virtual_hard_disk=os_hd,
        role_size='Small',
        resource_extension_references=resource_ext_refs,
        virtual_network_name=vnet_name,
        provision_guest_agent='true',
        network_config=network_config)
        return result
    else:
        result = svc.add_role(service_name=cs_name,deployment_name=deployment_name,role_name=role_name,system_config=system_config,os_virtual_hard_disk=os_hd,network_config=network_config,role_size=role_size,resource_extension_references=resource_ext_refs,provision_guest_agent=provision_guest_agent)
        return result

               
def Create_Virtual_Machine_New():
    
    ## Initializing cloud service and Vnet name

    cs_name = " "
    vnet_name = " "

    cs_name = input("Please enter the cloud service name")
    vnet_name = input("Please enter the vnet name")

    if len(cs_name) <= 0:
        Create_HostedService()
    vm_name = cs_name + "01"
    ### Modify the code to get Chef Extension

    res_ext_ref = Get_Res_Ext_List()
    #res_ext_ref = None   
    
    linux_config = LinuxConfigurationSet(host_name=vm_name,user_name="azureuser",user_password="MicrosoftDx1",disable_ssh_password_authentication="false")
    
    network = ConfigurationSet()
    network.configuration_set_type = "NetworkConfiguration"
    network.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('ssh', 'tcp', '22', '22'))
    network.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('http', 'tcp', '80', '80'))
    
        
    network_02 = ConfigurationSet()
    network_02.configuration_set_type = "NetworkConfiguration"
    network_02.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('ssh', 'tcp', '223', '22'))
    network_02.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('http', 'tcp', '8023', '8023'))
    
    network_03 = ConfigurationSet()
    network_03.configuration_set_type = "NetworkConfiguration"
    network_03.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('ssh', 'tcp', '224', '22'))
    network_03.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('http', 'tcp', '8024', '8024'))
    
        
    vm_number = " "
    
    #disk_name="debian77_01",
    #source_image_name="pipedriveimage"
    ### VM1
    os_hd = OSVirtualHardDisk(source_image_name="b39f27a8b8c64d52b05eac6a62ebad85__Ubuntu-14_04_1-LTS-amd64-server-20140927-en-us-30GB",media_link="https://<storage account name>.blob.core.windows.net/vhds/" + cs_name + "pipedrivevhd010101sgvr01.vhd",os="Linux")
    os_hd_01 = OSVirtualHardDisk(source_image_name="b39f27a8b8c64d52b05eac6a62ebad85__Ubuntu-14_04_1-LTS-amd64-server-20140927-en-us-30GB",media_link="https://<storage account name>.blob.core.windows.net/vhds/" + cs_name + "pipedrivevhd020202sgvr02.vhd",os="Linux")
    os_hd_02 = OSVirtualHardDisk(source_image_name="b39f27a8b8c64d52b05eac6a62ebad85__Ubuntu-14_04_1-LTS-amd64-server-20140927-en-us-30GB",media_link="https://<storage account name>.blob.core.windows.net/vhds/" + cs_name + "pipedrivevhd030303sgvr03.vhd",os="Linux")

    resvm_01 = Create_Virtual_Machine_Single(cs_name=cs_name+"01",
    deployment_name=cs_name+"01",    
    label=cs_name+"01",
    role_name=cs_name+"01",
    system_config=linux_config,
    os_hd=os_hd,
    role_size='Small',
    resource_ext_refs=res_ext_ref,
    vnet_name=vnet_name,
    provision_guest_agent="true",
    network_config=network,add_role=False,vm_number="01")
    

    # Install_Chef

    

    
    
    ## VM2

        
        
    linux_config_02 = LinuxConfigurationSet(host_name=cs_name+"02",user_name="azureuser",user_password="MicrosoftDx1",disable_ssh_password_authentication="false")

    resvm_02 = Create_Virtual_Machine_Single(cs_name=cs_name+"02",
    deployment_name=cs_name+"02",    
    label=cs_name+"02",
    role_name=cs_name+"02",
    system_config=linux_config_02,
    os_hd=os_hd_02,
    role_size='Small',
    resource_ext_refs=res_ext_ref,
    vnet_name=vnet_name,
    provision_guest_agent="true",
    network_config=network_02,add_role=False,vm_number="02")
    result_status_02 = False
    res_ops_status_02 = False

    
    
    
    linux_config_03 = LinuxConfigurationSet(host_name=cs_name+"03",user_name="azureuser",user_password="MicrosoftDx1",disable_ssh_password_authentication="false")

    resvm_03 = Create_Virtual_Machine_Single(cs_name=cs_name+"03",
    deployment_name=cs_name+"03",    
    label=cs_name+"03",
    role_name=cs_name+"03",
    system_config=linux_config_03,
    os_hd=os_hd_01,
    role_size='Small',
    resource_ext_refs=res_ext_ref,
    vnet_name=vnet_name,
    provision_guest_agent="true",
    network_config=network_03,add_role=False,vm_number="03")
    
    print("Submitted successfully...")    
    
        ## get the result status




  
        

  

               
if __name__ == "__main__":
    print("This script creates VM clusters, and also other Azure components. Enter 'vm' parameter to create VMs, 'cs' to create cloud service, 'sa' to create storage account")
    inp = input("Enter your choice")
    if inp == "vm":
        Create_Virtual_Machine_New()
    else:
        if inp == "cs":
            Create_HostedService()
        else:
            if inp == "sa":
                Create_StorageAccount()
            else:
                print("Invalid parameter exiting code") 

    