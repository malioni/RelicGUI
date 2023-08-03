import pandas as pd

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
