<?php
require_once 'config.php';
if($_POST['action'] == "Add Group") {
	$query = "INSERT INTO groups(GNAME, TAG) VALUES('". $_POST['gname'] . "', '" . $_POST['tag'] ."')";
	$result = mysqli_query($conn, $query);
	if($result) {
		header("Location: index.php");
	} else {
		header("Location: index.php?ERROR=" . mysqli_error($conn));
	}
} else {
	foreach($_POST['gname'] as $group) {
		$query = "DELETE FROM groups WHERE GNAME='" . $group . "'";
		$result = mysqli_query($conn, $query);
		if(!$result) {
			header("Location: index.php?ERROR=" . mysqli_error($conn));
		}
	}
	header("Location: index.php");
}
?>
