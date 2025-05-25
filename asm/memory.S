.nds
.relativeinclude off

.open "_project/new/rom/arm9/arm9.bin", 0
.orga 0
.headersize 0x2000000
.area 0xD8CA4

; move jump metadata in RAM to give more space to the text
.org 0x2030E68 :: dcd 0x2300000
.org 0x203138C :: dcd 0x2300000
.org 0x204077C :: dcd 0x2300000


.org 0x2040BE4 :: dcd 0x2300004
.org 0x2040BE8 :: dcd 0x2300006
.org 0x2040BEC :: dcd 0x2300008
.org 0x2040BF0 :: dcd 0x230000A

.org 0x2041268 :: dcd 0x2300008
.org 0x2041270 :: dcd 0x230000A
.org 0x2041274 :: dcd 0x230000C
.org 0x204127C :: dcd 0x2300000

; increase text memory size (0x3000 -> 0x4000 for 2 more lines)
.org 0x2040544 :: mov r2, 0x4000
.org 0x2040754 :: mov r2, 0x4000

; move text bytes in memory for people descriptions, to avoid overflow
.org 0x202581C :: mov r1, 0x300 
.org 0x202593C :: mov r1, 0x300

.endarea
.close