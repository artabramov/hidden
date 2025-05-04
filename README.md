# Hidden

Hidden is a secure data storage app that uses encryption and unrecoverable
deletion techniques to ensure the protection of your files. The app is
designed for both individual and collaborative use, offering role-based
access control with the ability to manage documents. Files are encrypted
using a unique secret key, preventing unauthorized access.

## How to install
```
make install
```

## The app is available at:
```
http://localhost/docs
```

## The docs are available at:
```
http://localhost/sphinx/
```

## How to run flake8 linter:
```
docker exec hidden /bin/sh -c 'flake8 --count --max-line-length=79 /hidden'
```

## How to run unit tests:
```
docker exec hidden /bin/sh -c 'cd /hidden && python3 -W ignore -m coverage run -m unittest discover -s ./tests -p *_tests.py -v'
```

## How to check coverage report:
```
docker exec hidden /bin/sh -c 'cd /hidden && python3 -m coverage report --omit ./tests/*'
```
