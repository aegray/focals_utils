###

# may need:
# sudo apt-get install libssl1.0.0 -y

# this generates a root cert that we can install on the glasses 
# then generates a key and signed certificate we can use 

openssl genrsa -des3 -out myCA.key 2048


# password for root cert is "password"  (no quotes)


openssl req -x509 -new -nodes -key myCA.key -sha256 -days 1825 -out myCA.pem




# create site certificate
openssl genrsa -out bysouth.com.key 2048

# create signing req
openssl req -new -key bysouth.com.key -out bysouth.com.csr

# sign
openssl x509 -req -in bysouth.com.csr -CA myCA.pem -CAkey myCA.key -CAcreateserial -out bysouth.com.crt -days 825 -sha256 -extfile bysouth.com.ext



# you can now add myCA.pem to /system/etc/ssl/certs/cacert.pem
# I included the fully updated version here in cacert.pem 

# We can then serve ssl content for *.bynorth.com with bysouth.com.crt and bysouth.com.key





# links for providing ssl content from android:
# https://stackoverflow.com/questions/30498206/how-make-ssl-server-socket-support-both-http-https-in-java
# https://stackoverflow.com/questions/37850134/what-is-the-certificate-enrollment-process




