filename=report/$(date "+%Y%m%d-%H%M%S").json
# behave -f json -o $filename features/login.feature
# behave -f json -o $filename --no-skipped --no-capture --tags=@trilho_ca

behave -f json -o $filename --no-skipped --no-capture --tags=@trilho_ca

if [ $? -ne 0 ]; then
    python send_email.py $filename
fi
