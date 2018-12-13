#!/usr/bin/python
import subprocess
import readline

#auto generates a SERIAL based on date of system
def SERIALGEN():
  import datetime
  RAWDATE = datetime.datetime.now()
  DATESTR = str(RAWDATE)[0:10]
  SERIAL = str((DATESTR)[0:4] + (DATESTR)[5:7] + (DATESTR)[8:10] + "00")
  return SERIAL

def BANNER():
   print """\n            ****************************************************************          
            *        Welcome to the super zone creator version 1.0!        *
            *  Follow the prompts as shown and this will do ALL the work!  *
            *      What it does: Create the files, fill in the headers     *
            *      add them to the zones file, and reconfig and reload     *
            *                          if needed                           *
            ****************************************************************"""

# this code(lines 22-44) was made by pootzko thank you dude!
# heavily modified to only generate /24 addresses ie stop at the third octet
# and accepts start ip and number of subnets as opposed to start and end IP
def RANGEMAKER(IPSTART,SUBNETS):
 # this first bit takes the start IP and makes an int list
 # meaning no .'s are involved in the data manipulation
 START = list(map(int, IPSTART.split(".")))
 # creates a TEMPIP value that will be worked with and starts the
 # ip range list
 TEMPIP = START
 TEMPIP.pop()
 IPRANGE = []
 # manually adds the .0 of the beginning octet so it isnt lost
 # in the loop
 IPRANGE.append(".".join(map(str, TEMPIP)))
 # runs the for loop to fill out the IPRANGE value
 ranger = int(SUBNETS)- 1
 for i in range(0,ranger):
    START[2] += 1
    # converts the TEMPIP value back into str and then maps it into list
    # that is then reunited with its .'s to build the IP address 
    IPRANGE.append(".".join(map(str, TEMPIP)))    
 return IPRANGE

#returns the default value if no value passed on user input or if it 
# is the same as the default, otherwise it returns the user input
def DEFAULTER(DEFAULTVALUE,QUERY):
  ENTEREDVALUE = raw_input(str(QUERY))
  if ENTEREDVALUE.strip() == '':
    return DEFAULTVALUE
  elif ENTEREDVALUE == DEFAULTVALUE:
    return DEFAULTVALUE
  else :
    return ENTEREDVALUE.lower()

# separates subnet and netmask, whether its cidr or dot notation
# if the mask section is less than 3 characters ie a 23 or 24 etc
# passes the value as an int if not returns the str instead so when this
# is passed to the netmaskgen function it can translate the cidr value or
# leave it as is, will also return the IP addres given the right flag. 0 
# returns the netmask and 1 returns the IP address
def IPCUTTER(IPBASE,IPMASK):
  for i in range(len(IPBASE)):
    if IPBASE[i] == "/":
      IPCUT = IPBASE.split("/")
      break
    else:
      IPCUT = IPBASE.split(" ")
  if IPMASK == 0:
    CUTCIDR = str(IPCUT[0])
  elif IPMASK == 1:
    if len(IPCUT[1]) < 3:
      CUTCIDR = int(IPCUT[1])
    else:
      CUTCIDR = str(IPCUT[1])
  return CUTCIDR

# generates the netmasks for /8-/31 in order to translate CIDR into netmask
# with the intention to pass to a different function to gen range based on
# netmask value, currently it translates cidr and if netmasks are passed it
# will just return the netmask value passed
def NETMASKGEN():
  MASKBASE = "255.0.0.0"
  MASKTEMP = list(map(int, MASKBASE.split(".")))
  MASKLIST = []
  MASKLIST.append(".".join(map(str, MASKTEMP)))
  INCREMENTER = 128
  i = 1
  while i != 4:
    if MASKTEMP[i] != 255:
      MASKTEMP[i] += int(INCREMENTER)
      INCREMENTER /= 2
    else:
      INCREMENTER = 128
      i += 1
    # if else to handle 0's because duplicate values are made
    # otherwise
    if INCREMENTER == 0:
      foo = 1
    else:
      MASKLIST.append(".".join(map(str, MASKTEMP)))
  MASKLIST.pop()
  return MASKLIST

# fucntion to make sure if a netmask bigger than a 
# 255.255.224.0 or smaller than a 255.255.255.0 
# is entered it does not allow the rest 
# of the script to complete
def NETMASKLIMITER(NETMASK,MASKLIST):
  for i in range(11,17):
    if len(str(NETMASK)) < 3:
      return 0
    else:
      if NETMASK == MASKLIST[i]:
        return NETMASK
  return 1

# compares the netmask and cidr and returns a netmask value
# for /19-/24 if its already a netmask it just returns the
# netmask
def MASKCOMPARE(CIDR):
  MASKLIST = list(NETMASKGEN())
  CIDRCHECK = NETMASKLIMITER(CIDR,MASKLIST)
  if CIDRCHECK == 0:
    for i in range(19,25):
      if CIDR == i:
        CIDR = MASKLIST[i-8]
    return CIDR
  elif CIDRCHECK == 1:
    return "00"
  else:
    return CIDR

