import sqlite3
import contextlib
import os

# plug your profile id in here
profile_id = 'f9psb5ao'
# plug in the name of the wishlist bookmark folder here
wishlist_folder_name = 'Ønskelista'

# make sure the wishes sqlite DB exists
cwd = os.getcwd()
if not os.path.exists(cwd + '\\wishes.sqlite'):
	print("wishes DB doesn't exist, try making it first")
	exit()

appdata = os.getenv('APPDATA')
profile_dir = appdata + '\\Mozilla\\Firefox\\Profiles\\' + profile_id + '.default'
ff_db_dir = profile_dir + '\\places.sqlite'

print('Creating wish list')
wish_list = [] # pun not intended
# grab all wishes and construct a datastructure suitable for insertion into a new database
with contextlib.closing(sqlite3.connect(ff_db_dir)) as ff_conn:
	cursor = ff_conn.cursor()

	print('Finding bookmark folder ID')
	folder_title = (wishlist_folder_name,)
	wishlist_cursor = cursor.execute('SELECT * FROM moz_bookmarks WHERE type=2 AND title=?', folder_title)
	wishlist_folder = wishlist_cursor.fetchone()
	folder_id = (wishlist_folder[0],) # index 0 = id

	print('Selecting wish bookmarks')
	wishes_cursor = cursor.execute('SELECT * FROM moz_bookmarks WHERE type=1 AND parent=?', folder_id)
	wishes = wishes_cursor.fetchall()
	
	print('Finding wish bookmark links')
	wish_links = [] # the 0th element will contain the link for the first wish in the wishes list
	for wish in wishes:
		fk = (wish[2],) # fk - the id of the row containing the link in moz_places

		place_cursor = cursor.execute('SELECT * FROM moz_places WHERE id=?', fk)
		place = place_cursor.fetchone()
		wish_links.append(place[1]) # 2nd element contains the link
		print('Found link for wish %s' % wish[0])

	for i,v in enumerate(wishes):
		# index 5 is bookmark title, 9 is last changed timestamp
		wish_data = (v[0], v[5], wish_links[i], v[9])
		wish_list.append(wish_data)

print('Wish list created!\n')
print('Inserting wishes into wishes database')

with contextlib.closing(sqlite3.connect('wishes.sqlite')) as bm_conn:
	cursor = bm_conn.cursor()

	# used to track which wishes should be removed
	all_wishes_cursor = cursor.execute('SELECT id FROM bookmarks')
	to_remove = all_wishes_cursor.fetchall()
	to_remove = [v[0] for v in to_remove] # it's returned as a list of tuples, sooo... :s

	for wish in wish_list:
		wish_id = (wish[0],)

		# check if the wish already exists in the database
		wish_cursor = cursor.execute('SELECT * FROM bookmarks WHERE wish_id=?', wish_id)
		wish_row = wish_cursor.fetchone()
		
		# update existing wish
		if wish_row:
			update_values = wish[1:] + wish[:1] # move wish_id to the last index
			test = cursor.execute('UPDATE bookmarks SET title=?, url=?, changed=? WHERE wish_id=?', update_values)

			# pop the wish from the list of wishes to be removed
			db_id = cursor.execute('SELECT id FROM bookmarks WHERE wish_id=?', wish_id).fetchone()[0]
			del to_remove[to_remove.index(db_id)]

			print('Updated wish %s in database' % wish[0])
		else:
			# brand new wish!!!
			cursor.execute('INSERT INTO bookmarks(wish_id, title, url, changed) VALUES (?, ?, ?, ?)', wish)
			print('Inserted wish %s into database' % wish[0])

	#to_remove = [v for v in to_remove if v is not None] relic of an ancient past where i did to_remove[i] = None to remove from to_remove
	if to_remove:
		print("%s wish(es) were slated for removal" % len(to_remove))
		for db_id in to_remove:
			db_id = (db_id,) #sqlite3 pls
			cursor.execute('DELETE FROM bookmarks WHERE id=?', db_id)

	bm_conn.commit()

print('All done. Wish database created!')