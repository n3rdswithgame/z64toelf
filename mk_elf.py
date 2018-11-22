#!/usr/bin/python3
import os
import shutil
import sys

from PyZ64.rom import Z64Rom
from PyZ64.types.overlay import Overlay
from PyZ64.types.overlay_tables import ParticleOverlayEntry, ActorOverlayEntry, GameStateEntry, MapMarkEntry, PlayerPauseEntry

from elffactory import ElfFactory

print(__file__)
if len(sys.argv) == 1:
	print('Expecting one more paramater')
	print('Usuage: ./mk_elf.py [romname]')
	sys.exit()



rom_loc = sys.argv[1]
print(f'Using rom: {rom_loc}')
test = Z64Rom.open(rom_loc)
overlays=[]
for name, c in [
	("game state tbl", GameStateEntry),
	("pause player tbl", PlayerPauseEntry),
	("ovl_map_mark_data tbl", MapMarkEntry),
	("actor ovl tbl", ActorOverlayEntry),
	("particle ovl tbl", ParticleOverlayEntry),
	]:
	address = test[name]
	start = address["start"]
	end = address["end"]
	step = c.size
	for addr in range(start,end,step):
		ovl = c(test.read(addr,step),addr)
		if ovl.vram_start:
			#print(f'\t[-]{test.getContainingFile(ovl.vrom_start).ljust(30)}\t\t{ovl.vrom_start:08x} - {ovl.vrom_end:08x}\t\t{ovl.vram_start:08x} - {ovl.vram_end:08x}')
			overlays.append(Overlay(
				test.getContainingFile(ovl.vrom_start),
				test.read(ovl.vrom_start, ovl.vrom_end - ovl.vrom_start),
				ovl.vram_start
			))

elfer = ElfFactory()



elfer.addSection('.code','ax','code.bin',test["code"]["start"], '@progbits',test.getRawFile('code'))

for ovl in overlays:
	vram = ovl.vram
	for section,flags,bits in [
		('text','ax','@progbits'),
		('data','aw','@progbits'),
		('rodata','a','@progbits'),
		('bss','aw','@nobits')
		]:
		raw = ovl.getSectionByName(section)
		secname = f'.{ovl.name}.{section}'
		binname = f'{secname[1:]}'
		
		elfer.addSection(secname, flags, binname, vram, bits, raw)
		vram += len(raw)

elfer.writeASM('asm.s')
elfer.writeLD('elfifier.ld')
elfer.writeBuildScripts()