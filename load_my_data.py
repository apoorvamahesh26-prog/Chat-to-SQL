import sqlite3
import pandas as pd

# Your Play Tennis Dataset
data = {
    "Outlook":     ["Sunny", "Sunny", "Overcast", "Rain", "Rain", "Overcast", "Sunny"],
    "Temperature": ["Hot", "Hot", "Hot", "Cold", "Cold", "Hot", "Hot"],
    "Humidity":    ["High", "High", "High", "High", "High", "High", "High"],
    "Windy":       [False, True, False, False, True, True, False],
    "PlayTennis":  ["No", "No", "Yes", "Yes", "No", "Yes", "No"]
}

df = pd.DataFrame(data)

print("Your Dataset:")
print(df)
print(f"\nTotal rows: {len(df)}")

# Save into database
conn = sqlite3.connect("company.db")
df.to_sql("tennis", conn, if_exists="replace", index=False)
conn.commit()
conn.close()

print("\n✅ Tennis dataset loaded into database successfully!")