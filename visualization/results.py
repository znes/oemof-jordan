import os

import pandas as pd
import numpy as np
from cydets.algorithm import detect_cycles

import matplotlib.pyplot as plt
from matplotlib import colors
import seaborn as sns


color = {
    "conventional": "dimgrey",
    "cavern-acaes": "crimson",
    "redox-battery": "violet",
    "lignite-st": "sienna",
    "coal-st": "dimgrey",
    "uranium-st": "yellow",
    "gas-gt": "gray",
    "gas-cc": "lightgray",
    "gas-de": "darkgray",
    "gas-st": "slategray",
    "solar-pv": "lightyellow",
    "wind-onshore": "skyblue",
    "wind-offshore": "steelblue",
    "biomass-st": "yellowgreen",
    "hydro-ror": "aqua",
    "hydro-phs": "purple",
    "phs": "purple",
    "hydro-reservoir": "magenta",
    "hydro-rsv": "magenta",
    "hydrogen-storage": "pink",
    "lithium-battery": "plum",
    "waste-st": "yellowgreen",
    "oil-ocgt": "black",
    "other": "red",
    "other-res": "orange",
    "demand": "slategray",
    "import": "mediumpurple",
    "storage": "plum",
    "battery": "plum",
    "mixed-st": "chocolate",
    "decentral_heat-hp": "darkcyan",
    "excess": "darkcyan",
    "shaleoil-st": "black",
    "fossil": "lightgray",
    "phs-king-talal": "skyblue",
    "phs-mujib": "powderblue",
    "phs-wadi-arab": "steelblue",
}
color_dict = {name: colors.to_hex(color) for name, color in color.items()}

path = os.path.join(os.path.expanduser("~"), "oemof-results", "jordan-scenario-report")

renewables = [
    "hydro-ror",
    "wind-onshore",
    "solar-pv",
]
phs_storages = [
     "phs-king-talal",
     "phs-mujib",
     "phs-wadi-arab",
    #"phs"
]
storages = ["lithium-battery"]

conventionals = [
    "gas-cc",
    "gas-gt",
    "gas-st",
    "gas-de",
    "shaleoil-st"
]



aut_scenarios  = ["AUT"] +["AUT-" + str(s) for s in range(70, 100, 10)]
conv_scenarios =  ["CONT"]
re_scenarios =  ["GRE"] + ["GRE-" + str(s) for s in range(40, 100, 10)]
base_scenarios =  ["BASE"]+ ["BASE-" + str(s) for s in range(40, 100, 10)]
sq_scenarios =  ["SQ"] + ["SQ-" + str(s) for s in range(10, 80, 10)]
fu_scenarios =  ["FU"] + ["FU-" + str(s) for s in range(10, 80, 10)]


all_capacities = pd.DataFrame()
co2 = pd.DataFrame()
co2[["CONT", "BASE", "GRE", "AUT"]]
energy = pd.DataFrame()
for dir in os.listdir(path):
    capacities = pd.read_csv(
        os.path.join(path, dir, "output", "capacities.csv"), index_col=0
    )
    capacities.set_index("to", append=True, inplace=True)
    capacities = (
        capacities.groupby(["to", "carrier", "tech"]).sum().unstack("to")
    )
    co2_emissions = pd.read_csv(
        os.path.join(path, dir, "output", "costs.csv"), index_col=0
    )
    co2_emissions.columns = [dir]
    co2 = pd.concat([co2, co2_emissions], axis=1, sort=False)
    capacities.index = ["-".join(i) for i in capacities.index]
    # capacities.groupby(level=[0]).sum()

    temp = pd.read_csv(
        os.path.join(path, dir, "output", "JO-electricity.csv"), index_col=0
    )
    temp = temp.sum()
    temp.name = dir
    energy = pd.concat([energy, temp], axis=1, sort=False)

    capacities.columns = capacities.columns.droplevel(0)
    capacities.columns = [dir]
    all_capacities = pd.concat(
        [all_capacities, capacities], axis=1, sort=False
    )

    capacities.groupby(level=[0]).sum()

