#!/usr/bin/python3
import os
import shutil
import sys

from PyZ64.rom import Z64Rom
from PyZ64.types.overlay import Overlay
from PyZ64.types.overlay_tables import ParticleOverlayEntry, ActorOverlayEntry, GameStateEntry, MapMarkEntry, PlayerPauseEntry

from elffactory import ElfFactory

sys.argv.append('base.z64')

if len(sys.argv) == 1:
	print('Expecting one more paramater')
	print('Usuage: ./mk_elf.py [romname]')
	sys.exit()



rom_loc = sys.argv[1]
print(f'Using rom: {rom_loc}')
rom = Z64Rom.open(rom_loc)
overlays=[]
for name, c in [
	("game state tbl", GameStateEntry),
	("pause player tbl", PlayerPauseEntry),
	("ovl_map_mark_data tbl", MapMarkEntry),
	("actor ovl tbl", ActorOverlayEntry),
	("particle ovl tbl", ParticleOverlayEntry),
	]:
	address = rom[name]
	start = address["start"]
	end = address["end"]
	step = c.size
	for addr in range(start,end,step):
		ovl = c(rom.read(addr,step),addr)
		if ovl.vram_start:
			#print(f'\t[-]{rom.getContainingFile(ovl.vrom_start).ljust(30)}\t\t{ovl.vrom_start:08x} - {ovl.vrom_end:08x}\t\t{ovl.vram_start:08x} - {ovl.vram_end:08x}')
			overlays.append(Overlay(
				rom.getContainingFile(ovl.vrom_start),
				rom.read(ovl.vrom_start, ovl.vrom_end - ovl.vrom_start),
				ovl.vram_start
			))

elfer = ElfFactory()
elfer.addSection('.exceptionVectors','aw','exceptionVectors.bin',0x80000000, '@nobits',b'\x00'*0x400)
elfer.addRawLD(f'\t_entry = 0x{rom.header.entryPoint:0x};')
elfer.addSection('.bootstrap','ax','bootstrap.bin',rom.header.entryPoint,'@progbits',rom.read(0x1000,rom['code']['start']-rom.header.entryPoint))
elfer.addSection('.code','ax','code.bin',rom["code"]["start"], '@progbits',rom.getRawFile('code'))

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