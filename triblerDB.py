'''
triblerDB v20150416 - John Moran (john@jtmoran.com)

triblerDB parses the "tribler.sdb" SQLite database used by the Tribler 
P2P application and displays all torrent files downloaded and searches
performed by the user.

Output is two files, "tribler_downloads.csv" and "tribler_searches.csv".

This script is has been tested up to Tribler v6.4.

If you receive an error stating that the file is encrypted or not a 
database, make sure the version of the sqlite3.dll file in your Python
DLLs directory is from the most current version of SQLite.

Options:
  
   -f, --file           Path to the tribler.sdb file
   -o, --output         Output directory (Default: current directory)'''

import getopt
import os
import sys
import sqlite3
import time

def main (argv):
	outDir = os.getcwd()
	triblerFile = ""
	#Get options
	try:
		opts, args = getopt.getopt(argv, "f:o:h", ["file=", "output=", "help"])
	#Getopt Error: display help and exit
	except getopt.GetoptError:
		print(__doc__)
		sys.exit(2)
	#Create opts dictionary
	optsDict = dict(opts)
	#Show help and exit
	if "-h" in optsDict or "--help" in optsDict:
		print(__doc__)
		raise SystemExit
	#If no file name specified
	if not "-f" in optsDict and not "--file" in optsDict:
		print("[-] Error: Tribler database file required!")
		print(__doc__)
		raise SystemExit
	#Set options
	for opt, arg in opts:		
		#File
		if opt in ("-f", "--file"):
			if not (os.path.exists(arg)):
				print("[-] File '%s' does not exist" % arg)
				print(__doc__)
				raise SystemExit
			else: 
				triblerFile = arg
		if opt in ("-o", "--output"):
			if not (os.path.exists(arg)):
				print("[-] Output directory '%s' does not exist" % arg)
				print(__doc__)
				raise SystemExit
			else: 
				outDir = arg
	print "\nRunning triblerDB...\n"
	#Parse Tribler DB file
	parseDownloads(triblerFile, outDir)
	parseSearches(triblerFile, outDir)

#Read Tribler downloads	
def parseDownloads (triblerFile, outDir):
	outFile = createFile(outDir, "tribler_downloads.csv")				
	dbConn = None
	#Attempt to connect to Tribler DB
	try:
		dbConn = sqlite3.connect(triblerFile)
		cur = dbConn.cursor()
		#Get download info
		with dbConn:    
			cur = dbConn.cursor() 
			cur.execute("SELECT Torrent.name, Torrent.infohash, Torrent.torrent_file_name, Torrent.length, Torrent.num_files, MyPreference.creation_time, MyPreference.progress, MyPreference.destination_path FROM MyPreference INNER JOIN Torrent ON MyPreference.torrent_id=Torrent.torrent_id")
			rows = cur.fetchall()
			downloadList = []
			for row in rows:
				fileInfo = []
				fileInfo.append('"%s"' % row[0])
				fileInfo.append('"%s"' % row[1])
				fileInfo.append('"%s"' % row[2])
				fileInfo.append('"%s"' % (row[3] / 1024))
				fileInfo.append('"%s"' % row[4])
				fileInfo.append('"%s GMT"' % time.ctime(row[5]))
				fileInfo.append('"%s"' % row[6])
				fileInfo.append('"%s"' % row[7])
				downloadList.append(fileInfo)
			for d in downloadList:
				appendFile(outFile, ",".join(d))
	#Unable to connect to Tribler DB 
	except sqlite3.Error, e:
		print "[-] Error %s:" % e.args[0]
		sys.exit(1)

#Read Tribler searches
def parseSearches (triblerFile, outDir):
	outFile = createFile(outDir, "tribler_searches.csv")				
	dbConn = None
	#Attempt to connect to Tribler DB
	try:
		dbConn = sqlite3.connect(triblerFile)
		cur = dbConn.cursor()
		#Get download info
		with dbConn:    
			cur = dbConn.cursor() 
			cur.execute("SELECT timestamp, message FROM UserEventLog WHERE type = 4")
			rows = cur.fetchall()
			searchList = []
			for row in rows:
				pos = row[1].find("q=")
				if pos > -1:
					searchInfo = []
					searchInfo.append('"%s"' % row[1][(pos + 2):])
					searchInfo.append('"%s GMT"' % time.ctime(row[0]))
					searchList.append(searchInfo)
			for s in searchList:
				appendFile(outFile, ",".join(s))
	#Unable to connect to Tribler DB 
	except sqlite3.Error, e:
		print "[-] Error %s:" % e.args[0]
		sys.exit(1)
#Write to file
def appendFile(outFile, outData):
	with open(outFile, "a") as file:
		file.write("%s\n" % outData)

#Create new file
def createFile(outDir, name):
	#Create output file name
	if outDir.endswith('/'): outDir = outDir[:-1]
	if outDir.endswith('\\'): outDir = outDir[:-1]
	fName = os.path.join(outDir, name)
	print("[+] Writing to '%s'" % fName)
	#Create file
	try:
		newFile = open(fName, "w+")
		if name == "tribler_downloads.csv": newFile.write('"Name","InfoHash","Torrent File Name","Size (KB)","Number of Files","Date/Time","Download Progress","Destination Path"\n')
		if name == "tribler_searches.csv": newFile.write('"Search Term","Date/Time"\n')
		newFile.close()
	#Error writing file
	except:
		print("[-] Error writing to to '%s'" % fName)
		raise SystemExit
	return fName
	
#Run main
if __name__ == "__main__":
	main(sys.argv[1:]) 
