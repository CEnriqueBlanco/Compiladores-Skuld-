  0:  LD     6,0(0) 	load maxaddress from location 0
  1:  ST     0,0(0) 	clear location 0
  2:  IN     0,0,0 	read integer for n
  3:  ST     0,0(5) 	read: store to n
  4:  LD     0,0(5) 	load id n
  5:  ST     0,0(6) 	op: push left
  6:  LDC    0,0(0) 	load const 0
  7:  LD     1,0(6) 	op: load left
  8:  SUB    0,1,0 	op ==
  9:  JEQ    0,2(7) 	br if true
 10:  LDC    0,0(0) 	false case
 11:  LDA    7,1(7) 	unconditional jmp
 12:  LDC    0,1(0) 	true case
 13:  JEQ    0,3(7) 	if: jmp to else
 14:  LDC    0,0(0) 	load const 0
 15:  OUT    0,0,0 	write ac
 16:  LDA    7,48(7) 	jmp to end
 17:  LD     0,0(5) 	load id n
 18:  ST     0,0(6) 	op: push left
 19:  LDC    0,1(0) 	load const 1
 20:  LD     1,0(6) 	op: load left
 21:  SUB    0,1,0 	op ==
 22:  JEQ    0,2(7) 	br if true
 23:  LDC    0,0(0) 	false case
 24:  LDA    7,1(7) 	unconditional jmp
 25:  LDC    0,1(0) 	true case
 26:  JEQ    0,3(7) 	if: jmp to else
 27:  LDC    0,1(0) 	load const 1
 28:  OUT    0,0,0 	write ac
 29:  LDA    7,35(7) 	jmp to end
 30:  LDC    0,0(0) 	load const 0
 31:  ST     0,1(5) 	assign: store to a
 32:  LDC    0,1(0) 	load const 1
 33:  ST     0,2(5) 	assign: store to b
 34:  LDC    0,2(0) 	load const 2
 35:  ST     0,4(5) 	assign: store to i
 36:  LD     0,4(5) 	load id i
 37:  ST     0,0(6) 	op: push left
 38:  LD     0,0(5) 	load id n
 39:  LD     1,0(6) 	op: load left
 40:  SUB    0,1,0 	op <=
 41:  JLE    0,2(7) 	br if true
 42:  LDC    0,0(0) 	false case
 43:  LDA    7,1(7) 	unconditional jmp
 44:  LDC    0,1(0) 	true case
 45:  JEQ    0,17(7) 	while: exit loop
 46:  LD     0,1(5) 	load id a
 47:  ST     0,0(6) 	op: push left
 48:  LD     0,2(5) 	load id b
 49:  LD     1,0(6) 	op: load left
 50:  ADD    0,1,0 	op +
 51:  ST     0,3(5) 	assign: store to temp
 52:  LD     0,2(5) 	load id b
 53:  ST     0,1(5) 	assign: store to a
 54:  LD     0,3(5) 	load id temp
 55:  ST     0,2(5) 	assign: store to b
 56:  LD     0,4(5) 	load id i
 57:  ST     0,0(6) 	op: push left
 58:  LDC    0,1(0) 	load const 1
 59:  LD     1,0(6) 	op: load left
 60:  ADD    0,1,0 	op +
 61:  ST     0,4(5) 	assign: store to i
 62:  LDA    7,-27(7) 	while: jmp back to test
 63:  LD     0,2(5) 	load id b
 64:  OUT    0,0,0 	write ac
 65:  HALT   0,0,0 	Fin del programa
