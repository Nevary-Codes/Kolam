class Node:
    def __init__(self, url):
        self.url = url
        self.prev = None
        self.next = None

class BrowserHistory:
    def __init__(self):
        self.current = None

    def visit(self, url):
        new_node = Node(url)
        if self.current:
            # clear forward history
            self.current.next = None
            new_node.prev = self.current
            self.current.next = new_node
        self.current = new_node
        print(self.current.url, end="\n")

    def back(self):
        if self.current and self.current.prev:
            self.current = self.current.prev
        print(self.current.url, end="\n")

    def forward(self):
        if self.current and self.current.next:
            self.current = self.current.next
        print(self.current.url, end="\n")


# Driver code
n = int(input().strip())
browser = BrowserHistory()

for _ in range(n):
    command = input().strip()
    if command.startswith("Visit"):
        parts = command.split()
        url = parts[1] if len(parts) > 1 else ""   # avoid empty
        if url:
            browser.visit(url)
    elif command == "Back":
        browser.back()
    elif command == "Forward":
        browser.forward()