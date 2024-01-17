import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np

def retrieve_droptable():
	res = requests.get('https://www.warframe.com/droptables')
	soup = BeautifulSoup(res.content, 'html.parser')
	relic_title = soup.find('h3', {'id': 'relicRewards'})  # Adjust based on your HTML structure
	relic_tables = relic_title.find_next_sibling('table')
	# Initialize lists to store data
	data = []

	# Iterate through the rows of the table
	for row in relic_tables.find_all('tr'):
		columns = row.find_all(['td', 'th'])
		name = columns[0].text.strip()
		if name == '':
			continue
		value = np.nan

		if len(columns) > 1:
			value = columns[1].text.strip()
		data.append({'Name': name, 'Value': value})

	# Create a DataFrame
	df = pd.DataFrame(data)

	# Display the DataFrame
	return df
	
def read_droptable():
	df = pd.read_csv("Warframe_Relic_Drop_Table.csv", header = None)
	df.dropna(inplace = True, how = 'all')
	df.reset_index(drop = True, inplace = True)
	df.columns = ["Name", "Value"]
	return df

def get_relic_list(df):
	return df.loc[df.Name.str.contains("Intact") & ~df.Name.str.contains("Requiem"), "Name"]

def create_item_df(df, intact_df):
	item_df = pd.DataFrame(columns = ["Item", "Relic", "Rarity"])

	for idx, relic in intact_df.items():
		for i in range(6):
			ix = idx + i + 1
			per_str = df.iloc[ix, 1]
			percentage = per_str[per_str.index("(") + 1:per_str.rindex("%")]
			item_df.loc[len(item_df)] = [df.iloc[ix, 0], relic, percentage]
	item_df.reset_index(drop = True, inplace = True)
	return item_df

def read_items_list(name):
	try:
		desired_items = pd.read_csv(name + ".csv", header = None)
		desired_items.columns = ["Name"]
		item_list = desired_items["Name"].tolist()
	except:
		item_list = []
	return item_list

def save_items_list(name, item_list):
	df = pd.DataFrame(item_list)
	df.to_csv(name + ".csv", header = False, index = False)


def calculate_scores(desired_items, item_df):
	scores = pd.DataFrame(columns = ["Score", "Items of Interest"])
	scores["Score"].astype(float)

	for item in desired_items:
		temp_df = item_df.loc[item_df["Item"] == item]
		multiplier = 1

		if sum(item.split("Prime", 1)[0] in s for s in desired_items) == 1:
			multiplier = 2.5
		
		for i,r in temp_df.iterrows():
			if r["Relic"] in scores.index:
				scores.loc[r["Relic"], "Score"] += 100. / float(r["Rarity"]) * multiplier
				scores.loc[r["Relic"], "Items of Interest"].append(item)
			else:
				scores.loc[r["Relic"], "Score"] = 100. / float(r["Rarity"]) * multiplier
				scores.loc[r["Relic"], "Items of Interest"] = [item]


	scores = scores.sort_values(by = "Score", ascending = False)
	return scores
