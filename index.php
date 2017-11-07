<?php
	date_default_timezone_set('Europe/Oslo');

	require('src/wish.php');
	require('src/wishmaster.php');

	$pdo = new \PDO('sqlite:wishes.sqlite', null, null);
	$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	$wishMaster = new WishMaster($pdo);

	function change_sort($a, $b){
		return ($a->getChangedTimestamp() < $b->getChangedTimestamp()) ? 1 : -1;
	}
?>

<!DOCTYPE html>
<html lang="no">
<title>Ønskelista</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
<link rel="stylesheet" href="css/style.css">

<header>
	<h2>ønskelista</h2>
	<p class="desc">
		Diverse tull direkte fra bokmerkeraden min som jeg synes det hadde vært kult å ha
		<br><br>
		Lista oppdateres hver dag kl. 12
	</p>
</header>

<div>
	<ul>
		<?php
			$wishes = $wishMaster->getAll();
			usort($wishes, "change_sort");

			foreach($wishes as $k => $wish){
		?>
				<?= '<a href="' . $wish->getURL() . '">' ?><li>
					<p class="card-title"><?= $wish->getTitle(); ?></p>
					<p class="changed"><?= 'Sist endret ' . $wish->getChangedTime(); ?></p>
				</li></a>
		<?php
			}
		?>
	</ul>
</div>

</html>