# Algorithms for mutual exclusion in a distributed system
## Lamportov protokol 
=====================================================

P1: c1=12 red_zahtjeva: 
P2: c2=7  red_zahtjeva: 
P3: c3=20 red_zahtjeva: 

P1 generira zahtjev(1, 12)
P1: c1=12, red_zahtjeva: zahtjev(1, 12)

P2 generira zahtjev(2, 7)
P2: c2=7,  red_zahtjeva: zahtjev(2, 7)

-----------------------------------------------------

P2 prima zahtjev(1, 12)
c2 = max(7, 12) + 1 = 13
salje odgovor(1, 13) prema P1
P2: c2=13,  red_zahtjeva: zahtjev(2, 7), zahtjev(1, 12) ---- red nije organiziran FIFO, nego prema log.satu

P3 prima zahtjev(1, 12)
c3 = max(20, 12) + 1 = 21
P3 salje odgovor(1, 21) prema P1
P3: c3=21 red_zahtjeva: zahtjev(1, 12)

P3 prima zahtjev(2, 7)
c3 = max(21, 7) + 1 = 22
P3 salje odgovor(2, 21) prema P2
P3: c3=22 red_zahtjeva: zahtjev(2, 7), zahtjev(1, 12)

P1 prima zahtjev(2, 7) 
c1 = max(12, 7) + 1 = 13
P1 salje odgovor(2, 13) prema P2 
P1: c1=13 red_zahtjeva: zahtjev(2, 7), zahtjev(1, 12)

-----------------------------------------------------

P1 prima odgovor(1, 21) od P3
c1 = max(13, 21) + 1 = 22

P1 prima odgovor(1, 13) od P2
c1 = max(22, 13) + 1 = 23 ---> primio sve odgovore

P2 prima odgovor(2, 22) od P3
c2 = max(13, 22) + 1 = 23

P2 prima odgovor(2, 13) od P1
c2 = max(23, 13) + 1 = 24 ---> primio sve odgovore

-----------------------------------------------------

P1: c1=23, red zahtjeva: zahtjev(2,7), zahtjev(1,12)
P2: c2=24, red zahtjeva: zahtjev(2,7), zahtjev(1,12) (u K.O.) ---> jer je prvi u redu cekanja
P3: c3=22, red zahtjeva: zahtjev(2,7), zahtjev(1,12)

P2 generira izlazak(2, 7)
P2: c2=24, red_zahtjeva: zahtjev(1, 12)

P3 prima izlazak(2, 7)
c3 = max(22, 7) + 1 = 23
P3: c3=23, red_zahtjeva: zahtjev(1, 12)

P1 prima izlazak(2, 7)
c1 = max(23, 7) + 1 = 24
P1: c1=24, red_zahtjeva: zahtjev(1, 12)

-----------------------------------------------------

P1: c1=24, red zahtjeva: zahtjev(1,12) (u K.O.) 
P2: c2=24, red zahtjeva: zahtjev(1,12)
P3: c3=23, red zahtjeva: zahtjev(1,12)

P1 generira izlazak(1, 12)
P1: c1=24, red_zahtjeva: 

P3 prima izlazak(1, 12)
c3 = max(23, 12) + 1 = 24
P3: c3=23, red_zahtjeva: 

P2 prima izlazak(1, 12)
c2 = max(24, 12) + 1 = 25
P2: c1=24, red_zahtjeva:

-----------------------------------------------------

P1: c1=24, red zahtjeva:
P2: c2=25, red zahtjeva:
P3: c3=24, red zahtjeva:

## Ricart i Agrawala
=====================================================

c1 = 12
c2 = 7
c3 = 20

zahtjev(1, 12)
zahtjev(2, 7)

c2 = max(7, 12) + 1 = 13
ne salje odgovor P1 jer je 7 < 12

c1 = max(12, 7) + 1 = 13
salje odgovor(1, 7) P2 jer je 7 < 12

c3 = max(20, 12) + 1 = 21
salje odgovor(3, 12) P1 jer je 12 < 20

c3 = max(21, 7) + 1 = 22
salje odgovor(3, 7) P2 jer je 7 < 21

-----------------------------------------------------

c1 = 13 prima odgovor(3, 12) od P3 ---> "primio 1 odg"
c1 = max(13, 12) + 1 = 14

c2 = 13 prima odgovor(1, 7) od P1 ---> "primio 1 odg"
c2 = max(13, 7) + 1 = 14

c2 = 14 prima odgovor(3, 7) od P3 ---> "primio oba odg" ---> K.O.
c2 = max(14, 7) + 1 = 15 

-----------------------------------------------------

nakon izlaska iz K.O. 
P2 salje odgovor(2, 12)

c1 = 14 prima odgovor(2, 12) od P2 ---> "primio oba odg" ---> K.O.
c1 = max(14, 12) + 1 = 15

-----------------------------------------------------

c1 = 15
c2 = 15
c3 = 22