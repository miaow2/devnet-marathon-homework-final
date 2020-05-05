# Финальная работа по DevNet Marathon

## Описание

[Ссылка](https://cisco.app.box.com/s/hd3d5rev9d0sr0ygie3x8p414fofr6wy) на домашнее задание

Используется Django + Nornir, следуйте пунктам в установке для запуска.

Вроде все делает по заданию, НО не отображает имена интерфейсов. Я взялся делать через mathplotlib + networx и там это не совсем тривиальная задача. Надо больше времени, что разобраться.

Веб открывается по ссылке http://127.0.0.1:8000/

Девайсы добавляются через админку Django, по умолчанию карта строится только между девайсами, которые есть в базе. 
Чтобы отображилсь все найденные связи, надо в файле настроек `devnet_map/devnet_map/settings.py` поменять параметр `ALL_CONNECTIONS` на `True`.

Настройки Nornir находятся в папке `devnet_map/lldp_map/inventory`. При каждом запуске сбора LLDP инвентори генерится из данных БД.

Логин и пароль берется из переменных среды `DEVNET_USERNAME`, `DEVNET_PASSWORD`. Поэтому перед запуском надо их задать.

Информация о топологии в машинном виде лежит в файлах `devnet_map/lldp_map/static/topology.json` и `topology-old.json`. Хранятся только две версии топологии.
При запуске сбора LLDP информация копируется из `topology.json` в `topology-old.json`. Новая информация записывается в `topology.json`. Это сделано для сравнения версий.

Картинки хранятся в файлах `devnet_map/lldp_map/static/topology.png` и `topology-diff.json`.

### Главная
`Add, Editing Devices` кнопка создания, редактирования и удаления девайсов.

`Build Topology` постройка новой топологии.

`Topology Difference` постройка разницы между топологиями.

Ниже таблица с девайсами и их IP адресами

![Главная](/images/Devices.jpg?raw=true)

### Топология

Кнопка `Back` возвращает на страницу с девайсами.

`Refresh` запускает заново сбор LLDP и обновляет список и картинку.

Далее идет список всех линков и картинка с топологией.

![Топология](/images/Topology.jpg?raw=true)

### Изменения топологии

Кнопка `Back` возвращает на страницу с девайсами.

`Refresh` запускает заново сравнение.

Не изменившиеся линки черного цвета, новые — зеленого, удаленные — карсного.

![Изменения](/images/Topology_diff.jpg?raw=true)

## Установка

Создадим папку под софт
```
cd /opt
sudo mkdir devnet_map
cd devnet_map
```

Клонируем в папку репозиторий
```
sudo git clone https://github.com/miaow2/devnet-marathon-homework-final.git .
```

Создаем виртуальное окружение для питона и активируем его
```
sudo python3 -m venv .venv
source .venv/bin/activate
```

Устанавливаем необходимые библиотеки
```
sudo pip3 install -r requirements.txt
```

Переходим в папку и создаем базу данных
```
cd devnet_map
sudo python3 manage.py migrate
```

Создаем супер пользователя для доступа к админке и созданию записей в БД
```
python3 manage.py createsuperuser
```

Запускаем сервер
```
sudo python3 manage.py runserver
```

После этого сервер будет доступен по ссылке http://127.0.0.1:8000/
