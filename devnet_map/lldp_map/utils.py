import json
import matplotlib.pyplot as plt
import networkx as nx
import textfsm

from nornir_scrapli.tasks import send_command

NORMALIZED_INTERFACES = {
    "FastEthernet": "Fe",
    "GigabitEthernet": "Gi",
    "TenGigabitEthernet": "Te",
    "FortyGigabitEthernet": "Fo",
    "Ethernet": "Eth",
    "Loopback": "Lo",
    "Portchannel": "Po",
}


def build(links):
    """ Отрисовка топологии """
    # создание графа
    graph = nx.MultiGraph()

    # добавление в граф инфы, какая нода с какйо соединениа
    for link in links:
        graph.add_edge(link[0].split()[0], link[1].split()[0], weight=1.0)

    # настройка заднего фона
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.tight_layout()
    pos = nx.spring_layout(graph)

    # добавление нод на картинку
    nx.draw_networkx(graph, pos, node_size=1500, arrows=False)
    # отрисовка линий между нодами
    for e in graph.edges:
        u, v, edge_id = e
        ax.annotate("", xy=pos[u], xycoords='data', xytext=pos[v], textcoords='data',
                    arrowprops=dict(arrowstyle="-",
                                    shrinkA=20, shrinkB=20,
                                    patchA=None, patchB=None,
                                    connectionstyle="arc3, rad=rrr".replace('rrr', str(0.3 * edge_id)
                                    ),
                                    ),
                    )
    filename = "lldp_map/static/topology.png"
    # сохранение в файл
    plt.savefig(filename)


def build_diff(links):
    """ Отрисовка разницы в топологии """
    # создание графа
    graph = nx.MultiGraph()
    # добавление в граф инфы, какая нода с какйо соединениа
    # по ключу определяется тип линка и назначется цвет отображения
    if links.get('exist'):
        for link in links['exist']:
            graph.add_edge(link[0].split()[0], link[1].split()[0], color='black')

    if links.get('new'):
        for link in links['new']:
            graph.add_edge(link[0].split()[0], link[1].split()[0], color='green')

    if links.get('old'):
        for link in links['old']:
            graph.add_edge(link[0].split()[0], link[1].split()[0], color='red')

    # настройка заднего фона
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.tight_layout()
    pos = nx.spring_layout(graph)

    # добавление нод на картинку
    nx.draw_networkx(graph, pos, node_size=1500, arrows=False)
    ax = plt.gca()
    # отрисовка линий между нодами
    for e in graph.edges:
        u, v, edge_id = e
        ax.annotate("", xy=pos[u], xycoords='data', xytext=pos[v], textcoords='data',
                    ha='center', va='top',
                    arrowprops=dict(arrowstyle="-", color=graph.get_edge_data(u, v)[edge_id]['color'],
                                    shrinkA=20, shrinkB=20,
                                    patchA=None,
                                    patchB=None,
                                    connectionstyle="arc3, rad=rrr".replace('rrr', str(0.3 * edge_id)
                                    ),
                                    ),
                    )
    filename = "lldp_map/static/topology-diff.png"
    # сохранение в файл
    plt.savefig(filename)


def gather_lldp(task, devices_list, links, all_connections):
    """
    Получение информации о lldp, парсинг и сбор в одну переменную
    """
    show_lldp_detial = task.run(task=send_command, command='show lldp neighbors')
    with open(r"lldp_map/inventory/cisco_ios_show_lldp_neighbors.textfsm") as f:
        re_table = textfsm.TextFSM(f) 
        parsed_output = re_table.ParseText(show_lldp_detial.result)
    for row in parsed_output:
        local_interface = normalize_interface(row[1])
        remote_interface = normalize_interface(row[3])
        if all_connections:
            remote_device = row[0].split('.')[0]
            links.put(tuple(sorted([f"{task.host} {local_interface}", f"{remote_device} {remote_interface}"])))
        else:
            if row[0] in devices_list:
                remote_device = row[0].split('.')[0]
                links.put(tuple(sorted([f"{task.host} {local_interface}", f"{remote_device} {remote_interface}"])))


def normalize_interface(interface):
    """
    Изменение имен интерфейсов на короткие
    """
    for name, short_name in NORMALIZED_INTERFACES.items():
        if interface.lower().startswith(name.lower()):
            return interface.replace(name, short_name)

    return interface