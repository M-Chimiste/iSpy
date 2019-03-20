# Purpose: To define a list of IP Addresses and then iterate through them in
# order to find all of the connections on the network
# The IP Address information is then passed through ns-lookup to allow
# for cross referencing to other reports.

# Import dependencies
import ipaddress as ip
import os
import platform
import time


# Function: readInput
# Purpose: import a CSV and return a list of IP Addresses
def readInputAddress(inputFile):
    file = open(inputFile, 'r')
    lines = file.readlines()
    inputIPs = []
    address = ''
    for i in lines:
        address = i.strip('\n')
        address = address.split(',')
        inputIPs.append(address[0])
    return inputIPs


def readInputDNS(inputFile):
    file = open(inputFile, 'r')
    lines = file.readlines()
    inputDNS = []
    dnsName = ''
    for i in lines:
        dnsName = i.strip('\n')
        dnsName = dnsName.split(',')
        inputDNS.append(dnsName[1].lower())
    return inputDNS


# Function: Define Network
# Purpose: To take the system IP Address and subnet mask and return a list of
# IP Addresses for the network.
def defineNetwork(address, mask):
    iPv4Address = address + "/" + mask
    networkList = []
    ipaddress = ""
    n = 0
    network = ip.IPv4Network(iPv4Address, False)
    for i in network:
        ipaddress = str(network[n])
        networkList.append(ipaddress)
        n = n + 1
    return networkList


class IPAddress:
    def __init__(self, address, pingResponse, isLive, name):
        self.address = address
        self.pingResponse = pingResponse
        self.isLive = isLive
        self.name = name


# Function: writeIPAddress
# Purpose: To input a class IPAddress and then write the values to a line in
# an output
    def writeIPAddress(self, IPAddress, f):
        address = str(IPAddress.address)
        response = str(IPAddress.pingResponse)
        isLive = str(IPAddress.isLive)
        DNS = str(IPAddress.name)
        line = address + ',' + response + ',' + isLive + ',' + DNS + '\n'
        f.write(line)


# Function: pinging
# Purpose: To ping a given network address and return a value
# Will also check os to make sure appropriate parameters
def pinging(address):
    isLive = False
    if platform.system().lower() == "windows":
        args = " -n 3 "
    else:
        args = " -c 3 "
    pingResponse = os.popen('ping ' + args + address).read()
    responseList = pingResponse.split('\n')
    response = responseList[2]
    if 'TTL=' in response:
        isLive = True
    return {'isLive': isLive, 'response': response}


# Function: nameLookUp
# Purpose: To get the DNS name of a system on network
def nameLookUp(address, isLive):
    nsResponse = os.popen('nslookup ' + address).read()
    nsResponseList = nsResponse.split('\n')
    name = nsResponseList[3]
    nameList = name.split(' ')
    index = len(nameList)-1
    name = nameList[index]
    if isLive is not True and name == '':
        name = 'No DNS Name Host Offline'
        return name
    elif isLive is True and name == '':
        name = 'No DNS Name Host Online'
        return name
    else:
        return name


# Function: fileNamer
# Purpose: To take a filename and an extension and generate a full file name
# Will check to make sure the name doesn't exist so that it isn't overwritten.
def fileNamer(filename, extension):
    n = 1
    fullFileName = filename + extension
    while os.path.exists(fullFileName):
        fullFileName = filename + "_" + str(n) + extension
        n = n + 1
    return fullFileName


# Function: iterateIPs
# Purpose: to input a list of IP addresses and write the output to a file.
def iterateIPs(networkList, f1, f2='', DNSList=[]):
    counter = 1
    totalLines = len(networkList)
    # Default behavior if option 1 is selected
    if len(DNSList) == 0:
        for i in networkList:
            time.sleep(2)
            print("Trying IP Address " + str(counter) + " of " + str(totalLines))
            percentage = counter / totalLines * 100
            percentage = float("{0:.2f}".format(percentage))
            print(str(percentage) + "% Complete")
            counter = counter + 1
            pingingVals = pinging(i)
            isLive = pingingVals['isLive']
            response = pingingVals['response']
            name = nameLookUp(i, isLive)
            if isLive is False:
                isLive = 'False'
                currentIP = IPAddress(i, response, isLive, name)
                IPAddress.writeIPAddress(currentIP, f1)
            else:
                isLive = 'True'
                currentIP = IPAddress(i, response, isLive, name)
                IPAddress.writeIPAddress(currentIP, f1)
        f1.close()
        # Behavior if option 2 is selected and you have a list of DNS names
    else:
        n = 0
        for i in networkList:
            time.sleep(2)
            print("Trying IP Address " + str(counter) + " of " + str(totalLines))
            percentage = counter / totalLines * 100
            percentage = float("{0:.2f}".format(percentage))
            print(str(percentage) + "% Complete")
            counter = counter + 1
            pingingVals = pinging(i)
            isLive = pingingVals['isLive']
            response = pingingVals['response']
            name = nameLookUp(i, isLive)
            if isLive:
                isLive = 'True'
                isLiveArray = ['True', isLive]
            else:
                isLive = 'False'
                isLiveArray = ['True', isLive]
            currentIP2 = IPAddress(i, response, isLive, name)
            IPAddress.writeIPAddress(currentIP2, f2)
            isLive = reportDifferences(isLiveArray)
            nameDNS = DNSList[n]
            DNSArray = [nameDNS, name]
            name = reportDifferences(DNSArray)
            currentIP = IPAddress(i, response, isLive, name)
            IPAddress.writeIPAddress(currentIP, f1)
            n = n + 1
        f1.close()
        f2.close()


