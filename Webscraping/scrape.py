# project: p3
# submitter: tjbuck
# partner: none
# hours: 20


from selenium.common.exceptions import NoSuchElementException
from IPython.core.display import Image, display
import pandas as pd
import requests
from collections import deque
import time

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        # 1. clear out visited set
        self.visited.clear()
        self.order.clear()
        # 2. start recursive search by calling dfs_visit
        return self.dfs_visit(node)

    def dfs_visit(self, node):
        if node in self.visited:
            return "(no value necessary)"
        self.visited.add(node)       
        self.order.append(node)
        child_list = self.go(node)
        for child in child_list:
            self.dfs_visit(child)
            
    def bfs_search(self, node):
        self.visited.clear()
        self.order.clear()
        return self.bfs_visit(node)
    
    def bfs_visit(self, node):
        todo = deque([node])
        self.order = [node]
        
        while len(todo) > 0:
            curr_node = todo.popleft()
            
            for child in self.go(curr_node):
                if child not in self.order:
                    todo.append(child)
                    self.order.append(child)
        return None
            
class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__() # call constructor method of parent class
        self.df = df

    def go(self, node):
        children = []
        # TODO: use `self.df` to determine what children the node has and append them
        for node, has_edge in self.df.loc[node].items():
            if has_edge == 1:
                children.append(node)
            
        return children

class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()
        self.msg = []
        
    def go(self, node):
        with open(f"file_nodes/{node}") as f:
            items = f.read()
        self.msg.append(items.split("\n")[0])
        children = items.split("\n")[1].split(",")
        return children
    
    def message(self):
        return "".join(self.msg)

import pandas as pd    
    
class WebSearcher(GraphSearcher):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.children = list()
        self.df_list = list()
        
    def go(self, start_url):
        self.driver.get(start_url)
        child = self.driver.find_elements(by = "tag name", value = "a")
        for link in child:
            self.children.append(link.get_attribute("href"))
        rows = []
        tbl = self.driver.find_element(by = "id", value = "locations-table")
        trs = tbl.find_elements(by = "tag name", value = "tr")
        header = trs[0].find_elements(by = "tag name", value = "th")
        header = [th.text for th in header]
        for tr in trs:
            row = tr.find_elements(by = "tag name", value = "td")
            row = [td.text for td in row]
            rows.append(row)

        self.df_list.append(pd.DataFrame(rows[1:], columns = header))
         
        return self.children
                             
    def table(self):
        big_df = pd.concat(self.df_list).reset_index(drop = True)
        big_df[["clue", "latitude", "longitude"]] = big_df[["clue", "latitude", "longitude"]].apply(pd.to_numeric)
        return big_df
          
def reveal_secrets(driver, url, travellog):
    item_list = []
    for item in travellog["clue"]:
        item = str(item)
        item_list.append(str(item))
    password = "".join(item_list)
    driver.get(url)
    search = driver.find_element(value = "password")
    button = driver.find_element(value = "attempt-button")
    search.clear()
    search.send_keys(password)
    button.click()
    
    attempts = 1
    for _ in range(attempts):
        try:
            new_button = driver.find_element(value = "securityBtn")
            new_button.click()
            break
        except NoSuchElementException:
            time.sleep(0.1)
    
    attempts = 15 
    for _ in range(attempts):
        try:
            location = driver.find_element(value = "location")
            image = driver.find_element(value = "image")
            image_source = requests.get(image.get_attribute("src"))
            with open("Current_Location.jpg", "wb") as f:
                f.write(image_source.content)
            break
        except NoSuchElementException:
            time.sleep(0.1)
            
    return location.text
                
         
                
            
   
        

    