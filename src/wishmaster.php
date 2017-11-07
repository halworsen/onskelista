<?php

use \PDO;

class WishMaster{
	public function __construct(PDO $pdo){
		$this->pdo = $pdo;
	}

	public function getCategorizedWishes(){
		$query = 'SELECT * FROM bookmarks WHERE type=2';
		$statement = $this->pdo->prepare($query);
		$statement->execute();

		$categories = [];
		foreach($statement->fetchAll() as $categoryData){
			$category = new WishCategory(
				$this->pdo,
				$categoryData['item_id'],
				$categoryData['title'],
				$categoryData['desc']
			);
			$categories[] = $category;
		}

		return $categories;
	}

	public function getAll(){
		$query = 'SELECT * FROM bookmarks ORDER BY changed ASC';
		$statement = $this->pdo->prepare($query);
		$statement->execute();

		$wishes = [];
		foreach($statement->fetchAll() as $bookmark){
			$wish = new Wish(
				$bookmark['title'],
				$bookmark['url'],
				$bookmark['changed']
			);
			$wishes[] = $wish;
		}

		return $wishes;
	}
}