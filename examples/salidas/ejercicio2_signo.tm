  0:  LD     6,0(0) 	load maxaddress from location 0
  1:  ST     0,0(0) 	clear location 0
  2:  IN     0,0,0 	read integer for num
  3:  ST     0,0(5) 	read: store to num
  4:  LD     0,0(5) 	load id num
  5:  ST     0,0(6) 	op: push left
  6:  LDC    0,0(0) 	load const 0
  7:  LD     1,0(6) 	op: load left
  8:  SUB    0,1,0 	op >
  9:  JGT    0,2(7) 	br if true
 10:  LDC    0,0(0) 	false case
 11:  LDA    7,1(7) 	unconditional jmp
 12:  LDC    0,1(0) 	true case
 13:  JEQ    0,3(7) 	if: jmp to else
 14:  LDC    0,0(0) 	load const 0
 15:  ST     0,1(5) 	assign: store to res
 16:  LDA    7,15(7) 	jmp to end
 17:  LD     0,0(5) 	load id num
 18:  ST     0,0(6) 	op: push left
 19:  LDC    0,0(0) 	load const 0
 20:  LD     1,0(6) 	op: load left
 21:  SUB    0,1,0 	op <
 22:  JLT    0,2(7) 	br if true
 23:  LDC    0,0(0) 	false case
 24:  LDA    7,1(7) 	unconditional jmp
 25:  LDC    0,1(0) 	true case
 26:  JEQ    0,3(7) 	if: jmp to else
 27:  LDC    0,1(0) 	load const 1
 28:  ST     0,1(5) 	assign: store to res
 29:  LDA    7,2(7) 	jmp to end
 30:  LDC    0,2(0) 	load const 2
 31:  ST     0,1(5) 	assign: store to res
 32:  LD     0,1(5) 	load id res
 33:  OUT    0,0,0 	write ac
 34:  HALT   0,0,0 	Fin del programa
