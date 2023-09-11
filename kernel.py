#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：BDD 
@File    ：kernel.py
@Author  ：ZiHao Li
@Date    ：2023/8/30 14:31 
"""
from dd import autoref as _bdd


def init_bdd(n, r):
    global BDD, Fa, Fb, Fc, Fd, k
    BDD = _bdd.BDD()
    for i in range(n):
        BDD.add_var('q%d' % i)
    Fa = []
    Fb = []
    Fc = []
    Fd = []
    for i in range(r):
        Fa.append(BDD.false)
        Fb.append(BDD.false)
        Fc.append(BDD.false)
        Fd.append(BDD.false)
    k = 0


def init_basis_state(basis):
    global BDD, Fd
    n = len(BDD.vars)
    assert basis < (1 << n), "Basis state is out of range!"
    tmp = dict()
    for i in range(n):
        tmp['q%d' % i] = bool((basis >> i) & 1)
    Fd[0] = BDD.cube(tmp)


def Car(A, B, C):
    return BDD.add_expr(r'({A} & {B}) | (({A} | {B}) & {C})'.format(A=A, B=B, C=C))


def Sum(A, B, C):
    return BDD.add_expr(r'{A} ^ {B} ^ {C}'.format(A=A, B=B, C=C))


def X(target):
    global Fa, Fb, Fc, Fd
    r = len(Fd)
    trans = lambda x: (BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.false}, x)) | (
            ~BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.true}, x))
    for i in range(r):
        Fa[i] = trans(Fa[i])
        Fb[i] = trans(Fb[i])
        Fc[i] = trans(Fc[i])
        Fd[i] = trans(Fd[i])


def Y(target):
    global Fa, Fb, Fc, Fd
    r = len(Fd)
    g = lambda x: (BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.false}, x)) | (
            ~BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.true}, x))
    d1 = lambda x: (BDD.var('q%d' % target) & x) | (~BDD.var('q%d' % target) & ~x)
    d2 = lambda x: (BDD.var('q%d' % target) & ~x) | (~BDD.var('q%d' % target) & x)
    Ca = []
    Ca.append(~BDD.var('q%d' % target))
    tmpa = []
    for i in range(r):
        Da = d1(g(Fc[i]))
        Ca.append(Car(Da, BDD.false, Ca[i]))
        tmpa.append(Sum(Da, BDD.false, Ca[i]))
    Cb = []
    Cb.append(~BDD.var('q%d' % target))
    tmpb = []
    for i in range(r):
        Db = d1(g(Fd[i]))
        Cb.append(Car(Db, BDD.false, Cb[i]))
        tmpb.append(Sum(Db, BDD.false, Cb[i]))
    Cc = []
    Cc.append(BDD.var('q%d' % target))
    tmpc = []
    for i in range(r):
        Dc = d2(g(Fa[i]))
        Cc.append(Car(Dc, BDD.false, Cc[i]))
        tmpc.append(Sum(Dc, BDD.false, Cc[i]))
    Cd = []
    Cd.append(BDD.var('q%d' % target))
    tmpd = []
    for i in range(r):
        Dd = d2(g(Fb[i]))
        Cd.append(Car(Dd, BDD.false, Cd[i]))
        tmpd.append(Sum(Dd, BDD.false, Cd[i]))
    # Overflow
    # 先进行符号拓展，然后算出提前溢出的部分，再进行符号位判断
    tmpa.append(Sum(d1(g(Fc[r - 1])), BDD.false, Ca[r]))
    tmpb.append(Sum(d1(g(Fd[r - 1])), BDD.false, Cb[r]))
    tmpc.append(Sum(d2(g(Fa[r - 1])), BDD.false, Cc[r]))
    tmpd.append(Sum(d2(g(Fb[r - 1])), BDD.false, Cd[r]))
    if tmpa[-1] == tmpa[-2] and tmpb[-1] == tmpb[-2] and tmpc[-1] == tmpc[-2] and tmpd[-1] == tmpd[-2]:
        tmpa.pop()
        tmpb.pop()
        tmpc.pop()
        tmpd.pop()
    Fa = tmpa.copy()
    Fb = tmpb.copy()
    Fc = tmpc.copy()
    Fd = tmpd.copy()


def Z(target):
    global Fa, Fb, Fc, Fd
    r = len(Fd)
    g = lambda x: (~BDD.var('q%d' % target) & x) | (BDD.var('q%d' % target) & ~x)

    def trans(x):
        Cx = []
        Cx.append(BDD.var('q%d' % target))
        tmpx = []
        for i in range(r):
            Gx = g(x[i])
            Cx.append(Car(Gx, BDD.false, Cx[i]))
            tmpx.append(Sum(Gx, BDD.false, Cx[i]))
        tmpx.append(Sum(g(x[r - 1]), BDD.false, Cx[r]))
        return tmpx.copy()

    Fa = trans(Fa)
    Fb = trans(Fb)
    Fc = trans(Fc)
    Fd = trans(Fd)
    # Overflow
    if Fa[-1] == Fa[-2] and Fb[-1] == Fb[-2] and Fc[-1] == Fc[-2] and Fd[-1] == Fd[-2]:
        Fa.pop()
        Fb.pop()
        Fc.pop()
        Fd.pop()


def H(target):
    global Fa, Fb, Fc, Fd, k
    r = len(Fd)
    g = lambda x: BDD.let({'q%d' % target: BDD.false}, x)
    d = lambda x: (~BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.true}, x)) | (BDD.var('q%d' % target) & ~x)

    def trans(x):
        Cx = []
        Cx.append(BDD.var('q%d' % target))
        tmpx = []
        for i in range(r):
            Gx = g(x[i])
            Dx = d(x[i])
            Cx.append(Car(Gx, Dx, Cx[i]))
            tmpx.append(Sum(Gx, Dx, Cx[i]))
        tmpx.append(Sum(g(x[r - 1]), d(x[r - 1]), Cx[r]))
        return tmpx.copy()

    Fa = trans(Fa)
    Fb = trans(Fb)
    Fc = trans(Fc)
    Fd = trans(Fd)
    k += 1
    # Overflow
    if Fa[-1] == Fa[-2] and Fb[-1] == Fb[-2] and Fc[-1] == Fc[-2] and Fd[-1] == Fd[-2]:
        Fa.pop()
        Fb.pop()
        Fc.pop()
        Fd.pop()


def S(target):
    global Fa, Fb, Fc, Fd
    r = len(Fd)
    trans1 = lambda x, y: (~BDD.var('q%d' % target) & x) | (BDD.var('q%d' % target) & y)
    g = lambda x, y: (~BDD.var('q%d' % target) & x) | (BDD.var('q%d' % target) & ~y)
    tmpa = []
    tmpb = []
    for i in range(r):
        tmpa.append(trans1(Fa[i], Fc[i]))
        tmpb.append(trans1(Fb[i], Fd[i]))
    tmpa.append(tmpa[-1])
    tmpb.append(tmpb[-1])

    def trans2(x, y):
        Cx = []
        Cx.append(BDD.var('q%d' % target))
        tmpx = []
        for i in range(r):
            Gx = g(x[i], y[i])
            Cx.append(Car(Gx, BDD.false, Cx[i]))
            tmpx.append(Sum(Gx, BDD.false, Cx[i]))
        tmpx.append(Sum(g(x[r - 1], y[r - 1]), BDD.false, Cx[r]))
        return tmpx.copy()

    Fc = trans2(Fc, Fa)
    Fd = trans2(Fd, Fb)
    Fa = tmpa.copy()
    Fb = tmpb.copy()
    # Overflow
    if Fa[-1] == Fa[-2] and Fb[-1] == Fb[-2] and Fc[-1] == Fc[-2] and Fd[-1] == Fd[-2]:
        Fa.pop()
        Fb.pop()
        Fc.pop()
        Fd.pop()


def T(target):
    global Fa, Fb, Fc, Fd
    r = len(Fd)
    trans1 = lambda x, y: (~BDD.var('q%d' % target) & x) | (BDD.var('q%d' % target) & y)
    g = lambda x, y: (~BDD.var('q%d' % target) & x) | (BDD.var('q%d' % target) & ~y)
    tmpa = []
    tmpb = []
    tmpc = []
    for i in range(r):
        tmpa.append(trans1(Fa[i], Fb[i]))
        tmpb.append(trans1(Fb[i], Fc[i]))
        tmpc.append(trans1(Fc[i], Fd[i]))
    tmpa.append(tmpa[-1])
    tmpb.append(tmpb[-1])
    tmpc.append(tmpc[-1])
    Cd = []
    Cd.append(BDD.var('q%d' % target))
    tmpd = []
    for i in range(r):
        Gd = g(Fd[i], Fa[i])
        Cd.append(Car(Gd, BDD.false, Cd[i]))
        tmpd.append(Sum(Gd, BDD.false, Cd[i]))
    tmpd.append(Sum(g(Fd[r - 1], Fa[r - 1]), BDD.false, Cd[r]))
    Fa = tmpa.copy()
    Fb = tmpb.copy()
    Fc = tmpc.copy()
    Fd = tmpd.copy()
    # Overflow
    if Fa[-1] == Fa[-2] and Fb[-1] == Fb[-2] and Fc[-1] == Fc[-2] and Fd[-1] == Fd[-2]:
        Fa.pop()
        Fb.pop()
        Fc.pop()
        Fd.pop()


def X2P(target):
    # Rx(pi/2) gate
    global Fa, Fb, Fc, Fd, k
    r = len(Fd)
    d = lambda x: (BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.false}, x)) | (
            ~BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.true}, x))

    def trans(x, y, C0):
        Cx = []
        Cx.append(C0)
        tmpx = []
        for i in range(r):
            Dx = d(x[i])
            Cx.append(Car(y[i], ~Dx, Cx[i]))
            tmpx.append(Sum(y[i], ~Dx, Cx[i]))
        tmpx.append(Sum(y[r - 1], ~d(x[r-1]), Cx[r]))
        return tmpx.copy()

    Fa = trans(Fc, Fa, BDD.true)
    Fb = trans(Fd, Fb, BDD.true)
    Fc = trans(Fa, Fc, BDD.false)
    Fd = trans(Fb, Fd, BDD.false)
    k += 1
    # Overflow
    if Fa[-1] == Fa[-2] and Fb[-1] == Fb[-2] and Fc[-1] == Fc[-2] and Fd[-1] == Fd[-2]:
        Fa.pop()
        Fb.pop()
        Fc.pop()
        Fd.pop()


def printBDD():
    print("Fa:")
    for i in range(len(Fa)):
        print(Fa[i].to_expr())
    print("Fb:")
    for i in range(len(Fb)):
        print(Fb[i].to_expr())
    print("Fc:")
    for i in range(len(Fc)):
        print(Fc[i].to_expr())
    print("Fd:")
    for i in range(len(Fd)):
        print(Fd[i].to_expr())


num_qubits = 1
r = 2
k = 1
init_bdd(num_qubits, r)
init_basis_state(0)
printBDD()
X2P(0)
printBDD()
