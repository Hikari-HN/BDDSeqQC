from dd import autoref as _bdd
from math import *


# bdd = _bdd.BDD()
# bdd.declare('x', 'y', 'z', 'w')

# # conjunction (in TLA+ syntax)
# u = bdd.add_expr(r'x /\ y')
# v = bdd.add_expr(r'x /\ w')
# s = bdd.let(dict(x=bdd.false), u)
# print(s.to_expr())
# print(u.to_expr())
# print(v.to_expr())
# # # substitute variables for variables (rename)
# # rename = dict(x='z', y='w')
# # v = bdd.let(rename, u)
# # # substitute constants for variables (cofactor)
# # values = dict(x=True, y=False)
# # v = bdd.let(values, u)
# # # substitute BDDs for variables (compose)
# # d = dict(x=bdd.add_expr(r'z \/ w'))
# # v = bdd.let(d, u)
# # # as Python operators
# # v = bdd.var('z') & bdd.var('w')
# u = bdd.var('x')
# v = bdd.add_expr(r'{A} ^ {B}'.format(A=u, B=bdd.true))
# s = bdd.add_expr(r'{A} ^ {B}'.format(A=u, B=~u))
# t = bdd.add_expr(r'{A} ^ {B}'.format(A=u, B=bdd.false))
# print(v.to_expr())
# print(s.to_expr())
# print(t.to_expr())

BDD = _bdd.BDD()
for i in range(3):
    BDD.add_var('q%d' % i)
Fa = []
Fb = []
Fc = []
Fd = []
for i in range(2000000):
    Fa.append(BDD.false)
    Fb.append(BDD.false)
    Fc.append(BDD.false)
    Fd.append(BDD.false)
k = 0



# def init_bdd(n, r):
#     global BDD, Fa, Fb, Fc, Fd, k
#     BDD = _bdd.BDD()
#     for i in range(n):
#         BDD.add_var('q%d' % i)
#     Fa = []
#     Fb = []
#     Fc = []
#     Fd = []
#     for i in range(r):
#         Fa.append(BDD.false)
#         Fb.append(BDD.false)
#         Fc.append(BDD.false)
#         Fd.append(BDD.false)
#     k = 0
#
#
# init_bdd(3, 100)

