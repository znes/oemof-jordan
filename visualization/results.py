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
    "hydro-phs-king-talal": "plum",
    "hydro-phs-mujib": "magenta",
    "hydro-phs-tannur": "purple",
}
color_dict = {name: colors.to_hex(color) for name, color in color.items()}

path = os.path.join(os.path.expanduser("~"), "oemof-results", "jordan")

renewables = [
    "hydro-ror",
    "wind-onshore",
    "solar-pv",
]
phs_storages = [
    "phs-king-talal",
    "phs-mujib",
    "phs-wadi-arab",
]
storages = ["lithium-battery"]

conventionals = [
    "gas-cc",
    "gas-gt",
    "shaleoil-st"
]




storage_scenarios  = ["STOR"] +["STOR-" + str(s) for s in range(40, 100, 10)]
conv_scenarios =  ["CONT"] #+ ["CONT-" + str(s) for s in range(10, 20, 10)]
re_scenarios =  ["RE"] + ["RE-" + str(s) for s in range(40, 100, 10)]
base_scenarios =  ["BASE"]+ ["BASE-" + str(s) for s in range(40, 100, 10)]
ee_scenarios =  ["EE"] + ["EE-" + str(s) for s in range(40, 100, 10)]

# base_scenarios.reverse()
# low_scenarios.reverse()
# high_scenarios.reverse()
# pv_scenarios.reverse()
# storage_scenarios.reverse()

all_capacities = pd.DataFrame()
co2 = pd.DataFrame()

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

co2.loc["Shadow Price in $/t"] = co2.loc["Shadow Price in $/t"] * -1

re_share = 1 - (
     energy.T[conventionals].sum(axis=1) / energy.T["JO-load"])
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
x = conv_scenarios + base_scenarios
#_df.index = [i.split("-")[1] for i in _df.index]
ax = (_df[x].T.divide(1000)).plot(
    kind="bar",
    stacked=True,
    color=[color_dict.get(c) for c in _df.index],
    rot=90,
)
lgd = ax.legend(
    loc="lower left",
    bbox_to_anchor=(0, -0.6),
    shadow=False,
    frameon=False,
    ncol=3,
)
ax.set_ylabel("Installed capacity in GW")
ax.grid(linestyle="--", lw=0.2)

# ax2 = ax.twinx()
# co2.loc["CO2 (Mio. t)", x].plot(
#     linestyle="", marker="D", color="orange", label="CO2", ax=ax2
# )
# #ax2.set_ylim(0, 9)
# ax2.set_ylabel("CO2 in Mio. t")
plt.xticks(rotation=45)

plt.savefig(
    "visualization/figures/installed_capacities.pdf".format(""),
    bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)

ax = co2[x].T.plot(
    kind="scatter", x="CO2 (Mio. t)", y="Shadow Price in $/t")
ax.grid(linestyle="--", lw=0.2)
ax.set_ylabel("Model CO2 Price in $/")
ax.set_xlabel("CO2 Emission in Mio. t")


# ax = (
#     storages[x]
#     .T.divide(1000)
#     .plot(
#         kind="bar",
#         stacked=True,
#         color=[color_dict.get(c) for c in storages.index],
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
#     "visualization/figures/storage_capacities-{}.pdf".format(select),
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
    os.path.join(path, base_scenarios[0], "output", "filling_levels.csv"), index_col=0,
    parse_dates=True
)
filling_levels2 = pd.read_csv(
    os.path.join(path, base_scenarios[3], "output", "filling_levels.csv"), index_col=0,
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
    cbar_kws={"label": "SOC in % \n Opt", "ticks": [0, 25, 50, 75, 100]},
)

