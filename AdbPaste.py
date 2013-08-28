#!/usr/bin/python

# GPV v3 code.
# writting in a hurry. No unit tests because most of the issues i get is because of the adb->sh translation
# if I could mock that up I wouldn't need this file...

import sys,os
class AdbPaste:
	"Pass a long string as input to an android device/emulator"

	key_dict = {
		#key is the string, value is the keycode the emulator expects to generate that string
		"0":7,
		"1":8,
		"2":9,
		"3":10,
		"4":11,
		"5":12,
		"6":13,
		"7":14,
		"8":15,
		"9":16,
		"*":17,
		"#":18,
		"A":29,
		"B":30,
		"C":31,
		"D":32,
		"E":33,
		"F":34,
		"G":35,
		"H":36,
		"I":37,
		"J":38,
		"K":39,
		"L":40,
		"M":41,
		"N":42,
		"O":43,
		"P":44,
		"Q":45,
		"R":46,
		"S":47,
		"T":48,
		"U":49,
		"V":50,
		"W":51,
		"X":52,
		"Y":53,
		"Z":54,
		",":55,
		".":56,
		"	":61,
		" ":62,
		"\n":66,
		"`":68,
		"-":69,
		"=":70,
		"[":71,
		"]":72,
		"\\":73,
		";":74,
		"'":75,
		"/":76,
		"@":77,
		"+":81,
		"(":162,
		")":163,
		#// note how there's no colon or single/double quotes and others... sigh. can't standardize one solution for it all
	}

	#// charaters that must be sent as keyevent because as string sh will complain.
	#// there is nothing i can do when calling it on windows because adb will just
	#// pass it forward to sh and things break.
	trouble = [' ', '\n', '	'] # i think space is only needed in adb.exe->sh... when running directly in unix it may not be needed
	inconvenience = [';', ')' ,'(', "'", '\\', '&', '#', '<', '>', '|']

	def __init__(self, input_string=""):
		self.addString( input_string )
	
	def addString(self, input_string):
		self.string_data = input_string

	def getKeys(self, fast=False):
		"thanks to some keys not being available, e.g. colon, we return an array of keycodes (int) or strings."
		r = []
		count = 0
		for c in self.string_data:
			count += 1
			# if char is in trouble list, create a new int element in the output
			if c in self.trouble:
				t = self.translate(c)
				r.append( t )
			# work around a bug in the emulator... if the browser starts to look on google
			#  while this script is 'typing' in the address bar, anything longer than 10 or so
			#  chars will fail on my box... so just make it slow here too... man, i hate the emulator.
			#if len(r) < 10: # or len(r[-1]) > 10:
			elif not fast and count > 7 and isinstance(r[-1], str) and len(r[-1]) > 7:
				r.append( c )
			else:
				#// if the last element is a safe string, continue to add to it
				# before anything, escape if needed
				if c == '"': # added this to CMD.exe issues, TODO: test on other platforms
					c = '\\\\\\"' # this will become \\\" to CMD when passing to adb.exe, which will become \" to sh, and finally " to the device
				# special case for > ,only way to escape them in windows when it is in a double quote and followed by anything is with ^
				# but adding the ^ in front, if there's no double quote in the string, CMD will not treat ^ as a special char and send it along
				elif sys.platform == "win32" and c == ">":
					if len(r)>0 and isinstance(r[-1], str) and '"' in r[-1]:
						c = "\\^>"
					else:
						c = "\\>"
				# ^ is a escape char in windows. it will be ignored
				elif sys.platform == "win32" and c == "^":
					c = "^^"
				elif c in self.inconvenience:
					c = '\\' + c

				#// here is something weird... $ does not need to be encoded (\$ results in \$ typed in the emulator) but it will
				#// also fail if it's not the last char in the string. proably sh at some point try to do variable subst
				if len(r) > 0 and isinstance(r[-1], str) and r[-1][-1] != '$':
					r[-1] += c
				else:
					#// otherwise, start a new safe string batch
					r.append( c )
		return r

	def sendKeys(self, key_list):
		for k in key_list:
			self.send( k );

	def send( self, key ):
		"sends a single key to the device/emulator"
		print('sending', key)
		if( isinstance(key, int) ):
			os.system('adb shell input keyevent %d'%key)
		else:
			os.system('adb shell input text "' + key + '"')

	def translate( self, char ):
		return self.key_dict[char] #// will fail on unkown values, so we can add them :)

if __name__=="__main__":
	arg = sys.argv[1:]
	#// --fast: must be 1st arg, i'm lazy. Will bypass the workaround of breaking longer strings
	#//         will mess up input in the browser or other input boxes that does network searchs
	#//         while you are typing. For sure!
	if arg[0] == "--fast":
		fast = True
		arg = arg[1:]
	else:
		fast = False
	
	#// --notab: Convert tabs into spaces. usefull for 'typing' a file into a textarea or field where tab would change focus
	if arg[0] == "--notab":
		notab = True
		arg = arg[1:]
	else:
		notab = False

	#// -- file: read the contents from a file, and not from stdin
	if arg[0] == "--file" and isinstance(arg[1], str):
		with open(arg[1], 'r') as content_file:
			arg = content_file.read()
			import re
			arg = re.sub('\t', ' ', arg)
	else:
		arg = " ".join(arg)
		
	paste = AdbPaste( arg )
	keys = paste.getKeys(fast)
	paste.sendKeys(keys)
