
import os
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta, timezone, date

USERNAME = os.getenv("GITHUB_USER", "AdarshAnand-cg")
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise ValueError("GITHUB_TOKEN is missing")

end_date = datetime.now(timezone.utc)
start_date = end_date - timedelta(days=90)

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks {
          firstDay
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

response = requests.post(
    "https://api.github.com/graphql",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={
        "query": query,
        "variables": {
            "login": USERNAME,
            "from": start_date.isoformat(),
            "to": end_date.isoformat()
        }
    },
    timeout=30
)

response.raise_for_status()
result = response.json()

if "errors" in result:
    raise RuntimeError(result["errors"])

weeks = result["data"]["user"]["contributionsCollection"][
    "contributionCalendar"
]["weeks"]

weekly_dates = []
weekly_counts = []

for week in weeks:
    week_total = 0

    for day in week["contributionDays"]:
        current_day = date.fromisoformat(day["date"])

        if start_date.date() <= current_day <= end_date.date():
            week_total += day["contributionCount"]

    weekly_dates.append(
        date.fromisoformat(week["firstDay"])
    )
    weekly_counts.append(week_total)

# Create chart
plt.rcParams["font.family"] = "DejaVu Sans"

fig, ax = plt.subplots(figsize=(13, 5))

background = "#0b1220"
fig.patch.set_facecolor(background)
ax.set_facecolor(background)

# Glowing line effect
ax.plot(
    weekly_dates,
    weekly_counts,
    color="#00e5ff",
    linewidth=8,
    alpha=0.10
)

ax.plot(
    weekly_dates,
    weekly_counts,
    color="#00e5ff",
    linewidth=2.8,
    marker="o",
    markersize=6,
    markerfacecolor="#ffffff",
    markeredgecolor="#00e5ff",
    markeredgewidth=2
)

# Area below line
ax.fill_between(
    weekly_dates,
    weekly_counts,
    color="#00e5ff",
    alpha=0.12
)

# Labels
ax.set_title(
    "WEEKLY GITHUB CONTRIBUTIONS · LAST 3 MONTHS",
    color="#ffffff",
    fontsize=15,
    fontweight="bold",
    pad=22
)

ax.set_xlabel("WEEK", color="#8b9bb4", labelpad=12)
ax.set_ylabel("CONTRIBUTIONS", color="#8b9bb4", labelpad=12)

# Week labels
week_labels = [
    f"{d.strftime('%b')} W{(d.day - 1) // 7 + 1}"
    for d in weekly_dates
]

ax.set_xticks(weekly_dates)
ax.set_xticklabels(
    week_labels,
    rotation=45,
    ha="right",
    fontsize=8,
    color="#a9b8d0"
)

ax.tick_params(axis="y", colors="#a9b8d0")
ax.grid(
    True,
    linestyle="--",
    linewidth=0.6,
    alpha=0.18,
    color="#8b9bb4"
)

for spine in ax.spines.values():
    spine.set_color("#263449")

ax.set_ylim(bottom=0)

plt.tight_layout()

os.makedirs("dist", exist_ok=True)

plt.savefig(
    "dist/weekly-contributions.svg",
    format="svg",
    facecolor=background,
    bbox_inches="tight"
)

print("Weekly contribution chart generated successfully!")
