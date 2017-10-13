# Used more general-purpose variable names
# base <= m, exp <= d, mod <= n
def expMod(base, exp, mod):
    if (exp == 0):
        return 1
    res = base
    for i in reversed(range(exp.bit_length()-1)):
        high = bool((exp >> i) & 1)
        res = (res*res*base) % mod if high else (res*res) % mod
    return res

