import requests
from bs4 import BeautifulSoup
import json
import sys,os
import re
import datetime
import time




def isLineAnIP(string):
	try:
		if(type(int(string[0])) == int):
			return True
		else:
			return False
	except Exception as e:
		return False
def pageRequest(workingList):
	target = "https://www.us-proxy.org/"
	print("Opening "+ target)
	r = requests.get(target)
	soup = BeautifulSoup(r.content, 'html.parser')
	info = soup.find("textarea", {"class": "form-control"})
	info = info.get_text()
	for line in info.splitlines():
		if(isLineAnIP(line) == True):
			print(line+"\t",end="\r")
			workingList.append(line)

def jsonRequest(workingList):
	proxyTargetJson = ["https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps"]
	for proxySite in proxyTargetJson:
		print("Opening "+proxySite)
		r = requests.get(proxySite)
		jsonList = json.loads(r.content)
		for proxy in jsonList["data"]:
			proxy = proxy["ip"] + ":" + proxy["port"]
			print(proxy,end="\r")
			workingList.append(proxy)
def txtRequest(workingList):
	proxyTargetTxt = ["https://spys.me/proxy.txt"]
	proxyTargetTxt.extend(["https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"])
	proxyTargetTxt.extend(["https://advanced.name/freeproxy/62412bf14e517"])
	for proxySite in proxyTargetTxt:
		#Format is IP:PORT:NONSENSE
		print("Opening "+proxySite)
		r = requests.get(proxySite)
		for proxy in r.iter_lines():
			proxy = str(proxy).strip("b'")
			try:
				if(type(int(proxy[0])) == int):
					proxy = proxy.split(":")
					ip = proxy[0]
					port = proxy[1]
					port = port.split(" ")
					port = port[0]
					proxy = str(ip) + ":" + str(port)
					print(proxy, end="\r")
					workingList.append(proxy)
				else:
					#badList.append(proxy)
					pass
					#print("not int")
			except Exception as e:
				continue
				#print(e)
def getProxy():
	workingList = []
	pageRequest(workingList)
	txtRequest(workingList)
	jsonRequest(workingList)
	print("Total Proxies Fetched: " +str(len(workingList)))
	outputFetchedProxies(workingList)
	while(True):
		selectionValidate = input("Validate Proxies? (Y/N): ")
		if(selectionValidate.lower() == "y"):
			validateProxies(workingList)
			break
		elif(selectionValidate.lower() == "n"):
			break
		else:
			print("Invalid Input.")
def checkProxy(ip,validatedList):
	proxies = {
   'http': ip,
   'https': ip,
	}
	try:
		r = requests.get("http://ip-api.com/line/",proxies=proxies)
		return True
	except Exception as e:
		#print(ip+"\tFailed")
		try:
			r = requests.get("http://www.whatismyip.com/ip-address-lookup/")
			return True
		except:
			return False


def validateProxies(workingList):
	validatedList = []
	badlist = []
	startTime = time.time()

	if(workingList == "None"):#If there are no items in workinglist then prompt the user to select from previously saved proxy files in the /proxies/ folder
		workingList = []
		directory = loadDirectories()
		if(directory != 0):
			script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
			absolutepath = os.path.join(script_dir, "proxies\\"+directory)
			#print("Loaded proxies from " + absolutepath)
			f = open(absolutepath, "r")
			for line in f:
				workingList.append(line)
			f.close()
	print("Checking "+str(len(workingList)) + " proxies")
	if(len(workingList) > 0):
		for number,line in enumerate(workingList):
			number+=1
			if(checkProxy(line,validatedList) == True):
				validatedList.append(line)
				print(line + "\tSuccess\t" + "("+str(number)+"/"+str(len(workingList))+")")
			else:
				badlist.append(line)
				print(line + "\tFailed\t" + "("+str(number)+"/"+str(len(workingList))+")")
		outputValidProxies(validatedList,startTime)

def outputFetchedProxies(workingList):
	date = datetime.datetime.now()
	newFileDate = str(date.year) + "-" + str(date.month)+ "-" +str(date.day) + "-" + str(date.hour)+str(date.minute)+str(date.second)
	newFile =  "proxylist_" + newFileDate + ".txt"
	with open("proxies/"+newFile, "w") as myfile:
		for item in workingList:
			myfile.write(item+"\n")
	myfile.close()

	print("Saved fetched proxies under proxies/"+newFile)
def outputValidProxies(validatedList,startTime):
	date = datetime.datetime.now()
	timeElapsed = time.time() - startTime
	print(str(len(validatedList)) +" valid proxies!")
	print("Took "+str(round(timeElapsed,2))+" seconds to validate proxies.")
	newFileDate = str(date.year) + "-" + str(date.month)+ "-" +str(date.day) + "-" + str(date.hour)+str(date.minute)+str(date.second)
	newFile =  "validatedproxies_" + newFileDate + ".txt"
	with open("validated/"+newFile, "w") as myfile:
		for item in validatedList:
			myfile.write(item+"\n")
	myfile.close()
	print("All validated proxies stored under validated/"+newFile)

def option1():
	try:
		getProxy()
	except KeyboardInterrupt:
		print("User Cancelled.")
def cuteTable(row1,row2,row3,row4,row5):
  #print(row1.ljust(4) + row2.ljust(3) + row3.ljust(30) + row4.rjust(8) + row5.rjust(4))
  print ("{:<2} {:<3}{:<30} {:<9} {:<2}".format(row1,row2,row3,row4,row5))


def loadDirectories():
	directory = "proxies"
	print("Files available to validate in directory '"+directory+"'")
	#print("|\t" +str("#") + "\t" + "Filename\t"+ "Size\t\t\t|")
	print("_________________________________________________")
	cuteTable("|","#","FileName","Size","|")
	files = {}

	for number,filename in enumerate(os.listdir(directory)):
		number+=1
		f = os.path.join(directory, filename)
		if os.path.isfile(f):
			files[str(number)] = filename#dictionary
			size = os.path.getsize(f) 
			size = size / 1000
			size = round(size,2)
			cuteTable("|",str(number),filename,str(size)+" KB","|")
			#print("|\t" +str(number) + "\t" + filename+ "\t"+str(size)+"KB\t|")
	print("_________________________________________________")
	if(files == {}):
		print("There are no files under the /proxies/ directory, store a proxy list there to check them!")
		return 0
	selectFile = input("Enter a number:")
	openFile = files[selectFile]
	print("Using file '" +openFile+"'")
	return openFile
def option2():
	validateProxies("None")
	#outputProxies()
	input("Press ENTER to continue")

while(True):
	print("______________________________________")
	print("\t1:\t Get new proxies")
	print("\t2:\t Validate saved proxies")
	print("______________________________________")
	option = input("Choose an option: ")
	if(option == "1"):
		option1()
	elif(option == "2"):
		option2()
	else:
		print("Invalid Option")