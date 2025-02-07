import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from click.formatting import iter_rows
from setuptools.config.expand import canonic_data_files
from sklearn.conftest import pyplot

tenor = [2, 5, 10, 30]
yields = [6, 7, 7.5, 8]

df = pd.DataFrame([tenor, yields]).transpose()
df = df.set_index(0)
# print(df)


def intrpolte (data, lower, upper, mid: float):
    mid_yields = []

    y1 = df.loc[lower]
    y2 = df.loc[upper]
    x1 = lower
    x2 = upper
    y = y1 + (y2-y1)/(x2-x1)*(mid-x1)

    # df.loc[mid]['tenor'] = mid
    df.loc[mid] = y
    mid_yields.append(y)
    return df.sort_values(1)

def yieldcurve():
    for i in range(30):
        if 2<i<5:
            intrpolte(df,2,5,i)
        if 5<i<10:
            intrpolte(df,5,10,i)
        if 10<i<30:
            intrpolte(df,10,30,i)
    return df.sort_values(1)

def fwds(x, y):
    ytm1 = yieldcurve().loc[x][1]
    ytm2 = yieldcurve().loc[y][1]
    t1 = x
    t2 = y

    fwd = ((1+ ytm2/100) ** t2)/((1 + ytm1/100) ** t1)
    return fwd

def fwdcurve(x):
    df1 = pd.DataFrame(yieldcurve())

    crve = []
    xYYz = []
    for row in df1.iterrows():
        if row[0]+x<=30:
            crve.append(fwds(row[0],row[0]+x))
            xYYz.append(f"{row[0]}YX{row[0]+x}Y")
    df2 = pd.DataFrame(np.transpose(crve), columns= [f"{x}YR forward curve %"], index = xYYz)

    return df2

def discount_curve():
    curve = pd.DataFrame(yieldcurve())
    curve["discount factor"] = 1 / (1 + (curve[1] / 100)) ** curve.index
    return curve

def bond_npv(n, cf, fv):
    a = []
    for i in range(n):
        a.append(i+1)

    for row in discount_curve().iterrows():
        if row[0] in a:
            # print(discount_curve()[discount_curve().index<=n])
            x = cf*discount_curve()[discount_curve().index<=n]["discount factor"]
            y = fv*discount_curve()[discount_curve().index == n]["discount factor"]
            z = x + y
        return f"The PV of the bond is {round(np.sum(x) + (y.values[0]),2)}$ per {fv} face value"

# print(bond_npv(2,6, 100))
# print(fwdcurve(1))
# print(yieldcurve())

def curveshifts(curve_drift, key_rate ,rate_delta):
    a = pd.DataFrame(discount_curve())
    abc = []
    for row in discount_curve().iterrows():
        if row[0] == key_rate and rate_delta != 0:
            abc.append((row[1] + rate_delta).tolist()[0])
        else:
            abc.append((row[1]+curve_drift).tolist()[0])
    a[1] = np.transpose(abc)
    a["discount factor"] = 1 / (1 + (a[1] / 100)) ** a.index
    a.rename(columns={1: 'yields'}, inplace=True)
    return a

# print(curveshifts(1,30, 7))

def bond_npv1(n, cf, fv, curve_drift, key_rate, rate_delta):
    curve = curveshifts(curve_drift, key_rate, rate_delta)
    # print(curve)
    a = []
    for i in range(n):
        a.append(i+1)

    for row in curve.iterrows():
        if row[0] in a:
            # print(curve[curve.index<=n])
            x = cf*curve[curve.index<=n]["discount factor"]
            y = fv*curve[curve.index == n]["discount factor"]
            z = x+y
        return f"The PV of the bond is {round(np.sum(x) + (y.values[0]),2)}$ per {fv} face value after the curve shift"


def curveshiftanalysis(n, cf, fv, curve_drift, key_rate, rate_delta):
    print((bond_npv(n, cf, fv)))
    print((bond_npv1(n, cf, fv, curve_drift, key_rate, rate_delta)))

curveshiftanalysis(10, 1, 100, 1, 6, 5)

plt.plot(fwdcurve(3))
plt.show()




