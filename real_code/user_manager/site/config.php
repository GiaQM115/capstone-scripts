<?php
$host = "localhost";
$user = "admin";
$password = "password1";
$db = "usermgt";
$port = "3000";
$conn = mysqli_connect($host, $user, $password, $db, $port);
if(mysqli_connect_errno()) {
	echo "Cannot connect to database!";
	exit();
}
?>
