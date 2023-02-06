from NetworkManager import network_manager
from Models.Result import Result

if __name__ == "__main__":
    result = Result("Arman", True)
    network_manager.NetworkManager(result).send_result()