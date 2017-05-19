#!/bin/python

#==========================================================
# created: wielgosz  2017-05-07
#
# 
#
#==========================================================

# Example from FSL log output
#
# /apps/x86_64_sci7/fsl-latest/bin/overlay 1 0 example_func -a thresh_zstat1 3.100011 6.435329 rendered_thresh_zstat1
# 
# /apps/x86_64_sci7/fsl-latest/bin/slicer rendered_thresh_zstat1 -S 2 750 rendered_thresh_zstat1.png

# Example of slicer
#
# Overlay mask on reference brain, axial slices
#
# overlay 1 0 bg_image -A mask 0 1 test
# slicer test -L 1 1 test.png

import sys
import subprocess
import shutil
import tempfile
import argparse

# --------------------------------------------------------------

desc='''\
Extends FSL slicer to generate combined series of sagittal and coronal, as well as axial slices. 
'''

parser = argparse.ArgumentParser(
	formatter_class=argparse.ArgumentDefaultsHelpFormatter,
	description=desc)

parser.add_argument("--min", type=int, default=0, help="starting slice")
parser.add_argument("--max", type=int, default=-1, help="ending slice (-1 for axis size)")
parser.add_argument("-s", "--step", type=int, default=5, help="increment between slices")
parser.add_argument("-w", "--width", type=int, default=8, help="slices per row in final image")
parser.add_argument("-o", "--slicer_opts", default="", help="passed directly to slicer")
parser.add_argument("axis", choices = ["x", "y", "z"], help="slice axis")
parser.add_argument("in_f", help="rendered .nii file")
parser.add_argument("out_f", help="png")

args = parser.parse_args()

if (args.max == -1):
	dim_idx = {"x":1, "y":2, "z":3}[args.axis]
	cmd = "fslsize %s | grep ^dim%d" % (args.in_f, dim_idx)
	slice_max = int(subprocess.check_output(cmd, shell=True).split()[1])
else:
	slice_max = args.max

# 
print args

# --------------------------------------------------------------

tmp=tempfile.mkdtemp(prefix="qc_slices_")
#print(tmp)

slices = range(args.min, slice_max, args.step)
print "slices = ", slices

row_starts = range(0, len(slices), args.width)
row_files = [ "%s/row%s.row.png" % (tmp, rs) for rs in row_starts]

for (rs, row_f) in zip(row_starts, row_files):
	slice_start = slices[rs]
	slice_end = slices[rs] + (args.step * args.width) - 1
	slice_range = range(slice_start, slice_end, args.step)
	print "row: ", slice_range
	#slice_range = [ slices[r] for r in range(rs, rs + args.width)]
	slice_files = [ "%s/slice%s.png" % (tmp, s) for s in slice_range ]
	for (slice_idx, slice_f) in zip(slice_range, slice_files):
		slicer_opts = ""
		slicer_out = "-%s -%s %s" % (args.axis, slice_idx, slice_f)
		cmd="slicer %s %s %s" % (args.in_f, args.slicer_opts, slicer_out)
		#print cmd
		subprocess.call(cmd, shell=True )

	cmd="pngappend %s %s" % (" + ".join(slice_files), row_f)
#	print cmd
	subprocess.call(cmd, shell=True)

cmd="pngappend %s %s" % (" - ".join(row_files), args.out_f)
#print cmd
subprocess.call("pngappend %s %s" % (" - ".join(row_files), args.out_f), shell=True)

shutil.rmtree(tmp)