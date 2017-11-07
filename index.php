<?php
	date_default_timezone_set('Europe/Oslo');

	require('src/util.php');
	require('src/category.php');
	require('src/wish.php');
	require('src/wishmaster.php');

	$pdo = new \PDO('sqlite:wishes.sqlite', null, null);
	$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	$wishMaster = new WishMaster($pdo);

	$categories = $wishMaster->getCategorizedWishes();
	usort($categories, 'alphabetical_title');
	// items with no category always go to the bottom
	usort($categories, 'category_sort');
?>

<!DOCTYPE html>
<html lang="no">
<title>Ønskelista</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
<link rel="stylesheet" href="css/style.css">

<header>
	<h2>ønskelista</h2>
	<p>
		Diverse tull direkte fra bokmerkeraden min som jeg synes det hadde vært kult å ha
		<br><br>
		Lista oppdateres hver dag kl. 12
	</p>
</header>

<div class="content">
	<ul class="categories">
		<?php
			foreach($categories as $k => $category){
				if($category->wishAmt() > 0){
		?>
					<h2><?= $category->getTitle(); ?></h2>
					<p><?= $category->getDesc(); ?></p>
					<ul class="wishes">

		<?php
					foreach($category->getWishes() as $k2 => $wish){
		?>

							<?= '<a href="' . $wish->getURL() . '" alt="hi">' ?>
								<li>
									<p class="card-title"><?= $wish->getTitle(); ?></p>
									<p class="desc"><?= $wish->getDesc(); ?></p>
									<p class="changed"><?= 'Sist endret ' . $wish->getChangedTime(); ?></p>
								</li>
							</a>
		<?php
					}
		?>

					</ul>

		<?php
				}
			}
		?>
	</ul>
</div>

</html>