re_share = (1-energy.loc[conventionals].sum() / energy.loc["JO-load"]).sort_index()
storages = all_capacities.loc[
    [c for c in phs_storages + storages if c in all_capacities.index]
]

_df = all_capacities.copy()
# _df.loc["fossil"] = _df.loc[[c for c in conventionals if c in _df.index]].sum()
_df.loc["phs"] = _df.loc[["hydro-" + c  for c in phs_storages if "hydro-"+ c in _df.index]].sum()

# _df = _df.drop([c for c in conventionals if c in _df.index])
_df = _df.drop(["hydro-" + c for c in phs_storages if "hydro-"+ c in _df.index])
_df = _df.loc[_df.index.sort_values()]

# select = "base"
# x = [i for i in _df.columns]
# x.sort()
# x.sort(key=len, reverse=False)
x = conv_scenarios + base_scenarios + re_scenarios + aut_scenarios
#_df.index = [i.split("-")[1] for i in _df.index]
order = ["gas-cc", "gas-de", "gas-gt", "gas-st", "shaleoil-st", "solar-pv", "wind-onshore", "hydro-ror" ,"phs", "lithium-battery"]


ax = (_df.loc[order][x].T.divide(1000)).plot(
    kind="bar",
    stacked=True,
    color=[color_dict.get(c) for c in _df.loc[order].index],
    rot=0,
)
ax.legend()
#ax.set_ylim(-60, 70)
handles, labels = ax.get_legend_handles_labels()
lgd = {k: v for k, v in dict(zip(handles, labels)).items()}
ax.set_ylabel("Installed capacity in GW")
ax.grid(linestyle="--", lw=0.2)

ax2 = ax.twinx()
re_share[x].multiply(100).plot(
    linestyle="", marker="D", color="orange", label="RE-share", ax=ax2
)
ax2.set_ylim(0, 100)
ax2.set_ylabel("RE-share in %")
plt.xticks(rotation=0)
lines2, labels2 = ax2.get_legend_handles_labels()
lgd = ax.legend(list(lgd.keys()) + lines2, list(lgd.values()) + labels2,
    loc="lower left",
    bbox_to_anchor=(-0.1, -0.35),
    shadow=False,
    frameon=False,
    ncol=4,
)
plt.savefig(
    "visualization/figures/installed_capacities.pdf".format(""),
    bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)
_df.loc[order][x].T.astype(int).to_latex(
        caption="Installed capacities in MW.",
        label="tab:installed_capacities",
        buf="visualization/tables/installed_capacities.tex")



#
# stors = all_capacities.loc[
#     [c for c in ["hydro-phs-wadi-arab", "hydro-phs-king-talal", "hydro-phs-mujib"] +
#      storages if c in all_capacities.index]
# ]
# stors.index = [i.replace("hydro-", "") for i in stors.index]
# stors[x].T.round(0).to_latex(
#         caption="Installed storage capacities in the scenarios in MW.",
#         label="tab:storage_capacities",
#         buf="visualization/tables/installed_storage_capacities.tex")
# ax = (
#     stors[x]
#     .T.divide(1000)
#     .plot(
#         kind="bar",
#         stacked=True,
#         color=[color_dict.get(c) for c in stors.index],
#         rot=45,
#     )
# )
# lgd = ax.legend(
#     loc="lower left",
#     bbox_to_anchor=(0, -0.5),
#     shadow=False,
#     frameon=False,
#     ncol=3,
# )
# ax.set_ylabel("Installed storage capacity in GW")
# ax.grid(linestyle="--", lw=0.2)
# plt.xticks(rotation=45)
# plt.savefig(
#     "visualization/figures/storage_capacities.pdf",
#     bbox_extra_artists=(lgd,),
#     bbox_inches="tight",
# )
# storages

