import sqlite3
import contextlib
import os

# plug your profile id in here
profile_id = 'f9psb5ao'
# plug in the name of the wishlist bookmark folder here
wishlist_folder_name = 'Ønskelista'

appdata = os.getenv('APPDATA')
profile_dir = appdata + '\\Mozilla\\Firefox\\Profiles\\' + profile_id + '.default'
ff_db_dir = profile_dir + '\\places.sqlite'

print('Creating wish list')
wish_list = {} # pun not intended

#############################################################################

# grab all wishes and construct a datastructure suitable for insertion into a new database
with contextlib.closing(sqlite3.connect(ff_db_dir)) as ff_conn:
	cursor = ff_conn.cursor()

	#########################################################################

	print('Finding bookmark folder ID')

	folder_title = (wishlist_folder_name,)
	wishlist_cursor = cursor.execute('SELECT * FROM moz_bookmarks WHERE type=2 AND title=?', folder_title)
	wishlist_folder = wishlist_cursor.fetchone()
	folder_id = wishlist_folder[0] # index 0 = id

	wish_list[folder_id] = {'name': 'Annet', 'desc': '', 'bookmarks': {}}

	#########################################################################

	print('Finding wish categories')

	categories_cursor = cursor.execute('SELECT * FROM moz_bookmarks WHERE type=2 AND parent=?', (folder_id,))
	category_data = categories_cursor.fetchall()

	for cat in category_data:
		wish_list[cat[0]] = {'name': cat[5], 'desc': '', 'bookmarks': {}}

	#########################################################################

	print('Finding wish bookmarks')

	statement_vars = []
	statement = 'SELECT * FROM moz_bookmarks WHERE type=1 AND (parent=?'
	for cat_id in wish_list:
		if cat_id != folder_id:
			statement += ' OR parent=?'
		statement_vars.append(cat_id)
	statement += ')'

	wish_cursor = cursor.execute(statement, statement_vars)
	wishes = wish_cursor.fetchall()
	
	print('Finding bookmark links')

	wish_links = [] # the 0th element will contain the link for the first wish in the wishes list
	for wish in wishes:
		fk = (wish[2],) # the id of the row containing the link in moz_places

		place_cursor = cursor.execute('SELECT * FROM moz_places WHERE id=?', fk)
		place = place_cursor.fetchone()

		wish_list[wish[3]]['bookmarks'][wish[0]] = {'name': wish[5], 'desc': '', 'link': place[1], 'changed': wish[9]}

	#########################################################################

	print('Finding descriptions')

	statement_vars = []
	statement = 'SELECT * FROM moz_items_annos WHERE type=3 AND (item_id=?'
	for cat_id in wish_list:
		if cat_id != folder_id:
			statement += ' OR item_id=?'
		statement_vars.append(cat_id)

		for wish_id in wish_list[cat_id]['bookmarks']:
			statement += ' OR item_id=?'
			statement_vars.append(wish_id)
	statement += ')'

	desc_cursor = cursor.execute(statement, statement_vars)
	descriptions = desc_cursor.fetchall()

	for desc in descriptions:
		if desc[1] in wish_list:
			wish_list[desc[1]]['desc'] = desc[4]

		for cat in wish_list:
			if desc[1] in wish_list[cat]['bookmarks']:
				wish_list[cat]['bookmarks'][desc[1]]['desc'] = desc[4]

print('Wish list created!\n')

#############################################################################

print('Inserting wishes into wishes database')

with contextlib.closing(sqlite3.connect('wishes.sqlite')) as bm_conn:
	cursor = bm_conn.cursor()

	# create tables in db
	with open('setup.sql', 'r') as setup:
		statement = ''
		for l in setup.readlines():
			statement += l
		cursor.execute(statement)

	# used to track which items should be removed
	all_items_cursor = cursor.execute('SELECT item_id FROM bookmarks')
	to_remove = list(all_items_cursor.fetchall())
	to_remove = [v[0] for v in to_remove]
	print(to_remove)

	for cat_id in wish_list:
		# check if the category already exists in the database
		category_cursor = cursor.execute('SELECT item_id FROM bookmarks WHERE type=2')
		category_ids = category_cursor.fetchall()
		category_ids = [v[0] for v in category_ids]

		if cat_id not in category_ids:
			values = (cat_id, wish_list[cat_id]['name'], wish_list[cat_id]['desc'])
			cursor.execute('INSERT INTO bookmarks(item_id, type, title, desc) VALUES (?, 2, ?, ?)', values)

		for id in category_ids:
			if id == cat_id:
				values = (wish_list[cat_id]['name'], wish_list[cat_id]['desc'], cat_id)
				cursor.execute('UPDATE bookmarks SET title=?, desc=? WHERE item_id=?', values)
	
				del to_remove[to_remove.index(cat_id)]

		wish_cursor = cursor.execute('SELECT item_id FROM bookmarks WHERE type=1')
		wish_ids = wish_cursor.fetchall()
		wish_ids = [v[0] for v in wish_ids]
		
		for wish_id in wish_list[cat_id]['bookmarks']:
			if wish_id not in wish_ids:
				bookmark = wish_list[cat_id]['bookmarks'][wish_id]
				values = (wish_id, cat_id, bookmark['name'], bookmark['desc'], bookmark['link'], bookmark['changed'])
				cursor.execute('INSERT INTO bookmarks (item_id, type, category, title, desc, url, changed) VALUES (?, 1, ?, ?, ?, ?, ?)', values)
				print('Inserted wish %s into database' % wish_id)

			for id in wish_ids:
				if id == wish_id:
					bookmark = wish_list[cat_id]['bookmarks'][wish_id]
					values = (cat_id, bookmark['name'], bookmark['desc'], bookmark['link'], bookmark['changed'], wish_id)
					cursor.execute('UPDATE bookmarks SET category=?, title=?, desc=?, url=?, changed=? WHERE item_id=?', values)

					del to_remove[to_remove.index(wish_id)]
					print('Updated wish %s in database' % wish_id)

	if to_remove:
		print("%s item(s) was/were slated for removal" % len(to_remove))
		for db_id in to_remove:
			db_id = (db_id,) #sqlite3 pls
			cursor.execute('DELETE FROM bookmarks WHERE item_id=?', db_id)

	bm_conn.commit()

print('All done. Wish database created!')