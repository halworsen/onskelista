<?php

class Wish{
	private $title, $url, $changed;

	public function __construct($title, $url, $changed){
		$this->title = $title;
		$this->url = $url;
		$this->changed = $changed;
	}

	public function getTitle(){
		return $this->title;
	}

	public function getURL(){
		return $this->url;
	}

	public function getChangedTimestamp(){
		return $this->changed;
	}

	public function getChangedTime(){
		return date('d.m.Y', $this->changed / 1000000); // firefox stores timestamp with accuracies greater than a second or someshit, so divide by 1 000 000
	}
}