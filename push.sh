git add ./
echo "Enter git commit message"
read  msg
git commit -m "$msg"
git push origin master
