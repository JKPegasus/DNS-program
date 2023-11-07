"""
Write code for your launcher here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
import random
from pathlib import Path
import os


def domain_check(domain: str) -> bool:

    # check if the domain is valid or not
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


def port_check(port: str) -> bool:
    
    try:
        # check if the port is valid or not
        if 1024 <= int(port) <= 65535:
            return True
        else:
            return False
    except ValueError:
        return False


def check_master(path: str) -> bool:

    f = open(path, "r")

    while True:

        line = f.readline()

        if not line:
            break

        split = line.split(",")

        if len(split) == 1:
            server_port = split[0]
            # check the port is valid or not
            if not port_check(server_port):
                return False
        else:
            domain, port = split
            # check the domain is valid or not
            if len(domain.split(".")) < 3:
                return False
            elif not domain_check(domain):
                return False
            # check the port is valid or not
            if not port_check(port):
                return False
    f.close()
    return True
    

def extraction(path: str, master_array: dict, port_array: list) -> int:

    f = open(path, "r")

    while True:

        line = f.readline()

        if not line:
            break

        split = line.split(",")

        if len(split) == 1:
            server_port = int(split[0].strip())
        else:
            domain, port = split

            root = domain.split(".")[-1]

            port_array.append(int(port.strip()))

            if root in master_array:
                master_array[root].append((domain, port))
            else:
                master_array[root] = [(domain, port)]
    f.close()

    return server_port


def generate_file(path: str, file_name: str, root_port: int, random_name: list, addr_port: list) -> None:

    f = open(f"{path}/{file_name}.conf", "w")
    f.write(f"{str(root_port)}\n")
    for i in range(len(random_name)):
        f.write(f"{random_name[i]}, {str(addr_port[i])}\n")
    f.close()


def generate_config(path: str, dict: dict, root: int, file_array: list, port_array: list) -> None:

     # Define the characters that can be included in the random string
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # Specify the length of the random string you want to generate
    string_length = 7

    # Generate the root config file
    root_domain = list(dict.keys())

    root_file, root_port = None, []

    while not root_file:

        root_file = ''.join(random.choice(characters) for _ in range(string_length))
        if root_file not in file_array:
            file_array.append(root_file)
        else:
            root_file = None

    while len(root_port) < len(root_domain):
        prev_port = []
        port = random.randint(1025, 65535)
        if port not in port_array:
            port_array.append(port)
            root_port.append(port)
            prev_port.append(port)
        else:
            # delete the port that is already used
            for i in prev_port:
                port_array.remove(i)
            root_port = []

    generate_file(path, root_file, root, root_domain, root_port)

    # Generate the tld config file
    for i in range(len(root_domain)):
        tld_domain, tld_port = [], []

        tld_file = None
        while not tld_file:
            tld_file = ''.join(random.choice(characters) for _ in range(string_length))
            if tld_file not in file_array:
                file_array.append(tld_file)
            else:
                tld_file = None


        tld_array = []
        for j in range(len(dict[root_domain[i]])):
            
            domain = '.'.join(dict[root_domain[i]][j][0].split(".")[-2:])
            if domain not in tld_array:
                tld_domain.append('.'.join(dict[root_domain[i]][j][0].split(".")[-2:]))
                tld_array.append(domain)
                
                port = None
                while not port:
                    port = random.randint(1025, 65535)
                    if port not in port_array:
                        port_array.append(port)
                        tld_port.append(port)
                    else:
                        port = None
            
                generate_file(path, tld_file, root_port[i], tld_domain, tld_port)
    
        # Generate the auth config file
        for partial in range(len(tld_array)):
            auth_domain, auth_port = [], []
            for k in range(len(dict[root_domain[i]])):
                auth_file = None
                while not auth_file:
                    auth_file = ''.join(random.choice(characters) for _ in range(string_length))
                    if auth_file not in file_array:
                        file_array.append(auth_file)
                    else:
                        auth_file = None
                
                if tld_array[partial] == '.'.join(dict[root_domain[i]][k][0].split(".")[-2:]):
                    auth_domain.append(dict[root_domain[i]][k][0])
                    auth_port.append(dict[root_domain[i]][k][1].strip())
                
            generate_file(path, auth_file, tld_port[partial], auth_domain, auth_port)



def main(args: list[str]) -> None:
    
    if len(args) != 2:
        print("INVALID ARGUMENTS")
        return
    
    master_path, single_path = args

    # check the master file is valid
    try:
        if not check_master(master_path):
            print("INVALID MASTER")
            return
    except FileNotFoundError:
        print("INVALID MASTER")
        return

    # check the single directory is valid or not
    if not Path(single_path).is_dir():
        print("NON-WRITABLE SINGLE DIR")
        return
    elif not Path(single_path).exists():
        print("NON-WRITABLE SINGLE DIR")
        return
    
    # generate the config file
    single_dict = {}
    port_array, file_array = [], []

    server_port = extraction(master_path, single_dict, port_array)
    #print(single_dict)

    generate_config(single_path, single_dict, server_port, file_array, port_array)

    #print("file_array: ", file_array)
    #print("port_array: ", port_array)

    # check the config file that is generated or not
    # for i in range(len(file_array)):
    #     if not Path(f"{single_path}/{file_array[i]}.conf").exists():
    #         print(f"CONFIG FILE: {file_array[i]} NOT GENERATED")
    #         return
    #     else:
    #         f = open(f"{single_path}/{file_array[i]}.conf", "r")
    #         content = f.readlines()
    #         print(f"Open file {file_array[i]}: ", content)
    #         f.close()

if __name__ == "__main__":
    main(argv[1:])