# investment cost analysis
all_capacities = pd.DataFrame()
storage_capacity = pd.DataFrame()
energy = pd.DataFrame()
objective = pd.DataFrame()
investment_cost = pd.DataFrame()
for dir in os.listdir(path):
    filling_levels = pd.read_csv(
        os.path.join(path, dir, "output", "filling_levels.csv"), index_col=0,
        parse_dates=True
    )
    capacities = pd.read_csv(
        os.path.join(path, dir, "output", "capacities.csv"), index_col=0
    )

    temp = pd.read_csv(
        os.path.join(path, dir, "output", "costs.csv"), index_col=0
    )
    temp = temp.loc["Objective value"]
    temp.name = dir
    temp.index = ["Objective"]
    objective = pd.concat([objective, temp], axis=1, sort=False)

    temp = pd.read_csv(
        os.path.join(path, dir, "output", "JO-electricity.csv"), index_col=0
    )

    temp["phs-cos"] = temp[phs_storages].clip(upper=0).sum(axis=1)
    temp["phs"] = temp[phs_storages].clip(lower=0).sum(axis=1)
    temp["battery-cos"] = temp["battery"].clip(upper=0)
    temp["battery"] = temp["battery"].clip(lower=0)
    temp["JO-load"] = temp["JO-load"] * -1
    temp["JO-electricity-excess"] = temp["JO-electricity-excess"] * -1
    temp = temp.sum()
    temp.name = dir
    energy = pd.concat([energy, temp], axis=1, sort=False)

    temp = pd.read_csv(
        os.path.join(path, dir, "output", "filling_levels.csv"), index_col=0,
    )
    temp = temp.max()
    temp.name = dir
    storage_capacity = pd.concat([storage_capacity, temp], axis=1, sort=False)

    capacities.set_index(
        ["to", "carrier", "tech", "type"], append=True, inplace=True
    )
    capacities.columns = [dir]
    all_capacities = pd.concat(
        [all_capacities, capacities], axis=1, sort=False
    )
    temp_p = pd.read_csv(
        os.path.join(path, dir, "output", "investment_power.csv"), index_col=0
    )
    temp_e = pd.read_csv(
        os.path.join(path, dir, "output", "investment_energy.csv"), index_col=0
    )
    temp = (temp_p.iloc[0] * temp_p.iloc[1]).to_frame()
    temp.loc[temp_e.columns] = (
        temp.loc[temp_e.columns] +
        (temp_e.iloc[0] * temp_e.iloc[1]).to_frame())
    temp.columns = [dir]
    investment_cost = pd.concat([temp, investment_cost], axis=1, sort=False)

fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)

filling_levels1 = pd.read_csv(
    os.path.join(path, base_scenarios[1], "output", "filling_levels.csv"), index_col=0,
    parse_dates=True
)
filling_levels2 = pd.read_csv(
    os.path.join(path, base_scenarios[5], "output", "filling_levels.csv"), index_col=0,
    parse_dates=True
)

fl = filling_levels1[phs_storages].sum(axis=1).to_frame() #.sum(axis=1).to_frame()
fl["Day"] = fl.index.dayofyear.values
fl["Hour"] = fl.index.hour.values
fl.set_index(["Hour", "Day"], inplace=True)
fl = fl.unstack("Day")
fl.columns = fl.columns.droplevel(0)
fl.sort_index(ascending=True, inplace=True)
fl = fl / fl.max() * 100
fl.sort_index(ascending=True, inplace=True)
fl2 = filling_levels2[phs_storages].sum(axis=1).to_frame() #.sum(axis=1).to_frame()

fl2["Day"] = fl2.index.dayofyear.values
fl2["Hour"] = fl2.index.hour.values
fl2.set_index(["Hour", "Day"], inplace=True)
fl2 = fl2.unstack("Day")
fl2.columns = fl2.columns.droplevel(0)
fl2.sort_index(ascending=True, inplace=True)
fl2 = fl2 / fl2.max() * 100
fl2.sort_index(ascending=True, inplace=True)


