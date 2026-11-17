  0:  LD     6,0(0) 	load maxaddress from location 0
  1:  ST     0,0(0) 	clear location 0
  2:  IN     0,0,0 	read integer for x
  3:  ST     0,0(5) 	read: store to x
  4:  LDC    0,0(0) 	load const 0
  5:  ST     0,0(6) 	op: push left
  6:  LD     0,0(5) 	load id x
  7:  LD     1,0(6) 	op: load left
  8:  SUB    0,1,0 	op <
  9:  JLT    0,2(7) 	br if true
 10:  LDC    0,0(0) 	false case
 11:  LDA    7,1(7) 	unconditional jmp
 12:  LDC    0,1(0) 	true case
 13:  JEQ    0,26(7) 	if: jmp to end
 14:  LDC    0,1(0) 	load const 1
 15:  ST     0,1(5) 	assign: store to fact
 16:  LD     0,1(5) 	load id fact
 17:  ST     0,0(6) 	op: push left
 18:  LD     0,0(5) 	load id x
 19:  LD     1,0(6) 	op: load left
 20:  MUL    0,1,0 	op *
 21:  ST     0,1(5) 	assign: store to fact
 22:  LD     0,0(5) 	load id x
 23:  ST     0,0(6) 	op: push left
 24:  LDC    0,1(0) 	load const 1
 25:  LD     1,0(6) 	op: load left
 26:  SUB    0,1,0 	op -
 27:  ST     0,0(5) 	assign: store to x
 28:  LD     0,0(5) 	load id x
 29:  ST     0,0(6) 	op: push left
 30:  LDC    0,0(0) 	load const 0
 31:  LD     1,0(6) 	op: load left
 32:  SUB    0,1,0 	op ==
 33:  JEQ    0,2(7) 	br if true
 34:  LDC    0,0(0) 	false case
 35:  LDA    7,1(7) 	unconditional jmp
 36:  LDC    0,1(0) 	true case
 37:  JEQ    0,-22(7) 	do-until: jmp back if false
 38:  LD     0,1(5) 	load id fact
 39:  OUT    0,0,0 	write ac
 40:  HALT   0,0,0 	Fin del programa
