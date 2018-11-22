import os
import shutil

asmtemplate = '''
.section {0},"{1}",{4}
.incbin "{2}"
'''

ldtemplate = '''
	. = 0x{3:08x};
	{0} : {{
		*({0}*)
	}}

'''

asmpreamble = ''
ldpreamble = '''
OUTPUT_FORMAT("elf32-bigmips", "elf32-bigmips", "elf32-littlemips")
OUTPUT_ARCH(mips)
ENTRY(_entry)
SECTIONS
{

'''

asmepilogue = ''
ldepilogue = '\n}\n'

cmd = '''
mips64-as {1} -o {0}out.o
mips64-ld {0}out.o -T {2} -o {3}.elf
'''

class ElfFactory(object):
	def __init__(self, outname='out', builddir = 'build/', bindir = 'bins/', asmtemplate=asmtemplate, ldtemplate=ldtemplate, asmpreamble=asmpreamble, ldpreamble=ldpreamble, asmepilogue=asmepilogue, ldepilogue=ldepilogue):
		self.incbins = ''
		self.ldlines = ''

		self.asmfile = ''
		self.ldfile = ''

		self.outname = outname

		self.builddir = builddir
		if self.builddir[-1] != '/':
			self.builddir += '/'

		self.bindir = bindir
		if self.bindir[-1] != '/':
			self.bindir += '/'

		self.asmtemplate = asmtemplate
		self.ldtemplate = ldtemplate

		self.asmpreamble = asmpreamble
		self.ldpreamble = ldpreamble

		self.asmepilogue = asmepilogue
		self.ldepilogue = ldepilogue

		shutil.rmtree(self.builddir, ignore_errors=True)

		os.mkdir(self.builddir)
		os.mkdir(self.wrapbuilddir(self.bindir))

	def wrapbuilddir(self,loc):
		return self.builddir + loc

	def addSection(self, secname, flag, binname, vaddr, bits, raw, *extra):
		binname = self.wrapbuilddir(self.bindir) + binname
		with open(binname,'wb') as f:
			f.write(raw)
		self.incbins += asmtemplate.format(secname, flag, binname, vaddr, bits, raw, *extra)
		self.ldlines += ldtemplate.format(secname, flag, binname, vaddr, bits, raw, *extra)

	def writeASM(self, filename):
		self.asmfile = self.wrapbuilddir(filename)
		with open(self.asmfile, 'w') as f:
			f.write(self.asmpreamble)
			f.write(self.incbins)
			f.write(self.asmepilogue)

	def writeLD(self,filename):
		self.ldfile = self.wrapbuilddir(filename)
		with open(self.ldfile, 'w') as f:
			f.write(self.ldpreamble)
			f.write(self.ldlines)
			f.write(self.ldepilogue)

	def writeBuildScripts(self):
		out = cmd.format(self.builddir, self.asmfile, self.ldfile, self.outname)
		with open('build.sh', 'w') as f:
			f.write('#!/bin/bash\n')
			f.write(out)
		with open('build.bat', 'w') as f:
			f.write(out)
		print('Run either build.sh or build.bat depending on your platorm')