axs[1] = sns.heatmap(
    data=fl2,
    xticklabels=False,
    yticklabels=4,
    cmap="RdYlBu",
    # vmax=vmax,
    # vmin=vmin,
    ax=axs[1],
    cbar_kws={"label": "SOC in % \n 60% RE"},
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


ax = investment_cost[
    conv_scenarios + base_scenarios].divide(1e9).T.plot(
        kind="bar",
        stacked=True,
        color=[color_dict.get(c) for c in investment_cost.index],
    rot=90,
)
lgd = ax.legend(
    loc="upper left",
    #bbox_to_anchor=(0, -0.6),
    shadow=False,
    frameon=False,
    ncol=2,
)
ax.set_ylabel("Total investment cost in B$")
ax.grid(linestyle="--", lw=0.2)
plt.savefig(
    "visualization/figures/investment_cost.pdf",
    bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)


lcoe = pd.DataFrame([
    objective[base_scenarios].divide(28e6).values[0],
    objective[ee_scenarios].divide(25e6).values[0],
    objective[storage_scenarios].divide(28e6).values[0],
    objective[re_scenarios].divide(28e6).values[0],
    objective[conv_scenarios].divide(28e6).values[0]],
    index=["Base", "EE", "STOR", "RE", "CONT"],
    columns=["C-Opt", "40%", "50%","60%", "70%", "80%", "90%"]).round(2)
ax = lcoe.T.plot(kind="line", marker="o", rot=0, color=sns.xkcd_palette(["windows blue", "amber", "purple", "magenta", "black"])) #cmap="YlGnBu"
ax.set_xlabel("Scenario")
ax.set_ylabel("LCOE in $/MWh")
lgd = ax.legend(
)
ax.grid(linestyle="--", lw=0.2)
plt.savefig(
    "visualization/figures/lcoe.pdf",
    bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)

lcoe.to_latex(
        caption="LCOE at different demand levels and CO2 reduction.",
        label="tab:lcoe",
        buf="visualization/tables/lcoe.tex")


energy = energy.drop(phs_storages + ["JO-electricity-shortage"])
energy.rename(index={"JO-load": "demand", "JO-electricity-excess": "excess"}, inplace=True)
ax = energy[conv_scenarios + base_scenarios].divide(1e6).T.plot(
kind="bar",
stacked=True,
color=[color_dict.get(i.replace("-cos", "")) for i in energy.index],
label=[i if not "-cos" in i else None for i in energy.index],
)
ax.legend()
#ax.set_ylim(-60, 70)
handles, labels = ax.get_legend_handles_labels()
lgd = {k: v for k, v in dict(zip(handles, labels)).items() if "-cos" not in v}
ax.set_ylabel("Energy in TWh")
ax.grid(linestyle="--", lw=0.5)
plt.xticks(rotation=90)

ax2 = ax.twinx()
co2.loc["CO2 (Mio. t)"][x].plot(
linestyle="", marker="o", markersize=4, color="darkred", label="RE share", ax=ax2
)
ax2.set_ylim(0, 10)
ax2.set_ylabel("CO2 emissions in Mio. ton")

lines2, labels2 = ax2.get_legend_handles_labels()
lgd = ax.legend(list(lgd.keys()) + lines2, list(lgd.values()) + labels2,
    loc="upper left",
    bbox_to_anchor=(-0.05, -0.3),
    ncol=4,
    borderaxespad=0,
    frameon=False)

# plt.plot(figsize=(10, 5))
plt.savefig(
    "visualization/figures/energy.pdf",
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

name = conv_scenarios[0]
select = energy[name]
range = [168*10, 168*10+168]
select.index = select.reset_index().index
ax = select["JO-load"].plot(
    linestyle="-",  color="darkred", label="Load", rot=45
)
select = select.drop(["JO-load", "JO-electricity-shortage"], axis=1)
select["phs"] = select[phs_storages].sum(axis=1)
select = select.drop(phs_storages, axis=1)

neg = select[["phs", "battery"]].clip(upper=0)
order = ["hydro-ror", "solar-pv", "wind-onshore", "gas-cc", "shaleoil-st", "gas-gt", "phs", "battery"]

select[order].clip(lower=0).iloc[range[0]: range[1]].plot.area(ax = ax,
    rot=45, color=[color_dict.get(c) for c in select[order].columns], lw=0)
ax.set_prop_cycle(None)
neg.plot.area(
    ax=ax, lw=0, legend=None, color=[color_dict.get(c) for c in neg.columns], stacked=True, rot=0)

ax.set_xlim(range)
ax.set_ylim(-1000, 8500)
ax.set_ylabel("Energy in MW")
ax.grid(linestyle="--", lw=0.2)

#ax2.set_ylim(0, 10)
ax2.set_ylabel("Electricity load in MW")
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
