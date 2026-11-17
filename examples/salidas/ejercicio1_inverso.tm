  0:  LD     6,0(0) 	load maxaddress from location 0
  1:  ST     0,0(0) 	clear location 0
  2:  IN     0,0,0 	read integer for a
  3:  ST     0,0(5) 	read: store to a
  4:  IN     0,0,0 	read integer for b
  5:  ST     0,1(5) 	read: store to b
  6:  IN     0,0,0 	read integer for c
  7:  ST     0,2(5) 	read: store to c
  8:  IN     0,0,0 	read integer for d
  9:  ST     0,3(5) 	read: store to d
 10:  LD     0,3(5) 	load id d
 11:  OUT    0,0,0 	write ac
 12:  LD     0,2(5) 	load id c
 13:  OUT    0,0,0 	write ac
 14:  LD     0,1(5) 	load id b
 15:  OUT    0,0,0 	write ac
 16:  LD     0,0(5) 	load id a
 17:  OUT    0,0,0 	write ac
 18:  HALT   0,0,0 	Fin del programa