# Function initializeOutput
# Purpose: Will write the first line of an output file
def initializeOutput(fullFileName):
    firstLine = "Address" + "," + "Response" + "," + "Is Live" + "," + "DNS Name" + "\n"
    f = open(fullFileName, 'w')
    f.write(firstLine)
    return f


# Function: reportDifferences
# Purpose: evaluate a list of two and determine changes
# Will return a single sring value.
def reportDifferences(x):
    return x[0] if x[0] == x[1] else '{} ---> {}'.format(*x)


# Function: generateFromIPCalculator
# Purpose: Take user input, generate a list of IP Addresses and write a file
# that contains the ping and nslookup values of that list.
def generateFromIPCalculator():
    willContinue = True
    outputFile = "Network_List"  # root output filename
    extensionName = ".csv"  # file extension
    fullFileName = fileNamer(outputFile, extensionName)
    outfile = initializeOutput(fullFileName)

    # Gather user input
    networkIP = input('Enter your network IP Address:  ')
    networkMask = input('Enter the subnet mask:  ')

    # Build the network list
    networkList = defineNetwork(networkIP, networkMask)
    totalLines = len(networkList)
    print("The network has a total of " + str(totalLines) + " IP Addresses")
    iterateIPs(networkList, outfile)

    # loop to verify input
    while willContinue:
        userInput = input("Action Complete.  Do you want to run the program again? (y/n)")
        if userInput == "y":
            shouldContinue = True
            willContinue = False
        elif userInput == "n":
            shouldContinue = False
            willContinue = False
        else:
            print("Invalid Entry, please try again.")
    return shouldContinue


# Function: generateFromInputList
# Purpose: To take an input of IPs and DNS names and output the results of
# pinging and nslookup
def generateFromInputList():
    willContinue = True
    inputs = "input.csv"
    outputFile = "Formatted_Network_List"
    extensionName = ".csv"
    outputFile2 = "Raw_Network_List"

    # Name the output file and initialize it
    fullFileName = fileNamer(outputFile, extensionName)
    outfile = initializeOutput(fullFileName)
    fullFileName2 = fileNamer(outputFile2, extensionName)
    outfile2 = initializeOutput(fullFileName2)

    # Read the input file
    networkList = readInputAddress(inputs)
    DNSList = readInputDNS(inputs)
    totalLines = len(networkList)
    print("The network has a total of " + str(totalLines) + " IP Addresses")
    iterateIPs(networkList, outfile, outfile2, DNSList)

    # Loop to verify input
    while willContinue:
        userInput = input("Action Complete.  Do you want to run the program again? (y/n)")
        if userInput == "y":
            shouldContinue = True
            willContinue = False
        elif userInput == "n":
            shouldContinue = False
            willContinue = False
        else:
            print("Invalid Entry, please try again.")
    return shouldContinue


# Function: generateFromExcludedList
# Purpose: To input a known list and exclude those elements from the scanning
# list in order to determine what is on the network.
def generateFromExcludedList():
    willContinue = True
    inputs = "input.csv"
    outputFile = "Excl_Network_List"
    extensionName = ".csv"
    file = open("test.txt", 'w')
    # Name the output file and initialize it
    fullFileName = fileNamer(outputFile, extensionName)
    outfile = initializeOutput(fullFileName)

    # Read the input file
    excNetworkList = readInputAddress(inputs)

    # Get user input for IP calculator
    networkIP = input('Enter your network IP Address:  ')
    networkMask = input('Enter the subnet mask:  ')
    calcNetworkList = defineNetwork(networkIP, networkMask)

    # Remove the getDuplicates
    networkList = list(set(calcNetworkList) - set(excNetworkList))
    totalLines = len(networkList)
    file.writelines(networkList)
    file.close()
    print("The network has a total of " + str(totalLines) + " IP Addresses")
    iterateIPs(networkList, outfile)
    # Loop to veryify input
    while willContinue:
        userInput = input("Action Complete.  Do you want to run the program again? (y/n)")
        if userInput == "y":
            shouldContinue = True
            willContinue = False
        elif userInput == "n":
            shouldContinue = False
            willContinue = False
        else:
            print("Invalid Entry, please try again.")
    return shouldContinue


# Main Loop
def main():
    shouldContinue = True
    print("Please select one of the following functions:")
    print("1. Generate an output by entering IP and subnet")
    print("2. Generate an output by importing a list of IP addresses")
    print("3. Generate and output by importing a list and an IP address and excluding the values in the input list")
    while shouldContinue:
        userInput = input("Please enter a number:  ")
        if userInput == '1':
            shouldContinue = generateFromIPCalculator()
        elif userInput == '2':
            shouldContinue = generateFromInputList()
        elif userInput == '3':
            shouldContinue = generateFromExcludedList()
        else:
            print("Invalid Entry, please try again")
            shouldContinue = True


# Main program logic
if __name__ == '__main__':
    main()
