import json
import os
import subprocess
import yaml

from django.shortcuts import render
from django.views.generic import View
from nornir import InitNornir
from queue import Queue

from .models import Device
from .utils import build, build_diff, gather_lldp
from devnet_map.settings import ALL_CONNECTIONS


class DevicesView(View):
    """
    Из бд запрашиаются все девайсы и рендирется страничка devices.html
    """
    def get(self, request):
        devices = Device.objects.all().order_by('name')
        return render(request, 'devices.html', {
            'devices': devices if devices else [],
        })


class TopologyDiffView(View):
    """
    Постройка различий в топологии сети
    """
    def get(self, request):
        # проверяем наличие файлов с топологиями
        try:
            with open("lldp_map/static/topology.json") as data_file:
                new = json.load(data_file)
                new_set = set()
                for item in new.items():
                    new_set.add(item)
        except FileNotFoundError:
            raise ValueError("Не был найден файл топологии, попробуйте сначала построить его")

        try:
            with open("lldp_map/static/topology-old.json") as data_file:
                old = json.load(data_file)
                old_set = set()
                for item in old.items():
                    old_set.add(item)
        except FileNotFoundError:
            raise ValueError("Не был найден файл старой топологии")

        # находим различия в файлах топологий
        # линки без изменений записываются в ключ exist
        # новые в — new, удаленные — old
        links_dict = dict()
        if new_set.intersection(old_set):
            links_dict['exist'] = new_set.intersection(old_set)
        if new_set.difference(old_set):
            links_dict['new'] = new_set.difference(old_set)
        if old_set.difference(new_set):
            links_dict['old'] = old_set.difference(new_set)

        # рисуем картинку
        links = dict()
        if links_dict:
            build_diff(links_dict)

        # делаем записи линков для отображения в текствовом виде на странице
        if links_dict.get('exist'):
            links['exist'] = list()
            for item in links_dict['exist']:
                links['exist'].append(f"{item[0].split()[0]} {item[0].split()[1]} <--> {item[1].split()[1]} {item[1].split()[0]} ")
        if links_dict.get('new'):
            links['new'] = list()
            for item in links_dict['new']:
                links['new'].append(f"{item[0].split()[0]} {item[0].split()[1]} <--> {item[1].split()[1]} {item[1].split()[0]} ")
        if links_dict.get('old'):
            links['old'] = list()
            for item in links_dict['old']:
                links['old'].append(f"{item[0].split()[0]} {item[0].split()[1]} <--> {item[1].split()[1]} {item[1].split()[0]} ")

        # рендерим страницу topology_diff.html с картинкой топологии и текстом
        return render(request, 'topology_diff.html', {
            'links': links,
        })


class TopologyView(View):
    """
    Постройка топологии сети
    """
    def get(self, request):
        # получаем все девайсы из бд
        devices = Device.objects.all()
        devices_dict = dict()

        # формируем инвентори и записываем в файл для норнира
        for device in devices:
            devices_dict[device.name] = dict()
            devices_dict[device.name]['hostname'] = device.ip_address
        with open(f"lldp_map/inventory/devices.yaml", 'w') as f:
            yaml.dump(devices_dict, f)

        # переменная для сбора инфы из lldp
        links = Queue()
        # запускаем норнир
        with InitNornir(config_file=f"lldp_map/inventory/config.yaml") as nr:
            # логин/пароль из переменных среды оси
            nr.inventory.defaults.username = os.getenv('DEVNET_USERNAME')
            nr.inventory.defaults.password = os.getenv('DEVNET_PASSWORD')
            print(nr.inventory.defaults.username)
            print(nr.inventory.defaults.password)
            # список всех хостов из инвентори
            devices_list = [host.name for host in nr.inventory.hosts.values()]
            # ALL_CONNECTIONS определяет все линки выводить или только между устройствами в БД
            nr.run(task=gather_lldp, devices_list=devices_list, links=links, all_connections=ALL_CONNECTIONS)

        # убираем дубли записей
        unique_links = set(list(links.queue))
        # предыдущий файл топологии переименоываем в topology-old.json
        subprocess.run(["mv", "lldp_map/static/topology.json", "lldp_map/static/topology-old.json"])
        # записываем актуальную топологию
        with open("lldp_map/static/topology.json", "w") as data_file:
            json.dump(dict(unique_links), data_file, indent=2)

        # строим граф
        build(unique_links)
        # делаем записи линков для отображения в текствовом виде на странице
        links = list()
        for item in unique_links:
            links.append(f"{item[0].split()[0]} {item[0].split()[1]} <--> {item[1].split()[1]} {item[1].split()[0]} ")

        # рендерим страницу topology.html с картинкой топологии и текстом
        return render(request, 'topology.html', {
            'links': links,
        })