# The same data, made with the nopurple-charts style kit.
import sys
sys.path.insert(0, "skills/charts/scripts")
from chart_style import hbar, finish

fig, ax = hbar(["Google Ads", "Organic Search", "Referrals", "Social Media", "Email"],
               [86, 54, 31, 22, 11], highlight="Google Ads")
finish(fig, kicker="Leads by channel, October 2026",
       title="Google Ads brought 42% of all leads: 86 of 204",
       source="Sample data.", path="leads.png")
