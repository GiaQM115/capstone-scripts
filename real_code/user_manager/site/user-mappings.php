<?php
require_once 'config.php';
$group = $_POST['gname'];
foreach($_POST['email'] as $addr) {
	if($_POST['action'] == "Add Map") {
		$query = "INSERT INTO mappings(GNAME, EMAIL) VALUES('". $group . "', '" . $addr ."')";
		$result = mysqli_query($conn, $query);
		if($result) {
			header("Location: index.php");
		} else {
			header("Location: index.php?ERROR=" . mysqli_error($conn));
		}
	} else {
		$query = "DELETE FROM mappings WHERE EMAIL='" . $addr . "' AND GNAME='" . $group ."'";
		$result = mysqli_query($conn, $query);
		if(!$result) {
			header("Location: index.php?ERROR=" . mysqli_error($conn));
		}
	}
	header("Location: index.php");
}
?>
