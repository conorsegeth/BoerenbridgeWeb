bruh = {'conor': -8, "haley": 23, "papa": 45, "mama": 5}

bruh = dict(sorted(bruh.items(), key=lambda item: item[1], reverse=True))
print(bruh)