# def init_bdd(n, r):
#     global BDD, Fa, Fb, Fc, Fd, k
#     BDD = _bdd.BDD()
#     for i in range(n):
#         BDD.add_var('q%d' % i)
#     Fa = []
#     Fb = []
#     Fc = []
#     Fd = []
#     for i in range(r):
#         Fa.append(BDD.false)
#         Fb.append(BDD.false)
#         Fc.append(BDD.false)
#         Fd.append(BDD.false)
#     k = 0
#
#
# def init_basis_state(basis):
#     global BDD, Fd
#     n = len(BDD.vars)
#     assert basis < (1 << n), "Basis state is out of range!"
#     tmp = dict()
#     for i in range(n):
#         tmp['q%d' % i] = bool((basis >> (n - 1 - i)) & 1)
#     Fd[0] = BDD.cube(tmp)
#
#
# def Car(A, B, C):
#     return BDD.add_expr(r'({A} & {B}) | (({A} | {B}) & {C})'.format(A=A, B=B, C=C))
#
#
# def Sum(A, B, C):
#     return BDD.add_expr(r'{A} ^ {B} ^ {C}'.format(A=A, B=B, C=C))
#
#
# def X(target):
#     global Fa, Fb, Fc, Fd
#     r = len(Fd)
#     trans = lambda x: (BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.false}, x)) | (
#             ~BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.true}, x))
#     for i in range(r):
#         Fa[i] = trans(Fa[i])
#         Fb[i] = trans(Fb[i])
#         Fc[i] = trans(Fc[i])
#         Fd[i] = trans(Fd[i])
#
#
# def Y(target):
#     global Fa, Fb, Fc, Fd
#     r = len(Fd)
#     g = lambda x: (BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.false}, x)) | (
#             ~BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.true}, x))
#     d1 = lambda x: (BDD.var('q%d' % target) & x) | (~BDD.var('q%d' % target) & ~x)
#     d2 = lambda x: (BDD.var('q%d' % target) & ~x) | (~BDD.var('q%d' % target) & x)
#     Ca = []
#     Ca.append(~BDD.var('q%d' % target))
#     tmpa = []
#     for i in range(r):
#         Da = d1(g(Fc[i]))
#         Ca.append(Car(Da, BDD.false, Ca[i]))
#         tmpa.append(Sum(Da, BDD.false, Ca[i]))
#     Cb = []
#     Cb.append(~BDD.var('q%d' % target))
#     tmpb = []
#     for i in range(r):
#         Db = d1(g(Fd[i]))
#         Cb.append(Car(Db, BDD.false, Cb[i]))
#         tmpb.append(Sum(Db, BDD.false, Cb[i]))
#     Cc = []
#     Cc.append(BDD.var('q%d' % target))
#     tmpc = []
#     for i in range(r):
#         Dc = d2(g(Fa[i]))
#         Cc.append(Car(Dc, BDD.false, Cc[i]))
#         tmpc.append(Sum(Dc, BDD.false, Cc[i]))
#     Cd = []
#     Cd.append(BDD.var('q%d' % target))
#     tmpd = []
#     for i in range(r):
#         Dd = d2(g(Fb[i]))
#         Cd.append(Car(Dd, BDD.false, Cd[i]))
#         tmpd.append(Sum(Dd, BDD.false, Cd[i]))
#     # Overflow
#     # 先进行符号拓展，然后算出提前溢出的部分，再进行符号位判断
#     tmpa.append(Sum(d1(g(Fc[r - 1])), BDD.false, Ca[r]))
#     tmpb.append(Sum(d1(g(Fd[r - 1])), BDD.false, Cb[r]))
#     tmpc.append(Sum(d2(g(Fa[r - 1])), BDD.false, Cc[r]))
#     tmpd.append(Sum(d2(g(Fb[r - 1])), BDD.false, Cd[r]))
#     if tmpa[-1] == tmpa[-2] and tmpb[-1] == tmpb[-2] and tmpc[-1] == tmpc[-2] and tmpd[-1] == tmpd[-2]:
#         tmpa.pop()
#         tmpb.pop()
#         tmpc.pop()
#         tmpd.pop()
#     Fa = tmpa.copy()
#     Fb = tmpb.copy()
#     Fc = tmpc.copy()
#     Fd = tmpd.copy()
#
#
# def Z(target):
#     global Fa, Fb, Fc, Fd
#     r = len(Fd)
#     g = lambda x: (~BDD.var('q%d' % target) & x) | (BDD.var('q%d' % target) & ~x)
#
#     def trans(x):
#         Cx = []
#         Cx.append(BDD.var('q%d' % target))
#         tmpx = []
#         for i in range(r):
#             Gx = g(x[i])
#             Cx.append(Car(Gx, BDD.false, Cx[i]))
#             tmpx.append(Sum(Gx, BDD.false, Cx[i]))
#         tmpx.append(Sum(g(x[r - 1]), BDD.false, Cx[r]))
#         return tmpx.copy()
#
#     Fa = trans(Fa)
#     Fb = trans(Fb)
#     Fc = trans(Fc)
#     Fd = trans(Fd)
#     # Overflow
#     if Fa[-1] == Fa[-2] and Fb[-1] == Fb[-2] and Fc[-1] == Fc[-2] and Fd[-1] == Fd[-2]:
#         Fa.pop()
#         Fb.pop()
#         Fc.pop()
#         Fd.pop()
#
#
# def H(target):
#     global Fa, Fb, Fc, Fd, k
#     r = len(Fd)
#     g = lambda x: BDD.let({'q%d' % target: BDD.false}, x)
#     d = lambda x: (~BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.true}, x)) | (BDD.var('q%d' % target) & ~x)
#
#     def trans(x):
#         Cx = []
#         Cx.append(BDD.var('q%d' % target))
#         tmpx = []
#         for i in range(r):
#             Gx = g(x[i])
#             Dx = d(x[i])
#             Cx.append(Car(Gx, Dx, Cx[i]))
#             tmpx.append(Sum(Gx, Dx, Cx[i]))
#         tmpx.append(Sum(g(x[r - 1]), d(x[r - 1]), Cx[r]))
#         return tmpx.copy()
#
#     Fa = trans(Fa)
#     Fb = trans(Fb)
#     Fc = trans(Fc)
#     Fd = trans(Fd)
#     k += 1
#     # Overflow
#     if Fa[-1] == Fa[-2] and Fb[-1] == Fb[-2] and Fc[-1] == Fc[-2] and Fd[-1] == Fd[-2]:
#         Fa.pop()
#         Fb.pop()
#         Fc.pop()
#         Fd.pop()
#
#
# def S(target):
#     global Fa, Fb, Fc, Fd
#     r = len(Fd)
#     trans1 = lambda x, y: (~BDD.var('q%d' % target) & x) | (BDD.var('q%d' % target) & y)
#     g = lambda x, y: (~BDD.var('q%d' % target) & x) | (BDD.var('q%d' % target) & ~y)
#     tmpa = []
#     tmpb = []
#     for i in range(r):
#         tmpa.append(trans1(Fa[i], Fc[i]))
#         tmpb.append(trans1(Fb[i], Fd[i]))
#     tmpa.append(tmpa[-1])
#     tmpb.append(tmpb[-1])
#
#     def trans2(x, y):
#         Cx = []
#         Cx.append(BDD.var('q%d' % target))
#         tmpx = []
#         for i in range(r):
#             Gx = g(x[i], y[i])
#             Cx.append(Car(Gx, BDD.false, Cx[i]))
#             tmpx.append(Sum(Gx, BDD.false, Cx[i]))
#         tmpx.append(Sum(g(x[r - 1], y[r - 1]), BDD.false, Cx[r]))
#         return tmpx.copy()
#
#     Fc = trans2(Fc, Fa)
#     Fd = trans2(Fd, Fb)
#     Fa = tmpa.copy()
#     Fb = tmpb.copy()
#     # Overflow
#     if Fa[-1] == Fa[-2] and Fb[-1] == Fb[-2] and Fc[-1] == Fc[-2] and Fd[-1] == Fd[-2]:
#         Fa.pop()
#         Fb.pop()
#         Fc.pop()
#         Fd.pop()
#
#
# def T(target):
#     global Fa, Fb, Fc, Fd
#     r = len(Fd)
#     trans1 = lambda x, y: (~BDD.var('q%d' % target) & x) | (BDD.var('q%d' % target) & y)
#     g = lambda x, y: (~BDD.var('q%d' % target) & x) | (BDD.var('q%d' % target) & ~y)
#     tmpa = []
#     tmpb = []
#     tmpc = []
#     for i in range(r):
#         tmpa.append(trans1(Fa[i], Fb[i]))
#         tmpb.append(trans1(Fb[i], Fc[i]))
#         tmpc.append(trans1(Fc[i], Fd[i]))
#     tmpa.append(tmpa[-1])
#     tmpb.append(tmpb[-1])
#     tmpc.append(tmpc[-1])
#     Cd = []
#     Cd.append(BDD.var('q%d' % target))
#     tmpd = []
#     for i in range(r):
#         Gd = g(Fd[i], Fa[i])
#         Cd.append(Car(Gd, BDD.false, Cd[i]))
#         tmpd.append(Sum(Gd, BDD.false, Cd[i]))
#     tmpd.append(Sum(g(Fd[r - 1], Fa[r - 1]), BDD.false, Cd[r]))
#     Fa = tmpa.copy()
#     Fb = tmpb.copy()
#     Fc = tmpc.copy()
#     Fd = tmpd.copy()
#     # Overflow
#     if Fa[-1] == Fa[-2] and Fb[-1] == Fb[-2] and Fc[-1] == Fc[-2] and Fd[-1] == Fd[-2]:
#         Fa.pop()
#         Fb.pop()
#         Fc.pop()
#         Fd.pop()
#
#
# def X2P(target):
#     # Rx(pi/2) gate
#     global Fa, Fb, Fc, Fd, k
#     r = len(Fd)
#     d = lambda x: (BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.false}, x)) | (
#             ~BDD.var('q%d' % target) & BDD.let({'q%d' % target: BDD.true}, x))
#
#     def trans1(x, y):
#         Cx = []
#         Cx.append(BDD.true)
#         tmpx = []
#         for i in range(r):
#             Dx = d(x[i])
#             Cx.append(Car(y[i], ~Dx, Cx[i]))
#             tmpx.append(Sum(y[i], ~Dx, Cx[i]))
#         tmpx.append(Sum(y[r - 1], ~d(x[r - 1]), Cx[r]))
#         return tmpx.copy()
#
#     def trans2(x, y):
#         Cx = []
#         Cx.append(BDD.false)
#         tmpx = []
#         for i in range(r):
#             Dx = d(x[i])
#             Cx.append(Car(y[i], Dx, Cx[i]))
#             tmpx.append(Sum(y[i], Dx, Cx[i]))
#         tmpx.append(Sum(y[r - 1], d(x[r - 1]), Cx[r]))
#         return tmpx.copy()
#
#     tmpa = trans1(Fc, Fa)
#     tmpb = trans1(Fd, Fb)
#     tmpc = trans2(Fa, Fc)
#     tmpd = trans2(Fb, Fd)
#     Fa = tmpa.copy()
#     Fb = tmpb.copy()
#     Fc = tmpc.copy()
#     Fd = tmpd.copy()
#     k += 1
#     # Overflow
#     if Fa[-1] == Fa[-2] and Fb[-1] == Fb[-2] and Fc[-1] == Fc[-2] and Fd[-1] == Fd[-2]:
#         Fa.pop()
#         Fb.pop()
#         Fc.pop()
#         Fd.pop()
#
#
# def Y2P(target):
#     # Ry(pi/2) gate
#     global Fa, Fb, Fc, Fd, k
#     r = len(Fd)
#     g = lambda x: BDD.let({'q%d' % target: BDD.false}, x)
#     d = lambda x: (BDD.var('q%d' % target) & x) | (~BDD.var('q%d' % target) & ~BDD.let({'q%d' % target: BDD.true}, x))
#
#     def trans(x):
#         Cx = []
#         Cx.append(~BDD.var('q%d' % target))
#         tmpx = []
#         for i in range(r):
#             Gx = g(x[i])
#             Dx = d(x[i])
#             Cx.append(Car(Gx, Dx, Cx[i]))
#             tmpx.append(Sum(Gx, Dx, Cx[i]))
#         tmpx.append(Sum(g(x[r - 1]), d(x[r - 1]), Cx[r]))
#         return tmpx.copy()
#
#     Fa = trans(Fa)
#     Fb = trans(Fb)
#     Fc = trans(Fc)
#     Fd = trans(Fd)
#     k += 1
#     # Overflow
#     if Fa[-1] == Fa[-2] and Fb[-1] == Fb[-2] and Fc[-1] == Fc[-2] and Fd[-1] == Fd[-2]:
#         Fa.pop()
#         Fb.pop()
#         Fc.pop()
#         Fd.pop()
#
#
# def CNOT(control, target):
#     global Fa, Fb, Fc, Fd
#     r = len(Fd)
#
#     def trans(x):
#         return (~BDD.var('q%d' % control) & x) | (BDD.var('q%d' % control) & BDD.var('q%d' % target) & BDD.let(
#             {'q%d' % control: BDD.true, 'q%d' % target: BDD.false}, x)) | (
#                 BDD.var('q%d' % control) & ~BDD.var('q%d' % target) & BDD.let(
#             {'q%d' % control: BDD.true, 'q%d' % target: BDD.true}, x))
#
#     for i in range(r):
#         Fa[i] = trans(Fa[i])
#         Fb[i] = trans(Fb[i])
#         Fc[i] = trans(Fc[i])
#         Fd[i] = trans(Fd[i])
#
#
# def CZ(control, target):
#     global Fa, Fb, Fc, Fd
#     r = len(Fd)
#     g = lambda x: (~(BDD.var('q%d' % control) & BDD.var('q%d' % target)) & x) | (
#             BDD.var('q%d' % control) & BDD.var('q%d' % target) & ~x)
#
#     def trans(x):
#         Cx = []
#         Cx.append(BDD.var('q%d' % control) & BDD.var('q%d' % target))
#         tmpx = []
#         for i in range(r):
#             Gx = g(x[i])
#             Cx.append(Car(Gx, BDD.false, Cx[i]))
#             tmpx.append(Sum(Gx, BDD.false, Cx[i]))
#         tmpx.append(Sum(g(x[r - 1]), BDD.false, Cx[r]))
#         return tmpx.copy()
#
#     Fa = trans(Fa)
#     Fb = trans(Fb)
#     Fc = trans(Fc)
#     Fd = trans(Fd)
#     # Overflow
#     if Fa[-1] == Fa[-2] and Fb[-1] == Fb[-2] and Fc[-1] == Fc[-2] and Fd[-1] == Fd[-2]:
#         Fa.pop()
#         Fb.pop()
#         Fc.pop()
#         Fd.pop()
#
#
# def Toffoli(control1, control2, target):
#     # CCNOT gate
#     global Fa, Fb, Fc, Fd
#     r = len(Fd)
#
#     def trans(x):
#         return (~(BDD.var('q%d' % control1) & BDD.var('q%d' % control2)) & x) | (
#                 BDD.var('q%d' % control1) & BDD.var('q%d' % control2) & BDD.var('q%d' % target) & BDD.let(
#             {'q%d' % control1: BDD.true, 'q%d' % control2: BDD.true, 'q%d' % target: BDD.false}, x)) | (
#                 BDD.var('q%d' % control1) & BDD.var('q%d' % control2) & ~BDD.var('q%d' % target) & BDD.let(
#             {'q%d' % control1: BDD.true, 'q%d' % control2: BDD.true, 'q%d' % target: BDD.true}, x))
#
#     for i in range(r):
#         Fa[i] = trans(Fa[i])
#         Fb[i] = trans(Fb[i])
#         Fc[i] = trans(Fc[i])
#         Fd[i] = trans(Fd[i])
#
#
# def Fredkin(control, target1, target2):
#     # CSWAP gate
#     global Fa, Fb, Fc, Fd
#     r = len(Fd)
#
#     def trans(x):
#         return (~(BDD.var('q%d' % control) & BDD.apply('^', BDD.var('q%d' % target1),
#                                                        BDD.var('q%d' % target2))) & x) | (
#                 BDD.var('q%d' % control) & BDD.var('q%d' % target1) & ~BDD.var('q%d' % target2) & BDD.let(
#             {'q%d' % control: BDD.true, 'q%d' % target1: BDD.false, 'q%d' % target2: BDD.true}, x)) | (
#                 BDD.var('q%d' % control) & ~BDD.var('q%d' % target1) & BDD.var('q%d' % target2) & BDD.let(
#             {'q%d' % control: BDD.true, 'q%d' % target1: BDD.true, 'q%d' % target2: BDD.false}, x))
#
#     for i in range(r):
#         Fa[i] = trans(Fa[i])
#         Fb[i] = trans(Fb[i])
#         Fc[i] = trans(Fc[i])
#         Fd[i] = trans(Fd[i])
#
#
# def printBDD():
#     print("Fa:")
#     for i in range(len(Fa)):
#         print(Fa[i].to_expr())
#     print("Fb:")
#     for i in range(len(Fb)):
#         print(Fb[i].to_expr())
#     print("Fc:")
#     for i in range(len(Fc)):
#         print(Fc[i].to_expr())
#     print("Fd:")
#     for i in range(len(Fd)):
#         print(Fd[i].to_expr())
#
#
# def get_total_bdd():
#     global Fa, Fb, Fc, Fd
#     r = len(Fd)
#     m = ceil(log2(r)) + 2  # The number of index Boolean variables
#     for i in range(m):
#         BDD.add_var('x%d' % i)
#     g = []
#     for i in range(r):
#         tmp = dict()
#         for j in range(2, m):
#             tmp['x%d' % j] = bool((i >> (j - 2)) & 1)
#         g.append(BDD.cube(tmp))
#     FA = BDD.false
#     FB = BDD.false
#     FC = BDD.false
#     FD = BDD.false
#     for i in range(r):
#         FA = BDD.apply('|', FA, g[i] & Fa[i])
#         FB = BDD.apply('|', FB, g[i] & Fb[i])
#         FC = BDD.apply('|', FC, g[i] & Fc[i])
#         FD = BDD.apply('|', FD, g[i] & Fd[i])
#     x0 = BDD.var('x0')
#     x1 = BDD.var('x1')
#     return (x0 & x1 & FA) | (x0 & ~x1 & FB) | (~x0 & x1 & FC) | (~x0 & ~x1 & FD)
#
#
# def measure():
#     pass