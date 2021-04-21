<?php
require_once 'config.php';
if($_POST['action'] == "Add User") {
	$query = "INSERT INTO users(FNAME, LNAME, EMAIL) VALUES('". $_POST['fname'] . "', '"  . $_POST['lname'] . "', '" . $_POST['email'] ."')";
	$result = mysqli_query($conn, $query);
	if($result) {
		header("Location: index.php");
	} else {
		header("Location: index.php?ERROR=" . mysqli_error($conn));
	}
} else {
	foreach($_POST['email'] as $addr) {
		$query = "DELETE FROM users WHERE EMAIL='" . $addr . "'";
		$result = mysqli_query($conn, $query);
		if(!$result) {
			header("Location: index.php?ERROR=" . mysqli_error($conn));
		}
	}
	header("Location: index.php");
}
?>
