# imports

Собрать образы

```bash
docker-compose build
```

Применить миграции и запустить локально

```bash
make mm
docker-compose up dev_api
```

Протестировать

```bash
docker-compose run --rm test_api pytest -sv
```
