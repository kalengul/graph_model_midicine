import socket
import threading
import json
import math
from clasterLib.ClusterInfo import ClusterInfo
from clasterLib.Sender import Sender
from vBBB_v2 import Bayesian

#Декоратор для модели обучаения, чтобы через сокеты связываться с ММК
# Тестовая функция
def MultiFunction(agent_way):
    x = float(agent_way[0]["SendValue"].replace(",", "."))
    print(x)
    y = float(agent_way[1]["SendValue"].replace(",", "."))
    print(y)
    return x * math.sin(4 * math.pi* x) + y * math.sin(4 * math.pi * y)

def LearnGraph(graph_learnd, agent_way):
    # Объявляем модуль для обучения сети
    bayesian = Bayesian("./drug_allopurinol.json")



# Обработчик для подключенных клиентов
def handler(client_socket, graph_learnd):
    while True:
        data_received = client_socket.recv(4096)
        read_data = data_received.decode()

        if not data_received: break

        data = json.loads(read_data)
        print(data)

        header = data.get('Header', "")
        body = data.get('Body', "")

        if (header == "StatusCommunication"):
            body_data = json.loads(body)
            if (body_data['Status'] == "start"):
                print("Session start request received")

                sender_response = Sender()
                sender_response.AddData("bool", "true")

                # Определяем сколько нужно слоев графа и количество значений
                # Добавляем к ответу для последующей генерации графа

                res_dict = sender_response.__dict__
                data_to_send = json.dumps(res_dict)
                client_socket.sendall(data_to_send.encode())

            elif (body_data['Status'] == "End"):
                print("Session end request received")
                sender_response = Sender()
                sender_response.AddData("bool", "true")
                res_dict = sender_response.__dict__
                data_to_send = json.dumps(res_dict)
                client_socket.sendall(data_to_send.encode())
        elif(header == "GetGraphInfo"):
            # Отправляем информацию для построения графа верочтностей ACO
            # Отправляется id узла и массив его состояний для таблицы conditional_probability (ACO строи граф с двумя уровнями слоев))
            # Создаем объект bayesian и получаем из него информацию о графе
            bayesian = Bayesian(graph_learnd)
            grphInfo = bayesian.GetInfo()

            sender_response = Sender()
            sender_response.AddData("GraphInfo", json.dumps(grphInfo))
            res_dict = sender_response.__dict__
            data_to_send = json.dumps(res_dict)
            client_socket.sendall(data_to_send.encode())
            
        elif (header == "MultyCalculation"):
            body_data = json.loads(body)
            multy_calculation_req = json.loads(body)
            for item in multy_calculation_req:
                # item['result'] = MultiFunction(item['Way_For_Send'])
                item['result'] = LearnGraph(graph_learnd, item['Way_For_Send']) # Обучаем БС

            sender_response = Sender()
            sender_response.AddData("MultyCalculation", json.dumps(multy_calculation_req))
            res_dict = sender_response.__dict__
            data_to_send = json.dumps(res_dict)
            client_socket.sendall(data_to_send.encode())


# Поднимаем сокеты
def start_server():
    clusterInfo = ClusterInfo() # Объявление конфигурации кластера
    server = socket.socket() # создаем объект сокета сервера
    server.bind((clusterInfo.IP, clusterInfo.PORT)) # привязываем сокет сервера к хосту и порту
    server.listen(100000000) # начинаем прослушиваение входящих подключений 
    print("Server starts")
    
    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")

        client_thread = threading.Thread(target=handler, args=(client_socket, "./drug_allopurinol.json"))
        client_thread.start()


if __name__ == "__main__":
    start_server()