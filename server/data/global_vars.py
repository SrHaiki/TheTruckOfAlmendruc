class GlobalVars:

    def __init__(self):
        self.rsa_pub = None
        self.rsa_priv = None
        self.list_of_routes_for_ligolo = []
    
    def get_rsa_pub(self):
        return self.rsa_pub
    
    def get_rsa_priv(self):
        return self.rsa_priv
    
    def set_rsa_pub(self, rsa_pub):
        self.rsa_pub = rsa_pub
        return
    
    def set_rsa_priv(self, rsa_priv):
        self.rsa_priv = rsa_priv
        return
    
    def add_item_to_list_of_routes_for_ligolo(self, ip_range):
        self.list_of_routes_for_ligolo.append(ip_range)
        return
    
    def del_item_to_list_of_routes_for_ligolo(self, ip_range):
        self.list_of_routes_for_ligolo.remove(ip_range)
        return
        