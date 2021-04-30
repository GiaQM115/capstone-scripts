echo -n "What is the admin/sending email address? "
read email
read -sp "Password: " pass
printf "\n"
read -sp "Retype Password: " check
while [[ $pass != $check ]]; do
	printf "\nPasswords do not match!\n"
	read -sp "Password: " pass
	printf "\n"
	read -sp "Retype Password: " check
done

sed -i "s/FROM_EMAIL = .*$/FROM_EMAIL = '$email'/" send_emails.py
sed -i "s/FROM_EMAIL_PASS = .*$/FROM_EMAIL_PASS = '$pass'/" send_emails.py

docker cp send_emails.py comparison-server:/send_emails.py
