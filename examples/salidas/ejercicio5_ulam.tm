  0:  LD     6,0(0) 	load maxaddress from location 0
  1:  ST     0,0(0) 	clear location 0
  2:  IN     0,0,0 	read integer for n
  3:  ST     0,0(5) 	read: store to n
  4:  LD     0,0(5) 	load id n
  5:  ST     0,0(6) 	op: push left
  6:  LDC    0,1(0) 	load const 1
  7:  LD     1,0(6) 	op: load left
  8:  SUB    0,1,0 	op >
  9:  JGT    0,2(7) 	br if true
 10:  LDC    0,0(0) 	false case
 11:  LDA    7,1(7) 	unconditional jmp
 12:  LDC    0,1(0) 	true case
 13:  JEQ    0,38(7) 	while: exit loop
 14:  LD     0,0(5) 	load id n
 15:  OUT    0,0,0 	write ac
 16:  LD     0,0(5) 	load id n
 17:  ST     0,0(6) 	op: push left
 18:  LDC    0,2(0) 	load const 2
 19:  LD     1,0(6) 	op: load left
 20:  DIV    0,1,0 	op /
 21:  ST     0,0(6) 	op: push left
 22:  LDC    0,2(0) 	load const 2
 23:  LD     1,0(6) 	op: load left
 24:  MUL    0,1,0 	op *
 25:  ST     0,0(6) 	op: push left
 26:  LD     0,0(5) 	load id n
 27:  LD     1,0(6) 	op: load left
 28:  SUB    0,1,0 	op ==
 29:  JEQ    0,2(7) 	br if true
 30:  LDC    0,0(0) 	false case
 31:  LDA    7,1(7) 	unconditional jmp
 32:  LDC    0,1(0) 	true case
 33:  JEQ    0,7(7) 	if: jmp to else
 34:  LD     0,0(5) 	load id n
 35:  ST     0,0(6) 	op: push left
 36:  LDC    0,2(0) 	load const 2
 37:  LD     1,0(6) 	op: load left
 38:  DIV    0,1,0 	op /
 39:  ST     0,0(5) 	assign: store to n
 40:  LDA    7,10(7) 	jmp to end
 41:  LD     0,0(5) 	load id n
 42:  ST     0,0(6) 	op: push left
 43:  LDC    0,3(0) 	load const 3
 44:  LD     1,0(6) 	op: load left
 45:  MUL    0,1,0 	op *
 46:  ST     0,0(6) 	op: push left
 47:  LDC    0,1(0) 	load const 1
 48:  LD     1,0(6) 	op: load left
 49:  ADD    0,1,0 	op +
 50:  ST     0,0(5) 	assign: store to n
 51:  LDA    7,-48(7) 	while: jmp back to test
 52:  LD     0,0(5) 	load id n
 53:  OUT    0,0,0 	write ac
 54:  HALT   0,0,0 	Fin del programa
