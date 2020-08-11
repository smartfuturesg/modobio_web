#!/bin/sh
docker network create modobio
docker run --name postgres_local --network modobio -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=modobio -p 5432:5432 -d postgres
docker build -t odyssey .
docker run --name odyssey --network modobio -e FLASK_APP=odyssey:create_app -e FLASK_ENV=development -e FLASK_DEV=local -e FLASK_DB_USER=postgres -e FLASK_DB_PASS=password -e FLASK_DB_HOST=postgres_local -e PYTHONPATH=/usr/src/app/src -p 5000:5000 -d odyssey
sleep 5
docker exec -it odyssey /bin/sh -c 'yes Y | flask db upgrade'; pw_hash=$(docker exec -it odyssey python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('123'))" | sed 's/\r//g'); query=$(echo "INSERT INTO \"Staff\" (email, firstname, lastname, fullname, password, is_admin) VALUES ('name@modobio.com', 'Name', 'Lastname', 'Name Lastname', '<password>', true);" | sed "s/<password>/$pw_hash/"); docker exec -it postgres_local psql -U postgres modobio -c "$query"
