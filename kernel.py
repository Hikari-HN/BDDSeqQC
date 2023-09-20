#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：BDD 
@File    ：kernel.py
@Author  ：ZiHao Li
@Date    ：2023/8/30 14:31 
"""
from math import ceil, log2, sqrt, pi
import cmath as cm
from dd import autoref as _bdd


class BDDSim:
    def __init__(self, n, r):
        self.BDD = _bdd.BDD()
        self.n = n
        self.r = r
        for i in range(self.n):
            self.BDD.add_var('q%d' % i)
        self.Fa = []
        self.Fb = []
        self.Fc = []
        self.Fd = []
        for i in range(self.r):
            self.Fa.append(self.BDD.false)
            self.Fb.append(self.BDD.false)
            self.Fc.append(self.BDD.false)
            self.Fd.append(self.BDD.false)
        self.k = 0

    def init_basis_state(self, basis):
        assert basis < (1 << self.n), "Basis state is out of range!"
        tmp = dict()
        for i in range(self.n):
            tmp['q%d' % i] = bool((basis >> (self.n - 1 - i)) & 1)
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
        self.simplify_tail()

    def Y(self, target):
        r = len(self.Fd)
        g = lambda x: (self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.false}, x)) | (
                ~self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.true}, x))
        d1 = lambda x: (self.BDD.var('q%d' % target) & x) | (~self.BDD.var('q%d' % target) & ~x)
        d2 = lambda x: (self.BDD.var('q%d' % target) & ~x) | (~self.BDD.var('q%d' % target) & x)

        def trans1(x):
            Cx = []
            Cx.append(~self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Dx = d1(g(x[i]))
                Cx.append(self.Car(Dx, self.BDD.false, Cx[i]))
                tmpx.append(self.Sum(Dx, self.BDD.false, Cx[i]))
            tmpx.append(self.Sum(d1(g(x[r - 1])), self.BDD.false, Cx[r]))
            return tmpx.copy()

        def trans2(x):
            Cx = []
            Cx.append(self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Dx = d2(g(x[i]))
                Cx.append(self.Car(Dx, self.BDD.false, Cx[i]))
                tmpx.append(self.Sum(Dx, self.BDD.false, Cx[i]))
            tmpx.append(self.Sum(d2(g(x[r - 1])), self.BDD.false, Cx[r]))
            return tmpx.copy()

        tmpa = trans1(self.Fc)
        tmpb = trans1(self.Fd)
        tmpc = trans2(self.Fa)
        tmpd = trans2(self.Fb)
        self.Fa = tmpa.copy()
        self.Fb = tmpb.copy()
        self.Fc = tmpc.copy()
        self.Fd = tmpd.copy()
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

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
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

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
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

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
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

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
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

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
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

    def Y2P(self, target):
        # Ry(pi/2) gate
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
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

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
        self.simplify_tail()

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
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

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
        self.simplify_tail()

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
        self.simplify_tail()

    def get_total_bdd(self):
        m = ceil(log2(self.r)) + 2  # The number of index Boolean variables
        for i in range(m):
            self.BDD.add_var('x%d' % i)
        g = []
        for i in range(self.r):
            tmp = dict()
            for j in range(2, m):
                tmp['x%d' % j] = bool((i >> (j - 2)) & 1)
            g.append(self.BDD.cube(tmp))
        FA = self.BDD.false
        FB = self.BDD.false
        FC = self.BDD.false
        FD = self.BDD.false
        for i in range(self.r):
            FA = self.BDD.apply('|', FA, g[i] & self.Fa[i])
            FB = self.BDD.apply('|', FB, g[i] & self.Fb[i])
            FC = self.BDD.apply('|', FC, g[i] & self.Fc[i])
            FD = self.BDD.apply('|', FD, g[i] & self.Fd[i])
        x0 = self.BDD.var('x0')
        x1 = self.BDD.var('x1')
        return (x0 & x1 & FA) | (x0 & ~x1 & FB) | (~x0 & x1 & FC) | (~x0 & ~x1 & FD)

    def get_prob(self, target_list, result_list):
        """
        target_list: the list of target qubits. NOTICE: Elements in a list cannot be the same!
        result_list: the list of measurement results.
        """
        if len(target_list) > len(result_list):
            target_list = target_list[:len(result_list)]
        if len(target_list) < self.n:
            next_list = self.get_next_list(target_list)
            return self.get_prob(next_list, result_list + [0]) + self.get_prob(next_list, result_list + [1])

        F = self.get_total_bdd()
        bool_list = [self.BDD.false, self.BDD.true]
        for i in range(len(target_list)):
            F = self.BDD.let({'q%d' % target_list[i]: bool_list[result_list[i]]}, F)
        FA = self.BDD.let({'x0': self.BDD.true, 'x1': self.BDD.true}, F)
        FB = self.BDD.let({'x0': self.BDD.true, 'x1': self.BDD.false}, F)
        FC = self.BDD.let({'x0': self.BDD.false, 'x1': self.BDD.true}, F)
        FD = self.BDD.let({'x0': self.BDD.false, 'x1': self.BDD.false}, F)
        a = self.get_value(FA)
        b = self.get_value(FB)
        c = self.get_value(FC)
        d = self.get_value(FD)
        w = cm.exp(1j * pi / 4)
        amplitude = (a * w ** 3 + b * w ** 2 + c * w + d) / pow(sqrt(2), self.k)
        return abs(amplitude) ** 2

    def measure(self, target_list, result_list):
        tmp = target_list.copy()
        print("The probability of measuring %s and getting %s is %f." % (
            target_list, result_list, self.get_prob(tmp, result_list)))

    def get_next_list(self, target_list):
        for i in range(self.n):
            if i not in target_list:
                target_list.append(i)
                break
        return target_list

    def get_value(self, bdd):
        m = ceil(log2(self.r)) + 2  # The number of index Boolean variables
        bool_list = [self.BDD.false, self.BDD.true]
        binary_list = []
        for i in range(self.r):
            tmp = dict()
            for j in range(2, m):
                tmp['x%d' % j] = bool_list[(i >> (j - 2)) & 1]
            flag = self.BDD.let(tmp, bdd)
            if flag == self.BDD.true:
                binary_list.append(1)
            else:
                binary_list.append(0)
        if binary_list[-1] == 0:
            return sum([(1 << i) if binary_list[i] == 1 else 0 for i in range(len(binary_list) - 1)])
        else:
            return -sum([(1 << i) if binary_list[i] == 0 else 0 for i in range(len(binary_list) - 1)]) - 1

    def simplify_tail(self):
        if self.Fa[0] == self.BDD.false and self.Fb[0] == self.BDD.false and self.Fc[0] == self.BDD.false and self.Fd[
            0] == self.BDD.false:
            self.Fa = self.Fa[1:]
            self.Fb = self.Fb[1:]
            self.Fc = self.Fc[1:]
            self.Fd = self.Fd[1:]
            self.k -= 2
        self.r = len(self.Fd)

    def simplify_overflow(self):
        if self.Fa[-1] == self.Fa[-2] and self.Fb[-1] == self.Fb[-2] and self.Fc[-1] == self.Fc[-2] and self.Fd[-1] == \
                self.Fd[-2]:
            self.Fa.pop()
            self.Fb.pop()
            self.Fc.pop()
            self.Fd.pop()

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


Sim = BDDSim(5, 2)
Sim.init_basis_state(0)
Sim.CNOT(0, 1)
Sim.CNOT(1, 2)
Sim.CNOT(2, 3)
Sim.H(0)
Sim.H(1)
Sim.H(2)
Sim.H(3)
Sim.CNOT(0, 4)
Sim.CNOT(1, 4)
Sim.CNOT(2, 4)
Sim.CNOT(3, 4)
Sim.measure([0], [1])
print(Sim.r)
