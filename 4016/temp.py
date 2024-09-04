import http.client

conn = http.client.HTTPSConnection("")

headers = { 'apiKeySecret': "HV53QHLOEJC7NKGPDPQWHQKTS2PJLLODCPj5+NnsOBSyybHynCl5QCicZCtkPMRDUHiO4h3LTDvB/G90rbV8QP7CNQCgwJjP" }

conn.request("GET", "finra/public/api/customers/b3cd90f0-0ae7-48e7-85f1-417fd416ba61/", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))