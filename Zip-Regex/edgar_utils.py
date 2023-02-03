import pandas as pd
import re
import netaddr
from bisect import bisect

global ips
ips = pd.read_csv("ip2location.csv")

def lookup_region(ip):
    ip_num = re.sub(r"[a-zA-Z]", "0", ip)
    final_ip = int(netaddr.IPAddress(ip_num))
    idx = bisect(ips["low"], final_ip)
    return ips.at[idx-1, "region"]

global lines_list
lines_list = []

class Filing:
    def __init__(self, html):
        self.dates = re.findall(r"19\d{2}-\d{2}-\d{2}|20\d{2}-\d{2}-\d{2}", html)
        try:
            self.sic = int(re.findall(r"SIC=(\d{3,4})", html)[0])
        except:
            self.sic = None
        self.addresses = []
        for addr_html in re.findall(r'<div class="mailer">([\s\S]+?)</div>', html):
            lines = []
            for line in re.findall(r'<span class="mailerAddress">([\s\S]+?)</span>', addr_html):
                lines.append(line.strip())
            if lines:
                self.addresses.append("\n".join(lines))
    
    def state(self):
        for item in self.addresses:
            if re.search(r"([A-Z]{2}).?\d{5}", item):
                return re.search(r"([A-Z]{2}).?\d{5}", item).group(1)
        return None