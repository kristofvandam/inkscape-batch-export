#!/usr/bin/python
import sys
import subprocess
import inkex
import os
from simplestyle import *
from lxml import etree

import gettext
_ = gettext.gettext
from subprocess import Popen, PIPE

sys.path.append('/usr/share/inkscape/extensions')

class BatchExSVG(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
		self.OptionParser.add_option("--path",action="store",type="string",dest="path",default=".",help="")
		self.OptionParser.add_option("--usefolders",action="store",type="inkbool",dest="use_folders",default="False",help="")

	def effect(self):
		svg_root = self.document.getroot()
		canvas_width  = self.unittouu(svg_root.get('width'))
		canvas_height = self.unittouu(svg_root.attrib['height'])

		children = svg_root.getchildren()
		path = self.options.path
		use_folders = self.options.use_folders
		layers = list()
		defs = None
		# go through all first-level children
		for child in children:
			tag = child.tag[child.tag.find("}")+1:]
			# remember defines: gradients and etc.
			if tag == "defs":
				defs = child
				#sys.stderr.write("Found 'defs' section.\n")
			# layers are groups in general, so detect them by 'g' tag 
			if tag == "g":
				layers.append( child )
				#sys.stderr.write( "Added layer to the list.\n" )

		#sys.stderr.write("Starting to process layers.\n")
		# go through all collected layers
		for layer in layers:
			layer_children = layer.getchildren()
			#sys.stderr.write("Dealing with " + layer.get("id") + "\n" )
			layername = layer.get("id")
			# create directory, if option is set
			if use_folders:
				dirpath = path + "/" + layername
				if not os.path.isdir( dirpath ):
					os.makedirs( dirpath )
			# traverse through all layer child objects
			for lchild in layer_children:
				tag = lchild.tag[lchild.tag.find("}")+1:]
				childname = lchild.get("id")
				filename = path + "/" + childname + ".svg"
				# correct filepath to use directory
				if use_folders:
					filename = path + "/" + layername + "/" + childname + ".svg"
				content = inkex.etree.tostring( lchild )

				q = {'x':0, 'y':0, 'width':0, 'height':0}
				for query in q.keys():
					p = Popen(
						'inkscape --query-%s --query-id=%s "%s"' % (query, childname, self.args[-1], ),
						shell=True,
						stdout=PIPE,
						stderr=PIPE,
					)
					p.wait()
					q[query] = p.stdout.read()

				# get width, height, center of bounding box 
				obj_width = float(q['width'])
				obj_height = float(q['height'])
				center_x = float(q['x'])
				center_y = float(q['y'])


				#sys.stderr.write( content )
				# get dimensions
				# x = lchild.get('x') #self.unittouu( lchild.get('x') )
				# y = self.unittouu( lchild.get('y') )
				# w = self.unittouu( lchild.get('width') )
				# h = self.unittouu( lchild.get('height') )
				# # dimensions for future document, in units
				# uw = self.uutounit( w, 'mm' )
				# uh = self.uutounit( h, 'mm' )
				#sys.stderr.write( "Exporting " + tag + " to " + filename + "\n" )
				# start export
				exsvg = open(filename,'w')
				exsvg.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
				exsvg.write('<svg\n')
				exsvg.write('width="' + str(obj_width) + 'mm"\n')
				exsvg.write('height="' + str(obj_height) + 'mm"\n')
				exsvg.write('viewBox="' + str(center_x) + ' ' + str(center_y) + ' ' + str(obj_width) + ' ' + str(obj_height) + '"\n')
				# exsvg.write('sodipodi:docname="' + name + '.svg">\n')
				exsvg.write('>\n')
				#write definitions
				if None != defs:
					exsvg.write( inkex.etree.tostring( defs ) )
					exsvg.write( '\n' )
				#write content
				exsvg.write( content )
				exsvg.write( '\n' )
				exsvg.write( '</svg>\n' )
				# end export
				exsvg.close()
				#sys.stderr.write('Done exporting ' + filename + '\n' )

def _main():
	e = BatchExSVG()
	e.affect()
	exit()

if __name__=="__main__":
	_main()
