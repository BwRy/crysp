# This code is part of crysp
# Copyright (C) 2009 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

from crysp.bits import *

# -----------------------------------------------------------------------------
# 3-DES with all keying options
class TDEA(object):
    size = 64

    def __init__(self,K1,K2=None,K3=None):
        if len(K1)>8:
            assert K2 is None
            assert K3 is None
            K1,K2,K3 = K1[:8],K1[8:],K1[16:]
            if K3=='': K3=K1
        if K2 is None:
            assert K3 is None
            K2 = K1
        if K3 is None:
            K3 = K1
        self.E1 = DES(K1)
        self.E2 = DES(K2)
        self.E3 = DES(K3)

    def enc(self,M):
        return self.E3.enc(self.E2.dec(self.E1.enc(M)))

    def dec(self,C):
        return self.E1.dec(self.E2.enc(self.E3.dec(C)))

# -----------------------------------------------------------------------------
# DES block cipher primitive
class DES(object):
    size = 64

    def __init__(self,K):
        assert len(K)==self.size/8
        self.K = Bits(K,self.size)

    def enc(self,M):
        assert len(M)==8
        M = Bits(M)
        K = self.K
        assert M.size==64
        k = PC1(K)
        blk = IP(M)
        L = blk[0:32]
        R = blk[32:64]
        for r in range(16):
            fout = F(R,k,r)
            L = L^fout
            L,R = R,L
        L,R = R,L
        C = Bits(0,64)
        C[0:32] = L
        C[32:64] = R
        return hex(IPinv(C))

    def dec(self,C):
        assert len(C)==8
        C = Bits(C)
        K = self.K
        assert C.size==64
        k = PC1(K)
        blk = IP(C)
        L = blk[0:32]
        R = blk[32:64]
        for r in range(16)[::-1]:
            fout = F(R,k,r)
            L = L^fout
            L,R = R,L
        L,R = R,L
        M = Bits(0,64)
        M[0:32] = L
        M[32:64] = R
        return hex(IPinv(M))

# DES internals:
#---------------

def subkey(k,r):
    C = k[0:28]
    D = k[28:56]
    shifts = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
    s = sum(shifts[:r+1])
    C = C>>s | C<<(28-s)
    D = D>>s | D<<(28-s)
    return PC2(C//D)

def F(R,k,r):
    RE = E(R)
    Z  = Bits(0,32)
    fk = subkey(k,r)
    s  = RE^fk
    ri,ro = 0,0
    for n in range(8):
        nri,nro = ri+6,ro+4
        x = s[ri:nri]
        i = x[(5,0)].ival
        j = x[(4,3,2,1)].ival
        Z[ro:nro] = Bits(S(n,(i<<4)+j),4)[::-1]
        ri,ro = nri,nro
    return P(Z)

def IP(M):
    assert M.size==64
    table = [57, 49, 41, 33, 25, 17, 9,  1,
    	     59, 51, 43, 35, 27, 19, 11, 3,
    	     61, 53, 45, 37, 29, 21, 13, 5,
    	     63, 55, 47, 39, 31, 23, 15, 7,
    	     56, 48, 40, 32, 24, 16, 8,  0,
    	     58, 50, 42, 34, 26, 18, 10, 2,
    	     60, 52, 44, 36, 28, 20, 12, 4,
    	     62, 54, 46, 38, 30, 22, 14, 6]
    return M[table]

def IPinv(M):
    assert M.size==64
    table = [39,  7, 47, 15, 55, 23, 63, 31,
	     38,  6, 46, 14, 54, 22, 62, 30,
	     37,  5, 45, 13, 53, 21, 61, 29,
	     36,  4, 44, 12, 52, 20, 60, 28,
	     35,  3, 43, 11, 51, 19, 59, 27,
	     34,  2, 42, 10, 50, 18, 58, 26,
	     33,  1, 41,  9, 49, 17, 57, 25,
	     32,  0, 40,  8, 48, 16, 56, 24]
    return M[table]

def PC1(K):
    table = [56, 48, 40, 32, 24, 16,  8,
	      0, 57, 49, 41, 33, 25, 17,
	      9,  1, 58, 50, 42, 34, 26,
	     18, 10,  2, 59, 51, 43, 35,
	     62, 54, 46, 38, 30, 22, 14,
	      6, 61, 53, 45, 37, 29, 21,
	     13,  5, 60, 52, 44, 36, 28,
	     20, 12,  4, 27, 19, 11,  3]
    return  K[table]

def PC2(K):
    assert K.size==56
    table = [13, 16, 10, 23,  0,  4,
	      2, 27, 14,  5, 20,  9,
	     22, 18, 11,  3, 25,  7,
	     15,  6, 26, 19, 12,  1,
	     40, 51, 30, 36, 46, 54,
	     29, 39, 50, 44, 32, 47,
	     43, 48, 38, 55, 33, 52,
	     45, 41, 49, 35, 28, 31]
    return  K[table]

def E(L):
    assert L.size==32
    table = [31,  0,  1,  2,  3,  4,
	      3,  4,  5,  6,  7,  8,
	      7,  8,  9, 10, 11, 12,
	     11, 12, 13, 14, 15, 16,
	     15, 16, 17, 18, 19, 20,
	     19, 20, 21, 22, 23, 24,
	     23, 24, 25, 26, 27, 28,
	     27, 28, 29, 30, 31,  0]
    return L[table]

def P(s):
    assert s.size==32
    table = [15, 6, 19, 20, 28, 11,
	     27, 16, 0, 14, 22, 25,
	     4, 17, 30, 9, 1, 7,
	     23,13, 31, 26, 2, 8,
	     18, 12, 29, 5, 21, 10,
	     3, 24]
    return  s[table]

def S(n,x):
    assert 0 <= n < 8
    assert 0 <= x < 64
    boxes = [
	     # S1
	     [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7,
	      0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8,
	      4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0,
	      15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
	     # S2
	     [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10,
	      3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5,
	      0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15,
	      13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
	     # S3
	     [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8,
	      13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1,
	      13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7,
	      1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
	     # S4
	     [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15,
	      13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9,
	      10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4,
	      3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
	     # S5
	     [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9,
	      14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6,
	      4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14,
	      11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
	     # S6
	     [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11,
	      10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8,
	      9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6,
	      4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
	     # S7
	     [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1,
	      13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6,
	      1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2,
	      6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
	     # S8
	     [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7,
	      1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2,
	      7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8,
	      2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
	]
    return Bits(boxes[n][x],4)




