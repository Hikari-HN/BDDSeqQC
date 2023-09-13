#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：BDD 
@File    ：kernel.py
@Author  ：ZiHao Li
@Date    ：2023/8/30 14:31 
"""
from dd import autoref as _bdd
from math import ceil, log2


class BDDSim:
    def __init__(self, n, r):
        self.BDD = _bdd.BDD()
        for i in range(n):
            self.BDD.add_var('q%d' % i)
        self.Fa = []
        self.Fb = []
        self.Fc = []
        self.Fd = []
        for i in range(r):
            self.Fa.append(self.BDD.false)
            self.Fb.append(self.BDD.false)
            self.Fc.append(self.BDD.false)
            self.Fd.append(self.BDD.false)
        self.k = 0
        self.r = r

    def init_basis_state(self, basis):
        n = len(self.BDD.vars)
        assert basis < (1 << n), "Basis state is out of range!"
        tmp = dict()
        for i in range(n):
            tmp['q%d' % i] = bool((basis >> (n - 1 - i)) & 1)
        self.Fd[0] = self.BDD.cube(tmp)

    def Car(self, A, B, C):
        return self.BDD.add_expr(r'({A} & {B}) | (({A} | {B}) & {C})'.format(A=A, B=B, C=C))

    def Sum(self, A, B, C):
        return self.BDD.add_expr(r'{A} ^ {B} ^ {C}'.format(A=A, B=B, C=C))

    def X(self, target):
        r = len(self.Fd)
        trans = lambda x: (self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.false}, x)) | (
                ~self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.true}, x))
        for i in range(r):
            self.Fa[i] = trans(self.Fa[i])
            self.Fb[i] = trans(self.Fb[i])
            self.Fc[i] = trans(self.Fc[i])
            self.Fd[i] = trans(self.Fd[i])
        self.r = len(self.Fd)

    def Y(self, target):
        r = len(self.Fd)
        g = lambda x: (self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.false}, x)) | (
                ~self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.true}, x))
        d1 = lambda x: (self.BDD.var('q%d' % target) & x) | (~self.BDD.var('q%d' % target) & ~x)
        d2 = lambda x: (self.BDD.var('q%d' % target) & ~x) | (~self.BDD.var('q%d' % target) & x)
        Ca = []
        Ca.append(~self.BDD.var('q%d' % target))
        tmpa = []
        for i in range(r):
            Da = d1(g(self.Fc[i]))
            Ca.append(self.Car(Da, self.BDD.false, Ca[i]))
            tmpa.append(self.Sum(Da, self.BDD.false, Ca[i]))
        Cb = []
        Cb.append(~self.BDD.var('q%d' % target))
        tmpb = []
        for i in range(r):
            Db = d1(g(self.Fd[i]))
            Cb.append(self.Car(Db, self.BDD.false, Cb[i]))
            tmpb.append(self.Sum(Db, self.BDD.false, Cb[i]))
        Cc = []
        Cc.append(self.BDD.var('q%d' % target))
        tmpc = []
        for i in range(r):
            Dc = d2(g(self.Fa[i]))
            Cc.append(self.Car(Dc, self.BDD.false, Cc[i]))
            tmpc.append(self.Sum(Dc, self.BDD.false, Cc[i]))
        Cd = []
        Cd.append(self.BDD.var('q%d' % target))
        tmpd = []
        for i in range(r):
            Dd = d2(g(self.Fb[i]))
            Cd.append(self.Car(Dd, self.BDD.false, Cd[i]))
            tmpd.append(self.Sum(Dd, self.BDD.false, Cd[i]))
        # Overflow
        # 先进行符号拓展，然后算出提前溢出的部分，再进行符号位判断
        tmpa.append(self.Sum(d1(g(self.Fc[r - 1])), self.BDD.false, Ca[r]))
        tmpb.append(self.Sum(d1(g(self.Fd[r - 1])), self.BDD.false, Cb[r]))
        tmpc.append(self.Sum(d2(g(self.Fa[r - 1])), self.BDD.false, Cc[r]))
        tmpd.append(self.Sum(d2(g(self.Fb[r - 1])), self.BDD.false, Cd[r]))
        if tmpa[-1] == tmpa[-2] and tmpb[-1] == tmpb[-2] and tmpc[-1] == tmpc[-2] and tmpd[-1] == tmpd[-2]:
            tmpa.pop()
            tmpb.pop()
            tmpc.pop()
            tmpd.pop()
        self.Fa = tmpa.copy()
        self.Fb = tmpb.copy()
        self.Fc = tmpc.copy()
        self.Fd = tmpd.copy()
        self.r = len(self.Fd)

    def Z(self, target):
        r = len(self.Fd)
        g = lambda x: (~self.BDD.var('q%d' % target) & x) | (self.BDD.var('q%d' % target) & ~x)

        def trans(x):
            Cx = []
            Cx.append(self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Gx = g(x[i])
                Cx.append(self.Car(Gx, self.BDD.false, Cx[i]))
                tmpx.append(self.Sum(Gx, self.BDD.false, Cx[i]))
            tmpx.append(self.Sum(g(x[r - 1]), self.BDD.false, Cx[r]))
            return tmpx.copy()

        self.Fa = trans(self.Fa)
        self.Fb = trans(self.Fb)
        self.Fc = trans(self.Fc)
        self.Fd = trans(self.Fd)
        # Overflow
        if self.Fa[-1] == self.Fa[-2] and self.Fb[-1] == self.Fb[-2] and self.Fc[-1] == self.Fc[-2] and self.Fd[-1] == \
                self.Fd[-2]:
            self.Fa.pop()
            self.Fb.pop()
            self.Fc.pop()
            self.Fd.pop()
        self.r = len(self.Fd)

    def H(self, target):
        r = len(self.Fd)
        g = lambda x: self.BDD.let({'q%d' % target: self.BDD.false}, x)
        d = lambda x: (~self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.true}, x)) | (
                self.BDD.var('q%d' % target) & ~x)

        def trans(x):
            Cx = []
            Cx.append(self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Gx = g(x[i])
                Dx = d(x[i])
                Cx.append(self.Car(Gx, Dx, Cx[i]))
                tmpx.append(self.Sum(Gx, Dx, Cx[i]))
            tmpx.append(self.Sum(g(x[r - 1]), d(x[r - 1]), Cx[r]))
            return tmpx.copy()

        self.Fa = trans(self.Fa)
        self.Fb = trans(self.Fb)
        self.Fc = trans(self.Fc)
        self.Fd = trans(self.Fd)
        self.k += 1
        # Overflow
        if self.Fa[-1] == self.Fa[-2] and self.Fb[-1] == self.Fb[-2] and self.Fc[-1] == self.Fc[-2] and self.Fd[-1] == \
                self.Fd[-2]:
            self.Fa.pop()
            self.Fb.pop()
            self.Fc.pop()
            self.Fd.pop()
        self.r = len(self.Fd)

    def S(self, target):
        r = len(self.Fd)
        trans1 = lambda x, y: (~self.BDD.var('q%d' % target) & x) | (self.BDD.var('q%d' % target) & y)
        g = lambda x, y: (~self.BDD.var('q%d' % target) & x) | (self.BDD.var('q%d' % target) & ~y)
        tmpa = []
        tmpb = []
        for i in range(r):
            tmpa.append(trans1(self.Fa[i], self.Fc[i]))
            tmpb.append(trans1(self.Fb[i], self.Fd[i]))
        tmpa.append(tmpa[-1])
        tmpb.append(tmpb[-1])

        def trans2(x, y):
            Cx = []
            Cx.append(self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Gx = g(x[i], y[i])
                Cx.append(self.Car(Gx, self.BDD.false, Cx[i]))
                tmpx.append(self.Sum(Gx, self.BDD.false, Cx[i]))
            tmpx.append(self.Sum(g(x[r - 1], y[r - 1]), self.BDD.false, Cx[r]))
            return tmpx.copy()

        self.Fc = trans2(self.Fc, self.Fa)
        self.Fd = trans2(self.Fd, self.Fb)
        self.Fa = tmpa.copy()
        self.Fb = tmpb.copy()
        # Overflow
        if self.Fa[-1] == self.Fa[-2] and self.Fb[-1] == self.Fb[-2] and self.Fc[-1] == self.Fc[-2] and self.Fd[-1] == \
                self.Fd[-2]:
            self.Fa.pop()
            self.Fb.pop()
            self.Fc.pop()
            self.Fd.pop()
        self.r = len(self.Fd)

    def T(self, target):
        r = len(self.Fd)
        trans1 = lambda x, y: (~self.BDD.var('q%d' % target) & x) | (self.BDD.var('q%d' % target) & y)
        g = lambda x, y: (~self.BDD.var('q%d' % target) & x) | (self.BDD.var('q%d' % target) & ~y)
        tmpa = []
        tmpb = []
        tmpc = []
        for i in range(r):
            tmpa.append(trans1(self.Fa[i], self.Fb[i]))
            tmpb.append(trans1(self.Fb[i], self.Fc[i]))
            tmpc.append(trans1(self.Fc[i], self.Fd[i]))
        tmpa.append(tmpa[-1])
        tmpb.append(tmpb[-1])
        tmpc.append(tmpc[-1])
        Cd = []
        Cd.append(self.BDD.var('q%d' % target))
        tmpd = []
        for i in range(r):
            Gd = g(self.Fd[i], self.Fa[i])
            Cd.append(self.Car(Gd, self.BDD.false, Cd[i]))
            tmpd.append(self.Sum(Gd, self.BDD.false, Cd[i]))
        tmpd.append(self.Sum(g(self.Fd[r - 1], self.Fa[r - 1]), self.BDD.false, Cd[r]))
        self.Fa = tmpa.copy()
        self.Fb = tmpb.copy()
        self.Fc = tmpc.copy()
        self.Fd = tmpd.copy()
        # Overflow
        if self.Fa[-1] == self.Fa[-2] and self.Fb[-1] == self.Fb[-2] and self.Fc[-1] == self.Fc[-2] and self.Fd[-1] == \
                self.Fd[-2]:
            self.Fa.pop()
            self.Fb.pop()
            self.Fc.pop()
            self.Fd.pop()
        self.r = len(self.Fd)

    def X2P(self, target):
        # Rx(pi/2) gate
        r = len(self.Fd)
        d = lambda x: (self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.false}, x)) | (
                ~self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.true}, x))

        def trans1(x, y):
            Cx = []
            Cx.append(self.BDD.true)
            tmpx = []
            for i in range(r):
                Dx = d(x[i])
                Cx.append(self.Car(y[i], ~Dx, Cx[i]))
                tmpx.append(self.Sum(y[i], ~Dx, Cx[i]))
            tmpx.append(self.Sum(y[r - 1], ~d(x[r - 1]), Cx[r]))
            return tmpx.copy()

        def trans2(x, y):
            Cx = []
            Cx.append(self.BDD.false)
            tmpx = []
            for i in range(r):
                Dx = d(x[i])
                Cx.append(self.Car(y[i], Dx, Cx[i]))
                tmpx.append(self.Sum(y[i], Dx, Cx[i]))
            tmpx.append(self.Sum(y[r - 1], d(x[r - 1]), Cx[r]))
            return tmpx.copy()

        tmpa = trans1(self.Fc, self.Fa)
        tmpb = trans1(self.Fd, self.Fb)
        tmpc = trans2(self.Fa, self.Fc)
        tmpd = trans2(self.Fb, self.Fd)
        self.Fa = tmpa.copy()
        self.Fb = tmpb.copy()
        self.Fc = tmpc.copy()
        self.Fd = tmpd.copy()
        self.k += 1
        # Overflow
        if self.Fa[-1] == self.Fa[-2] and self.Fb[-1] == self.Fb[-2] and self.Fc[-1] == self.Fc[-2] and self.Fd[-1] == \
                self.Fd[-2]:
            self.Fa.pop()
            self.Fb.pop()
            self.Fc.pop()
            self.Fd.pop()
        self.r = len(self.Fd)

    def Y2P(self, target):
        # Ry(pi/2) gate
        # TODO BUGGY
        r = len(self.Fd)
        g = lambda x: self.BDD.let({'q%d' % target: self.BDD.false}, x)
        d = lambda x: (self.BDD.var('q%d' % target) & x) | (
                ~self.BDD.var('q%d' % target) & ~self.BDD.let({'q%d' % target: self.BDD.true}, x))

        def trans(x):
            Cx = []
            Cx.append(~self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Gx = g(x[i])
                Dx = d(x[i])
                Cx.append(self.Car(Gx, Dx, Cx[i]))
                tmpx.append(self.Sum(Gx, Dx, Cx[i]))
            tmpx.append(self.Sum(g(x[r - 1]), d(x[r - 1]), Cx[r]))
            return tmpx.copy()

        self.Fa = trans(self.Fa)
        self.Fb = trans(self.Fb)
        self.Fc = trans(self.Fc)
        self.Fd = trans(self.Fd)
        self.k += 1
        # Overflow
        if self.Fa[-1] == self.Fa[-2] and self.Fb[-1] == self.Fb[-2] and self.Fc[-1] == self.Fc[-2] and self.Fd[-1] == \
                self.Fd[-2]:
            self.Fa.pop()
            self.Fb.pop()
            self.Fc.pop()
            self.Fd.pop()
        self.r = len(self.Fd)

    def CNOT(self, control, target):
        r = len(self.Fd)

        def trans(x):
            return (~self.BDD.var('q%d' % control) & x) | (
                    self.BDD.var('q%d' % control) & self.BDD.var('q%d' % target) & self.BDD.let(
                {'q%d' % control: self.BDD.true, 'q%d' % target: self.BDD.false}, x)) | (
                    self.BDD.var('q%d' % control) & ~self.BDD.var('q%d' % target) & self.BDD.let(
                {'q%d' % control: self.BDD.true, 'q%d' % target: self.BDD.true}, x))

        for i in range(r):
            self.Fa[i] = trans(self.Fa[i])
            self.Fb[i] = trans(self.Fb[i])
            self.Fc[i] = trans(self.Fc[i])
            self.Fd[i] = trans(self.Fd[i])
        self.r = len(self.Fd)

    def CZ(self, control, target):
        r = len(self.Fd)
        g = lambda x: (~(self.BDD.var('q%d' % control) & self.BDD.var('q%d' % target)) & x) | (
                self.BDD.var('q%d' % control) & self.BDD.var('q%d' % target) & ~x)

        def trans(x):
            Cx = []
            Cx.append(self.BDD.var('q%d' % control) & self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Gx = g(x[i])
                Cx.append(self.Car(Gx, self.BDD.false, Cx[i]))
                tmpx.append(self.Sum(Gx, self.BDD.false, Cx[i]))
            tmpx.append(self.Sum(g(x[r - 1]), self.BDD.false, Cx[r]))
            return tmpx.copy()

        self.Fa = trans(self.Fa)
        self.Fb = trans(self.Fb)
        self.Fc = trans(self.Fc)
        self.Fd = trans(self.Fd)
        # Overflow
        if self.Fa[-1] == self.Fa[-2] and self.Fb[-1] == self.Fb[-2] and self.Fc[-1] == self.Fc[-2] and self.Fd[-1] == \
                self.Fd[-2]:
            self.Fa.pop()
            self.Fb.pop()
            self.Fc.pop()
            self.Fd.pop()
        self.r = len(self.Fd)

    def Toffoli(self, control1, control2, target):
        # CCNOT gate
        r = len(self.Fd)

        def trans(x):
            return (~(self.BDD.var('q%d' % control1) & self.BDD.var('q%d' % control2)) & x) | (
                    self.BDD.var('q%d' % control1) & self.BDD.var('q%d' % control2) & self.BDD.var(
                'q%d' % target) & self.BDD.let(
                {'q%d' % control1: self.BDD.true, 'q%d' % control2: self.BDD.true, 'q%d' % target: self.BDD.false},
                x)) | (self.BDD.var('q%d' % control1) & self.BDD.var('q%d' % control2) & ~self.BDD.var(
                'q%d' % target) & self.BDD.let(
                {'q%d' % control1: self.BDD.true, 'q%d' % control2: self.BDD.true, 'q%d' % target: self.BDD.true}, x))

        for i in range(r):
            self.Fa[i] = trans(self.Fa[i])
            self.Fb[i] = trans(self.Fb[i])
            self.Fc[i] = trans(self.Fc[i])
            self.Fd[i] = trans(self.Fd[i])

    def Fredkin(self, control, target1, target2):
        # CSWAP gate
        r = len(self.Fd)

        def trans(x):
            return (~(self.BDD.var('q%d' % control) & self.BDD.apply('^', self.BDD.var('q%d' % target1),
                                                                     self.BDD.var('q%d' % target2))) & x) | (
                    self.BDD.var('q%d' % control) & self.BDD.var('q%d' % target1) & ~self.BDD.var(
                'q%d' % target2) & self.BDD.let(
                {'q%d' % control: self.BDD.true, 'q%d' % target1: self.BDD.false, 'q%d' % target2: self.BDD.true},
                x)) | (
                    self.BDD.var('q%d' % control) & ~self.BDD.var('q%d' % target1) & self.BDD.var(
                'q%d' % target2) & self.BDD.let(
                {'q%d' % control: self.BDD.true, 'q%d' % target1: self.BDD.true, 'q%d' % target2: self.BDD.false}, x))

        for i in range(r):
            self.Fa[i] = trans(self.Fa[i])
            self.Fb[i] = trans(self.Fb[i])
            self.Fc[i] = trans(self.Fc[i])
            self.Fd[i] = trans(self.Fd[i])
        self.r = len(self.Fd)

    def get_total_bdd(self):
        r = len(self.Fd)
        m = ceil(log2(r)) + 2  # The number of index Boolean variables
        for i in range(m):
            self.BDD.add_var('x%d' % i)
        g = []
        for i in range(r):
            tmp = dict()
            for j in range(2, m):
                tmp['x%d' % j] = bool((i >> (j - 2)) & 1)
            g.append(self.BDD.cube(tmp))
        FA = self.BDD.false
        FB = self.BDD.false
        FC = self.BDD.false
        FD = self.BDD.false
        for i in range(r):
            FA = self.BDD.apply('|', FA, g[i] & self.Fa[i])
            FB = self.BDD.apply('|', FB, g[i] & self.Fb[i])
            FC = self.BDD.apply('|', FC, g[i] & self.Fc[i])
            FD = self.BDD.apply('|', FD, g[i] & self.Fd[i])
        x0 = self.BDD.var('x0')
        x1 = self.BDD.var('x1')
        return (x0 & x1 & FA) | (x0 & ~x1 & FB) | (~x0 & x1 & FC) | (~x0 & ~x1 & FD)

    def measure(self):
        pass

    def print_bdd(self):
        print("Fa:")
        for i in range(len(self.Fa)):
            print(self.Fa[i].to_expr())
        print("Fb:")
        for i in range(len(self.Fb)):
            print(self.Fb[i].to_expr())
        print("Fc:")
        for i in range(len(self.Fc)):
            print(self.Fc[i].to_expr())
        print("Fd:")
        for i in range(len(self.Fd)):
            print(self.Fd[i].to_expr())


Sim = BDDSim(3, 2)
Sim.init_basis_state(5)
Sim.print_bdd()
Sim.Fredkin(0, 1, 2)
Sim.print_bdd()
