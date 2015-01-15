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
import optparse
from optparse import OptionParser

subscription_id = "5c78935e-b33b-4b89-b627-b32fd08408f5"

if __name__ == "__main__":
    request_id = ""
    parser = OptionParser()
    parser.add_option("-r","--r",dest="request_id")
    if len(sys.argv) > 0:
        opts,args = parser.parse_args(sys.argv)
        request_id = opts.request_id
        print(request_id)
        if request_id != "":            
            AzureHttpRequests.get_request("https://management.core.windows.net/" + subscription_id +"/operations/" + request_id, request_id)
        else:
            print("Invalid parameter please enter the request ID using the -r, --r paramater")
    else:
        print("Please enter the request ID using the -r, --r parameter")