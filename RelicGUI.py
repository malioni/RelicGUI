import PySimpleGUI as sg
import relics as rel

f18 = ("Helvetica", 18)
f16 = ("Helvetica", 16)
f14 = ("Helvetica", 14)
f12 = ("Helvetica", 12)

# Used GUI element definitions
def text_el(*args, **kwargs):
	return sg.Text(*args, **kwargs)

def combo_el(*args, **kwargs):
	return sg.Combo(*args, **kwargs, default_value = args[0][0], enable_events = True)

def search_el(name, *args, **kwargs):
	return [sg.Combo(*args, key = name + "-COMBO", **kwargs, font = f14, size = max(len(x) for x in args[0]))]

def update_add_rmv_btns(name, *args, **kwargs):
	return [sg.Button("Update", key = name + "-UPDATE", **kwargs, font = f14),
		sg.Button("+", key = name + "-ADD", font = f14, size = 3),
		sg.Button("-", key = name + "-REMOVE", font = f14, size = 3)]

def listbox_el(name, *args, **kwargs):
	return [sg.Listbox(*args, **kwargs, enable_events=True, key = name + "-LISTBOX", font = f14)]

def clear_save_btn_el(name):
	return [sg.Button("Clear", key = name + "-CLEAR", font = f12),
		sg.Button("Save", key = name + "-SAVE", font = f12),
		sg.Button("Load", key = name + "-LOAD", font = f12)]

def set_up_gui():
	# GUI Settings
	sg.theme("DarkTeal6")

def define_layout(desired_items, all_items, owned_relics, absent_relics, all_relics, data, row_colors):
	# Layout definition
	relic_item_col = [
		[text_el("Choose Relic Tier: ", font = f18), combo_el(["Lith", "Meso", "Neo", "Axi"], key = "RELIC-TIER", font = f16)],
		[text_el("Desired Items:", font = f18)],
		search_el("ITEMS", all_items),
		update_add_rmv_btns("ITEMS"),
		listbox_el("ITEMS", desired_items, size = (max(len(x) for x in all_items), 20)),
		clear_save_btn_el("ITEMS")
	]

	owned_col = [
		[text_el("Owned Relics", font = f18)],
		search_el("OWNED", all_relics),
		update_add_rmv_btns("OWNED"),
		listbox_el("OWNED", owned_relics, size = (max(len(x) for x in all_items), 7)),
		clear_save_btn_el("OWNED"),
		[text_el("Absent Relics", font = f18)],
		search_el("ABSENT", all_relics),
		update_add_rmv_btns("ABSENT"),
		listbox_el("ABSENT",absent_relics, size = (max(len(x) for x in all_items), 7)),
		clear_save_btn_el("ABSENT")
	]

	headings = ['Relic', 'Score', 'Items']

	results_col = [[sg.Table(data, headings=headings, justification='left', key='-TABLE-',
		row_colors = row_colors, font = f14, num_rows = 20, auto_size_columns = False, col_widths = [10,5,60])]]

	l = [
		[
			sg.Column(relic_item_col),
			sg.VSeperator(),
        	sg.Column(owned_col)
        ],
        [
        	sg.Column(results_col)
		]
	]
	return l

def update_btn_evt(box_val, full_list):
	temp_list = full_list
	if box_val != "":
		temp_list = [item for item in full_list if box_val.lower() in item.lower()]
	return temp_list

def add_btn_evt(box_val, full_list, partial_list):
	if box_val in full_list:
		partial_list.append(box_val)

def remove_btn_evt(box_val, partial_list):
	if box_val in partial_list:
		partial_list.remove(box_val)

def handle_list_evts(event, values, window, names, full_lists, partial_lists):
	for i in range(len(names)):
		if event == (names[i] + "-UPDATE"):
			window[names[i] + "-COMBO"].update(value = values[names[i] + "-COMBO"], values = update_btn_evt(values[names[i] + "-COMBO"],
				full_lists[i]))

		if event == (names[i] + "-ADD"):
			add_btn_evt(values[names[i] + "-COMBO"], full_lists[i], partial_lists[i])
			window[names[i] + "-LISTBOX"].update(sorted(partial_lists[i]))

		if event == (names[i] + "-REMOVE"):
			remove_btn_evt(values[names[i] + "-COMBO"], partial_lists[i])
			window[names[i] + "-LISTBOX"].update(sorted(partial_lists[i]))

		if event == (names[i] + "-LISTBOX"):
			window[names[i] + "-COMBO"].update(value = values[names[i]+ "-LISTBOX"][0])

		if event == (names [i] + "-CLEAR"):
			partial_lists[i][:] = []
			window[names[i] + "-LISTBOX"].update(partial_lists[i])

		if event == (names[i] + "-SAVE"):
			rel.save_items_list(names[i], sorted(partial_lists[i]))

		if event == (names[i] + "-LOAD"):
			partial_lists[i][:] = rel.read_items_list(names[i])
			window[names[i] + "-LISTBOX"].update(sorted(partial_lists[i]))

def colored_rows(owned_relics, absent_relics, data_df):
	colors = []

	mod_df = data_df.reset_index()

	for idx, row in mod_df.iterrows():
		if row["index"] in owned_relics:
			colors.append((idx, 'green'))
		elif row["index"] in absent_relics:
			colors.append((idx, 'red'))
		else:
			colors.append((idx, '#3B7EDD'))

	return colors


if __name__ == "__main__":
	rel.retrieve_droptable()
	# Retrieve droptable from Warframe website
	droptable = rel.retrieve_droptable()

	relic_df = rel.get_relic_list(droptable)
	relic_df = relic_df.apply(lambda s: s.split(" (Intact)",1)[0])

	# Create a dataframe that contains the items with their respective info
	item_df = rel.create_item_df(droptable, relic_df)

	desired_items = sorted(rel.read_items_list("ITEMS"))

	all_items = sorted(item_df["Item"].unique())

	all_relics = sorted(relic_df.tolist())

	owned_relics = sorted(rel.read_items_list("OWNED"))

	absent_relics = sorted(rel.read_items_list("ABSENT"))

	data_df = rel.calculate_scores(desired_items, item_df[item_df["Relic"].str.contains("Lith")])
	data_df['Score'] = data_df['Score'].astype(int)
	data_df['Score'] = data_df['Score'].astype(str)
	row_colors = colored_rows(owned_relics, absent_relics, data_df)
	data_list = data_df.reset_index().values.tolist()

	l = define_layout(desired_items, all_items, owned_relics, absent_relics, all_relics, data_list, row_colors)
	window = sg.Window(title = "Void Relic GUI", layout = l, resizable = True)

	while True:
		event, values = window.read()
		if event == "Exit" or event == sg.WIN_CLOSED:
			break

		handle_list_evts(event, values, window, ["ITEMS", "OWNED", "ABSENT"], [all_items, all_relics, all_relics],
			[desired_items, owned_relics, absent_relics])

		data_df = rel.calculate_scores(desired_items, item_df[item_df["Relic"].str.contains(values["RELIC-TIER"])])
		data_df['Score'] = data_df['Score'].astype(int)
		data_df['Score'] = data_df['Score'].astype(str)
		row_colors = colored_rows(owned_relics, absent_relics, data_df)
		data_list = data_df.reset_index().values.tolist()
		window["-TABLE-"].update(values = data_list, row_colors = row_colors)

	window.close()

