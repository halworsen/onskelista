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
print('Populating template')

with open('template.html', 'r') as template:
	body = template.read()

	wishes_html = ''
	# populate with wishes
	for wish in wish_list:
		title = wish[1]
		url = wish[2]

		wishes_html += ('<li><a href="' + url + '">' + title + '</a></li>\n\t')

	body = body.format(wishes_html)

	with open('index.html', 'w') as index:
		index.write(body)

print('Done!')
