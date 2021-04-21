<?php
$host = "192.168.1.4";
$user = "admin";
$password = "Password-123";
$db = "usermgt";
$port = "3000";
$conn = mysqli_connect($host, $user, $password, $db, $port);
if(mysqli_connect_errno()) {
	echo "Cannot connec to DB. Contact administrator.";
	echo mysqli_connect_error();
	exit();
}
?>
