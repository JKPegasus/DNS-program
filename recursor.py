"""
Write code for your recursor here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
import socket


def recursor(domain: str, ip_port: tuple, time_out: int, index: int, count: int) -> int:

    if count == 0:
        print(ip_port[1])
        return
    
    # create a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        # set the socket option
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # check if the ip address is valid
        try:
            sock.connect(ip_port)
            
        except ConnectionRefusedError:

            # check which level has the error
            if count == 3:
                print("FAILED TO CONNECT TO ROOT")
                return
            elif count == 2:
                print("FAILED TO CONNECT TO TLD")
                return
            else:
                print("FAILED TO CONNECT TO AUTH")
                return
        
        sock.settimeout(time_out)
    
        split = domain.split('.')[index:]

        if len(split) > 1 and count > 1:
            request = '.'.join(split) + "\n"
        elif len(split) == 1 and count > 1:
            request = split[0] + "\n"
        else:
            request = domain + "\n"

        #print("request: " + request)
        sock.send(request.encode())

        # receive the response from the root server
        try:
            server_response = sock.recv(ip_port[1]).decode().strip()
        except TimeoutError:
            print("NXDOMAIN")
            return
        
        if server_response == "NXDOMAIN":
            print("NXDOMAIN")
            return

        # close the socket
        sock.close()
    
    recursor(domain, ('127.0.0.1', int(server_response)), time_out, index-1, count-1)


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



def main(args: list[str]) -> None:
    # TODO
    
    # check if the number of arguments is correct

    if len(args) != 2:
        print("INVALID ARGUMENTS")
        return
    
    try:
        root_port = int(args[0])
        # check if the port number is valid
        if root_port < 0 or root_port > 65536:
            print("INVALID ARGUMENTS")
            return
        time_out = args[1]
        for i in time_out:
            if i == ".":
                time_out = float(time_out)
                break
        else:
            time_out = int(time_out)
        
    except IndexError:
        print("INVALID ARGUMENTS")
        return

    # recursor loop
    while True:

        try:
            domain = input("")
            #print(domain)

            count, length = 3, len(domain.split('.'))

            # check if the domain is valid

            if len(domain.split('.')) < 3:
                print("INVALID")
                continue

            if not domain_check(domain):
                print("INVALID")
                continue

            recursor(domain, ('127.0.0.1', root_port), time_out, length-1, count)
        
        except EOFError:
            break



if __name__ == "__main__":
    main(argv[1:])
