CREATE TABLE IF NOT EXISTS `bookmarks` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`item_id`	INTEGER,
	`type` INTEGER,
	`category` INTEGER,
	`title`	TEXT,
	`desc` TEXT,
	`url`	TEXT,
	`changed`	INTEGER
);