axs[0] = sns.heatmap(
    data=fl,
    xticklabels=False,
    yticklabels=4,
    cmap="RdYlBu",
    # vmax=vmax,
    # vmin=vmin,
    ax=axs[0],
    cbar_kws={"label": "SOC in % \n Base-40", "ticks": [0, 25, 50, 75, 100]},
)

axs[1] = sns.heatmap(
    data=fl2,
    xticklabels=False,
    yticklabels=4,
    cmap="RdYlBu",
    # vmax=vmax,
    # vmin=vmin,
    ax=axs[1],
    cbar_kws={"label": "SOC in % \n Base-80"},
)

for a in axs:
    #for a in aa:
    a.set_yticklabels(axs[1].get_yticklabels(), rotation=0, fontsize=8)
    a.set_xticklabels(axs[1].get_xticklabels(), rotation=0, fontsize=8)
    a.set_ylim(0, 24)
    a.set_xlim(0, 365)
    a.set_ylabel("Hour of Day", fontsize=8)

axs[1].set_xlabel("Day of Year")
axs[0].set_xlabel("")
axs[0].set_xticklabels("")

plt.savefig(
    "visualization/figures/heatmap_soc.pdf",
    bbox_inches="tight",
)

investment_cost.loc["phs"] = investment_cost.loc[[c for c in phs_storages if c in investment_cost.index]].sum()
investment_cost = investment_cost.drop([c for c in phs_storages if c in investment_cost.index])
x = sq_scenarios + fu_scenarios
invest_plot = investment_cost[x].divide(1e9).T


ax = invest_plot.plot(
        kind="bar",
        stacked=True,
        color=[color_dict.get(c) for c in investment_cost.index],
    rot=90,
)
lgd = ax.legend(
    loc="upper left",
    bbox_to_anchor=(-0.05, -0.25),
    shadow=False,
    frameon=False,
    ncol=4,
)
ax.set_ylabel("Total annualised investment cost in Billio US $")
ax.grid(linestyle="--", lw=0.2)

plt.savefig(
    "visualization/figures/investment_cost-report.pdf",
    bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)
invest_plot.multiply(1e3).round(2).fillna("-").to_latex(
        caption="Investment cost in Mio. US $. ",
        label="tab:investment_cost",
        buf="visualization/tables/investment_cost-report.tex")

from oemof.tools.economics import annuity
aut_scenarios  = ["AUT"] +["AUT-" + str(s) for s in range(40, 100, 10)]
conv_scenarios =  ["CONT"] #+ ["CONT-" + str(s) for s in range(10, 20, 10)]
re_scenarios =  ["GRE"] + ["GRE-" + str(s) for s in range(40, 100, 10)]
base_scenarios =  ["BASE"]+ ["BASE-" + str(s) for s in range(40, 100, 10)]
base_invest = (annuity(800, 20, 0.05) * 1000) * 1.035 * 4293
base_invest = 0
lcoe = pd.DataFrame([
    objective[conv_scenarios].add(base_invest).divide(28e6).values[0],
    objective[base_scenarios].add(base_invest).divide(28e6).values[0],
    objective[re_scenarios].add(base_invest).divide(28e6).values[0],
    objective[aut_scenarios].add(base_invest).divide(28e6).values[0]],
    index=["CONT", "BASE", "GRE", "AUT"],
    columns=["REF", "40%", "50%", "60%", "70%", "80%", "90%"]).round(2)

ax = lcoe.T.plot(kind="line", marker="o", rot=0,
    color=sns.xkcd_palette(["windows blue", "amber", "purple", "magenta", "black"])) #cmap="YlGnBu"
ax.set_xlabel("Scenario")
ax.set_ylabel("LCOE in $/MWh")
ax.set_ylim(0, 120)
lgd = ax.legend(
)
ax.grid(linestyle="--", lw=0.2)
plt.savefig(
    "visualization/figures/lcoe.pdf",
    bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)
lcoe = lcoe.fillna("-")
lcoe.to_latex(
        caption="LCOE in US $/MWh.",
        label="tab:lcoe",
        buf="visualization/tables/lcoe.tex")
