# Önálló laboratórium
BME Project Laboratory course - 2015/2016/2 semester

## Feladat
Feladatom  a  téma  során,  hogy  megismerkedjek  az  SDN  hálózatok  monitorozásának lehetőségeivel, tehát, hogy hogyan lehet olyan QoS(Quality  of  Service)paramétereket mérni SDN hálózatokban, mint a felhasznált és az elérhető sávszélesség, a csomagvesztés vagy  a késleltetés. Illetve az ötletek megvalósítása hálózat emulátorban.

## A mérési környezet
Mininetben szimulálva a python scriptekben definiált topológia.
```
       h1
       |
h2 -- s1 ---- s2 -- h3
       |   X   |
       s3      s4
       |       |
       h4      h5