# This takes the netmask and returns how many subnets
# should be made based on that netmask
def SUBNETTER(MASK):
  NETBASE = list(map(int, "255.255.224.0".split(".")))
  NETSPLIT = list(map(int, MASK.split(".")))
  INCREMENTDOWN = 16
  SUBNETS = "32"
  if NETSPLIT[2] == 224:
    return SUBNETS
  else:
    while NETBASE[2] != 256:
      SUBNETS = str(INCREMENTDOWN)
      NETBASE[2] += INCREMENTDOWN
      INCREMENTDOWN /= 2
      if NETSPLIT[2] == NETBASE[2]:
        return SUBNETS

# changes the ownership and permissions of the zone files
def CHMODOWNER(ZONELIST):
  for i in range(len(ZONELIST)):
    subprocess.call(["sudo","chown", "root:named", str(ZONELIST[i])])
    subprocess.call(["sudo","chmod", "775", str(ZONELIST[i])])
  print "\nThe zone file(s) have been given the following permissions and ownership (775) (root:named)."

# makes the files and fills them with the DNS header
# also makes a list of the filenames so they can be manipulated
def FILEGEN (ZONENUM,DOMAIN):
  ZONELIST = list(())
  for i in range(0,ZONENUM):
    with open("db." + str(DOMAIN[i]),"w+") as ZONEFILE:
      ZONEFILE.write("$TTL " + str(TTL) + "\n" + "@            IN SOA  ns1.neonova.net. hostmaster.neonova.net. (\n                        " + str(SERIALGEN()) + " ; Serial      \n                        43200      ; refresh (12 hours)\n                        3600       ; retry (1 hour)\n                        604800     ; expire (1 week)\n                        900        ; minimum (15 minutes)\n                        )\n                        NS      ns1.neonova.net.\n                        NS      ns2.neonova.net.")
      ZONELIST.append("./db." + str(DOMAIN[i]))
  print "\nThe following files have been created:\n"
  for i in range(0,ZONENUM):
    print str(ZONELIST[i][2::])
  CHMODOWNER(ZONELIST)
  return ZONELIST

# Moves the files to the entered path by calling bash
def FILEMOVER(ZONELIST,ZONEPATH):
  if ZONEPATH == ".":
    print "\nNo files have moved as the script has been run from the\ndirectory the files should be in."
  else:
    for i in range(len(ZONELIST)):
      subprocess.call(["mv", str(ZONELIST[i]), str(ZONEPATH)])
    print "\nThe generated files have been moved to " + ZONEPATH + "'s directory."

# removes leading directory path entries so that the zone entries
# only have /master/domain.ext or /master/rev/domain.ext
def ZONEADDERPATHGET(ZONEPATH):
  PATH = list(map(str, ZONEPATH.split("/")))
  if ZONEPATH[0] == ".":
    import os
    GETPATH = os.getcwd()
    PATH = list(map(str, GETPATH.split("/")))
    PATH.remove("var")
    PATH.remove("named")
    PATH.remove("chroot")
    PATH.remove("var")
    PATH.remove("named")
  elif PATH[1] == "var":
    PATH = list(map(str, ZONEPATH.split("/")))
    PATH.remove("")
    PATH.remove("var")
    PATH.remove("named")
  return PATH

# reverse the IP and adds in-addr.arpa for IPs or
# just the domain if forward zone
def IPREVERSER(DIRECTION,DOMAIN,i):
  if DIRECTION == "reverse":
        NETSPLIT = list(map(int, DOMAIN[i].split(".")))
        NETSPLIT.reverse()
        NETJOIN = ".".join(map(str, NETSPLIT)) + ".IN-ADDR.ARPA"
  elif DIRECTION == "forward":
        NETJOIN = DOMAIN[i]
  return NETJOIN

# creates a file called zoneadder that contains the zone entries for the
# created zone files, creates a bash script to move the contents of that
# file into the zones file of the indicated directory and then removes
# both of those files. Also makes a backup of the zones file just in case
def ZONEADDER(DOMAIN,DIRECTION,ZONEPATH):
  REFDOMAIN = "/".join(map(str, ZONEADDERPATHGET(ZONEPATH)))
  ENTRYLIST = list(())
  for i in range(0,len(DOMAIN)):
    NETJOIN = IPREVERSER(DIRECTION,DOMAIN,i)
    ZONEENTRY = "\nzone \"" + NETJOIN + r"""" {""" + "\n        type master;\n        file \"" + REFDOMAIN + r"/db." + DOMAIN[i] + "\";\n};"
    ENTRYLIST.append(ZONEENTRY)
  for i in range(0, len(ENTRYLIST)):
    with open("zoneadder","a") as ZONEENTRY:
      ZONEENTRY.write(ENTRYLIST[i])
  subprocess.call(["mv", "zoneadder",ZONEPATH])
  with open("basher","w+") as BASHER:
    BASHER.write("#!/bin/bash\necho \"$(cat "+ZONEPATH+"/zoneadder)\" >> "+ZONEPATH+"/zones")
  subprocess.call(["sudo","cp",ZONEPATH+"/zones",ZONEPATH+"/zones.bak"])
  subprocess.call(["chmod","775","basher"])
  subprocess.call(["sudo","./basher"])
  subprocess.call(["sudo","rm","basher"])
  subprocess.call(["sudo","rm",ZONEPATH+"/zoneadder"])
  print "\nThe zone entries have been added successfully!"

