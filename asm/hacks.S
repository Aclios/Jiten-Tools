.nds
.relativeinclude off

.open "_project/new/rom/arm9/arm9.bin", 0
.orga 0
.headersize 0x2000000

; Char per line -> pixel per line + change r11 purpose
.org 0x204059C :: add r10, r10, #1
.org 0x20405A0 :: mov r8, r10, lsl#8
.org 0x20405A8 :: cmp r10, #8

; 1 byte per character instead of 2; use the second one as the character width
.org 0x2040630 :: ldrb r1, [r4] ; load character
.org 0x2040634 :: add r4, r4, #1 ; next character
.org 0x2040648 :: ldrb r6, [r3] ; load the font
.org 0x204064C :: b #0x2092100 ; Hook for 92100

; Load width from the modified font

.org 0x2092100
.area 0x100, 0
    cmp r1, r6
    moveq r2, #1
    ldrsb r11, [r3, #1] ; load the width
    beq #0x2040668
    ldrsb r6, [r3, #2]
    add r3, r3, #2
    add r0, r0, #2
    b #0x2040660
.endarea
; Hooks + add width instead of 1

.org 0x20406F8 :: add r0, r0, #0
.org 0x2040700 :: mov r2, r11
.org 0x2040708 :: bl #0x2092200 ; new glyph loading
.org 0x204070c :: add r0, r0, #0x100
.org 0x204071c :: add r1, r2 , r1
.org 0x2040720 :: add r0, r0, #0
.org 0x2040724 :: mov r2, r11
.org 0x2040728 :: bl #0x2092200 ; new glyph loading
.org 0x204072C :: bl #0x2092500


.org 0x2092500
.area 0x50, 0
    add r8, r8, r11 ; add width
    cmp r5, #0
    ldrne r2, [PC, #0x10]
    addne r2, r2, r9, lsl#5
    ldrneh r0, [r2, #0x18] ; hitbox width
    addne r0, r0, r11
    strneh r0, [r2, #0x18] ; hitbox width
    bx lr
    dcd 0x2300000
.endarea
; New font routine


.org 0x2092200
.area 0x100, 0
    stmfd sp!, {r3, r4, r6, r7, r9}
    mov r2, #0 ; x font iterator
    mov r6, #0 ; y font iterator
    mov r12, r0 ; ram pointer
    add r9, r8, r2 ; x canva pos

    mov r4, r9, lsr#10 ; mod 1024
    sub r7, r9, r4, lsl#10
    add r12, r12, r4, lsl#13 ; line 4

    mov r4, r7, lsr#8 ; mod 256
    sub r7, r7, r4, lsl#8
    add r12, r12, r4, lsl#9 ; next line

    mov r4, r7, lsr#6 ; mod 64
    sub r7, r7, r4, lsl#6
    add r12, r12, r4, lsl#11 ; block line offset

    mov r4, r7, lsr#3 ; mod 8
    add r12, r12, r4, lsl#5 ; 8x8 block offset
    sub r7, r7, r4, lsl#3

    mov r4, r7, lsr#1
    add r12, r12, r4 ; x offset

    add r12, r12, r6, lsl#2 ; y offset


    ldrsb r3, [r1] ; read 1 byte (2 pixels)
    tst r2, #1 ; is r2 odd
    moveq r3, r3, lsr#4 ; if so, we get the second pixel from the byte
    andne r3, r3, 0xF ; otherwise, we get the first pixel of the byte
    add r7, r5, #1
    mul r3, r3, r7 ; coloring
    tst r9, #1 ; is r9 odd
    streqb r3, [r12] ; write in the RAM (first pixel)
    ldrneb r7, [r12]
    addne r3, r7, r3, lsl#4
    strneb r3, [r12] ; write in the RAM (second pixel)
 
    add r2, r2, #1 ; we read 1 pixel
    tst r2, #1
    addne r1, r1, #1 ; go to next byte if we read the 2 pixels of the previous one
    cmp r2, 0x7 ; check if we read the full line of the first 8x8 tile
    addeq r1, r1, 0x1C ; go to the same line of the second tile
    cmp r2, 0xF ; check if we read the 2nd 8x8 tile line
    addeq r6, r6, #1 ; increase line
    subeq r1, r1, 0x20 ; go to the first pixel of the line
    moveq r2, #0 ; reset r2
    cmp r6, #8 ; check if we read the 8 lines
    bne #0x209220C ; loop
    ldmfd sp!, {r3, r4, r6, r7, r9}
    bx lr
.endarea
; new routine for jump between pages -> flexible hitbox

.org 0x2031264 :: ldr r2, [r5, 0x30] ; metadata line idx
.org 0x2031268 :: ldr r0, [PC, 0x11C] ; 0x2023000
.org 0x203126C :: add r0, r0, r2, lsl#4
.org 0x2031270 :: ldrh r2, [r0, 0x16] ; x coord
.org 0x2031274 :: str r2, [SP]
.org 0x2031278 :: ldrh r2, [r0, 0x14] ; y coord
.org 0x203127C :: str r2, [SP, #4]
.org 0x2031280 :: ldrh r2, [r0, 0x18] ; hitbox width
.org 0x2031284 :: str r2, [SP, #8]
.org 0x2031288 :: mov r2, 0x10 ; hitbox height
.org 0x203128C :: str r2, [SP, #0xC]
.org 0x2031290 :: add r0, SP, #0
.org 0x2031294 :: b 0x203129C

.org 0x20405E0 :: b 0x2092450

.org 0x2040688 :: cmp r5, #0
.org 0x2040694 :: beq 0x20406E8


.org 0x2092450
.area 0x50, 0
    cmp r5, #0
    moveq r5, #1
    movne r5, #0
    addne r9, r9, #1
    bne 0x2040730
    b 0x20405EC
.endarea

.org 0x20406C0 :: b #0x2092400

.org 0x2092400
.area 0x50, 0
    stmfd sp!, {r4, r7}
    add r2, r2, r9, lsl#5
    str r0, [r2]
    mov r5, r0 ; = 1 if page not read ( = red), 2 if page have been read (= blue)
    mov r0, r8, lsr#8 ; line count
    mov r7, #0x18 ; text y offset
    mov r4, #0x10 ; line
    mla r0, r0, r4, r7 ; y coord top left of hitbox
    ldrh r7, [r2, #0x14] ; y start of hitbox
    cmp r7, 0 ; y start of hitbox
    streqh r0, [r2, #0x14] ; y start of hitbox
    and r0, r8, #0xff ; x pos
    mov r7, #0x14 ; text x offset
    add r0, r0, r7 ; x coord top left of hitbox
    ldrh r7, [r2, #0x16]
    cmp r7, 0
    streqh r0, [r2, #0x16] ; x start of hitbox

    ldmfd sp!, {r4, r7}
    b #0x20406C8
.endarea

; -------------------------------------------------------------

; openings & credits

.org 0x202F064 :: mov r0, #0xe 
.org 0x202F070 :: mov r1, #0xc
.org 0x202EEEC :: b #0x2092320


.org 0x2092320
.area 0x30, 0
    ldreqb r7, [r1, #2] ; width
    ldreq r12, [PC, #0x10]
    streqb r7, [r12, #0x3A] ; store width
    beq 0x202EF00
    ldrsb r3, [r1, #3]
    add r1, r1, #3
    b 0x202EEF4
    dcd 0x2182DA8
.endarea

.org 0x202F074 :: b 0x2092370


.org 0x2092370
.area 0x20, 0
    ldrh r5, [r2, #0x38] ; x offset
    ldrb r0, [r2, #0x3A] ; width
    add r4, r5, r4
    add r5, r5, r0
    strh r5, [r2, #0x38]
    b 0x202F078
.endarea

; code 8 (carriage return)
.org 0x202E2E4 :: b 0x2092390


.org 0x2092390
.area 0x10, 0
    mov r2, 0 
    strh r2, [r4, #0x38] ; reset x offset
    b 0x202E2E8
.endarea

; reset x offset when the window is cleared (code 7)

.org 0x202E28C :: b 0x20923A0


.org 0x20923A0
.area 0x10, 0
    strh r3, [r4, #0x38] ; reset x offset
    strb r3, [r4, #0x20] ; reset char count
    b 0x202E290
.endarea

;.org 0x202EE34 :: add r6, r8, r9, lsl#5
.org 0x202F0B8 :: dcd 0x2260000
;.org 0x202F0D4 :: dcd 0x2183F10
;.org 0x202F0D8 :: dcd 0x2183F12
;.org 0x202F0DC :: dcd 0x2183F08
;.org 0x202F0E0 :: dcd 0x2183F0C

.close