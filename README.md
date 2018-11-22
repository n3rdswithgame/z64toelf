# z64toelf
### ver 0.1
Example using my [PyZ64](https://github.com/n3rdswithgame/PyZ64) python library. It parses the supplied rom, specifically the overlay tables and a file table as part PyZ64), and generates and elf executable from [code](https://wiki.cloudmodding.com/oot/Code_(File)) and the overlays placing all of these files at virtual address they were compiled for.

Currently this can only work with 1.0 uncompressed roms as my PyZ64 library only supports that well enough to build the elf. That will improve when I work on the library more

## Prerequisites
This will not build the elf, only generate the extract the needed information from the rom and build an assembler file and a linker script. You still need a MIPS toolchain (other naitive toolchains will work but are not officially supported) and in your path. I highly recommend using [glankk's n64 toolchain](https://github.com/glankk/n64) and follow his instructions, except make sure to add `-j` or `-j2` or `-j4` to speed up building

## Instillation and executing
```bash
git clone --recursive https://github.com/n3rdswithgame/z64toelf.git
cd z64toelf #or what ever directory you cloned into
chmod u+x mk_elf.py #not needed for windows or if you want to invoke with python
./mk_elf.py [rom.z64] #or python3 mkelf.py [rom.z64]
bash build.sh #or chmod and ./build.sh
#run build.bat instead for windows
```
Once running either `build.sh` or `build.bat` you will have an `out.elf` in the root this project dir unless you change the default output of ElfFactory.

## Customizing output

There is some output custimization that will get documented at soon, but it can all be seen in elffactory.py

## Thanks
Thanks glankk for helping me figure my dumb error with section flags