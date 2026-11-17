  0:  LD     6,0(0) 	load maxaddress from location 0
  1:  ST     0,0(0) 	clear location 0
  2:  LDC    0,84(0) 	char 'T'
  3:  OUTC   0,0,0 	write char
  4:  LDC    0,101(0) 	char 'e'
  5:  OUTC   0,0,0 	write char
  6:  LDC    0,99(0) 	char 'c'
  7:  OUTC   0,0,0 	write char
  8:  LDC    0,108(0) 	char 'l'
  9:  OUTC   0,0,0 	write char
 10:  LDC    0,101(0) 	char 'e'
 11:  OUTC   0,0,0 	write char
 12:  LDC    0,97(0) 	char 'a'
 13:  OUTC   0,0,0 	write char
 14:  LDC    0,32(0) 	char ' '
 15:  OUTC   0,0,0 	write char
 16:  LDC    0,117(0) 	char 'u'
 17:  OUTC   0,0,0 	write char
 18:  LDC    0,110(0) 	char 'n'
 19:  OUTC   0,0,0 	write char
 20:  LDC    0,32(0) 	char ' '
 21:  OUTC   0,0,0 	write char
 22:  LDC    0,110(0) 	char 'n'
 23:  OUTC   0,0,0 	write char
 24:  LDC    0,117(0) 	char 'u'
 25:  OUTC   0,0,0 	write char
 26:  LDC    0,109(0) 	char 'm'
 27:  OUTC   0,0,0 	write char
 28:  LDC    0,101(0) 	char 'e'
 29:  OUTC   0,0,0 	write char
 30:  LDC    0,114(0) 	char 'r'
 31:  OUTC   0,0,0 	write char
 32:  LDC    0,111(0) 	char 'o'
 33:  OUTC   0,0,0 	write char
 34:  LDC    0,58(0) 	char ':'
 35:  OUTC   0,0,0 	write char
 36:  LDC    0,32(0) 	char ' '
 37:  OUTC   0,0,0 	write char
 38:  IN     0,0,0 	read integer for n
 39:  ST     0,0(5) 	read: store to n
 40:  LDC    0,69(0) 	char 'E'
 41:  OUTC   0,0,0 	write char
 42:  LDC    0,108(0) 	char 'l'
 43:  OUTC   0,0,0 	write char
 44:  LDC    0,32(0) 	char ' '
 45:  OUTC   0,0,0 	write char
 46:  LDC    0,100(0) 	char 'd'
 47:  OUTC   0,0,0 	write char
 48:  LDC    0,111(0) 	char 'o'
 49:  OUTC   0,0,0 	write char
 50:  LDC    0,98(0) 	char 'b'
 51:  OUTC   0,0,0 	write char
 52:  LDC    0,108(0) 	char 'l'
 53:  OUTC   0,0,0 	write char
 54:  LDC    0,101(0) 	char 'e'
 55:  OUTC   0,0,0 	write char
 56:  LDC    0,32(0) 	char ' '
 57:  OUTC   0,0,0 	write char
 58:  LDC    0,100(0) 	char 'd'
 59:  OUTC   0,0,0 	write char
 60:  LDC    0,101(0) 	char 'e'
 61:  OUTC   0,0,0 	write char
 62:  LDC    0,108(0) 	char 'l'
 63:  OUTC   0,0,0 	write char
 64:  LDC    0,32(0) 	char ' '
 65:  OUTC   0,0,0 	write char
 66:  LDC    0,110(0) 	char 'n'
 67:  OUTC   0,0,0 	write char
 68:  LDC    0,117(0) 	char 'u'
 69:  OUTC   0,0,0 	write char
 70:  LDC    0,109(0) 	char 'm'
 71:  OUTC   0,0,0 	write char
 72:  LDC    0,101(0) 	char 'e'
 73:  OUTC   0,0,0 	write char
 74:  LDC    0,114(0) 	char 'r'
 75:  OUTC   0,0,0 	write char
 76:  LDC    0,111(0) 	char 'o'
 77:  OUTC   0,0,0 	write char
 78:  LDC    0,32(0) 	char ' '
 79:  OUTC   0,0,0 	write char
 80:  LDC    0,101(0) 	char 'e'
 81:  OUTC   0,0,0 	write char
 82:  LDC    0,115(0) 	char 's'
 83:  OUTC   0,0,0 	write char
 84:  LDC    0,58(0) 	char ':'
 85:  OUTC   0,0,0 	write char
 86:  LDC    0,32(0) 	char ' '
 87:  OUTC   0,0,0 	write char
 88:  LD     0,0(5) 	load id n
 89:  ST     0,0(6) 	op: push left
 90:  LDC    0,2(0) 	load const 2
 91:  LD     1,0(6) 	op: load left
 92:  MUL    0,1,0 	op *
 93:  ST     0,1(5) 	assign: store to doble
 94:  LD     0,1(5) 	load id doble
 95:  OUT    0,0,0 	write ac
 96:  HALT   0,0,0 	Fin del programa
