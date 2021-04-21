<!DOCTYPE html>
<head>
<title>User/Group Management</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<?php
	if($_GET["ERROR"]) {
		echo "<span class='error'>An error occured, database unchanged!<br>Error: " . $_GET['ERROR'] . "</span>";
	} 
?>


<div class="section-head" style="background-color: #324851;">
<h1>Current Groups</h1>
<div class="scrollbox">
<?php
require_once 'config.php';
$query = "SELECT DISTINCT GNAME FROM groups";
$groups = mysqli_query($conn, $query);
while($group = mysqli_fetch_assoc($groups)) {
	$query = "SELECT users.FNAME, users.LNAME, mappings.GNAME FROM users INNER JOIN mappings ON users.EMAIL=mappings.EMAIL WHERE mappings.GNAME='" . $group['GNAME'] . "'";
	$result = mysqli_query($conn, $query);
	echo "<h2>" . $group['GNAME'] . "</h2>";
	while($row = mysqli_fetch_assoc($result)) {
		echo "<li>" . $row['FNAME'] . " " . $row['LNAME'] . "</li>";
	}
}
?>
</div>
</div>


<div class="section-head" style="background-color: #34675C;">
<h1>Add/remove a group</h1>
<form action="groups.php" method="POST">
<div class="scrollbox">
<h2>Current Groups</h2>
<?php
require_once 'config.php';
$query = "SELECT DISTINCT GNAME FROM groups";
$groups = mysqli_query($conn, $query);
while($names = mysqli_fetch_assoc($groups)) {
	$query = "SELECT TAG FROM groups WHERE GNAME='" . $names['GNAME'] . "'";
	$result = mysqli_query($conn, $query);
	$notifies = " (";
	while($row = mysqli_fetch_assoc($result)) {
		$notifies = $notifies . $row['TAG'] . ", ";
	}
	echo "<li><input type='checkbox' name='gname[]' value='" . $names['GNAME'] . "'>" . $names['GNAME'] . substr($notifies, 0, -2) . ")</input></li>";
}
?>
</div>
<input type="submit" name="action" value="Delete Groups" />
</form>
<form action="groups.php" method="POST">
<input type="text" name="gname" placeholder="Group Name">
<input type="text" name="tag" placeholder="Tag">
<br>
<input type="submit" name="action" value="Add Group" />
</form>
</div>


<div class="section-head" style="background-color: #324851;">
<h1>Add/remove a user</h1>
<form action="users.php" method="POST">
<div class="scrollbox">
<h2>Current Users</h2>
<?php
require_once 'config.php';
$query = "SELECT * FROM users";
$result = mysqli_query($conn, $query);
while($row = mysqli_fetch_assoc($result)) {
	echo "<li><input type='checkbox' name='email[]' value='" . $row['EMAIL'] . "'>" . $row['FNAME'] . " " . $row['LNAME'] . ": " . $row['EMAIL'] . "</input></li>";
}
?>
</div>
<input type="submit" name="action" value="Delete Users" />
</form>
<form action="users.php" method="POST">
<input type="text" name="fname" placeholder="User First Name">
<input type="text" name="lname" placeholder="User Last Name">
<input type="text" name="email" placeholder="User Email">
<br>
<input type="submit" name="action" value="Add User" />
</form>
</div>


<div class="section-head" style="background-color: #7DA3A1;">
<h1>Add/remove a mapping</h1>
<form action="user-mappings.php" method="POST">
<div class="scrollbox">
<h2>Select Users</h2>
<?php
require_once 'config.php';
$query = "SELECT * FROM users";
$result = mysqli_query($conn, $query);
while($row = mysqli_fetch_assoc($result)) {
	echo "<li><input type='checkbox' name='email[]' value='" . $row['EMAIL'] . "'>" . $row['FNAME'] . " " . $row['LNAME'] . ": " . $row['EMAIL'] . "</input></li>";
}
?>
</div>
<div style="width: 70%; margin: 0 auto 3% auto;">
<h2>Select Group</h2>
<select name="gname">
<?php
require_once 'config.php';
$query = "SELECT DISTINCT GNAME FROM groups";
$groups = mysqli_query($conn, $query);
while($names = mysqli_fetch_assoc($groups)) {
	echo "<option value='" . $names['GNAME'] . "'>" . $names['GNAME'] . "</option>";
}
?>
</select>
</div>
<input type="submit" style="margin-bottom: 1%;" name="action" value="Add Map" />
<input type="submit" style="margin-top: 0;" name="action" value="Remove Map" />
</form>
</div>


</body>
</html>