# energy plot ----------------------------------------------------------------
names = {
    "gas-cc": ['Amman-East', 'CC-New', 'Samra1', 'Samra2', 'Samra3','Samra4', "Qatrana", "Zarqa-ACWA"],
    "gas-de": ['IPP3', 'IPP4'],
    "gas-st": ['Aqaba2'],
    "gas-gt": ['Amman-South', 'GT-New',  'Rehab', 'Risha'],
    "shaleoil-st": ['Oil-Shale', 'Oil-New']
}
e = energy.drop(["JO-electricity-shortage"])
#order = ["gas-cc", "gas-gt", "gas-st", "gas-de", "shaleoil-st", "phs", "battery"]
x = conv_scenarios  + base_scenarios + re_scenarios + aut_scenarios
e = e[x].dropna()
e.rename(index={"JO-load": "demand", "JO-electricity-excess": "excess"}, inplace=True)
e = e.T
# for k,v in names.items():
#     e[k] = e[k].sum(axis=1)
#     e = e.drop(k, axis=1)

ax = e.divide(1e6).plot(
    kind="bar",
    stacked=True,
    color=[color_dict.get(i.replace("-cos", "")) for i in e.columns],
    label=[i if not "-cos" in i else None for i in e.columns],
)
ax.legend()
#ax.set_ylim(-60, 70)
handles, labels = ax.get_legend_handles_labels()
lgd = {k: v for k, v in dict(zip(handles, labels)).items() if "-cos" not in v}
ax.set_ylabel("Energy in TWh")
ax.grid(linestyle="--", lw=0.5)
plt.xticks(rotation=00)

ax2 = ax.twinx()

co2.loc["CO2 (Mio. t)"][x].plot(
linestyle="", marker="o", markersize=4, color="darkred", label="CO2", ax=ax2
)
ax2.set_ylim(0, 10)
ax2.set_ylabel("CO2 emissions in Mio. ton")

lines2, labels2 = ax2.get_legend_handles_labels()
lgd = ax.legend(list(lgd.keys()) + lines2, list(lgd.values()) + labels2,
    loc="lower left",
    bbox_to_anchor=(-0.05, -0.4),
    ncol=4,
    borderaxespad=0,
    frameon=False)

# plt.plot(figsize=(10, 5))
plt.savefig(
    "visualization/figures/energy.pdf",
    bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)
e.divide(1e6).round(2).to_latex(
    caption="Energy supply and demand in TWh.",
    label="tab:energy",
    buf="visualization/tables/energy.tex")

# -operation flh ------------------------------------------------

e = energy.drop(phs_storages + ["JO-electricity-shortage"])
#order = ["gas-cc", "gas-gt", "gas-st", "gas-de", "shaleoil-st", "phs", "battery"]
e.rename(index={"JO-load": "demand", "JO-electricity-excess": "excess"}, inplace=True)
e = e[fu_scenarios]
c = all_capacities[fu_scenarios].xs('capacity', level=4)
c.index = c.index.droplevel([1,2,3])

e, c = e.dropna(), c.dropna()
flh = (e / c).drop(
    renewables + phs_storages + ["demand", "excess", "phs", "phs-cos", "battery", "battery-cos"])
flh.divide(1e6).round(0).to_latex(
    caption="Fulload hours of conventional units in SQ.",
    label="tab:flh_sq",
    buf="visualization/tables/flh-sq.tex")


ax = flh.plot(
        kind="bar", cmap="Blues", rot=60)
ax.grid(linestyle="--", lw=0.2)
ax.set_ylabel("Fulload hours")
lgd = ax.legend(
    loc="upper left",
    bbox_to_anchor=(0, -0.3),
    ncol=4,
    borderaxespad=0,
    frameon=False)
plt.savefig(
    "visualization/figures/conventional-flh-sq.pdf",
    bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)
# Operation --------------------------------------------------------------------

