<?php

function change_sort($a, $b){
	return ($a->getChangedTimestamp() < $b->getChangedTimestamp()) ? 1 : -1;
}

function alphabetical_title($a, $b){
	return strcmp($a->getTitle(), $b->getTitle());
}

// :  )
function category_sort($a, $b){
	return ($a->getTitle() == "Annet");
}