<?php

use \PDO;

class WishCategory{
	private $id, $title, $desc, $wishes;

	public function __construct(PDO $pdo, $id, $title, $desc){
		$this->pdo = $pdo;
		$this->id = $id;
		$this->title = $title;
		$this->desc = $desc;

		$this->populate();
	}

	public function populate(){
		$query = 'SELECT * FROM bookmarks WHERE category=:catID ORDER BY changed ASC';
		$statement = $this->pdo->prepare($query);
		$statement->bindParam(':catID', $this->id, PDO::PARAM_INT);
		$statement->execute();

		$this->wishes = [];
		foreach($statement->fetchAll() as $bookmark){
			$wish = new Wish(
				$bookmark['title'],
				$bookmark['desc'],
				$bookmark['url'],
				$bookmark['changed']
			);
			$this->wishes[] = $wish;
		}

		usort($this->wishes, "change_sort");
	}

	public function wishAmt(){
		return count($this->wishes);
	}

	public function getTitle(){
		return $this->title;
	}

	public function getDesc(){
		return $this->desc;
	}

	public function getWishes(){
		return $this->wishes;
	}
}