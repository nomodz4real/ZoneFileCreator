# ZoneFileCreator
Python 2.7 script to dynamically create zone files with a standard DNS header and configure the files to the configured specifications.

This was created initially to help make multiple reverse zone files quickly, fill them with a standard header, and then add them to a 
central zones file that allows the DNS service to find the files when lookups are run against that server.

Version 1 will take the filepath(linux environment) entered by the user, or a default value is used, as well as the direction the zone 
file is for , either forward or reverse DNS, entered by the user as well as a TTL or Time to live value. For forward DNS it asks the 
user to enter the number of files they need and then gathers the domain names from them for the given amount of files. For reverse DNS it
will accept a range of IP addresses written in either NETWORK NETMASK notation or NETWORK/CIDR notation and makes the files based on that 
entry.

Once all this is done the files are made, permissions and ownderships are changed for them, they are moved to the given directory, a file 
is generated with zone entries formatted for an authoritative dns server, a bash script file is then made to move the contents of the made 
into the zones file. The user is then given the option to reconfigure and reload the files which is the last step needed to ensure that the
zone files added are able to be used in lookups on the internet.

Currently there are some features missing and I will lay out my plans for these features in a separate file.
