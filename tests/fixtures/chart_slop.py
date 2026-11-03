# A typical AI-made chart: every slop pattern chart_check.py looks for.
import matplotlib.pyplot as plt

channels = ["Google Ads", "Organic Search", "Referrals", "Social Media", "Email"]
leads = [86, 54, 31, 22, 11]
colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
ax1.pie(leads, labels=channels, colors=colors, explode=[0.1, 0, 0, 0, 0], shadow=True, autopct="%1.1f%%")
ax1.set_title("📊 Lead Source Distribution Overview")

ax2.bar(channels, leads, color=colors)
ax2.set_ylim(10, 90)
ax2.set_title("Leads by Channel")
ax2.grid(True, alpha=0.3)
plt.xticks(rotation=45)
ax3 = ax2.twinx()
ax3.plot(channels, [4.1, 3.2, 2.8, 2.1, 1.5])
ax2.legend(["Leads"])
plt.savefig("leads.png")
