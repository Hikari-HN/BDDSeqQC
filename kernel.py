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
    global BDD, Fa, Fb, Fc, Fd
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
    trans = lambda x: BDD.let({'q%d' % target: BDD.false}, x) & BDD.var('q%d' % target) | (
            BDD.let({'q%d' % target: BDD.true}, x) & ~BDD.var('q%d' % target))
    for i in range(r):
        Fa[i] = trans(Fa[i])
        Fb[i] = trans(Fb[i])
        Fc[i] = trans(Fc[i])
        Fd[i] = trans(Fd[i])


def Y(target):
    global Fa, Fb, Fc, Fd
    r = len(Fd)
    g = lambda x: BDD.let({'q%d' % target: BDD.false}, x) & BDD.var('q%d' % target) | (
            BDD.let({'q%d' % target: BDD.true}, x) & ~BDD.var('q%d' % target))
    d = lambda x: (BDD.var('q%d' % target) & x) | (~BDD.var('q%d' % target) & ~x)
    Ca = []
    Ca.append(~BDD.var('q%d' % target))
    for i in range(r - 1):
        Da = d(g(Fc[i]))
        Ca.append(Car(Da, BDD.false, Ca[i]))
        Fa[i] = Sum(Da, BDD.false, Ca[i])
    Cb = []
    Cb.append(BDD.var('q%d' % target))
    for i in range(r - 1):
        Db = d(g(Fd[i]))
        Cb.append(Car(Db, BDD.false, Cb[i]))
        Fb[i] = Sum(Db, BDD.false, Cb[i])
    Cc = []
    Cc.append(BDD.var('q%d' % target))
    for i in range(r - 1):
        Dc = d(g(Fa[i]))
        Cc.append(Car(Dc, BDD.false, Cc[i]))
        Fc[i] = Sum(Dc, BDD.false, Cc[i])
    Cd = []
    Cd.append(~BDD.var('q%d' % target))
    for i in range(r - 1):
        Dd = d(g(Fb[i]))
        Cd.append(Car(Dd, BDD.false, Cd[i]))
        Fd[i] = Sum(Dd, BDD.false, Cd[i])


num_qubits = 3
r = 3
init_bdd(num_qubits, r)
init_basis_state(0)
print(Fa[0].to_expr())
print(Fb[0].to_expr())
print(Fc[0].to_expr())
print(Fd[0].to_expr())
Y(0)
print(Fa[0].to_expr())
print(Fb[0].to_expr())
print(Fc[0].to_expr())
print(Fd[0].to_expr())
