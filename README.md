Trailer Feed
=========
Movie trailer sync to local folder


Basic example usage
```
    ./trailerfeed.py /home/ryan/Videos/Trailers
```

The above will then download any trailers on the 'Just Added' list which are not in the local folder

Download 1080p example
```
    ./trailerfeed.py -s 1080 /home/ryan/Videos/Trailers
```

Setup
-------------
If downloaded via git clone. Run 
```
    git submodule init 
    git submodule update
```
from cloned folder to download modules pytrailer and requests

Tools used
--------------
[pytrailer](https://github.com/sochotnicky/pytrailer)
[requests](https://github.com/kennethreitz/requests)


License
----

[BSD 3-Clause](http://www.opensource.org/licenses/BSD-3-Clause)



