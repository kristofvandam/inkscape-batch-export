#!/usr/bin/python
import sys
import subprocess
import inkex
import os
from simplestyle import *

# png export
class BatchExPNG(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
		self.OptionParser.add_option("--dpi",action="store",type="int",dest="dpi",default="320",help="")
		self.OptionParser.add_option("--path",action="store",type="string",dest="path",default=".",help="")
		self.OptionParser.add_option("--usefolders",action="store",type="inkbool",dest="use_folders",default="False",help="")
		self.OptionParser.add_option("--adddpi",action="store",type="inkbool",dest="add_dpi",default="False",help="")

	def effect(self):
		#sys.stderr.write("Starting batch PNG export.\n")
		# retrieve CLI options
		path=self.options.path
		dpi = self.options.dpi
		use_folders = self.options.use_folders
		add_dpi = self.options.add_dpi
		# get current file name to pass it to the Inkscape CLI
		curfile = self.args[-1]

		# check if need to add dpi suffix
		if add_dpi:
			path = path + "/" + str(dpi) + "dpi"
			if not os.path.isdir( path ):
				os.makedirs( path )

		# prepare layers list
		layers = list()

		# get XML root
		svg_root = self.document.getroot();
		for child in svg_root.getchildren():
			tag = child.tag[child.tag.find("}")+1:]
			if "g" == tag:
				layers.append( child )
				#sys.stderr.write("Added '" + child.get("id" ) + "' to layers list\n")
			
		# go through layers
		for layer in layers:
			layername = layer.get("id")
			#sys.stderr.write("Processing '" + layername + "'\n")
			if use_folders:
				dirpath = path + "/" + layername 
				if not os.path.isdir(dirpath):
					os.makedirs(dirpath)
			for obj in layer.getchildren():
				id = obj.get("id")
				objname = id
				if add_dpi:
					objname = id + "_" + str(dpi) + "dpi"
				filename = path + "/" + objname + ".png"
				if use_folders:
					filename = path + "/" + layername + "/" + objname + ".png"
				#sys.stderr.write("Exporting '" + filename + "' from " + curfile + "\n")
				command = ( "inkscape", "-z", "-i", id, "-j", "-e",filename, "-d",str(dpi), "--export-area-snap", curfile )
				proc = subprocess.Popen( command, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
				proc.wait()

		'''if len(self.selected) == 0:
			sys.stderr.write("Works for selections only")
			exit()'''
		# export all selected ids 
		'''for id in self.selected:
			filename = path + "/" + id + ".png"
			sys.stderr.write("Exporting " + id + " to: " + filename + "\n" )
			command = ( "inkscape", "-z", "-i", id, "-j", "-e",filename, "-d",str(dpi), "--export-area-snap", curfile )
			proc = subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			proc.wait()'''

def _main():
	e = BatchExPNG()
	e.affect()
	exit()

if __name__=="__main__":
	_main()