# reconfigures the zones file and reloads the domains
def RECONRELOAD(DIRECTION,DOMAIN,ZONEPATH):
  AREYOUSURE = DEFAULTER("no","\nAbout to reconfig zones and reload the files\nIs it okay to proceed(yes/no)(default is no)")
  if AREYOUSURE == "yes":
    subprocess.call(["sudo","rndc", "reconfig", ZONEPATH+"/zones"])
    for i in range(0,len(DOMAIN)):
      NETJOIN = IPREVERSER(DIRECTION,DOMAIN,i)
      subprocess.call(["sudo","rndc", "reload", ZONEPATH+"/"+str(DOMAIN[i])])
    print "\nThe Zones file has been reconfigured and the files have been reloaded."
  else:
    print "\nNo files were reconfigured or reloaded."

# makes 2 lists with variations of forward, compares them to user entry
# and returns a standard "forward" or "reverse"
def DIRECTIONGETTER():
  yes = "no"
  while yes != "yes":
    DIRECTION = raw_input("\nIs this for forward or reverse DNS(default is forward): ").lower()
    FORWARDLIST = list(("","forward","fwd","forwar","forw","for","f"))
    REVERSELIST = list(("","reverse","rev","revers","rever","re","r"))
    for i in range(len(FORWARDLIST)):
      if DIRECTION.lower() == FORWARDLIST[i]:
        DIRECTION = FORWARDLIST[1]
        return DIRECTION
      elif DIRECTION.lower() == REVERSELIST[i]:
        DIRECTION = REVERSELIST[1]
        return DIRECTION
    print "\nThat isn't a valid entry, try again."

def ZONEPATHVERIFIER():
  yes = "no"
  while yes != "yes":
    ZONEPATH = DEFAULTER(".","\nEnter the filepath these files need to be added to \nan example being '/var/named/master/neonova.net'(default is current path): ")
    if ZONEPATH[0] == ".":
      import os 
      GETPATH = os.getcwd()
      if GETPATH[0:17] == "/var/named/chroot":
        print "\nThis script will place the files in the current directory."
        break
      else:
        print "\nHey bud, you need to enter a /var/named/master style directory or be in one.\nTry again"
    elif ZONEPATH[0:17] == "/var/named/master":
      print "\nThis script will move the files to " + ZONEPATH + "."
      break
    else:
      print "\nHey bud, you need to enter a /var/named/master style directory or be in one.\nTry again"
  return ZONEPATH

BANNER()
yes = "no"
while yes != "yes":
 DOMAIN = list(())
 #Future feature to configure premade zones, not active
 #NEWOLD = DEFAULTER("new","\nIs this a new zone file(s) or an old zone file(s)\n(old meaning file(s) being moved from a third party DNS provider)(default is new):")
 ZONEPATH = ZONEPATHVERIFIER()
 DIRECTION = DIRECTIONGETTER()
 # FILEDIR work in progress, need to call bash to pwd and pass as variable to pass to DEFAULTER 
 #FILEDIR = DEFAULTER(" ","\nEnter the directory the files should go in\n(Default is current directory path or pwd for the bashers)\n#CaseSensitiveBecauseLinux: ")
 TTL = DEFAULTER("3600","\nEnter the TTL(default 3600): ")
 if DIRECTION == "forward":
  ZONENUM = int(DEFAULTER(1,"\nEnter the number of needed files(default is 1 file): "))
  # for loop that ends at the user given number of files
  # generates a list of values to allow for multiple domains
  for i in range(0,ZONENUM): 
    DOMAIN.append(DEFAULTER("test.net","\nEnter domain, for example neonova.net(default is test.net): "))
  break
 elif DIRECTION == "reverse":
  FULLSUBNET = DEFAULTER("10.0.0.0/24","\nEnter IP NETMASK(MAX is a 255.255.224.0) or IP/CIDRVALUE(MAX is a /19)\nfor example: 192.168.1.0 255.255.255.0 or 192.168.1.0/24(default is 10.0.0.0/24): ")
  MASK = MASKCOMPARE(IPCUTTER(FULLSUBNET,0))
  IP = IPCUTTER(FULLSUBNET,1)
  if len(str(MASK)) < 3:
    print "\nTry again knucklehead, this script will only let you break things so much.\n"
  else:
    ZONENUM = int(SUBNETTER(MASK))
    if ZONENUM == 0:
      ZONENUM += 1
    DOMAIN = RANGEMAKER(IP,ZONENUM)
    break
 else:
  print "\nTry again knucklehead, error handling is expensive!\n"

FILEMOVER(FILEGEN(ZONENUM,DOMAIN),ZONEPATH)
ZONEADDER(DOMAIN,DIRECTION,ZONEPATH)
RECONRELOAD(DIRECTION,DOMAIN,ZONEPATH)
print "\n\nAll done! Woo!"