energy = {}
for dir in os.listdir(path):

    temp = pd.read_csv(
        os.path.join(path, dir, "output", "JO-electricity.csv"), index_col=0
    )
    energy[dir] = temp

name = base_scenarios[0]
select = energy[name]

names = {
    "gas-cc": ['Amman-East', 'CC-New', 'Samra1', 'Samra2', 'Samra3','Samra4', "Qatrana", "Zarqa-ACWA"],
    "gas-de": ['IPP3', 'IPP4'],
    "gas-st": ['Aqaba2'],
    "gas-gt": ['Amman-South', 'GT-New',  'Rehab', 'Risha'],
    "shaleoil-st": ['Oil-Shale', 'Oil-New']
}

range = [168*30, 168*30+168]
select.index = select.reset_index().index
ax = select["JO-load"].plot(
    linestyle="-",  color="darkred", label="Load", rot=45
)
select = select.drop(["JO-load", "JO-electricity-shortage"], axis=1)
#for k,v in names.items():
#    select[k] = select[v].sum(axis=1)
#    select = select.drop(v, axis=1)

#select["phs"] = select[phs_storages].sum(axis=1)
#select = select.drop(phs_storages, axis=1)

neg = select[["phs", "battery"]].clip(upper=0)
order = ["hydro-ror", "solar-pv", "wind-onshore", "gas-cc", "gas-gt", "gas-st", "gas-de", "shaleoil-st", "phs", "battery"]

select[[c for c in order if c in select.columns]].clip(lower=0).iloc[range[0]: range[1]].plot.area(ax = ax,
    rot=45, color=[color_dict.get(c) for c in select[order].columns], lw=0)
ax.set_prop_cycle(None)
neg.plot.area(
    ax=ax, lw=0, legend=None, color=[color_dict.get(c) for c in neg.columns], stacked=True, rot=0)

ax.set_xlim(range)
ax.set_ylim(-500, 7000)
ax.set_ylabel("Energy in MW")
ax.grid(linestyle="--", lw=0.2)

#ax2.set_ylim(0, 10)
lgd = ax.legend(
    loc="upper left",
    bbox_to_anchor=(-0.05, -0.15),
    ncol=4,
    borderaxespad=0,
    frameon=False)
plt.savefig(
    "visualization/figures/dispacht-{}.pdf".format(name),
    bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)



# Cylces ---------------------------------------------------------
cycles = {}
cycles_h = {}
cycles_l = {}

for dir in os.listdir(path):
    df = pd.read_csv(
        os.path.join(path, dir, "output", "filling_levels.csv"),
        index_col=[0],
        parse_dates=True,
    )
    df["phs"] = df[[c for c in df.columns if "phs" in c]].sum(axis=1)
    if sum(df["battery"] != 0):
        cycles_l[dir] = detect_cycles(df["battery"])
    if sum(df["phs"] != 0):
        cycles_h[dir] = detect_cycles(df["phs"])

for v in base_scenarios:
    if v in cycles_l:
        ax = sns.jointplot(
            x=cycles_l[v]["duration"] / np.timedelta64(1, "h"),
            y=cycles_l[v]["doc"],
            marginal_kws=dict(bins=100, rug=True),
            kind="scatter",
            color="m",
            edgecolor="purple",
        )
        ax.set_axis_labels(
            "Duration of cycle in h", "Normalised depth of cycle"
        )
        plt.savefig("visualization/figures/cycles-battery-{}.pdf".format(v))
    if v in cycles_h:
        ax = sns.jointplot(
            x=cycles_h[v]["duration"] / np.timedelta64(1, "h"),
            y=cycles_h[v]["doc"],
            marginal_kws=dict(bins=100, rug=True),
            kind="scatter",
            color="skyblue",
            edgecolor="darkblue",
        )
        ax.set_axis_labels(
            "Duration of cycle in h", "Normalised depth of cycle"
        )
        plt.savefig("visualization/figures/cycles-phs-{}.pdf".format(v))
