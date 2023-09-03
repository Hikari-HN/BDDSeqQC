from dd import autoref as _bdd

bdd = _bdd.BDD()
bdd.declare('x', 'y', 'z', 'w')

# conjunction (in TLA+ syntax)
u = bdd.add_expr(r'x /\ y')
v = bdd.add_expr(r'x /\ w')
s = bdd.let(dict(x=bdd.false), u)
print(s.to_expr())
print(u.to_expr())
print(v.to_expr())
# # substitute variables for variables (rename)
# rename = dict(x='z', y='w')
# v = bdd.let(rename, u)
# # substitute constants for variables (cofactor)
# values = dict(x=True, y=False)
# v = bdd.let(values, u)
# # substitute BDDs for variables (compose)
# d = dict(x=bdd.add_expr(r'z \/ w'))
# v = bdd.let(d, u)
# # as Python operators
# v = bdd.var('z') & bdd.var('w')
