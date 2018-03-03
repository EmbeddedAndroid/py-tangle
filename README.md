# Usage:

git clone https://github.com/EmbeddedAndroid/py-tangle.git
cd py-tangle
docker build -t tangle .
docker run -it tangle:latest python /root/tangle.py --address <tangle address>

# Parameters:
´
```
-a <tangle addres>
-host http(s)://<node address>
-port <node port>
```
