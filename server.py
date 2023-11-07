"""
Write code for your server here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
import socket


def domain_check(domain: str) -> bool:

    # check if the domain is valid
    c,b,a = False, False, False
    
    split = domain.split(".")
    third, second, first = split[-1], split[-2], ''.join(split[:-2])

    if third.replace("-", "").isalnum():
        a = True

    if second.replace("-", "").isalnum():
        b = True
    
    if (first[0] != "." or first[-1] != ".") and first.replace("-", "").replace(".", "").isalnum():
        c = True
    
    return a and b and c


def partial_domain_check(domain: str) -> bool:

    # check if the domain is valid
    for i in domain.split('.'):
        if not i.replace("-", "").isalnum():
            return False
    return True


def port_check(port: str) -> bool:
    
    try:
        # check if the port is valid
        if 1024 <= int(port) <= 65535:
            return True
        else:
            return False
    
    except ValueError:
        return False
    
    
def readConfig(config: str) -> tuple or bool:

    ele_dict = {}
    # add the element to the dictionary
    f = open(config, "r")
    while True:
        line = f.readline().strip()
        if not line:
            break
        split = line.split(",")
        if len(split) == 1:
            server_port = split[0]
        else:
            domain, port = split
            if domain in ele_dict.keys() and port not in ele_dict.values():
                return False
            ele_dict[domain] = port+"\n"
    f.close()

    return (ele_dict, server_port)


def addElementCheck(hostname: str, addPort: str, check_dict: dict) -> dict or bool:

    # check if the domain is valid
    if len(hostname.split('.')) >= 3:
        if not domain_check(hostname):
            return
    else:
        if not partial_domain_check(hostname):
            return

    # check if the port is valid
    if not port_check(addPort):
        return

    # check if the element and port are already in the dictionary
    if addPort in check_dict.values():
        return
    elif hostname in check_dict.keys():
        check_dict[hostname] = addPort + "\n"
    else:
        check_dict[hostname] = addPort + "\n"


def delElementCheck(hostname: str, check_dict: dict) -> dict:

    # check if the domain is valid
    if len(hostname.split('.')) >= 3:
        if not domain_check(hostname):
            return
    else:
        if not partial_domain_check(hostname):
            return

    # check if the element is in the dictionary
    if hostname in check_dict.keys():
        del check_dict[hostname]
    


def check_valid(server_dict: dict, server_port: str) -> bool:
    # TODO

    flag = True

    if not port_check(server_port):
        return False

    for key in server_dict:

        domain, port = key, server_dict[key]

        length = len(domain.split('.'))

        if length >= 3:
            if not domain_check(domain):
                return False
        else:
            if not partial_domain_check(domain):
                return False
        
        if not port_check(port):
            return False

    return flag


def get_port(dict: dict, domain: str) -> int:
   
   # find the port number for the domain
   for key in dict:
       if key == domain:
           return dict[key]


def main(args: list[str]) -> None:
    
    # check if the arguments are valid
    if len(args) != 1:
        print("INVALID ARGUMENTS")
        return

    config = args[0]

    # check if the config file is valid
    try:
        # gain the dictionary and server port from the config file
        response = readConfig(config)
        if not response:
            print("INVALID CONFIGURATION")
            return
        else:
            config_dict, server_port = response
            server_port = int(server_port.strip())
    except FileNotFoundError:
        print("INVALID CONFIGURATION")
        return
    
    # check if the config file is valid
    valid = check_valid(config_dict, server_port)
    if not valid:
        print("INVALID CONFIGURATION")
        return
    
    ip_port = ('127.0.0.1', server_port)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(ip_port)


    while True:
        server_socket.listen()

        conn, addr = server_socket.accept()

        data = str(conn.recv(server_port).strip().decode())

        # gain the command
        command = data.split(" ")[0]

        if command == "!EXIT":
            break
        elif command == "!ADD":
            host_name, add_port = data.split(" ")[1], data.split(" ")[2]
            addElementCheck(host_name, add_port, config_dict)
        elif command == "!DEL":
            host_name= data.split(" ")[1]
            delElementCheck(host_name, config_dict)
        else:
            response = get_port(config_dict, data)

            if not response:
                print("resolve " + data + " to NXDOMAIN") 
                conn.sendto("NXDOMAIN\n".encode(), addr)
            else:
                print("resolve " + data + " to " + str(response).strip()) 
                conn.sendto((str(response)).encode(), addr)
    


if __name__ == "__main__":

    main(argv[1:])
