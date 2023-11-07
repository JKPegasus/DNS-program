"""
Write code for your launcher here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
from pathlib import Path


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


def partial_domain_check(domain: str) -> bool:

    # check if the domain is valid
    for i in domain.split('.'):
        if not i.replace("-", "").isalnum():
            return False
    return True


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


def check_single(path: str) -> bool:

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
                if not partial_domain_check(domain):
                    return False
            else:
                if not domain_check(domain):
                    return False
            # check the port is valid or not
            if not port_check(port):
                return False
    f.close()
    return True


def extract_single(path: str) -> list:
    
    singles = Path(path)

    single_paths = []

    for path in singles.iterdir():

        single_paths.append(path)
    
    return single_paths


def extract_domain(master_path: str, verify_dict: dict) -> None:

    f = open(master_path, "r")

    while True:

        line = f.readline()

        if not line:
            break

        split = line.split(",")

        if len(split) == 1:
            server_port = int(split[0].strip())
        else:
            domain, port = split

            verify_dict[(domain, port)] = False
            
    f.close()


def verify_single(auth: str, root_port: str, single_paths: list, master_dict: dict) -> bool:

    # collect the result
    if len(auth.split('.')) >= 3:
        if (auth, root_port) in master_dict:
            master_dict[(auth, root_port)] = True
    
    # find the root content
    for path in single_paths:

        f = open(path, "r")

        line = f.readline()

        content = f.readlines()

        root_found = False

        for i in content:
            if i.split(",")[0].count(".") == 0:
                root_found = True
            else:
                root_found = False
        
        # delete the root path
        if root_found:
            single_paths.remove(path)

        if line == root_port or root_found:
            f.seek(0)

            root_content = f.readlines()[1:]
            #print("content: ", root_content)
            
            for i in range(len(root_content)):
                
                domain, port = root_content[i].split(",")
                if port == root_port:
                    return False
                
                if verify_single(domain, port, single_paths, master_dict) == False:
                    return False
            break

        f.close()


def main(args: list[str]) -> None:
    
    if len(args) != 2:
        print("invalid arguments")
        return
    
    master_path, single_path = args

    # check the master file is valid
    try:
        if not check_master(master_path):
            print("invalid master")
            return
    except FileNotFoundError:
        print("invalid master")
        return

    # check the single directory is valid or not
    if not Path(single_path).is_dir():
        print("singles io error")
        return
    elif not Path(single_path).exists():
        print("singles io error")
        return

    # gain the single file list
    paths = extract_single(single_path)

    # check the single file is valid or not
    for path in paths:
        if not check_single(path):
            print("invalid single")
            return

    # gain the root port and domain:port dict
    verify_dict = {}
    extract_domain(master_path, verify_dict)

    # verify the single file
    if verify_single("", "Not exist", paths, verify_dict) == False:
        print("neq")
        return

    #print("verify_dict: ", verify_dict)

    for boolean in verify_dict.values():
        if not boolean:
            print("neq")
            return
    print("eq")
    return

if __name__ == "__main__":
    main(argv[1:])
