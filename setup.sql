CREATE TABLE `bookmarks` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`wish_id`	INTEGER,
	`title`	TEXT,
	`url`	TEXT,
	`changed`	INTEGER
);